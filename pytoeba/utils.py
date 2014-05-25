"""
Common functionality used in save() methods and the like live here.
This is basically anything that can be abstracted away for readability
like hashing or getting a media path, etc...
"""

from django.conf import settings
import os


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

