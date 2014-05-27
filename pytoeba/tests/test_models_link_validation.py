from pytoeba.models import Link, Sentence
from pytest import raises
from django.db import IntegrityError
from django.contrib.auth.models import User
from pytoeba.test_helpers import db_validate_blank, db_validate_null
import pytest


@pytest.fixture
def link(db):
    testuser = User(username='user', password='pass')
    testuser.save()
    s1 = Sentence(
    hash_id='hash1', lang='eng', text='test1', sim_hash=123,
    added_by=testuser, length=1
    )
    s1.save()
    s2 = Sentence(
    hash_id='hash2', lang='eng', text='test2', sim_hash=123,
    added_by=testuser, length=1
    )
    s2.save()
    link = Link(side1=s1, side2=s2, level=1)
    return link


@pytest.mark.django_db
@pytest.mark.usefixture('link')
class TestLinkValidation():

    def test_default(db):
        assert len(Link.objects.all()) == 0
        link = Link()
        assert raises(IntegrityError, link.save)

    def test_minimum_defaults(db, link):
        link.save()
        assert len(Link.objects.all()) == 1
        assert link.side1.text == 'test1'
        assert link.side2.text == 'test2'
        assert link.level == 1

    def test_side1_validation(db, link):
        with raises(ValueError):
            link.side1 = None

    def test_side2_validation(db, link):
        with raises(ValueError):
            link.side2 = None

    def test_level_validation(db, link):
        db_validate_blank(link, 'level')
        db_validate_null(link, 'level')
