from pytoeba.models import Log, Sentence
from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from pytoeba.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
import pytest


@pytest.fixture
def log(db):
    testuser = User(username='user', password='pass')
    testuser.save()
    s1 = Sentence(
    hash_id='hash', lang='eng', text='test', sim_hash=123,
    added_by=testuser, length=1
    )
    s1.save()
    log = Log(sentence=s1, type='cad', done_by=testuser)
    return log


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
        assert log.done_by.username == 'user'
        assert log.change_set == None
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
