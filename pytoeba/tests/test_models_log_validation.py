from pytoeba.models import Log
from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from pytoeba.tests.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('log')
class TestLogValidation():

    def test_default(db):
        assert len(Log.objects.all()) == 0
        log = Log()
        assert raises(IntegrityError, log.save)

    def test_minimum_defaults(db, log):
        log.save()
        assert len(Log.objects.all()) == 1
        assert log.sentence.text == 'test'
        assert log.type == 'cad'
        assert log.done_by.username == 'user'
        assert log.change_set == None
        assert log.target_id == 'hash'
        assert log.done_on

    def test_sentence_validation(db, log):
        with raises(ValueError):
            log.sentence = None

    def test_type_validation(db, log):
        db_validate_blank(log, 'type')
        db_validate_max_length(log, 'type', 3)
        # strings not in LOG_ACTION shouldn't validate
        log.type = 'tt'
        assert raises(ValidationError, log.full_clean)
        db_validate_null(log, 'type')

    def test_done_by_validation(db, log):
        with raises(ValueError):
            log.done_by = None

    def test_change_set_validation(db, log):
        db_validate_max_length(log, 'change_set', 500)
        db_validate_null(log, 'change_set', True)

    def test_target_id_validation(db, log):
        db_validate_max_length(log, 'target_id', 40)
        db_validate_null(log, 'target_id', True)
