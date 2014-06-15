"""
All pytoeba models live here. Operations are done using custom managers
so be extra careful with the ORM.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import login
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import escape

from .choices import (
    LANGS, LOG_ACTIONS, PRIVACY, COUNTRIES, PROFICIENCY, VOTE_ON, USER_STATUS,
    MARKUPS
    )
from .managers import (
    SentenceManager, CorrectionManager, TagManager, PytoebaUserManager,
    MessageManager
    )
from .utils import (
    get_audio_path, get_user, now, sentence_presave, correction_presave,
    tag_presave, uuid, bulk_create, redraw_subgraph, bulk_create
    )
from .exceptions import NotEditableError

User = settings.AUTH_USER_MODEL

class Sentence(models.Model):
    """
    Holds all relevant info about a sentence. Operation logic lives
    in pytoeba.managers and saving logic in pytoeba.utils. Using this
    model directly for CRUD operations without going through the custom
    manager can be disastrous.
    """
    # for backwards compatibility with the current tatoeba
    # will be removed in the future
    sent_id = models.IntegerField(db_index=True, blank=True, null=True)
    # this is a unique identifier, uuid4()
    hash_id = models.CharField(
        db_index=True, max_length=32, blank=False, null=False, unique=True
        )
    lang = models.CharField(
        db_index=True, max_length=4, blank=False, null=False, choices=LANGS
        )
    text = models.CharField(max_length=500, blank=False, null=False)
    sim_hash = models.BigIntegerField(
        db_index=True, blank=False, null=False, editable=False
        )
    added_by = models.ForeignKey(
        User, editable=False, related_name='sent_addedby_set', blank=False,
        null=False
        )
    added_on = models.DateTimeField(
        db_index=True, auto_now_add=True, editable=False
        )
    modified_on = models.DateTimeField(
        db_index=True, auto_now=True, editable=False
        )
    owner = models.ForeignKey(
        User, editable=False, related_name='sent_owner_set', null=True,
        default=None
        )
    links = models.ManyToManyField('self', through='Link', symmetrical=False)
    is_editable = models.BooleanField(db_index=True, default=True)
    has_correction = models.BooleanField(db_index=True, default=False)
    is_active = models.BooleanField(db_index=True, default=False)
    is_deleted = models.BooleanField(db_index=True, default=False)
    # this field is for fast filtering based on sentence word length
    length = models.IntegerField(
        db_index=True, editable=False, blank=False, null=False
        )

    objects = SentenceManager()

    class Meta:
        # this multicolumn index should make accessing sentences/lang pairs
        # fast enough for real-time duplication
        index_together = [
            ['text', 'lang'],
        ]
        # this enforces uniqueness of sentences submitted, uses the above
        # index.
        unique_together = (
            ('text', 'lang'),
        )

    def __unicode__(self):
        return '[%s - %s - %s]' % (self.text, self.lang, self.owner)

    def save(self, *args, **kwargs):
        """
        Overrides django's default save() to autopopulate
        hash fields when text is added or is updated.
        """
        self = sentence_presave(self)

        if kwargs.has_key('update_fields'):
            kwargs['update_fields'] += ['modified_on']
            if 'text' in kwargs['update_fields']:
                kwargs['update_fields'] += ['length', 'sim_hash']

        super(Sentence, self).save(*args, **kwargs)

    def edit(self, text):
        """
        Edits the current sentence instance. If the
        sentence is locked throws an error. Updates
        the text field with a given one and adds
        a Log entry.
        """
        user = get_user()
        if not self.is_editable:
            raise NotEditableError
        self.text = text
        self.save(update_fields=['text'])
        Log.objects.create(
            sentence=self, type='sed', done_by=user, change_set=text,
            source_hash_id=self.hash_id, source_lang=self.lang
            )

    def delete(self):
        """
        Deletes the current sentence instance. Sets is_deleted
        to false and adds a Log entry.
        """
        user = get_user()
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
        Log.objects.create(
            sentence=self, type='srd', done_by=user, source_hash_id=self.hash_id,
            source_lang=self.lang
            )

    def lock(self):
        """
        Locks the current sentence instance by setting
        is_editable to false and adds a Log entry.
        """
        user = get_user()
        self.is_editable = False
        self.save(update_fields=['is_editable'])
        Log.objects.create(
            sentence=self, type='sld', done_by=user, source_hash_id=self.hash_id,
            source_lang=self.lang
            )

    def unlock(self):
        """
        Unlocks the current sentence instance by setting
        is_editable to true and adds a Log entry.
        """
        user = get_user()
        self.is_editable = True
        self.save(update_fields=['is_editable'])
        Log.objects.create(
            sentence=self, type='sul', done_by=user, source_hash_id=self.hash_id,
            source_lang=self.lang
            )

    def adopt(self):
        """
        Assigns the current sentence to a user by setting
        the user object on the owner field and adds a log
        entry.
        """
        user = get_user()
        self.owner = user
        self.save(update_fields=['owner'])
        Log.objects.create(
            sentence=self, type='soa', done_by=user, source_hash_id=self.hash_id,
            source_lang=self.lang
            )

    def release(self):
        """
        Releases the current sentence from the user's
        ownership by setting the owner field to null/none
        and adds a log entry.
        """
        user = get_user()
        self.owner = None
        self.save(update_fields=['owner'])
        Log.objects.create(
            sentence=self, type='sor', done_by=user, source_hash_id=self.hash_id,
            source_lang=self.lang
            )

    def change_language(self, lang):
        """
        Changes the language on the current sentence
        by updating the lang field and adds a log entry.
        """
        user = get_user()
        old_lang = self.lang
        self.lang = lang
        self.save(update_fields=['lang'])
        Log.objects.create(
            sentence=self, type='slc', done_by=user, source_hash_id=self.hash_id,
            source_lang=old_lang, target_lang=self.lang
            )

    @classmethod
    def _tuplize_links_unlinks(cls, source, target, user, _type='link'):
        link_tuples = []
        logs = []
        if _type == 'link':
            _type = 'lad'
        elif _type == 'unlink':
            _type = 'lrd'
        else:
            raise Exception("Operation not supported")

        for sent1 in source:
            for sent2 in target:
                link_tuples.append((sent1.id, sent2.id))
                link_tuples.append((sent2.id, sent1.id))
                logs.append(
                    Log(
                        sentence=sent1, type=_type, done_by=user,
                        source_hash_id=sent1.hash_id, source_lang=sent1.lang,
                        target_id=sent2.id, target_hash_id=sent2.hash_id,
                        target_lang=sent2.lang
                        )
                    )
                logs.append(
                    Log(
                        sentence=sent2, type=_type, done_by=user,
                        source_hash_id=sent2.hash_id, source_lang=sent2.lang,
                        target_id=sent1.id, target_hash_id=sent1.hash_id,
                        target_lang=sent1.lang
                        )
                    )

        return link_tuples, logs

    @classmethod
    def _link_or_unlink(
        cls, user, source_links=[], target_links=[], source_unlinks=[],
        target_unlinks=[]
            ):
        """
        Simple wrapper around pytoeba.utils.redraw_subgraph.
        Turns links into tuples and adds log entries.
        """

        links = []
        unlinks = []
        logs = []

        if source_links:
            links, link_logs = cls._tuplize_links_unlinks(
                                    source_links, target_links, user
                                    )

        if source_unlinks:
            unlinks, unlink_logs = cls._tuplize_links_unlinks(
                                        source_unlinks, target_unlinks, user,
                                        _type='unlink'
                                        )

        redraw_subgraph(links=links, unlinks=unlinks)
        logs.extend(link_logs)
        logs.extend(unlink_logs)
        bulk_create(logs)

    def link(self, sent):
        """
        Adds a link between two sentences bidirectionally and
        adds 2 log entries. Uses special methods in .utils to
        recalculate the graph if needed.
        """
        user = get_user()
        self._link_or_unlink(user, source_links=[self], target_links=[sent])

    def bulk_link(self, sents):
        """
        Bulk links the sentence instance to a sentence queryset
        """
        user = get_user()
        self._link_or_unlink(user, source_links=[self], target_links=sents)


    def unlink(self, sent):
        """
        Removes a link between two sentences bidirectionally and
        adds 2 log entries.
        """
        user = get_user()
        self._link_or_unlink(user, source_unlinks=[self], target_unlinks=[sent])

    def bulk_unlink(self, sents):
        user = get_user()
        self._link_or_unlink(user, source_unlinks=[self], target_unlinks=sents)

    def translate(self, text, lang='auto'):
        """
        Translates the current sentence by adding a new
        sentence and then linking it to the current
        sentence. Leaves logging to the add/link calls.
        """
        sent = self.add(text, lang)
        self.link(sent)

    def correct(self, text, reason=''):
        """
        Creates a correction object with the given text
        and automatically links it to the current sentence
        and logs the operation.
        """
        Correction.objects.add_to_obj(self, text, reason)

    def accept_correction(self, corr_id):
        """
        Takes the id of an existing correction linked to
        the current sentence and (through accept_corr_obj)
        sets the sentence text field to that correction's
        text field (applying it on the sentence). It then
        rejects other corrections that are submitted for
        this sentence at that time. Logs all operations.
        """
        corr = Correction.objects.get(hash_id=corr_id)
        self.accept_corr_obj(corr)

    def accept_corr_obj(self, corr):
        user = get_user()
        self.text = corr.text
        self.save(update_fields=['text'])
        Log.objects.create(
            sentence=self, type='cac', done_by=user, change_set=self.text,
            source_hash_id=self.hash_id, source_lang=self.lang,
            target_id=corr.id, target_hash_id=corr.hash_id
            )
        corr._base_delete()
        Correction.objects.filter(sentence=self).reject()
        self.has_correction = False
        self.save(update_fields=['has_correction'])

    def reject_correction(self, corr_id):
        """
        Removes a submitted correction by id. Logs the
        operation.
        """
        corr = Correction.objects.get(hash_id=corr_id)
        corr.reject()

    def force_correction(self, corr_id):
        """
        Essentially the same behavior as accept_correction
        except the log entry says it was forced by another
        user and not accepted by the owner himself.
        """
        corr = Correction.objects.get(hash_id=corr_id)
        self.force_corr_obj(corr)

    def force_corr_obj(self, corr):
        user = get_user()
        self.text = corr.text
        self.save(update_fields=['text'])
        Log.objects.create(
            sentence=self, type='cfd', done_by=user, change_set=corr.text,
            source_hash_id=self.hash_id, source_lang=self.lang,
            target_id=corr.id, target_hash_id=corr.hash_id
            )
        corr._base_delete()
        Correction.objects.filter(sentence=self).reject()
        self.has_correction = False
        self.save(update_fields=['has_correction'])

    def auto_force_correction(self):
        """
        Enforces one correction (earliest submitted by id) on the
        current sentence from the set of submitted corrections for
        it. Calls force_corr_obj and therefore shares the same
        behavior as force_correction. Mainly for use by help bots
        that run periodically.
        """
        corrs = Correction.objects.filter(sentence=self)
        corr = corrs[0]
        self.force_corr_obj(corr)

    def add_tag(self, text):
        """
        Adds an existing tag to the current sentence. Creates a
        SentenceTag object and logs the operation.
        """
        loctag = LocalizedTag.objects.get(text=text)
        self.add_tag_obj(loctag.tag)

    def add_new_tag(self, text, lang):
        """
        Adds a brand new tag (node) with the text given as a
        localization then adds it to the current sentence with
        a SentenceTag object. Logs the operation.
        """
        tag = Tag.objects.add_new(text, lang)
        self.add_tag_obj(tag)

    def add_tag_obj(self, tag):
        user = get_user()
        sentag = SentenceTag.objects.create(
            sentence=self, tag=tag, added_by=user
            )
        Log.objects.create(
            sentence=self, type='tad', done_by=user,
            source_hash_id=self.hash_id, source_lang=self.lang,
            target_id=sentag.tag.id, target_hash_id=sentag.tag.hash_id
            )

    def delete_tag(self, text):
        """
        Removes the tag from the current sentence by deleting
        the SentenceTag object storing this info. The actual
        Tag object is not affected.
        """
        user = get_user()
        loctag = LocalizedTag.objects.get(text=text)
        sentag = SentenceTag.objects.get(sentence=self, tag_id=loctag.tag_id)
        sentag.delete()
        Log.objects.create(
            sentence=self, type='trd', done_by=user,
            source_hash_id=self.hash_id, source_lang=self.lang,
            target_id=sentag.tag_id, target_hash_id=sentag.tag.hash_id
            )


class Link(models.Model):
    """
    Sentences are linked by a unidirectional link (applied bidirectionally for
    now). This table can be extended in the future to have metadata per link
    with more fields. Distances are stored in the level field and calculated
    on import, and recalculated by the sentence manager every time a link is
    altered in a subgraph.
    """
    side1 = models.ForeignKey(Sentence, related_name='side1_set')
    side2 = models.ForeignKey(Sentence, related_name='side2_set')
    level = models.IntegerField(
        db_index=True, editable=False, blank=False, null=False
        )

    class Meta:
        index_together = [
            ['side1', 'side2'],
            ['side1', 'level'],
            ['side2', 'level'],
            ['side1', 'side2', 'level'],
        ]

        unique_together = (
            ('side1', 'side2'),
        )

    def __unicode__(self):
        return '[%s] -(%s)-> [%s]' % (
            self.side1.text, self.level, self.side2.text
            )


class Log(models.Model):
    """
    This model links a sentence to some kind of operation, as defined
    in the LOG_ACTIONS tuple in pytoeba.choices. The logs attatched to
    each sentence is automatically generated from information stored
    here based on the LOG_MESSAGES dictionary. Extending the actions
    should be as simple as extending the LANGS tuple, add a new entry
    and restart the server.
    """
    sentence = models.ForeignKey(Sentence)
    type = models.CharField(
        db_index=True, max_length=3, editable=False, blank=False, null=False,
        choices=LOG_ACTIONS
        )
    done_by = models.ForeignKey(
        User, editable=False, related_name='log_doneby_set'
        )
    done_on = models.DateTimeField(auto_now_add=True, editable=False)
    # This is intended to be a free field for versioning
    # It's purely textual and should contain only one piece
    # of relevant information. For sentence/comment/corrections-
    # related changes, the text is stored. Reference to the
    # exact sentence/comment/correction edited is stored as
    # a hash_id in the source_hash_id field. For tags the tag name
    # is stored. For links, nothing is stored in change_set
    # and the hash_id of the target sentence is stored in hash_id.
    # The level that is logged is always /only/ the direct link.
    # Otherwise for operations with no versioning required like
    # sentence adoption this field defaults to NULL.
    change_set = models.CharField(max_length=500, null=True, default=None)
    # there should probably be a source_id here too that points to sentence_id
    # but making this work in django requires some ugly hack, so
    # settling for an ugly property i guess for now, no queryset support
    target_id = models.IntegerField(db_index=True, blank=True, null=True)
    source_hash_id = models.CharField(
        db_index=True, max_length=32, editable=False, blank=True, null=True,
        )
    target_hash_id = models.CharField(
        db_index=True, max_length=32, editable=False, blank=True, null=True,
        )
    source_lang = models.CharField(
        db_index=True, max_length=4, blank=True, null=True, choices=LANGS
        )
    target_lang = models.CharField(
        db_index=True, max_length=4, blank=True, null=True, choices=LANGS
        )

    class Meta:
        index_together = [
            ['source_lang', 'target_lang'],
        ]

    def __unicode__(self):
        return '%s on %s by %s change: %s' % (
            self.type, self.sentence, self.done_by, self.change_set
            )


class Correction(models.Model):
    """
    This holds a proposed correction to some sentence. It can be applied by the
    owner or rejected. Not rejecting it will force the correction at some point
    It can also be forced for whatever reason by moderators. Users adding it
    can also annotate it with a reason. It's designed so that a user can add
    multiple possible corrections to a single sentence all of which can be
    modified by either the owner or the original submitter before acception.
    As usual operations are abstracted on the manager and should go through it.
    """
    hash_id = models.CharField(
        db_index=True, max_length=32, blank=False, null=False, unique=True
        )
    sentence = models.ForeignKey(Sentence)
    text = models.CharField(max_length=500, blank=False, null=False)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(
        db_index=True, auto_now_add=True, editable=False
        )
    modified_on = models.DateTimeField(
        db_index=True, auto_now=True, editable=False
        )
    reason = models.CharField(max_length=200, blank=True)

    objects = CorrectionManager()

    def __unicode__(self):
        return '%s => %s' % (self.sentence.text, self.text)

    def save(self, *args, **kwargs):
        """
        Autopopulates the hash_id. Also handles adding
        the modified_on field to selective field updates.
        If the object is saved for the first time
        has_correction is handled on the sentence.
        """
        self = correction_presave(self)

        if kwargs.has_key('update_fields'):
            kwargs['update_fields'] += ['modified_on']

        super(Correction, self).save(*args, **kwargs)

    def edit(self, text):
        """
        Edits the text field on a given correction and
        logs the operation.
        """
        user = get_user()
        self.text = text
        self.save(update_fields=['text'])
        sent = self.sentence
        Log.objects.create(
            sentence=sent, type='ced', done_by=user, change_set=text,
            source_hash_id=sent.hash_id, source_lang=sent.lang,
            target_id=self.id, target_hash_id=self.hash_id
            )

    def _base_delete(self):
        super(Correction, self).delete()

    @classmethod
    def _get_corrections_by_sent(cls, sent):
        return cls.objects.filter(sentence=sent)

    def delete(self):
        """
        Deletes a correction. This is the analog of rejection but
        done by the submitter of the correction himself. Handles
        setting has_correction to false on the sentence when the
        last attached correction is deleted for that sentence.
        """
        user = get_user()
        self._base_delete()
        sent = self.sentence
        Log.objects.create(
            sentence=sent, type='crd', done_by=user,
            source_hash_id=sent.hash_id, source_lang=sent.lang,
            target_id=self.id, target_hash_id=self.hash_id
            )
        sent_corrs = self._get_corrections_by_sent(sent)
        if not sent_corrs:
            sent.has_correction = False
            sent.save(update_fields=['has_correction'])

    def reject(self):
        """
        Provides the base implementation for sentence.reject_correction
        and sentence.reject_corr_obj. They should all behave similarly.
        """
        user = get_user()
        self._base_delete()
        sent = self.sentence
        Log.objects.create(
            sentence=sent, type='crj', done_by=user,
            source_hash_id=sent.hash_id, source_lang=sent.lang,
            target_id=self.id, target_hash_id=self.hash_id
            )

    def accept(self):
        """
        Uses sentence.accept_corr_obj as its base implementation
        as the opposite would've entailed a performance penalty.
        Should have the same behavior as sentence.accept_correction.
        """
        # a read is probably faster than a join
        # use the ones proxied on sentence
        self.sentence.accept_corr_obj(self)

    def force(self):
        """
        Proxy to the implementation on Sentence. Same behavior as
        sentence.force_correction.
        """
        self.sentence.force_corr_obj(self)


class Tag(models.Model):
    """
    This is probably a pretty desperate attempt at trying not to replicate
    the sentences table and api. This table anchors all tags that are directly
    related, allowing for localizations to be accessed from a common point.
    This design allows for fast access and normalization but quickly
    complicates things when users don't realize that a tag could've been
    translated and not added. Merging the two nodes would require handling
    a number of edge cases. All involving remapping the tag links from one
    node to another and removing one of them.
    """
    hash_id = models.CharField(
        db_index=True, max_length=32, blank=False, null=False, unique=True
        )
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(
        db_index=True, auto_now_add=True, editable=False
        )

    objects = TagManager()

    def __unicode__(self):
        return 'Tag ' + str(self.id)

    def save(self, *args, **kwargs):
        """
        Autopopulates the hash_id.
        """
        self = tag_presave(self)

        super(Tag, self).save()

    def get_localization(self, lang):
        """
        Gets a localization for this tag by language.
        """
        return LocalizedTag.objects.get(tag=self, lang=lang)

    def get_all_localizations(self):
        """
        Gets all localizations referencing this tag.
        """
        return LocalizedTag.objects.filter(tag=self)

    def merge(self, tag):
        """
        Remaps localizations and tagged sentences from one
        tag to another then removes then now defunct tag.
        This operation isn't logged for now.
        """
        sentags = SentenceTag.objects.filter(tag=tag)
        sentags.update(tag=self)
        loctags = LocalizedTag.objects.filter(tag=tag)
        loctags.update(tag=self)
        tag.delete()

    def translate(self, text, lang):
        """
        Adds a localization to an existing tag. Not logged yet.
        """
        LocalizedTag.objects.create(tag=self, text=text, lang=lang)


class LocalizedTag(models.Model):
    """
    Holds info about a tag localized in multiple languages and translated by
    being anchored to the same Tag instance (think same node in a tree).
    """
    tag = models.ForeignKey(Tag)
    text = models.CharField(
        max_length=100, blank=False, null=False, db_index=True
        )
    lang = models.CharField(
        max_length=4, choices=LANGS, blank=False, null=False
        )

    class Meta:
        index_together = [
            ['tag', 'lang'],
        ]
        # this enforces one localization per tag on the db level, uses the
        # above index.
        unique_together = (
            ('tag', 'lang'),
        )

    def __unicode__(self):
        return '%s - %s - %s' % (self.tag, self.lang, self.text)


class SentenceTag(models.Model):
    """
    Stores an entry every time a tag is associated with a sentence.
    """
    sentence = models.ForeignKey(Sentence)
    tag = models.ForeignKey(Tag)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        index_together = [
            ['sentence', 'tag'],
        ]
        # this enforces one unique tag per sentence on the db level, uses the
        # above index.
        unique_together = (
            ('sentence', 'tag'),
        )

    def __unicode__(self):
        return '<%s> %s' % (self.tag, self.sentence.text)


class Audio(models.Model):
    """
    Stores a reference to the audio file on disk. Uses the sentence id
    to name them on upload. Respects your MEDIA_ROOT settings. One
    sentence can have multiple audio files by multiple users. It also
    can store some metadata like bitrate and accent in the future
    These can be automatically extracted from the file metadata on upload
    and from the user's profile info.
    """
    hash_id = models.CharField(
        db_index=True, max_length=32, blank=False, null=False, unique=True
        )
    sentence = models.ForeignKey(Sentence)
    audio_file = models.FileField(upload_to=get_audio_path, null=False, blank=False)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return '[%s] %s' % (self.audio_file, self.sentence)


class PytoebaUser(AbstractUser):
    """
    Centralizes all info relating to users and their profile
    info. Inherits from the auth model's AbstractUser class
    and therefore behaves the way django's User model would
    and is fully compatible with django.contrib.auth system.
    """
    email_unconfirmed = models.EmailField(blank=True, default='test@test.com')
    email_confirmation_key = models.CharField(max_length=40, blank=True)
    email_confirmation_key_created_on = models.DateTimeField(
        blank=True, null=True
        )
    privacy = models.CharField(
        max_length=1, choices=PRIVACY, default='o', blank=False,
        null=False
        )
    country = models.CharField(
        max_length=2, choices=COUNTRIES, blank=True, null=True
        )
    birthday = models.DateTimeField(blank=True, null=True)
    # This is strictly for filtering, permissions are handled
    # exclusively through links to django.contrib.auth.Group
    status = models.CharField(
        db_index=True, max_length=1, choices=USER_STATUS, default='u',
        editable=False, null=False
        )
    with_status_vote_count = models.IntegerField(default=0)
    against_status_vote_count = models.IntegerField(default=0)
    about_text = models.TextField()
    about_markup = models.CharField(max_length=2, choices=MARKUPS, default='')
    about_html = models.TextField()

    objects = PytoebaUserManager()

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.about_text:
            self.about_text = escape(self.about_text)
            self.about_html = markup_to_html(
                self.about_text, self.about_markup
                )
        super(PytoebaUser, self).save(*args, **kwargs)

    def activate_account(self):
        """
        Sets user to active. Not to be used
        directly.
        """
        if not self.is_active:
            self.is_active = True
            self.save(update_fields=['is_active'])

    def deactivate_account(self):
        """
        Sets user to inactive. Not to be used directly.
        """
        if self.is_active:
            self.is_active = False
            self.save(update_fields=['is_active'])

    def minimum_profile_filled(self):
        if self.is_active:
            return True

        if self.username and self.email_confirmed and \
            len(self.userlang_set.all()) >= 1:
            self.activate_account()
            return True

        return False

    @property
    def email_confirmed(self):
        """
        Checks if there's an unconfirmed email
        pending. An empty string would return
        True.
        """
        return not bool(self.email_unconfirmed)

    def generate_email_confirmation_key(self):
        """
        Generates an activation key using a salted
        sha1 hash.
        """
        key = uuid4() + uuid4()
        self.email_confirmation_key = key
        self.email_confirmation_key_created_on = now()

    def reissue_email_confirmation_key(self):
        """
        Regenerates an activation key and resets the
        activation period for the user.
        """
        self.generate_email_confirmation_key()
        self.date_joined = now()
        self.save()

    @property
    def email_confirmation_key_expired(self):
        """
        Checks if the confirmation code has been issued
        for too long to be accepted. The grace period
        is defined in settings.CONFIRMATION_PERIOD.
        """
        expiration_date = self.date_joined + timedelta(settings.CONFIRMATION_PERIOD)
        if now() >= expiration_date:
            return True
        return False

    def confirm_email(self, key):
        """
        Confirms the user's email given the confirmation
        key sent to his e-mail.
        """
        if self.email_confirmation_key_expired:
            return False
        
        if self.email_confirmation_key == key:
            self.email_unconfirmed = ''
            self.save(update_fields=['email_unconfirmed'])
            return True

        return False

    def reset_password(old, new):
        """
        Resets the user password given the old
        password. Returns True if successful.
        """
        if self.check_password(old):
            self.set_password(new)
            return True
        return False

    def send_confirmation_email(self):
        """
        Sends an email to confirm the email address. In case
        there's already a confirmed e-mail, an old message
        is sent to that e-mail to notify the user of the change
        then sends a new message with the confirmation key to
        the new e-mail.
        """
        context = {'user': self,
                  'new_email': self.email_unconfirmed,
                  'protocol': get_protocol(),
                  'confirmation_key': self.email_confirmation_key,
                  'site': Site.objects.get_current()}

        subject_old = render_to_string(
            'emails/confirmation_email_subject_old.txt', context
            )
        subject_old = ''.join(subject_old.splitlines())

        message_old = render_to_string(
            'emails/confirmation_email_message_old.txt', context
            )

        if self.email:
            self.email_user(subject_old, message_old, settings.DEFAULT_FROM_EMAIL)

        subject_new = render_to_string(
            'emails/confirmation_email_subject_new.txt', context
            )
        subject_new = ''.join(subject_new.splitlines())

        message_new = render_to_string(
            'emails/confirmation_email_message_new.txt', context
            )

        send_mail(
            subject_new, message_new, settings.DEFAULT_FROM_EMAIL,
            [self.email_unconfirmed]
            )

    def change_email(self, email):
        """
        Changes the email address for a user. A user needs
        to verify this new email address before it becomes
        active.
        """
        self.email_unconfirmed = email
        self.generate_email_confirmation_key()
        self.save()
        self.send_confirmation_email()

    def verify_lang(self, lang):
        user_lang = UserLang.objects.get(user=self, lang=lang)
        self._verify_lang_obj(user_lang)

    def _verify_lang_obj(self, user_lang):
        if user_lang.is_trusted:
            return True
        if user_lang.with_vote_count >= REQUIRED_LANG_VOTES \
        and not user_lang.is_trusted:
            user_lang.is_trusted = True
            user_lang.save(update_fields=['is_trusted'])
            return True
        return False

    def add_lang_vote(self, user, lang, is_with=True):
        user_lang = UserLang.objects.get(user=user, lang=lang)
        vote = UserVote.objects.create(
            user=self, type='lp', is_with=is_with, target_id=user_lang.id
            )
        if is_with:
            user_lang.with_vote_count += 1
            user_lang.save(update_fields=['with_vote_count'])
        else:
            user_lang.against_vote_count += 1
            user_lang.save(update_fields=['against_vote_count'])

        self._verify_lang_obj(user_lang)

    def verify_status(self, status='t'):
        return self._verify_status_obj(self, status)

    @classmethod
    def _verify_status_obj(cls, user, status='t'):
        return cls.objects._verify_status_obj(user, status)

    def add_status_vote(self, user, status='t', is_with=True):
        vote = UserVote.objects.create(
        user=self, type='sp', is_with=is_with, target_id=user.id
        )
        if is_with:
            user.with_status_vote_count += 1
            user.save(update_fields=['with_status_vote_count'])
        else:
            user.against_status_vote_count += 1
            user.save(update_fields=['against_status_vote_count'])

        self._verify_status_obj(user, status)

    @classmethod
    def authenticate(cls, username, password):
        return cls.objects.authenticate(username, password)

    def login(self, request):
        login(self, request)

# mother of terrible hacks, blame django for not letting me override
# the damn field
PytoebaUser._meta.get_field('is_active').default = False


class UserLang(models.Model):
    """
    Stores languages that users claim they know and has
    links to the votes other users cast to confirm their
    claims. Use this through the user manager api and
    not directly.
    """
    user = models.ForeignKey(User, editable=False, related_name='userlang_set')
    lang = models.CharField(
        max_length=4, choices=LANGS, blank=False, null=False, db_index=True
        )
    proficiency = models.CharField(
        max_length=1, choices=PROFICIENCY, blank=False, null=False
        )
    is_trusted = models.BooleanField(default=False)
    votes = models.ManyToManyField('UserVote', editable=False)
    with_vote_count = models.IntegerField(
        default=0, editable=False, null=False
        )
    against_vote_count = models.IntegerField(
        default=0, editable=False, null=False
        )

    class Meta:
        # this multicolumn index should make accessing user/lang pairs
        # fast enough for ensuring one unique language per user
        index_together = [
            ['user', 'lang'],
        ]
        # this enforces one unique lang per user on the db level, uses the
        # above index.
        unique_together = (
            ('user', 'lang'),
        )

    def realign_vote_count(self):
        self.with_vote_count = UserVote.objects\
            .filter(id=self.id, is_with=True).count()
        self.against_vote_count = UserVote.objects\
            .filter(id=self.id, is_with=False).count()
        self.save(update_fields=['with_vote_count', 'against_vote_count'])


class UserVote(models.Model):
    """
    Keeps track of all votes cast by users. The type field
    stores what the vote is about. The target_id references
    some object, so it's generic and can be used for Sentences
    UserLangs or anything else in the future. Use this model
    through the user manager api.
    """
    user = models.ForeignKey(User, editable=False)
    type = models.CharField(
        max_length=2, choices=VOTE_ON, blank=False, null=False
        )
    is_with = models.BooleanField(default=True)
    target_id = models.IntegerField()

    class Meta:
        index_together = [
            ['user', 'type', 'target_id'],
        ]
        # enforces 1 unique vote type per object for each voter
        unique_together = (
            ('user', 'type', 'target_id'),
        )


class Message(models.Model):
    """
    A private message from a user to another.
    """
    subject = models.CharField(max_length=120)
    body = models.TextField()
    sender = models.ForeignKey(User, related_name='sent_messages')
    recipient = models.ForeignKey(
        User, related_name='received_messages', null=True, blank=True
        )
    parent_msg = models.ForeignKey(
        'self', related_name='next_messages', null=True, blank=True
        )
    sent_on = models.DateTimeField(null=True, blank=True)
    read_on = models.DateTimeField(null=True, blank=True)
    replied_on = models.DateTimeField(null=True, blank=True)
    sender_deleted_on = models.DateTimeField(
        db_index=True, null=True, blank=True
        )
    recipient_deleted_on = models.DateTimeField(
        db_index=True, null=True, blank=True
        )

    objects = MessageManager()
    
    class Meta:
        index_together = [
            ['recipient', 'recipient_deleted_on'],
            ['sender', 'sender_deleted_on'],
        ]

    def __unicode__(self):
        return self.subject

    def save(self, **kwargs):
        if not self.id:
            self.sent_on = now()
        super(Message, self).save(**kwargs)

    def new(self):
        """
        Returns whether the recipient has read the message or not
        """
        if not self.read_on:
            return False
        return True

    def replied(self):
        """
        Returns whether the recipient has written a reply to this message
        """
        return bool(self.replied_on)

    def mark_read(self):
        """
        Marks a message as read.
        """
        if not self.read_on:
            self.read_on = now()
            self.save(update_fields=['read_on'])

    def mark_unread(self):
        """
        Marks a message as unread.
        """
        if self.read_at:
            self.read_at = None
            self.save(update_fields=['read_on'])
