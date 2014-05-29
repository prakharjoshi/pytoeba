from pytoeba.models import Tag
from pytoeba.utils import work_as
from copy import deepcopy
import pytest


@pytest.mark.django_db
@pytest.mark.usefixture('tag', 'loctag', 'user')
class TestTagInstanceMethods():

    def test_tag_save(db, tag):
        assert tag.hash_id == ''
        tag.save()
        assert tag.hash_id

    def test_tag_get_localization(db, tag, user, loctag):
        tag.save()
        loctag.save()
        assert tag.get_localization('eng') == loctag

    def test_tag_get_all_localizations(db, tag, user, loctag):
        tag.save()
        assert len(tag.get_all_localizations()) == 0
        loctag2 = deepcopy(loctag)
        loctag.save()
        loctag2.lang = 'fra'
        loctag2.save()
        assert len(tag.get_all_localizations()) == 2
        locs = tag.get_all_localizations()
        assert locs[0] == loctag
        assert locs[1] == loctag2

    def test_tag_merge(db, tag, sent, user):
        sent.save()
        tag2 = deepcopy(tag)
        tag.save()
        tag2.save()
        tag.translate('OK', 'eng')
        tag2.translate('oki', 'fra')
        with work_as(user):
            sent.add_tag('oki')
        assert len(Tag.objects.all()) == 2
        assert sent.sentencetag_set.all()[0].tag == tag2
        tag.merge(tag2)
        assert len(Tag.objects.all()) == 1
        locs = Tag.objects.all()[0].get_all_localizations()
        assert len(locs) == 2
        assert locs[0].text == 'OK'
        assert locs[1].text == 'oki'
        assert sent.sentencetag_set.all()[0].tag == tag

    def test_tag_translate(db, tag):
        tag.save()
        assert len(tag.get_all_localizations()) == 0
        tag.translate('OK', 'eng')
        assert len(tag.get_all_localizations()) == 1
        assert tag.get_localization('eng').text == 'OK'
