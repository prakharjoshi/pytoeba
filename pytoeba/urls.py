from django.conf.urls import patterns, include, url
from .views import SentenceAdd

urlpatterns = patterns('',
    url(r'^sentence/add/$', SentenceAdd.as_view(), name='sentence_add'),
)
