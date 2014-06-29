from django.conf.urls import patterns, include, url
from .api import PyapiApi
from .api import (
    SentenceResource, LogResource, CorrectionResource, TagResource, 
    SentenceTagResource, UserResource, MessageResource
)


api = PyapiApi(api_name='api')
api.register(SentenceResource())
api.register(LogResource())
api.register(CorrectionResource())
api.register(TagResource())
api.register(SentenceTagResource())
api.register(UserResource())
api.register(MessageResource())


urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
