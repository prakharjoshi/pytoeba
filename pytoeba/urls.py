from django.conf.urls import patterns, include, url
from .views import (
    social_auth_callback, social_auth_disconnect, social_auth_login_request
    )
from .views import SentenceAdd
from .api import PyapiApi
from .api import (
SentenceResource, LogResource, CorrectionResource, TagResource, 
SentenceTagResource, UserResource, MessageResource, SentenceSearchResource,
TagSearchResource, CommentSearchResource, WallSearchResource, MessageSearchResource,
UserSearchResource
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
    url(r'^sentence/add/$', SentenceAdd.as_view(), name='sentence_add'),

    url(
        r'^social_auth/login_request/(?P<backend_name>[^/]+)/$',
        social_auth_login_request, name='social_auth_login_request'
        ),
    url(
        r'^social_auth/login_callback/(?P<backend_name>[^/]+)/$',
        social_auth_callback, name='social_auth_callback'
        ),
    url(
        r'^social_auth/disconnect/(?P<backend_name>[^/]+)/$',
        social_auth_disconnect, name='social_auth_disconnect'
        ),
    url(
        r'^social_auth/disconnect/(?P<backend_name>[^/]+)/(?P<association_id>[^/]+)/$',
        social_auth_disconnect, name='social_auth_disconnect_individual'
        ),
    url(r'^', include(api.urls)),
)
