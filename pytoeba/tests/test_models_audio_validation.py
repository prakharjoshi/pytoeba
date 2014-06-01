from pytoeba.models import Audio
from pytest import raises
from django.db import IntegrityError
from pytoeba.tests.test_helpers import (
    db_validate_blank, db_validate_null, db_validate_max_length
    )
from django.conf import settings
from django.core.files import File
import pytest
import os


@pytest.mark.django_db
@pytest.mark.usefixture('audio')
class TestAudioValidation():

    def test_default(db):
        assert len(Audio.objects.all()) == 0
        audio = Audio()
        assert raises(IntegrityError, audio.save)

    def test_minimum_defaults(db, audio):
        audio.save()
        assert len(Audio.objects.all()) == 1
        assert audio.hash_id == 'hash2'
        assert audio.sentence.text == 'test'
        assert audio.audio_file.path == os.path.join(
            settings.MEDIA_ROOT,
            audio.sentence.hash_id + '-' + audio.hash_id + '.mp3'
            )
        assert audio.added_by.username == 'user'
        assert audio.added_on

    def test_hash_id_validation(db, audio):
        db_validate_blank(audio, 'hash_id')
        db_validate_max_length(audio, 'hash_id', 40)
        # validating null for this field directly is almost impossible
        # thanks to the audio_file field, which tries to concatenate
        # the None assigned to hash_id to a string to set the filename
        # before saving, will just go ahead and test that
        audio.hash_id = None
        assert raises(TypeError, audio.save)

    def test_sentence_validation(db, audio):
        with raises(ValueError):
            audio.sentence = None

    def test_audio_file_validation(db, audio):
        # This still needs file format validation (major security issue)
        db_validate_blank(audio, 'audio_file')
        # validating null=False here is tricky, django stores a reference to
        # an empty FieldFile instance, it should probably just be removed
        # from the schema
        audio.audio_file = None
        audio.save()
        assert audio.audio_file == File(None)

    def test_added_by_validation(db, audio):
        with raises(ValueError):
            audio.added_by = None
