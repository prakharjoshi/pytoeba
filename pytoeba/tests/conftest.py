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
