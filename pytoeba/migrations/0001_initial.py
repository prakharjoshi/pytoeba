# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sentence'
        db.create_table(u'pytoeba_sentence', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sent_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('hash_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=4, db_index=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('sim_hash', self.gf('django.db.models.fields.BigIntegerField')(db_index=True)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_addedby_set', to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='sent_owner_set', null=True, to=orm['pytoeba.PytoebaUser'])),
            ('is_editable', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('has_correction', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('length', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Sentence'])

        # Adding unique constraint on 'Sentence', fields ['text', 'lang']
        db.create_unique(u'pytoeba_sentence', ['text', 'lang'])

        # Adding index on 'Sentence', fields ['text', 'lang']
        db.create_index(u'pytoeba_sentence', ['text', 'lang'])

        # Adding model 'Link'
        db.create_table(u'pytoeba_link', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('side1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='side1_set', to=orm['pytoeba.Sentence'])),
            ('side2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='side2_set', to=orm['pytoeba.Sentence'])),
            ('level', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Link'])

        # Adding unique constraint on 'Link', fields ['side1', 'side2']
        db.create_unique(u'pytoeba_link', ['side1_id', 'side2_id'])

        # Adding index on 'Link', fields ['side1', 'side2']
        db.create_index(u'pytoeba_link', ['side1_id', 'side2_id'])

        # Adding index on 'Link', fields ['side1', 'level']
        db.create_index(u'pytoeba_link', ['side1_id', 'level'])

        # Adding index on 'Link', fields ['side2', 'level']
        db.create_index(u'pytoeba_link', ['side2_id', 'level'])

        # Adding index on 'Link', fields ['side1', 'side2', 'level']
        db.create_index(u'pytoeba_link', ['side1_id', 'side2_id', 'level'])

        # Adding model 'Log'
        db.create_table(u'pytoeba_log', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3, db_index=True)),
            ('done_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='log_doneby_set', to=orm['pytoeba.PytoebaUser'])),
            ('done_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('change_set', self.gf('django.db.models.fields.CharField')(default=None, max_length=500, null=True)),
            ('target_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('source_hash_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, null=True, blank=True)),
            ('target_hash_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=32, null=True, blank=True)),
            ('source_lang', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=4, null=True, blank=True)),
            ('target_lang', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=4, null=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Log'])

        # Adding index on 'Log', fields ['source_lang', 'target_lang']
        db.create_index(u'pytoeba_log', ['source_lang', 'target_lang'])

        # Adding model 'Correction'
        db.create_table(u'pytoeba_correction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Correction'])

        # Adding model 'Tag'
        db.create_table(u'pytoeba_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Tag'])

        # Adding model 'LocalizedTag'
        db.create_table(u'pytoeba_localizedtag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Tag'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=4)),
        ))
        db.send_create_signal(u'pytoeba', ['LocalizedTag'])

        # Adding unique constraint on 'LocalizedTag', fields ['tag', 'lang']
        db.create_unique(u'pytoeba_localizedtag', ['tag_id', 'lang'])

        # Adding index on 'LocalizedTag', fields ['tag', 'lang']
        db.create_index(u'pytoeba_localizedtag', ['tag_id', 'lang'])

        # Adding model 'SentenceTag'
        db.create_table(u'pytoeba_sentencetag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('tag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Tag'])),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['SentenceTag'])

        # Adding unique constraint on 'SentenceTag', fields ['sentence', 'tag']
        db.create_unique(u'pytoeba_sentencetag', ['sentence_id', 'tag_id'])

        # Adding index on 'SentenceTag', fields ['sentence', 'tag']
        db.create_index(u'pytoeba_sentencetag', ['sentence_id', 'tag_id'])

        # Adding model 'Audio'
        db.create_table(u'pytoeba_audio', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hash_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32, db_index=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('audio_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Audio'])

        # Adding model 'PytoebaUser'
        db.create_table(u'pytoeba_pytoebauser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email_unconfirmed', self.gf('django.db.models.fields.EmailField')(default='test@test.com', max_length=75, blank=True)),
            ('email_confirmation_key', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('email_confirmation_key_created_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('privacy', self.gf('django.db.models.fields.CharField')(default='o', max_length=1)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='u', max_length=1, db_index=True)),
            ('with_status_vote_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('against_status_vote_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('about_text', self.gf('django.db.models.fields.TextField')()),
            ('about_markup', self.gf('django.db.models.fields.CharField')(default='', max_length=2)),
            ('about_html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'pytoeba', ['PytoebaUser'])

        # Adding M2M table for field groups on 'PytoebaUser'
        m2m_table_name = db.shorten_name(u'pytoeba_pytoebauser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pytoebauser', models.ForeignKey(orm[u'pytoeba.pytoebauser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pytoebauser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'PytoebaUser'
        m2m_table_name = db.shorten_name(u'pytoeba_pytoebauser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pytoebauser', models.ForeignKey(orm[u'pytoeba.pytoebauser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['pytoebauser_id', 'permission_id'])

        # Adding model 'UserLang'
        db.create_table(u'pytoeba_userlang', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='userlang_set', to=orm['pytoeba.PytoebaUser'])),
            ('lang', self.gf('django.db.models.fields.CharField')(max_length=4, db_index=True)),
            ('proficiency', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('is_trusted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('with_vote_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('against_vote_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal(u'pytoeba', ['UserLang'])

        # Adding unique constraint on 'UserLang', fields ['user', 'lang']
        db.create_unique(u'pytoeba_userlang', ['user_id', 'lang'])

        # Adding index on 'UserLang', fields ['user', 'lang']
        db.create_index(u'pytoeba_userlang', ['user_id', 'lang'])

        # Adding M2M table for field votes on 'UserLang'
        m2m_table_name = db.shorten_name(u'pytoeba_userlang_votes')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userlang', models.ForeignKey(orm[u'pytoeba.userlang'], null=False)),
            ('uservote', models.ForeignKey(orm[u'pytoeba.uservote'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userlang_id', 'uservote_id'])

        # Adding model 'UserVote'
        db.create_table(u'pytoeba_uservote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('is_with', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('target_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'pytoeba', ['UserVote'])

        # Adding unique constraint on 'UserVote', fields ['user', 'type', 'target_id']
        db.create_unique(u'pytoeba_uservote', ['user_id', 'type', 'target_id'])

        # Adding index on 'UserVote', fields ['user', 'type', 'target_id']
        db.create_index(u'pytoeba_uservote', ['user_id', 'type', 'target_id'])

        # Adding model 'Message'
        db.create_table(u'pytoeba_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['pytoeba.PytoebaUser'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='received_messages', null=True, to=orm['pytoeba.PytoebaUser'])),
            ('parent_msg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='next_messages', null=True, to=orm['pytoeba.Message'])),
            ('sent_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('read_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('replied_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sender_deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('recipient_deleted_on', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Message'])

        # Adding index on 'Message', fields ['recipient', 'recipient_deleted_on']
        db.create_index(u'pytoeba_message', ['recipient_id', 'recipient_deleted_on'])

        # Adding index on 'Message', fields ['sender', 'sender_deleted_on']
        db.create_index(u'pytoeba_message', ['sender_id', 'sender_deleted_on'])

        # Adding model 'Comment'
        db.create_table(u'pytoeba_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sentence', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.Sentence'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('is_deleted', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Comment'])

        # Adding model 'Wall'
        db.create_table(u'pytoeba_wall', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
        ))
        db.send_create_signal(u'pytoeba', ['Wall'])

        # Adding model 'WallThread'
        db.create_table(u'pytoeba_wallthread', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wall', self.gf('django.db.models.fields.related.ForeignKey')(related_name='threads', to=orm['pytoeba.Wall'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sticky', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'pytoeba', ['WallThread'])

        # Adding M2M table for field subscribers on 'WallThread'
        m2m_table_name = db.shorten_name(u'pytoeba_wallthread_subscribers')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('wallthread', models.ForeignKey(orm[u'pytoeba.wallthread'], null=False)),
            ('pytoebauser', models.ForeignKey(orm[u'pytoeba.pytoebauser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['wallthread_id', 'pytoebauser_id'])

        # Adding model 'WallPost'
        db.create_table(u'pytoeba_wallpost', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('wall', self.gf('django.db.models.fields.related.ForeignKey')(related_name='wall_posts', to=orm['pytoeba.Wall'])),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thread_posts', to=orm['pytoeba.WallThread'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('added_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pytoeba.PytoebaUser'])),
            ('added_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('modified_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('body_text', self.gf('django.db.models.fields.TextField')()),
            ('body_markup', self.gf('django.db.models.fields.CharField')(default='', max_length=2)),
            ('body_html', self.gf('django.db.models.fields.TextField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
        ))
        db.send_create_signal(u'pytoeba', ['WallPost'])


    def backwards(self, orm):
        # Removing index on 'Message', fields ['sender', 'sender_deleted_on']
        db.delete_index(u'pytoeba_message', ['sender_id', 'sender_deleted_on'])

        # Removing index on 'Message', fields ['recipient', 'recipient_deleted_on']
        db.delete_index(u'pytoeba_message', ['recipient_id', 'recipient_deleted_on'])

        # Removing index on 'UserVote', fields ['user', 'type', 'target_id']
        db.delete_index(u'pytoeba_uservote', ['user_id', 'type', 'target_id'])

        # Removing unique constraint on 'UserVote', fields ['user', 'type', 'target_id']
        db.delete_unique(u'pytoeba_uservote', ['user_id', 'type', 'target_id'])

        # Removing index on 'UserLang', fields ['user', 'lang']
        db.delete_index(u'pytoeba_userlang', ['user_id', 'lang'])

        # Removing unique constraint on 'UserLang', fields ['user', 'lang']
        db.delete_unique(u'pytoeba_userlang', ['user_id', 'lang'])

        # Removing index on 'SentenceTag', fields ['sentence', 'tag']
        db.delete_index(u'pytoeba_sentencetag', ['sentence_id', 'tag_id'])

        # Removing unique constraint on 'SentenceTag', fields ['sentence', 'tag']
        db.delete_unique(u'pytoeba_sentencetag', ['sentence_id', 'tag_id'])

        # Removing index on 'LocalizedTag', fields ['tag', 'lang']
        db.delete_index(u'pytoeba_localizedtag', ['tag_id', 'lang'])

        # Removing unique constraint on 'LocalizedTag', fields ['tag', 'lang']
        db.delete_unique(u'pytoeba_localizedtag', ['tag_id', 'lang'])

        # Removing index on 'Log', fields ['source_lang', 'target_lang']
        db.delete_index(u'pytoeba_log', ['source_lang', 'target_lang'])

        # Removing index on 'Link', fields ['side1', 'side2', 'level']
        db.delete_index(u'pytoeba_link', ['side1_id', 'side2_id', 'level'])

        # Removing index on 'Link', fields ['side2', 'level']
        db.delete_index(u'pytoeba_link', ['side2_id', 'level'])

        # Removing index on 'Link', fields ['side1', 'level']
        db.delete_index(u'pytoeba_link', ['side1_id', 'level'])

        # Removing index on 'Link', fields ['side1', 'side2']
        db.delete_index(u'pytoeba_link', ['side1_id', 'side2_id'])

        # Removing unique constraint on 'Link', fields ['side1', 'side2']
        db.delete_unique(u'pytoeba_link', ['side1_id', 'side2_id'])

        # Removing index on 'Sentence', fields ['text', 'lang']
        db.delete_index(u'pytoeba_sentence', ['text', 'lang'])

        # Removing unique constraint on 'Sentence', fields ['text', 'lang']
        db.delete_unique(u'pytoeba_sentence', ['text', 'lang'])

        # Deleting model 'Sentence'
        db.delete_table(u'pytoeba_sentence')

        # Deleting model 'Link'
        db.delete_table(u'pytoeba_link')

        # Deleting model 'Log'
        db.delete_table(u'pytoeba_log')

        # Deleting model 'Correction'
        db.delete_table(u'pytoeba_correction')

        # Deleting model 'Tag'
        db.delete_table(u'pytoeba_tag')

        # Deleting model 'LocalizedTag'
        db.delete_table(u'pytoeba_localizedtag')

        # Deleting model 'SentenceTag'
        db.delete_table(u'pytoeba_sentencetag')

        # Deleting model 'Audio'
        db.delete_table(u'pytoeba_audio')

        # Deleting model 'PytoebaUser'
        db.delete_table(u'pytoeba_pytoebauser')

        # Removing M2M table for field groups on 'PytoebaUser'
        db.delete_table(db.shorten_name(u'pytoeba_pytoebauser_groups'))

        # Removing M2M table for field user_permissions on 'PytoebaUser'
        db.delete_table(db.shorten_name(u'pytoeba_pytoebauser_user_permissions'))

        # Deleting model 'UserLang'
        db.delete_table(u'pytoeba_userlang')

        # Removing M2M table for field votes on 'UserLang'
        db.delete_table(db.shorten_name(u'pytoeba_userlang_votes'))

        # Deleting model 'UserVote'
        db.delete_table(u'pytoeba_uservote')

        # Deleting model 'Message'
        db.delete_table(u'pytoeba_message')

        # Deleting model 'Comment'
        db.delete_table(u'pytoeba_comment')

        # Deleting model 'Wall'
        db.delete_table(u'pytoeba_wall')

        # Deleting model 'WallThread'
        db.delete_table(u'pytoeba_wallthread')

        # Removing M2M table for field subscribers on 'WallThread'
        db.delete_table(db.shorten_name(u'pytoeba_wallthread_subscribers'))

        # Deleting model 'WallPost'
        db.delete_table(u'pytoeba_wallpost')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pytoeba.audio': {
            'Meta': {'object_name': 'Audio'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'audio_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"})
        },
        u'pytoeba.comment': {
            'Meta': {'object_name': 'Comment'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'pytoeba.correction': {
            'Meta': {'object_name': 'Correction'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pytoeba.link': {
            'Meta': {'unique_together': "(('side1', 'side2'),)", 'object_name': 'Link', 'index_together': "[['side1', 'side2'], ['side1', 'level'], ['side2', 'level'], ['side1', 'side2', 'level']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'side1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'side1_set'", 'to': u"orm['pytoeba.Sentence']"}),
            'side2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'side2_set'", 'to': u"orm['pytoeba.Sentence']"})
        },
        u'pytoeba.localizedtag': {
            'Meta': {'unique_together': "(('tag', 'lang'),)", 'object_name': 'LocalizedTag', 'index_together': "[['tag', 'lang']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Tag']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        u'pytoeba.log': {
            'Meta': {'object_name': 'Log', 'index_together': "[['source_lang', 'target_lang']]"},
            'change_set': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '500', 'null': 'True'}),
            'done_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_doneby_set'", 'to': u"orm['pytoeba.PytoebaUser']"}),
            'done_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"}),
            'source_hash_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'source_lang': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'target_hash_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'target_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'target_lang': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'})
        },
        u'pytoeba.message': {
            'Meta': {'object_name': 'Message', 'index_together': "[['recipient', 'recipient_deleted_on'], ['sender', 'sender_deleted_on']]"},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': u"orm['pytoeba.Message']"}),
            'read_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': u"orm['pytoeba.PytoebaUser']"}),
            'recipient_deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'replied_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': u"orm['pytoeba.PytoebaUser']"}),
            'sender_deleted_on': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'sent_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120'})
        },
        u'pytoeba.pytoebauser': {
            'Meta': {'object_name': 'PytoebaUser'},
            'about_html': ('django.db.models.fields.TextField', [], {}),
            'about_markup': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'}),
            'about_text': ('django.db.models.fields.TextField', [], {}),
            'against_status_vote_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'birthday': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_confirmation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'email_confirmation_key_created_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email_unconfirmed': ('django.db.models.fields.EmailField', [], {'default': "'test@test.com'", 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'privacy': ('django.db.models.fields.CharField', [], {'default': "'o'", 'max_length': '1'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'with_status_vote_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'pytoeba.sentence': {
            'Meta': {'unique_together': "(('text', 'lang'),)", 'object_name': 'Sentence', 'index_together': "[['text', 'lang']]"},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_addedby_set'", 'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'has_correction': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '4', 'db_index': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'links': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pytoeba.Sentence']", 'through': u"orm['pytoeba.Link']", 'symmetrical': 'False'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'sent_owner_set'", 'null': 'True', 'to': u"orm['pytoeba.PytoebaUser']"}),
            'sent_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'sim_hash': ('django.db.models.fields.BigIntegerField', [], {'db_index': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'pytoeba.sentencetag': {
            'Meta': {'unique_together': "(('sentence', 'tag'),)", 'object_name': 'SentenceTag', 'index_together': "[['sentence', 'tag']]"},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sentence': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Sentence']"}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.Tag']"})
        },
        u'pytoeba.tag': {
            'Meta': {'object_name': 'Tag'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pytoeba.userlang': {
            'Meta': {'unique_together': "(('user', 'lang'),)", 'object_name': 'UserLang', 'index_together': "[['user', 'lang']]"},
            'against_vote_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trusted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lang': ('django.db.models.fields.CharField', [], {'max_length': '4', 'db_index': 'True'}),
            'proficiency': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'userlang_set'", 'to': u"orm['pytoeba.PytoebaUser']"}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['pytoeba.UserVote']", 'symmetrical': 'False'}),
            'with_vote_count': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'pytoeba.uservote': {
            'Meta': {'unique_together': "(('user', 'type', 'target_id'),)", 'object_name': 'UserVote', 'index_together': "[['user', 'type', 'target_id']]"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_with': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'target_id': ('django.db.models.fields.IntegerField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"})
        },
        u'pytoeba.wall': {
            'Meta': {'object_name': 'Wall'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pytoeba.wallpost': {
            'Meta': {'object_name': 'WallPost'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'body_html': ('django.db.models.fields.TextField', [], {}),
            'body_markup': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2'}),
            'body_text': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'modified_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thread_posts'", 'to': u"orm['pytoeba.WallThread']"}),
            'wall': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'wall_posts'", 'to': u"orm['pytoeba.Wall']"})
        },
        u'pytoeba.wallthread': {
            'Meta': {'object_name': 'WallThread'},
            'added_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pytoeba.PytoebaUser']"}),
            'added_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subscriptions'", 'blank': 'True', 'to': u"orm['pytoeba.PytoebaUser']"}),
            'wall': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'threads'", 'to': u"orm['pytoeba.Wall']"})
        }
    }

    complete_apps = ['pytoeba']