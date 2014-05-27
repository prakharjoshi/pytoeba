from pytoeba.models import Tag, LocalizedTag, SentenceTag, Sentence
from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from pytoeba.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.fixture
def tag(db):
    testuser = User(username='user', password='pass')
    testuser.save()
    s1 = Sentence(
        hash_id='hash', lang='eng', text='test', sim_hash=123,
        added_by=testuser, length=1
        )
    s1.save()
    tag = Tag(hash_id='hash2', added_by=testuser)
    return tag


@pytest.mark.django_db
class TestTagValidation():

    def test_default(db):
        assert len(Tag.objects.all()) == 0
        tag = Tag()
        assert raises(IntegrityError, tag.save)

    def test_minimum_defaults(db, tag):
        tag.save()
        assert len(Tag.objects.all()) == 1
        assert tag.id
        assert tag.hash_id == 'hash2'
        assert tag.added_by.username == 'user'
        assert tag.added_on

    def test_hash_id_validation(db, tag):
        db_validate_blank(tag, 'hash_id')
        db_validate_max_length(tag, 'hash_id', 40)
        db_validate_null(tag, 'hash_id')

    def test_added_by_validation(db, tag):
        with raises(ValueError):
            tag.added_by = None


@pytest.fixture
def loctag(db):
    testuser = User(username='user', password='pass')
    testuser.save()
    s1 = Sentence(
        hash_id='hash', lang='eng', text='test', sim_hash=123,
        added_by=testuser, length=1
    )
    s1.save()
    tag = Tag(hash_id='hash2', added_by=testuser)
    tag.save()
    loctag = LocalizedTag(tag=tag, text='test2', lang='eng')
    return loctag


@pytest.mark.django_db
class TestLocalizedTagValidation():

    def test_default(db):
        assert len(LocalizedTag.objects.all()) == 0
        loctag = LocalizedTag()
        assert raises(IntegrityError, loctag.save)

    def test_minimum_defaults(db, loctag):
        loctag.save()
        assert len(LocalizedTag.objects.all()) == 1
        assert loctag.tag.hash_id == 'hash2'
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


@pytest.fixture
def sentag(db):
    testuser = User(username='user', password='pass')
    testuser.save()
    s1 = Sentence(
        hash_id='hash', lang='eng', text='test', sim_hash=123,
        added_by=testuser, length=1
    )
    s1.save()
    tag = Tag(hash_id='hash2', added_by=testuser)
    tag.save()
    loctag = LocalizedTag(tag=tag, text='test2', lang='eng')
    loctag.save()
    sentag = SentenceTag(
        sentence=s1, localized_tag=loctag, tag=tag, added_by=testuser
        )
    return sentag


@pytest.mark.django_db
class TestSentenceTagValidation():

    def test_default(db):
        assert len(SentenceTag.objects.all()) == 0
        sentag = SentenceTag()
        assert raises(IntegrityError, sentag.save)

    def test_minimum_defaults(db, sentag):
        sentag.save()
        assert len(SentenceTag.objects.all()) == 1
        assert sentag.sentence.text == 'test'
        assert sentag.localized_tag.text == 'test2'
        assert sentag.tag.hash_id == 'hash2'
        assert sentag.added_by.username == 'user'
        assert sentag.added_on

    def test_sentence_validation(db, sentag):
        with raises(ValueError):
            sentag.sentence = None

    def test_localized_tag_validation(db, sentag):
        with raises(ValueError):
            sentag.localized_tag = None

    def test_tag_validation(db, sentag):
        with raises(ValueError):
            sentag.tag = None

    def test_added_by_validation(db, sentag):
        with raises(ValueError):
            sentag.added_by = None
