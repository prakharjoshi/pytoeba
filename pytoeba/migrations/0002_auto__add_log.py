# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Log'
        db.create_table(u'pytoeba_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('done_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_doneby_set', to=orm['auth.User'])),
            ('done_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('change_set', self.gf('django.db.models.fields.CharField')(default=None, max_length=500, null=True)),
            ('target_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=40, null=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Log'])


    def backwards(self, orm):
        # Deleting model 'Log'
        db.delete_table(u'pytoeba_log')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pytoeba.link': {
            'Meta': {'object_name': 'Link'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'side1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'side1_set'", 'to': u"orm['pytoeba.Sentence']"}),
            'side2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'side2_set'", 'to': u"orm['pytoeba.Sentence']"})
        },
        u'pytoeba.log': {
            'Meta': {'object_name': 'Log'},
            'change_set': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '500', 'null': 'True'}),
            'done_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_doneby_set'", 'to': u"orm['auth.User']"}),
            'done_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"}),
            'target_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'pytoeba.sentence': {
            'Meta': {'unique_together': "(('text', 'lang'),)", 'object_name': 'Sentence', 'index_together': "[['text', 'lang']]"},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_addedby_set'", 'to': u"orm['auth.User']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'has_correction': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'link': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pytoeba.Sentence']", 'through': u"orm['pytoeba.Link']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'sent_owner_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'sent_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'sim_hash': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        }
    }

    complete_apps = ['pytoeba']