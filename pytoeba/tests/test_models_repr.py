from pytoeba.models import *
from django.contrib.auth.models import User
import inspect
import pytest


@pytest.fixture
def cls_members():
    user = User()
    sent = Sentence()
    link = Link(side1=sent, side2=sent)
    log = Log(sentence=sent, done_by=user)
    corr = Correction(sentence=sent)
    tag = Tag()
    loctag = LocalizedTag(tag=tag)
    sentag = SentenceTag(sentence=sent, localized_tag=loctag)
    audio = Audio(sentence=sent)

    return locals()


def test_all_models_define_string_repr(cls_members):
    """
    This checks that all models defined in
    pytoeba.models defines a __unicode__
    method. This is a good practice for having
    a quick string representation for the objects
    in django admin and django shell or when
    repr() is called directly on the object
    """
    for cls in cls_members.itervalues():
        name = cls.__class__.__name__
        default_rep = '<%s: %s object>' % (name, name)
        assert not default_rep == repr(cls), \
            """
            Please define __unicode__ on your model,
            then add an instance for it in the
            cls_members fixture
            """
