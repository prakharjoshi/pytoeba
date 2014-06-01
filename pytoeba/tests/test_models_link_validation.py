from pytoeba.models import Link
from pytest import raises
from django.db import IntegrityError
from pytoeba.tests.test_helpers import db_validate_blank, db_validate_null
import pytest


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
        assert link.side1.text == 'test'
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
