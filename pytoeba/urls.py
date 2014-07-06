from django.conf.urls import patterns, include, url
from .api import PyapiApi
from .api import (
    SentenceResource, LogResource, CorrectionResource, TagResource, 
    SentenceTagResource, UserResource, MessageResource, SentenceSearchResource,
    TagSearchResource, CommentSearchResource, WallSearchResource,
    MessageSearchResource, UserSearchResource
)


api = PyapiApi(api_name='api')
api.register(SentenceResource())
api.register(LogResource())
api.register(CorrectionResource())
api.register(TagResource())
api.register(SentenceTagResource())
api.register(UserResource())
api.register(MessageResource())
api.register(SentenceSearchResource())
api.register(TagSearchResource())
api.register(CommentSearchResource())
api.register(WallSearchResource())
api.register(MessageSearchResource())
api.register(UserSearchResource())


urlpatterns = patterns('',
    url(r'^', include(api.urls)),
)
