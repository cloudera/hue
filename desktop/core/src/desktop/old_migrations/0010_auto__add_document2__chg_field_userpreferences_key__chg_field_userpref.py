# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Document2'
        db.create_table('desktop_document2', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='doc2_owner', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('uuid', self.gf('django.db.models.fields.CharField')(default='', max_length=32, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='', max_length=32, db_index=True)),
            ('data', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('extra', self.gf('django.db.models.fields.TextField')(default='')),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('version', self.gf('django.db.models.fields.SmallIntegerField')(default=1, db_index=True)),
            ('is_history', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('desktop', ['Document2'])

        # Adding M2M table for field tags on 'Document2'
        m2m_table_name = db.shorten_name('desktop_document2_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document2', models.ForeignKey(orm['desktop.document2'], null=False)),
            ('to_document2', models.ForeignKey(orm['desktop.document2'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_document2_id', 'to_document2_id'])

        # Adding M2M table for field dependencies on 'Document2'
        m2m_table_name = db.shorten_name('desktop_document2_dependencies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_document2', models.ForeignKey(orm['desktop.document2'], null=False)),
            ('to_document2', models.ForeignKey(orm['desktop.document2'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_document2_id', 'to_document2_id'])


        # Changing field 'UserPreferences.key'
        db.alter_column('desktop_userpreferences', 'key', self.gf('django.db.models.fields.CharField')(default='', max_length=20))

        # Changing field 'UserPreferences.value'
        db.alter_column('desktop_userpreferences', 'value', self.gf('django.db.models.fields.TextField')(default='', max_length=4096))

        # Changing field 'DocumentPermission.perms'
        db.alter_column('desktop_documentpermission', 'perms', self.gf('django.db.models.fields.TextField')())

        # Changing field 'DocumentTag.tag'
        db.alter_column('desktop_documenttag', 'tag', self.gf('django.db.models.fields.SlugField')(default='', max_length=50))

        # Changing field 'Document.extra'
        db.alter_column('desktop_document', 'extra', self.gf('django.db.models.fields.TextField')())

        # Changing field 'Document.name'
        db.alter_column('desktop_document', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Document.description'
        db.alter_column('desktop_document', 'description', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):
        # Deleting model 'Document2'
        db.delete_table('desktop_document2')

        # Removing M2M table for field tags on 'Document2'
        db.delete_table(db.shorten_name('desktop_document2_tags'))

        # Removing M2M table for field dependencies on 'Document2'
        db.delete_table(db.shorten_name('desktop_document2_dependencies'))


        # Changing field 'UserPreferences.key'
        db.alter_column('desktop_userpreferences', 'key', self.gf('django.db.models.fields.CharField')(max_length=20, null=True))

        # Changing field 'UserPreferences.value'
        db.alter_column('desktop_userpreferences', 'value', self.gf('django.db.models.fields.TextField')(max_length=4096, null=True))

        # Changing field 'DocumentPermission.perms'
        db.alter_column('desktop_documentpermission', 'perms', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'DocumentTag.tag'
        db.alter_column('desktop_documenttag', 'tag', self.gf('django.db.models.fields.SlugField')(max_length=50, null=True))

        # Changing field 'Document.extra'
        db.alter_column('desktop_document', 'extra', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Document.name'
        db.alter_column('desktop_document', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Document.description'
        db.alter_column('desktop_document', 'description', self.gf('django.db.models.fields.TextField')(null=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'desktop.document': {
            'Meta': {'object_name': 'Document'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc_owner'", 'to': "orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['desktop.DocumentTag']", 'db_index': 'True', 'symmetrical': 'False'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        'desktop.document2': {
            'Meta': {'object_name': 'Document2'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'dependencies_rel_+'", 'db_index': 'True', 'to': "orm['desktop.Document2']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_history': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc2_owner'", 'to': "orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags_rel_+'", 'db_index': 'True', 'to': "orm['desktop.Document2']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'db_index': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'6f8fe9aff12d44d0a2b01c863822dfa1'", 'max_length': '32', 'db_index': 'True'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        'desktop.documentpermission': {
            'Meta': {'object_name': 'DocumentPermission'},
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['desktop.Document']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['auth.Group']", 'db_table': "'documentpermission_groups'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perms': ('django.db.models.fields.TextField', [], {'default': "'read'"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['auth.User']", 'db_table': "'documentpermission_users'", 'symmetrical': 'False'})
        },
        'desktop.documenttag': {
            'Meta': {'object_name': 'DocumentTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'tag': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'desktop.settings': {
            'Meta': {'object_name': 'Settings'},
            'collect_usage': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tours_and_tutorials': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        'desktop.userpreferences': {
            'Meta': {'object_name': 'UserPreferences'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'value': ('django.db.models.fields.TextField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['desktop']