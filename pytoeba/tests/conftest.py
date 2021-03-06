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
    user = PytoebaUser(username='user', password='pass')
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


@pytest.fixture(scope='session')
def log(db, sent_saved, user):
    from pytoeba.models import Log
    log = Log(sentence=sent_saved, type='cad', done_by=user, target_id=sent_saved.id)
    return log


@pytest.fixture(scope='session')
def corr(db, sent_saved, user):
    from pytoeba.models import Correction
    corr = Correction(sentence=sent_saved, text='test2', added_by=user)
    return corr


@pytest.fixture(scope='session')
def tag(db, user):
    from pytoeba.models import Tag
    tag = Tag(added_by=user)
    return tag


@pytest.fixture(scope='session')
def loctag(db, tag):
    from pytoeba.models import LocalizedTag
    tag.save()
    loctag = LocalizedTag(tag=tag, text='test2', lang='eng')
    return loctag


@pytest.fixture(scope='session')
def sentag(db, sent_saved, user, tag, loctag):
    from pytoeba.models import SentenceTag
    tag.save()
    loctag.save()
    sentag = SentenceTag(
        sentence=sent_saved, tag=tag, added_by=user
        )
    return sentag


@pytest.fixture(scope='session')
def audio(db, request, user, sent_saved):
    from pytoeba.models import Audio
    from django.conf import settings
    from django.core.files import File
    path = os.path.join(
        settings.MEDIA_ROOT, sent_saved.hash_id + '-' + 'hash2'
        )
    ft = open(path, 'w+')
    f = File(ft)
    audio = Audio(
        hash_id='hash2', sentence=sent_saved, audio_file=f, added_by=user
        )

    def fin():
        ft.close()
        os.remove(path)
        try:
            os.remove(
                os.path.join(
                    settings.MEDIA_ROOT,
                    sent_saved.hash_id + '-' + 'hash2' + '.mp3'
                    )
                )
        except OSError:
            pass
    request.addfinalizer(fin)

    return audio
