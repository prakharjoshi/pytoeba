"""
All pytoeba models live here. Operations are done using custom managers
so be extra careful with the ORM.
"""

from django.db import models
from django.contrib.auth.models import User
from .choices import LANGS, LOG_ACTIONS
from .managers import SentenceManager, CorrectionManager, TagManager
from .utils import get_audio_path, get_user, sha1, truncated_sim_hash, now
from .exceptions import NotEditableError


class Sentence(models.Model):
    """
    Holds all relevant info about a sentence. Operation logic lives
    in pytoeba.managers and saving logic in pytoeba.utils. Using this
    model directly for CRUD operations without going through the custom
    manager can be disastrous.
    """
    sent_id = models.IntegerField(db_index=True, blank=True, null=True)
    # this is a unique identifier, sha1(user + text + lang)
    hash_id = models.CharField(
        db_index=True, max_length=40, blank=False, null=False, unique=True
        )
    lang = models.CharField(
        max_length=4, blank=False, null=False, choices=LANGS
        )
    text = models.CharField(max_length=500, blank=False, null=False)
    sim_hash = models.BigIntegerField(
        db_index=True, blank=False, null=False, editable=False
        )
    added_by = models.ForeignKey(
        User, editable=False, related_name='sent_addedby_set', blank=False,
        null=False
        )
    added_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)
    owner = models.ForeignKey(
        User, editable=False, related_name='sent_owner_set', null=True,
        default=None
        )
    links = models.ManyToManyField('self', through='Link', symmetrical=False)
    is_editable = models.BooleanField(default=True)
    has_correction = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # this field is for fast filtering based on sentence word length
    length = models.IntegerField(editable=False, blank=False, null=False)

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
        if self.text and self.lang and self.added_by:
            self.hash_id = sha1(self.text + self.lang + self.added_by.username)
        if self.text:
            self.length = len(self.text)
            self.sim_hash = truncated_sim_hash(self.text)
        if not self.id:
            self.owner = self.added_by
        if kwargs.has_key('update_fields'):
            kwargs['update_fields'] += ['modified_on']
            if 'text' in kwargs['update_fields']:
                kwargs['update_fields'] += ['hash_id', 'length', 'sim_hash']
        super(Sentence, self).save(*args, **kwargs)

    @classmethod
    def add(cls, text, lang='auto'):
        sent = cls.objects.add(text, lang)
        return sent

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
            target_id=self.hash_id
            )

    def delete(self):
        """
        Deletes the current sentence instance. Sets is_deleted
        to false and adds a Log entry.
        """
        user = get_user()
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
        Log.objects.create(sentence=self, type='srd', done_by=user)

    def lock(self):
        """
        Locks the current sentence instance by setting
        is_editable to false and adds a Log entry.
        """
        user = get_user()
        self.is_editable = False
        self.save(update_fields=['is_editable'])
        Log.objects.create(sentence=self, type='sld', done_by=user)

    def unlock(self):
        """
        Unlocks the current sentence instance by setting
        is_editable to true and adds a Log entry.
        """
        user = get_user()
        self.is_editable = True
        self.save(update_fields=['is_editable'])
        Log.objects.create(sentence=self, type='sul', done_by=user)

    def adopt(self):
        """
        Assigns the current sentence to a user by setting
        the user object on the owner field and adds a log
        entry.
        """
        user = get_user()
        self.owner = user
        self.save(update_fields=['owner'])
        Log.objects.create(sentence=self, type='soa', done_by=user)

    def change_language(self, lang):
        """
        Changes the language on the current sentence
        by updating the lang field and adds a log entry.
        """
        user = get_user()
        self.lang = lang
        self.save(update_fields=['lang'])
        Log.objects.create(sentence=self, type='slc', done_by=user)

    def release(self):
        """
        Releases the current sentence from the user's
        ownership by setting the owner field to null/none
        and adds a log entry.
        """
        user = get_user()
        self.owner = None
        self.save(update_fields=['owner'])
        Log.objects.create(sentence=self, type='sor', done_by=user)

    def link(self, sent):
        """
        Adds a link between two sentences bidirectionally and
        adds 2 log entries. Uses special methods in .utils to
        recalculate the graph if needed.
        """
        user = get_user()
        Link.objects.create(side1=self, side2=sent, level=1)
        Link.objects.create(side1=sent, side2=self, level=1)
        Log.objects.create(
            sentence=self, type='lad', done_by=user, target_id=sent.hash_id
            )
        Log.objects.create(
            sentence=sent, type='lad', done_by=user, target_id=self.hash_id
            )

    def bulk_link(self, sents):
        for sent in sents:
            self.link(sent)

    def unlink(self, sent):
        """
        Removes a link between two sentences bidirectionally and
        adds 2 log entries.
        """
        user = get_user()
        link = Link.objects.get(side1=self, side2=sent, level=1)
        link.delete()
        link = Link.objects.get(side1=sent, side2=self, level=1)
        link.delete()
        Log.objects.create(
            sentence=self, type='lrd', done_by=user, target_id=sent.hash_id
            )
        Log.objects.create(
            sentence=sent, type='lrd', done_by=user, target_id=self.hash_id
            )

    def bulk_unlink(self, sents):
        for sent in sents:
            self.unlink(sent)

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
            target_id=corr.hash_id
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
            target_id=corr.hash_id
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
            sentence=self, type='tad', done_by=user, target_id=tag.hash_id
            )

    def delete_tag(self, text):
        """
        Removes the tag from the current sentence by deleting
        the SentenceTag object storing this info. The actual
        Tag object is not affected.
        """
        loctag = LocalizedTag.objects.get(text=text)
        user = get_user()
        sentag = SentenceTag.objects.get(sentence=self, tag=loctag.tag)
        sentag.delete()
        Log.objects.create(
            sentence=self, type='trd', done_by=user,
            target_id=loctag.tag.hash_id
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
    level = models.IntegerField(editable=False, blank=False, null=False)

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
        max_length=3, editable=False, blank=False, null=False,
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
    # a hash_id in the target_id field. For tags the tag name
    # is stored. For links, nothing is stored in change_set
    # and the hash_id of the target sentence is stored in hash_id.
    # The level that is logged is always /only/ the direct link.
    # Otherwise for operations with no versioning required like
    # sentence adoption this field defaults to NULL.
    change_set = models.CharField(max_length=500, null=True, default=None)
    target_id = models.CharField(
        db_index=True, max_length=40, editable=False, blank=True, null=True,
        )

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
        db_index=True, max_length=40, blank=False, null=False, unique=True
        )
    sentence = models.ForeignKey(Sentence)
    text = models.CharField(max_length=500, blank=False, null=False)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)
    modified_on = models.DateTimeField(auto_now=True, editable=False)
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
        if self.text:
            self.hash_id = sha1(self.text + now())
        if not self.id and self.sentence:
            sent = self.sentence
            sent.has_correction = True
            sent.save(update_fields=['has_correction'])
        if kwargs.has_key('update_fields'):
            kwargs['update_fields'] += ['modified_on']
            if 'text' in kwargs['update_fields']:
                kwargs['update_fields'] += ['hash_id']
        super(Correction, self).save(*args, **kwargs)

    def edit(self, text):
        """
        Edits the text field on a given correction and
        logs the operation.
        """
        user = get_user()
        self.text = text
        self.save(update_fields=['text'])
        Log.objects.create(
            sentence=self.sentence, type='ced', done_by=user, change_set=text,
            target_id=self.hash_id
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
            target_id=self.hash_id
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
        Log.objects.create(
            sentence=self.sentence, type='crj', done_by=user,
            target_id=self.hash_id
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
        db_index=True, max_length=40, blank=False, null=False, unique=True
        )
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)

    objects = TagManager()

    def __unicode__(self):
        return 'Tag ' + str(self.id)

    def save(self, *args, **kwargs):
        """
        Autopopulates the hash_id.
        """
        username = self.added_by.username
        if username:
            self.hash_id = sha1(username + now())
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
        # this multicolumn index should make accessing sentences/lang pairs
        # fast enough for ensuring one localization per tag
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
        db_index=True, max_length=40, blank=False, null=False, unique=True
        )
    sentence = models.ForeignKey(Sentence)
    audio_file = models.FileField(upload_to=get_audio_path, null=False, blank=False)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return '[%s] %s' % (self.audio_file, self.sentence)
