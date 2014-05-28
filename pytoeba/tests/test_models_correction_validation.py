from pytoeba.models import Correction
from pytest import raises
from django.db import IntegrityError
from pytoeba.tests.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('corr')
class TestCorrectionValidation():

    def test_default(db):
        assert len(Correction.objects.all()) == 0
        corr = Correction()
        assert raises(IntegrityError, corr.save)

    def test_minimum_defaults(db, corr):
        corr.save()
        assert len(Correction.objects.all()) == 1
        assert corr.hash_id == 'hash2'
        assert corr.sentence.text == 'test'
        assert corr.text == 'test2'
        assert corr.added_by.username == 'user'
        assert corr.added_on
        assert corr.modified_on
        assert corr.reason == ''

    def test_hash_id_validation(db, corr):
        db_validate_blank(corr, 'hash_id')
        db_validate_max_length(corr, 'hash_id', 40)
        db_validate_null(corr, 'hash_id')

    def test_sentence_validation(db, corr):
        with raises(ValueError):
            corr.sentence = None

    def test_text_validation(db, corr):
        db_validate_blank(corr, 'text')
        db_validate_max_length(corr, 'text', 500)
        db_validate_null(corr, 'text')

    def test_added_by_validation(db, corr):
        with raises(ValueError):
            corr.added_by = None

    def test_reason_validation(db, corr):
        db_validate_blank(corr, 'reason', True)
        db_validate_max_length(corr, 'reason', 200)
