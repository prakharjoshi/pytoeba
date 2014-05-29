from pytoeba.models import Log, Correction
from pytoeba.utils import work_as
from django.db import IntegrityError
from copy import deepcopy
from pytest import raises
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('corr', 'user')
class TestCorrectionInstanceMethods():

    def test_correction_save(db, corr):
        corr.save()
        # test if update_fields makes autoadding of hash_id in save fail
        corr_old = deepcopy(corr)
        corr.text = 'test'
        corr.save(update_fields=['text'])
        assert corr.hash_id != corr_old.hash_id
        assert corr.modified_on != corr_old.modified_on
        # test if modified_on is changed even if text isn't involved
        corr_old = deepcopy(corr)
        corr.reason = 'test'
        corr.save(update_fields=['reason'])
        assert corr.modified_on != corr_old.modified_on
        # test if hashing is skipped if text is missing
        corr.text = None
        assert raises(IntegrityError, corr.save)

    def test_correction_edit(db, corr, user):
        corr.save()
        assert corr.text == 'test2'
        with work_as(user):
            corr.edit('test')
        assert corr.text == 'test'
        assert len(Log.objects.filter(type='ced')) == 1

    def test_correction_delete(db, corr, user):
        corr.save()
        sent = corr.sentence
        assert sent.has_correction == True
        assert len(Correction.objects.all()) == 1
        with work_as(user):
            corr.delete()
        assert len(Correction.objects.all()) == 0
        assert len(Log.objects.filter(type='crd')) == 1
        assert sent.has_correction == False

    def test_correction_accept(db, corr, user):
        corr.save()
        corr2 = deepcopy(corr)
        corr2.id = None
        corr2.text = 'test'
        corr2.save()
        sent = corr.sentence
        assert len(Correction.objects.all()) == 2
        with work_as(user):
            corr.accept()
        assert len(Correction.objects.all()) == 0
        assert sent.text == 'test2'
        assert len(Log.objects.filter(type='cac')) == 1
        assert len(Log.objects.filter(type='crj')) == 1

    def test_correction_reject(db, corr, user):
        corr.save()
        assert len(Correction.objects.all()) == 1
        with work_as(user):
            corr.reject()
        assert len(Correction.objects.all()) == 0
        assert len(Log.objects.filter(type='crj')) == 1

    def test_correction_force(db, corr, user):
        corr.save()
        corr2 = deepcopy(corr)
        corr2.id = None
        corr2.text = 'test'
        corr2.save()
        sent = corr.sentence
        assert len(Correction.objects.all()) == 2
        with work_as(user):
            corr.force()
        assert len(Correction.objects.all()) == 0
        assert sent.text == 'test2'
        assert len(Log.objects.filter(type='cfd')) == 1
        assert len(Log.objects.filter(type='crj')) == 1
