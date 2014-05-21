"""
All pytoeba models live here. Operations are done using custom managers
so be extra careful with the ORM.
"""

from django.db import models
from django.contrib.auth.models import User
from .choices import LANGS, LOG_ACTIONS


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
    link = models.ManyToManyField('self', through='Link', symmetrical=False)
    is_editable = models.BooleanField(default=True)
    has_correction = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # this field is for fast filtering based on sentence word length
    length = models.IntegerField(editable=False, blank=False, null=False)

    class Meta:
        # this multicolumn index should make accessing sentences/lang pairs
        # fast enough for real-time duplication
        index_together = [
            ['text', 'lang'],
        ]
        # this enforces uniqueness of sentences submitted, uses the above
        # index, will be adding test for it later.
        unique_together = (
            ('text', 'lang'),
        )

    def __unicode__(self):
        return '[%s - %s - %s]' % (self.text, self.lang, self.owner)


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

    def __unicode__(self):
        return '%s => %s' % (self.sentence.text, self.text)


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

    def __unicode__(self):
        return 'Tag ' + self.id


class LocalizedTag(models.Model):
    """
    Holds info about a tag localized in multiple languages and translated by
    being anchored to the same Tag instance (think same node in a tree).
    """
    tag = models.ForeignKey(Tag)
    text = models.CharField(max_length=100, blank=False, null=False)
    lang = models.CharField(
        max_length=4, choices=LANGS, blank=False, null=False
        )

    def __unicode__(self):
        return '%s - %s - %s' % (self.tag, self.lang, self.text)


class SentenceTag(models.Model):
    """
    Stores an entry every time a tag is associated with a sentence.
    """
    sentence = models.ForeignKey(Sentence)
    # for faster access to localizations
    tag = models.ForeignKey(Tag)
    # just to be sure which exact tag in which language got added
    localized_tag = models.ForeignKey(LocalizedTag)
    added_by = models.ForeignKey(User, editable=False)
    added_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return '<%s> %s' % (self.localized_tag.text, self.sentence.text)
