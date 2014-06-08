"""
Common functionality used in save() methods and the like live here.
This is basically anything that can be abstracted away for readability
like hashing or getting a media path, etc...
"""

from django.conf import settings
from django.utils import timezone
from django.db import connections
from django.db.models.fields import AutoField
from django.db.models.loading import get_model

from contextlib import contextmanager
from threading import local
from .exceptions import UnknownUserError
from docutils.core import publish_parts
from importlib import import_module
from collections import defaultdict

import os
import uuid
import simhash


def get_audio_path(instance, filename):
    """
    Recieves an instance of the Audio model and returns an appropriate
    filename/filepath (the hash_id + audio_file hash) for the save()
    function of the FileField to use.
    """
    return os.path.join(
        settings.MEDIA_ROOT,
        instance.sentence.hash_id + '-' + instance.hash_id + '.mp3'
        )

def now():
    return timezone.now()


def uuid4():
    return uuid.uuid4().hex


def sim_hash(text):
    return simhash.Simhash(text).value


def truncated_sim_hash(text):
    return int('%.19s' % (sim_hash(text)))


thread_local_storage = local()

@contextmanager
def work_as(user):
    if not hasattr(thread_local_storage, 'temp_user_list'):
        thread_local_storage.temp_user_list = []

    thread_local_storage.temp_user_list.append(user)
    yield
    thread_local_storage.temp_user_list.pop()


def get_user():
    if not hasattr(thread_local_storage, 'temp_user_list') or \
       not thread_local_storage.temp_user_list:
        raise UnknownUserError(
            "Please wrap this in a work_as context manager and provide a \
            User object."
            )
    return thread_local_storage.temp_user_list[-1]


def sentence_presave(sent):
    if not sent.id:
        sent.hash_id = uuid4()
        sent.owner = sent.added_by
    if sent.text:
        sent.length = len(sent.text)
        sent.sim_hash = truncated_sim_hash(sent.text)

    return sent


def correction_presave(corr):
    if not corr.id and corr.sentence:
        corr.hash_id = uuid4()
        sent = corr.sentence
        sent.has_correction = True
        sent.save(update_fields=['has_correction'])

    return corr


def tag_presave(tag):
    if not tag.id:
        tag.hash_id = uuid4()

    return tag


def rest(text):
    return publish_parts(text, writer_name='html')['body']


def import_path(path):
    module = '.'.join(path.split('.')[:-1])
    cls = path.split('.')[-1]
    module = import_module(module)
    cls = getattr(module, cls)
    return cls


graph_backend = import_path(settings.GRAPH_BACKEND)

def redraw_subgraph(links=[], unlinks=[]):
    Sentence = get_model('pytoeba', 'Sentence')
    Link = get_model('pytoeba', 'Link')

    link_qs = Link.objects.none()
    for link in links:
        link_qs = link_qs | \
             Link.objects.filter(side1_id=link[0]) | \
             Link.objects.filter(
                side1__in=Sentence.objects.filter(
                    side1_set__in=Link.objects.filter(side1_id=link[0])
                    ),
                level=1
                ) | \
             Link.objects.filter(side2_id=link[0]) | \
             Link.objects.filter(
                side2__in=Sentence.objects.filter(
                    side2_set__in=Link.objects.filter(side2_id=link[0])
                    ),
                level=1
                ) | \
             Link.objects.filter(side1_id=link[1]) | \
             Link.objects.filter(
                side1__in=Sentence.objects.filter(
                    side1_set__in=Link.objects.filter(side1_id=link[1])
                    ),
                level=1
                ) | \
             Link.objects.filter(side2_id=link[1]) | \
             Link.objects.filter(
                side2__in=Sentence.objects.filter(
                    side2_set__in=Link.objects.filter(side2_id=link[1])
                    ),
                level=1
                )

    unlink_qs = Link.objects.none()
    for unlink in unlinks:
        unlink_qs = unlink_qs | \
            Link.objects.filter(side1_id=unlink[0], side2_id=unlink[1], level=1)

    subgraph_links = list(link_qs | unlink_qs)
    subgraph = graph_backend(subgraph_links)

    for link in links:
        subgraph.add_edge(link[0], link[1])

    for unlink in unlinks:
        subgraph.remove_edge(link[0], link[1])

    relinked_subgraph_links = subgraph.get_recomputed_links(
        created=True, updated=True, deleted=True
        )

    created = relinked_subgraph_links['created']
    updated = relinked_subgraph_links['updated']
    deleted = relinked_subgraph_links['deleted']

    if created:
        created = bulk_create(created)

    if updated:
        bulk_update(updated, update_fields=['level'], case_fields=['side1_id', 'side2_id'])

    if deleted:
        bulk_delete(deleted)


def fix_pythonism(value):
    if not value:
        if value is None:
            value = 'NULL'
        if isinstance(value, unicode):
            value = '\'\''
    if isinstance(value, bool):
        value = unicode(value).upper()

    return value


def bulk_create(objs, using='default'):
    ref_obj = objs[0]
    meta = ref_obj._meta
    model = meta.model
    fields = meta.fields

    return model._base_manager._insert(objs, fields=fields, using=using)


def bulk_delete(objs, case_field='id', using='default', as_sql=False):
    connection = connections[using]
    # using objects not from the same table will break everything
    ref_obj = objs[0]
    meta = ref_obj._meta
    case_field = [f for f in meta.fields if f.attname == case_field][0]

    cf_vals = []
    for obj in objs:
        val = getattr(obj, case_field.attname)
        val = case_field.get_db_prep_save(val, connection)
        val = fix_pythonism(val)
        cf_vals.append(val)

    sql = []
    params = []

    sql.append('DELETE FROM %s ' % meta.db_table)
    sql.append('WHERE %s IN (%%s)' % case_field)

    params.append(', '.join(cf_vals))

    sql = ''.join(sql)
    if as_sql:
        return sql, params

    connection.cursor().execute(sql, params)


def bulk_update(objs, case_field='id', using='default', update_fields=[],
                case_fields=[], as_sql=False):
    connection = connections[using]
    # using objects not from the same table will break everything
    ref_obj = objs[0]
    meta = ref_obj._meta
    fields = meta.fields
    update_fields = update_fields or meta.get_all_field_names()
    # get actual field object for case_field by name
    case_field = [f for f in fields if f.attname == case_field][0]
    if case_fields:
        case_fields = [f for f in fields if f.attname in case_fields]
    # filter out auto fields and fields not specified in update_fields
    fields = [
        f
        for f in fields
        if not isinstance(f, AutoField) and f.attname in update_fields
        ]

    # initialize cases
    cases = {}
    for field in fields:
        cases[field.column] = defaultdict(dict)

    # populate a case per field with case_field/field value pairs
    # the defaultdict ensures unique values per case per case_field
    for obj in objs:
        # get raw values appropriate for the db backend
        if not case_fields:
            cf_value = case_field.get_db_prep_save(
                getattr(obj, case_field.attname), connection
                )
            for field in fields:
                f_value = field.get_db_prep_save(
                    getattr(obj, field.attname), connection
                    )
                f_value = fix_pythonism(f_value)
                cases[field.column].update({cf_value: f_value})
        else:
            cf_values = []
            for field in case_fields:
                cf_value = field.get_db_prep_save(
                    getattr(obj, field.attname), connection
                    )
                cf_value = fix_pythonism(cf_value)
                cf_values.append(cf_value)
            cf_values = tuple(cf_values)
            for field in fields:
                f_value = field.get_db_prep_save(
                    getattr(obj, field.attname), connection
                    )
                f_value = fix_pythonism(f_value)
                cases[field.column].update({cf_values: f_value})

    # build sql query
    indent = '    '
    newline = '\n'
    sql = []
    params = []

    sql.append('UPDATE %s' % meta.db_table)
    sql.append(newline)
    sql.append(indent)
    sql.append('SET')
    sql.append(newline)

    cf_vals = set()
    for case, values in cases.iteritems():

        sql.append(indent * 2)
        if not case_fields:
            sql.append('%s = CASE %s' % (case, case_field.attname))
        else:
            sql.append('%s = CASE' % case)
        sql.append(newline)

        for cf_value, field_value in values.items():

            cf_vals.add(cf_value)
            if not case_fields:
                sql.append(indent * 3)
                sql.append('WHEN %s THEN %s')
                sql.append(newline)
                params.append(cf_value)
                params.append(field_value)
            else:
                cond = []
                for cf in case_fields:
                    cond.append('%s = %%s' % cf.attname)
                cond = ' AND '.join(cond)
                sql.append(indent * 3)
                sql.append('WHEN (%s) THEN %%s' % cond)
                sql.append(newline)
                for cf_v in cf_value:
                    params.append(cf_v)
                params.append(field_value)

        sql.append(indent * 2)
        sql.append('END,')
        sql.append(newline)

    sql.pop()
    sql.pop()
    sql.append('END')
    sql.append(newline)

    if not case_fields:
        sql.append('WHERE %s IN (%%s)' % case_field.attname)
        params.append(', '.join(str(v) for v in cf_vals))
    else:
        if connection.vendor != 'sqlite': # change this connection.vendor
            cfs = ', '.join([cf.attname for cf in case_fields])
            sql.append('WHERE (%s) IN (%%s)' % cfs)
            cf_param = []
            for cf_v in cf_vals:
                cf_param.append('(' + ', '.join(str(v) for v in cf_v) + ')')
            params.append(', '.join(cf_param))
        else:
            comps = []
            for cf in case_fields:
                comps.append('%s = %%s' % cf.attname)
            comps = ' AND '.join(comps)

            cond = []
            for cf_v in cf_vals:
                cond.append('(%s)' % comps)
                for v in cf_v:
                    params.append(str(v))
            cond = ' OR '.join(cond)

            sql.append('WHERE %s' % cond)

    sql = ''.join(sql)
    if as_sql:
        return sql, params

    connection.cursor().execute(sql, params)


def bulk_upsert(objs, case_field='id', using='default', _return=True):
    # get some basic info about the objects, they all have to be for the same
    # table or well, things can go horribly wrong.
    ref_obj = objs[0]
    meta = ref_obj._meta
    model = meta.model
    fields = meta.fields

    # handle common case first, case_field is id
    # missing ids will always be inserts
    if case_field == 'id':
        all_objs = set(objs)
        for_insert = set(obj for obj in objs if not obj.id)
        for_update = all_objs - for_insert
        bulk_update(for_update, case_field, using)
        # bypass the fucking stupid forced batch_size in django's bulk_create
        for_insert = bulk_create(for_insert, using=using)
        return list(for_insert), list(for_update)

    # handle the more generic case
    # we don't know if some of these fields in case_field (that should be
    # unique btw, or you're fucked hardcore) are actually already there
    # so we do a select to find out
    cf_vals = [getattr(obj, case_field) for obj in objs]
    filter_kwargs = {case_field+'__in': cf_vals}
    all_objs = set(objs)
    for_update = set(model.objects.filter(**filter_kwargs))
    for_insert = all_objs - for_update
    bulk_update(for_update, case_field, using)
    # bypass the fucking stupid forced batch_size in django's bulk_create
    for_insert = model._base_manager._insert(for_insert, fields=fields, using=using)

    if _return:
        return list(for_insert), list(for_update)
