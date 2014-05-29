from pytoeba.models import Sentence
from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from pytoeba.tests.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('sent')
class TestSentenceValidation():

    def test_default(db):
        assert len(Sentence.objects.all()) == 0
        sent = Sentence()
        assert raises(ObjectDoesNotExist, sent.save)

    def test_minimum_defaults(db, sent):
        sent.save()
        assert len(Sentence.objects.all()) == 1
        assert sent.hash_id == 'cb76d46f29a17e92fb9851dcd079e606819e1324'
        assert sent.lang == 'eng'
        assert sent.text == 'test'
        assert sent.sim_hash == 1461820776567902744
        assert sent.added_by.username == 'user'
        assert sent.length == 4
        assert sent.added_on
        assert sent.modified_on
        assert sent.is_editable == True
        assert sent.is_active == False
        assert sent.has_correction == False
        assert sent.is_deleted == False
        assert sent.links
        assert sent.owner == sent.added_by
        assert len(sent.links.all()) == 0

    def test_sent_id_validation(db, sent):
        sent.save()
        db_validate_blank(sent, 'sent_id', True)
        db_validate_null(sent, 'sent_id', True)
        sent.sent_id = ''
        assert raises(ValueError, sent.save)
        sent.sent_id = 'test'
        assert raises(ValueError, sent.save)

    def test_hash_id_validation(db, sent):
        db_validate_blank(sent, 'hash_id')
        db_validate_max_length(sent, 'hash_id', 40)
        # should be impossible to set this to a non-auto value
        sent.hash_id = None
        sent.save()
        assert sent.hash_id
        assert sent.hash_id == 'cb76d46f29a17e92fb9851dcd079e606819e1324'
        sent.text = ''
        db_validate_null(sent, 'hash_id')

    def test_lang_validation(db, sent):
        db_validate_blank(sent, 'lang')
        db_validate_max_length(sent, 'lang', 4)
        # a string not in LANGS shouldn't validate
        sent.lang = 'tt'
        assert raises(ValidationError, sent.full_clean)
        db_validate_null(sent, 'lang')

    def test_text_validation(db, sent):
        db_validate_blank(sent, 'text')
        db_validate_max_length(sent, 'text', 500)
        db_validate_null(sent, 'text')

    def test_sim_hash_validation(db, sent):
        # setting a non-auto value should be impossible
        sent.sim_hash = None
        sent.save()
        assert sent.sim_hash
        sent.text = ''
        db_validate_null(sent, 'sim_hash')

    def test_added_by_validation(db, sent):
        with raises(ValueError):
            sent.added_by = None

    def test_owner_validation(db, sent):
        # check if the reverse relation works and is empty
        assert sent.added_by.sent_owner_set
        assert len(sent.added_by.sent_owner_set.all()) == 0
        db_validate_null(sent, 'owner', True)

    def test_length_validation(db, sent):
        db_validate_blank(sent, 'length')
        # setting a value manually should be impossible
        sent.length = None
        sent.save()
        assert sent.length
        assert sent.length == 4
        sent.text = ''
        db_validate_null(sent, 'length')

    def test_text_lang_unique_validation(db, sent):
        sent.save()
        sent.id = None
        assert raises(IntegrityError, sent.save)
