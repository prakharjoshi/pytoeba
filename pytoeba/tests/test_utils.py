from pytoeba.models import PytoebaUser
from pytoeba.models import Log
from pytoeba.utils import work_as, get_user
from pytoeba.exceptions import UnknownUserError
from pytest import raises
import pytest
import threading


@pytest.mark.django_db
@pytest.mark.usefixture('sent')
def test_work_as_raises_error(db, sent):
    sent.save()
    assert raises(UnknownUserError, sent.delete)


@pytest.mark.django_db
@pytest.mark.usefixture('sent', 'user')
def test_work_as(db, sent, user):
    sent.save()
    with work_as(user):
        sent.delete()
    log = Log.objects.get(sentence=sent)
    assert log.done_by == user


@pytest.mark.django_db
@pytest.mark.usefixture('sent', 'user', 'sent2')
def test_work_as_nested(db, sent, sent2, user):
    sent2.save()
    sent.save()
    user2 = PytoebaUser()
    user2.save()
    with work_as(user2):
        sent2.delete()
        with work_as(user):
            sent.delete()
    log = Log.objects.get(sentence=sent)
    assert log.done_by == user
    log2 = Log.objects.get(sentence=sent2)
    assert log2.done_by == user2


current_user = None

@pytest.mark.django_db
@pytest.mark.usefixture('user')
def test_work_as_thread_safe(db, user):

    barrier = [threading.Event() for _ in xrange(3)]
    user1 = user
    user2 = PytoebaUser()
    user2.save()


    def task1():
        global current_user
        with work_as(user1):
            barrier[0].set()
            barrier[1].wait()
            current_user = get_user()
            barrier[2].set()

    def task2():
        barrier[0].wait()
        with work_as(user2):
            barrier[1].set()
            barrier[2].wait()

    threads = [threading.Thread(target=task1), threading.Thread(target=task2)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert current_user == user1
