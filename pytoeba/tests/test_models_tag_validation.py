from pytoeba.models import Tag, LocalizedTag, SentenceTag, Sentence, PytoebaUser
from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from pytoeba.tests.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('tag')
class TestTagValidation():

    def test_default(db):
        assert len(Tag.objects.all()) == 0
        tag = Tag()
        assert raises(IntegrityError, tag.save)

    def test_minimum_defaults(db, tag):
        tag.save()
        assert len(Tag.objects.all()) == 1
        assert tag.id
        assert tag.hash_id
        assert isinstance(tag.hash_id, str)
        assert tag.added_by.username == 'user'
        assert tag.added_on

    def test_hash_id_validation(db, tag):
        db_validate_blank(tag, 'hash_id')
        db_validate_max_length(tag, 'hash_id', 40)
        user = PytoebaUser()
        user.save()
        tag.added_by = user

    def test_added_by_validation(db, tag):
        with raises(ValueError):
            tag.added_by = None


@pytest.mark.django_db
@pytest.mark.usefixture('loctag')
class TestLocalizedTagValidation():

    def test_default(db):
        assert len(LocalizedTag.objects.all()) == 0
        loctag = LocalizedTag()
        assert raises(IntegrityError, loctag.save)

    def test_minimum_defaults(db, loctag):
        loctag.save()
        assert len(LocalizedTag.objects.all()) == 1
        assert loctag.tag.hash_id
        assert loctag.text == 'test2'
        assert loctag.lang == 'eng'

    def test_tag_validation(db, loctag):
        with raises(ValueError):
            loctag.tag = None

    def test_text_validation(db, loctag):
        db_validate_blank(loctag, 'text')
        db_validate_max_length(loctag, 'text', 100)
        db_validate_null(loctag, 'text')

    def test_lang_validation(db, loctag):
        db_validate_blank(loctag, 'lang')
        db_validate_max_length(loctag, 'lang', 4)
        # a random iso code not in LANGS shouldn't validate
        loctag.lang = 'tt'
        assert raises(ValidationError, loctag.full_clean)
        db_validate_null(loctag, 'lang')


@pytest.mark.django_db
@pytest.mark.usefixture('sentag')
class TestSentenceTagValidation():

    def test_default(db):
        assert len(SentenceTag.objects.all()) == 0
        sentag = SentenceTag()
        assert raises(IntegrityError, sentag.save)

    def test_minimum_defaults(db, sentag):
        sentag.save()
        assert len(SentenceTag.objects.all()) == 1
        assert sentag.sentence.text == 'test'
        assert sentag.tag.hash_id
        assert sentag.added_by.username == 'user'
        assert sentag.added_on

    def test_sentence_validation(db, sentag):
        with raises(ValueError):
            sentag.sentence = None

    def test_tag_validation(db, sentag):
        with raises(ValueError):
            sentag.tag = None

    def test_added_by_validation(db, sentag):
        with raises(ValueError):
            sentag.added_by = None
