"""
Common functionality used in save() methods and the like live here.
This is basically anything that can be abstracted away for readability
like hashing or getting a media path, etc...
"""
from django.conf import settings
from contextlib import contextmanager
from threading import local
from .exceptions import UnknownUserError
import os
import hashlib
import simhash
import datetime


def get_audio_path(instance, filename):
    """
    Recieves an instance of the Audio model and returns an appropriate
    filename/filepath (the hash_id + audio_file hash) for the save()
    function of the FileField to use.
    """
    return os.path.join(
        settings.MEDIA_ROOT,
        instance.sentence.hash_id + '-' + instance.hash_id + '.mp3'
        )


def sha1(text):
    return hashlib.sha1(text).hexdigest()


def sim_hash(text):
    return simhash.Simhash(text).value


def truncated_sim_hash(text):
    return int('%.19s' % (sim_hash(text)))


def now():
    return datetime.datetime.now().isoformat()


thread_local_storage = local()

@contextmanager
def work_as(user):
    if not hasattr(thread_local_storage, 'temp_user_list'):
        thread_local_storage.temp_user_list = []

    thread_local_storage.temp_user_list.append(user)
    yield
    thread_local_storage.temp_user_list.pop()


def get_user():
    if not thread_local_storage.temp_user_list:
        raise UnknownUserError(
            "Please wrap this in a work_as context manager and provide a \
            User object."
            )
    return thread_local_storage.temp_user_list[-1]
