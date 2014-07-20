from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from .models import Sentence
from .utils import work_as
from .forms import SentenceAddForm


def social_auth_login_request(request, backend_name, *args, **kwargs):
    return redirect(request.user.social_auth_request_url(
        request, backend_name, *args, **kwargs
        ))


@csrf_exempt
def social_auth_callback(request, backend_name, *args, **kwargs):
    return request.user.social_auth_login(
        backend_name, request, *args, **kwargs
        )


@login_required
@require_POST
@csrf_protect
def social_auth_disconnect(request, backend_name, association_id=None):
    return request.user.social_auth_disconnect(
        backend_name, request, association_id
        )


class SentenceAdd(FormView):
    template_name = 'sentence_add.html'
    form_class = SentenceAddForm
    success_url = reverse_lazy('sentence_add') #change this to sent detail view

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        return super(SentenceAdd, self).form_valid(form)
