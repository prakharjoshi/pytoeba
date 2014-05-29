from pytoeba.models import Log, Sentence, Link, Tag
from pytoeba.utils import work_as
from pytoeba.exceptions import NotEditableError
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from pytest import raises
from copy import deepcopy
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('sent', 'user')
class TestSentenceInstanceMethods():

    def test_sentence_delete(db, sent, user):
        sent.save()
        assert sent.is_deleted == False
        with work_as(user):
            sent.delete()
        assert sent.is_deleted == True
        log = Log.objects.get(sentence=sent)
        assert log.done_by == user
        assert log.type == 'srd'

    def test_sentence_save(db, sent):
        sent.save()
        # test if update_fields makes autoadding of hash_id in save fail
        sent.text = 'test2'
        sent_old = deepcopy(sent)
        sent.save(update_fields=['text'])
        sent_new = Sentence.objects.filter(text='test2')[0]
        assert sent_new.hash_id != sent_old.hash_id
        assert sent_new.sim_hash != sent_old.sim_hash
        assert sent_new.length != sent_old.length
        assert sent_new.modified_on != sent_old.modified_on
        # test if update_fields modifies the date on modified_on if text
        # isn't involved as well
        sent.is_deleted = True
        sent_old = deepcopy(sent)
        sent.save(update_fields=['is_deleted'])
        sent_new = Sentence.objects.filter(is_deleted=True)[0]
        assert sent_new.modified_on != sent_old.modified_on
        # test if hashing is skipped if crucial field is missing
        # the db should catch this problem
        sent.text = None
        assert raises(IntegrityError, sent.save)

    def test_sentence_edit(db, sent, user):
        sent.save()
        assert sent.text == 'test'
        with work_as(user):
            sent.edit('test2')
        assert sent.text == 'test2'
        with work_as(user):
            sent.lock()
            assert raises(NotEditableError, sent.edit, '')

    def test_sentence_lock(db, sent, user):
        sent.save()
        assert sent.is_editable == True
        with work_as(user):
            sent.lock()
        assert sent.is_editable == False

    def test_sentence_unlock(db, sent, user):
        sent.save()
        with work_as(user):
            sent.lock()
        assert sent.is_editable == False
        with work_as(user):
            sent.unlock()
        assert sent.is_editable == True

    def test_sentence_adopt(db, sent, user):
        sent.save() # first save will set user as the owner
        sent.owner = None
        sent.save()
        assert sent.owner == None
        with work_as(user):
            sent.adopt()
        assert sent.owner == user

    def test_sentence_release(db, sent, user):
        sent.save()
        assert sent.owner == user
        with work_as(user):
            sent.release()
        assert sent.owner == None

    def test_sentence_change_language(db, sent, user):
        sent.save()
        assert sent.lang == 'eng'
        with work_as(user):
            sent.change_language('fra')
        assert sent.lang == 'fra'

    def test_sentence_link(db, sent, user, sent2):
        sent.save()
        sent2.save()
        assert len(Link.objects.all()) == 0
        with work_as(user):
            sent.link(sent2)
        assert len(Link.objects.all()) == 2
        link = Link.objects.all()[0]
        assert link.side1 == sent
        assert link.side2 == sent2
        link = Link.objects.all()[1]
        assert link.side1 == sent2
        assert link.side2 == sent

    def test_sentence_unlink(db, sent, user, sent2):
        sent.save()
        sent2.save()
        with work_as(user):
            sent.link(sent2)
        assert len(Link.objects.all()) == 2
        with work_as(user):
            sent.unlink(sent2)
        assert len(Link.objects.all()) == 0

    def test_sentence_translate(db, sent, user):
        sent.save()
        assert len(Link.objects.all()) == 0
        with work_as(user):
            sent.translate('test2', 'eng')
        links = Link.objects.all()
        assert len(links) == 2
        assert links[0].side2.text == 'test2'

    def test_sentence_correct(db, sent, user):
        sent.save()
        assert len(sent.correction_set.all()) == 0
        with work_as(user):
            sent.correct('some correction')
        assert len(sent.correction_set.all()) == 1
        corr = sent.correction_set.all()[0]
        assert corr.text == 'some correction'

    def test_sentence_accept_correction(db, sent, user):
        sent.save()
        with work_as(user):
            sent.correct('some correction')
            sent.correct('some other correction')
        assert len(sent.correction_set.all()) == 2
        corr_id = sent.correction_set.all()[0].hash_id
        with work_as(user):
            sent.accept_correction(corr_id)
        assert len(sent.correction_set.all()) == 0
        assert sent.text == 'some correction'
        assert len(Log.objects.filter(type='cac')) == 1
        assert len(Log.objects.filter(type='crj')) == 1

    def test_sentence_reject_correction(db, sent, user):
        sent.save()
        with work_as(user):
            sent.correct('some correction')
        assert len(sent.correction_set.all()) == 1
        corr_id = sent.correction_set.all()[0].hash_id
        with work_as(user):
            sent.reject_correction(corr_id)
        assert len(sent.correction_set.all()) == 0
        assert len(Log.objects.filter(type='crj')) == 1

    def test_sentence_force_correction(db, sent, user):
        sent.save()
        with work_as(user):
            sent.correct('some correction')
            sent.correct('some other correction')
        assert len(sent.correction_set.all()) == 2
        corr_id = sent.correction_set.all()[0].hash_id
        with work_as(user):
            sent.force_correction(corr_id)
        assert len(sent.correction_set.all()) == 0
        assert sent.text == 'some correction'
        assert len(Log.objects.filter(type='cfd')) == 1

    def test_sentence_auto_force_correction(db, sent, user):
        sent.save()
        with work_as(user):
            sent.correct('some correction')
            sent.correct('some other correction')
        assert len(sent.correction_set.all()) == 2
        with work_as(user):
            sent.auto_force_correction()
        assert len(sent.correction_set.all()) == 0
        assert sent.text == 'some correction'
        assert len(Log.objects.filter(type='cfd')) == 1
        assert len(Log.objects.filter(type='crj')) == 1

    def test_sentence_add_new_tag(db, sent, user):
        sent.save()
        assert len(sent.sentencetag_set.all()) == 0
        with work_as(user):
            sent.add_new_tag('OK', 'eng')
        assert len(sent.sentencetag_set.all()) == 1
        sentag = sent.sentencetag_set.all()[0]
        assert sentag.tag.get_localization('eng').text == 'OK'
        assert sentag.sentence == sent

    def test_sentence_add_tag(db, sent, user):
        sent.save()
        assert raises(ObjectDoesNotExist, sent.add_tag, 'OK')
        with work_as(user):
            Tag.objects.add_new('OK', 'eng')
        assert len(sent.sentencetag_set.all()) == 0
        with work_as(user):
            sent.add_tag('OK')
        assert len(sent.sentencetag_set.all()) == 1
        sentag = sent.sentencetag_set.all()[0]
        assert sentag.tag.get_localization('eng').text == 'OK'
        assert sentag.sentence == sent

    def test_sentence_delete_tag(db, sent, user):
        sent.save()
        assert raises(ObjectDoesNotExist, sent.delete_tag, 'OK')
        with work_as(user):
            sent.add_new_tag('OK', 'eng')
        assert len(sent.sentencetag_set.all()) == 1
        with work_as(user):
            sent.delete_tag('OK')
        assert len(sent.sentencetag_set.all()) == 0

@pytest.mark.django_db
@pytest.mark.usefixture('sent', 'user')
class TestSentenceQuerySetMethods():

    def test_sentence_qs_all(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.delete()
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().all()) == 1
        assert Sentence.objects.filter().all()[0] == sent2

    def test_sentence_qs_deleted(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.delete()
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().deleted()) == 1
        assert Sentence.objects.filter().deleted()[0] == sent

    def test_sentence_qs_active(db, sent, user, sent2):
        sent.save()
        sent2.is_active = True
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().active()) == 1
        assert Sentence.objects.filter().active()[0] == sent2

    def test_sentence_qs_inactive(db, sent, user, sent2):
        sent.save()
        sent2.is_active = True
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().inactive()) == 1
        assert Sentence.objects.filter().inactive()[0] == sent

    def test_sentence_qs_locked(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.lock()
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().locked()) == 1
        assert Sentence.objects.filter().locked()[0] == sent

    def test_sentence_qs_unlocked(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.lock()
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().unlocked()) == 1
        assert Sentence.objects.filter().unlocked()[0] == sent2

    def test_sentence_qs_orphan(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.release()
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().orphan()) == 1
        assert Sentence.objects.filter().orphan()[0] == sent

    def test_sentence_qs_needs_correction(db, sent, user, sent2):
        sent.save()
        with work_as(user):
            sent.correct('testing')
        sent2.save()
        assert len(Sentence.objects.filter()) == 2
        assert len(Sentence.objects.filter().needs_correction()) == 1
        assert Sentence.objects.filter().needs_correction()[0] == sent

    def test_sentence_qs_delete(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.all()
        assert len(sents) == 2
        with work_as(user):
            sents.delete()
        assert len(Sentence.objects.all()) == 0
        sents = Sentence.objects.filter(is_deleted=True)
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2

    def test_sentence_qs_lock(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.filter(is_editable=True)
        assert len(sents) == 2
        with work_as(user):
            sents.lock()
        sents = Sentence.objects.filter(is_editable=False)
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2

    def test_sentence_qs_unlock(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.all()
        with work_as(user):
            sents.lock()
        sents = Sentence.objects.filter(is_editable=False)
        assert len(sents) == 2
        with work_as(user):
            sents.unlock()
        assert len(Sentence.objects.all())
        sents = Sentence.objects.filter(is_editable=True)
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2

    def test_sentence_qs_release(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.all()
        assert len(sents) == 2
        with work_as(user):
            sents.release()
        sents = Sentence.objects.filter(owner=None)
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2

    def test_sentence_qs_adopt(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.all()
        with work_as(user):
            sents.release()
        sents = Sentence.objects.filter(owner=None)
        assert len(sents) == 2
        with work_as(user):
            sents.adopt()
        sents = Sentence.objects.exclude(owner=None)
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2

    def test_sentence_qs_change_language(db, sent, user, sent2):
        sent.save()
        sent2.save()
        sents = Sentence.objects.filter(lang='eng')
        assert len(sents) == 2
        with work_as(user):
            sents.change_language('fra')
        sents = Sentence.objects.filter(lang='fra')
        assert len(sents) == 2
        assert sents[0] == sent
        assert sents[1] == sent2
