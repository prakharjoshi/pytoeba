from django.conf.urls import url

from .utils import work_as

from tastypie.resources import Resource, BaseModelResource, DeclarativeMetaclass, ResourceOptions
from tastypie.utils import trailing_slash
from tastypie import http

from types import MethodType
from collections import defaultdict
import inspect


class PyapiOptions(ResourceOptions):
    pyapi_funcs = {}


class PyapiDeclarativeMetaclass(DeclarativeMetaclass):
    def __new__(cls, name, bases, attrs):
        new_class = super(PyapiDeclarativeMetaclass, cls).__new__(cls, name, bases, attrs)
        opts = getattr(new_class, 'Meta', None)
        new_class._meta = PyapiOptions(opts)

        if new_class._meta and getattr(new_class._meta, 'queryset'):
            setattr(new_class._meta, 'object_class', new_class._meta.queryset.model)

        if opts:
            pyapi = new_class._meta.queryset.model.objects
            pyapi_settings = new_class._meta.pyapi_funcs
            func_include = pyapi_settings.get('include')
            funcs = defaultdict(dict)

            if func_include:
                for func in func_include:
                    pyapi_func = getattr(pyapi, func, None)

                    if pyapi_func:
                        args = inspect.getargspec(pyapi_func).args
                        del args[0]

                        settings = pyapi_settings.get('funcs') or {}
                        settings_func = settings.get(func) or {}
                        funcs[func]['func'] = pyapi_func
                        funcs[func]['arguments'] = args
                        funcs[func]['resource_type'] = settings_func.get('resource_type') or 'detail'

                        funcs[func]['response_class'] = settings_func.get('response_class') or http.HttpCreated
                        funcs[func]['allowed_methods'] = settings_func.get('allowed_methods') or ['post']
                        funcs[func]['description'] = settings_func.get('description') or ''

            pyapi_settings['funcs'] = funcs
            new_class._meta.pyapi_funcs = pyapi_settings

            new_class.add_pyapi_calls()

        include_fields = getattr(new_class._meta, 'fields', [])
        excludes = getattr(new_class._meta, 'excludes', [])
        field_names = list(new_class.base_fields.keys())

        for field_name in field_names:
            if field_name == 'resource_uri':
                continue
            if field_name in new_class.declared_fields:
                continue
            if len(include_fields) and not field_name in include_fields:
                del(new_class.base_fields[field_name])
            if len(excludes) and field_name in excludes:
                del(new_class.base_fields[field_name])

        # Add in the new fields.
        new_class.base_fields.update(new_class.get_fields(include_fields, excludes))

        if getattr(new_class._meta, 'include_absolute_url', True):
            if not 'absolute_url' in new_class.base_fields:
                new_class.base_fields['absolute_url'] = fields.CharField(attribute='get_absolute_url', readonly=True)
        elif 'absolute_url' in new_class.base_fields and not 'absolute_url' in attrs:
            del(new_class.base_fields['absolute_url'])

        return new_class


class PyapiResource(BaseModelResource):
    __metaclass__ = PyapiDeclarativeMetaclass

    def prepend_urls(self):
        urls = []
        for pyapi_func in self._meta.pyapi_funcs['funcs'].keys():
            func_namespace = self._meta.resource_name + '_' + pyapi_func
            urls.append(
                url(r'^(?P<resource_name>%s)/%s%s$' % (self._meta.resource_name, pyapi_func, trailing_slash()), self.wrap_view(pyapi_func), name=func_namespace)
                )

            pyapi_schema = pyapi_func + '_schema'
            schema_namespace = self._meta.resource_name + '_' + pyapi_func + '_schema'
            urls.append(
                url(r'^(?P<resource_name>%s)/%s/schema%s$' % (self._meta.resource_name, pyapi_func, trailing_slash()), self.wrap_view(pyapi_schema), name=schema_namespace)
                )

        return urls

    @classmethod
    def add_pyapi_calls(cls):

        def build_pyapi_call(settings):

            def pyapi_schema(self, request, **kwargs):
                self.method_check(request, allowed=['get'])
                self.is_authenticated(request)
                self.throttle_check(request)
                self.log_throttled_access(request)

                data = settings.copy()
                data['default_format'] = self._meta.default_format
                del data['func']
                data['response_code'] = data['response_class'].status_code
                del data['response_class']

                return self.create_response(request, data)

            def pyapi_call_detail(self, request, **kwargs):
                self.method_check(request, allowed=settings['allowed_methods'])
                self.is_authenticated(request)
                self.throttle_check(request)
                self.log_throttled_access(request)

                data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

                with work_as(request.user):
                    args = [data[arg] for arg in settings['arguments']]
                    affected_object = settings['func'](*args)

                response_data = None
                if affected_object:
                    bundle = self.build_bundle(obj=affected_object, request=request)
                    response_data = self.full_dehydrate(bundle)

                return self.create_response(request, response_data, response_class=settings['response_class'])

            if settings['resource_type'] == 'detail': return pyapi_schema, pyapi_call_detail

            def pyapi_call_list(self, request, **kwargs):
                self.method_check(request, allowed=settings['allowed_methods'])
                self.is_authenticated(request)
                self.throttle_check(request)
                self.log_throttled_access(request)

                data = self.deserialize(request, request.body, format=request.META.get('CONTENT_TYPE', 'application/json'))

                with work_as(request.user):
                    affected_objects = settings['func'](**data)

                response_data = None
                if affected_objects:
                    reponse_data = []

                    for obj in affected_objects:
                        bundle = self.build_bundle(obj=obj, request=request)
                        data.append(self.full_dehydrate(bundle))

                return self.create_response(request, response_data, response_class=settings['response_class'])

            if settings['resource_type'] == 'list': return pyapi_schema, pyapi_call_list


        for call_name, settings in cls.Meta.pyapi_funcs['funcs'].items():
            schema_name = call_name + '_schema'
            pyapi_schema, pyapi_call = build_pyapi_call(settings)
            setattr(cls, call_name, MethodType(pyapi_call, None, cls))
            setattr(cls, schema_name, MethodType(pyapi_schema, None, cls))
