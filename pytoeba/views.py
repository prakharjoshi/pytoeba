from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from .models import Sentence
from .utils import work_as
from .forms import SentenceAddForm


class SentenceAdd(FormView):
    template_name = 'sentence_add.html'
    form_class = SentenceAddForm
    success_url = reverse_lazy('sentence_add') #change this to sent detail view

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super(SentenceAdd, self).form_valid(form)
