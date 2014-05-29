from .test_helpers import template_used
from pytoeba.forms import SentenceForm
import pytest


@pytest.fixture()
def sent_add_resp(client):
    response = client.get('/sentence/add/')
    return response

@pytest.mark.django_db
class TestSentenceAddView():

    def test_response(db, sent_add_resp):
        assert sent_add_resp.status_code == 200

    def test_template(db, sent_add_resp):
        assert template_used(sent_add_resp, 'sentence_add.html')

    def test_form(db, sent_add_resp):
        assert isinstance(sent_add_resp.context['form'], SentenceForm)


