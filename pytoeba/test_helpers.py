from pytest import raises
from django.db import IntegrityError
from django.core.exceptions import ValidationError


def db_validate_blank(instance, field, default=False):
    setattr(instance, field, '')
    if default:
        instance.full_clean()
    else:
        assert raises(ValidationError, instance.full_clean)


def db_validate_null(instance, field, default=False):
    setattr(instance, field, None)
    if default:
        instance.save()
    else:
        assert raises(IntegrityError, instance.save)


def db_validate_max_length(instance, field, length):
    setattr(instance, field, '1' * (length + 1))
    assert raises(ValidationError, instance.full_clean)
