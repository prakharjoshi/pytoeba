import os
import sys
import pytest


def pytest_configure():
    # change this to run the tests on your machine
    # hardcoded for now, checking whether env vars
    # are set or not is pita
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pytoeba_dev.settings'
    settings_path = '/home/lool0/dabblings/pytoeba_dev/'
    sys.path.append(settings_path)


@pytest.fixture(scope='session')
def user(db):
    from pytoeba.models import PytoebaUser
    user = User(username='user', password='pass')
    user.save()
    return user


@pytest.fixture(scope='session')
def sent(db, user):
    from pytoeba.models import Sentence
    sent = Sentence(lang='eng', text='test', added_by=user)
    return sent


@pytest.fixture(scope='session')
def sent2(db, user):
    from pytoeba.models import Sentence
    sent2 = Sentence(lang='eng', text='test2', added_by=user)
    return sent2


@pytest.fixture(scope='session')
def sent_saved(db, sent):
    sent_saved = sent
    sent_saved.save()
    return sent_saved


@pytest.fixture(scope='session')
def link(db, sent_saved, sent2, user):
    from pytoeba.models import Link, Sentence
    s1 = sent_saved
    s2 = sent2
    s2.save()
    link = Link(side1=s1, side2=s2, level=1)
    return link
