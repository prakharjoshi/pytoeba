"""
All pytoeba models live here. Operations are done using custom managers
so be extra careful with the ORM.
"""

from django.db import models
from django.conf import settings

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
