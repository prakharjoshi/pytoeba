from django.forms import ModelForm
from .models import Sentence


class SentenceForm(ModelForm):

    class Meta:
        model = Sentence
        fields = ['text', 'lang']

class SentenceAddForm(SentenceForm):

        def save(self, **kwargs):
            user = self.instance.added_by
            text = self.instance.text
            lang = self.instance.lang

            with work_as(user):
                sent = Sentence.objects.add(text, lang)
            return sent
