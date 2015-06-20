# encoding: utf-8
import logging
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import connection, models

from desktop.models import Document

LOG = logging.getLogger(__name__)

class Migration(SchemaMigration):

    def forwards(self, orm):

        # On SQLite, database transactions (which are used by
        # `Document.objects.sync`) requires autocommit to be turned on. South
        # however doesn't enable this by default.
        if connection.vendor == 'sqlite':
            autocommit = connection.get_autocommit()
            connection.set_autocommit(True)

        # Adding model 'Document'
        if 'desktop_document' not in connection.introspection.table_names():
            db.create_table('desktop_document', (
                ('description', self.gf('django.db.models.fields.TextField')(default='')),
                ('extra', self.gf('django.db.models.fields.TextField')(default='')),
                ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
                ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
                ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
                ('version', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
                ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='doc_owner', to=orm['auth.User'])),
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('name', self.gf('django.db.models.fields.TextField')(default='')),
            ))
            db.send_create_signal('desktop', ['Document'])

        # Adding model 'DocumentPermission'
        if 'desktop_documentpermission' not in connection.introspection.table_names():
            db.create_table('desktop_documentpermission', (
                ('perms', self.gf('django.db.models.fields.TextField')(default='read')),
                ('doc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['desktop.Document'])),
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ))
            db.send_create_signal('desktop', ['DocumentPermission'])

        # Adding M2M table for field users on 'DocumentPermission'
        if 'documentpermission_users' not in connection.introspection.table_names():
            db.create_table('documentpermission_users', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('documentpermission', models.ForeignKey(orm['desktop.documentpermission'], null=False)),
                ('user', models.ForeignKey(orm['auth.user'], null=False))
            ))
            db.create_unique('documentpermission_users', ['documentpermission_id', 'user_id'])

        # Adding M2M table for field groups on 'DocumentPermission'
        if 'documentpermission_groups' not in connection.introspection.table_names():
            db.create_table('documentpermission_groups', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('documentpermission', models.ForeignKey(orm['desktop.documentpermission'], null=False)),
                ('group', models.ForeignKey(orm['auth.group'], null=False))
            ))
            db.create_unique('documentpermission_groups', ['documentpermission_id', 'group_id'])

        # Adding model 'DocumentTag'
        if 'desktop_documenttag' not in connection.introspection.table_names():
            db.create_table('desktop_documenttag', (
                ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
                ('tag', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ))
            db.send_create_signal('desktop', ['DocumentTag'])

        # Adding M2M table for field tags on 'Document'
        if 'desktop_document_tags' not in connection.introspection.table_names():
            db.create_table('desktop_document_tags', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('document', models.ForeignKey(orm['desktop.document'], null=False)),
                ('documenttag', models.ForeignKey(orm['desktop.documenttag'], null=False))
            ))
            db.create_unique('desktop_document_tags', ['document_id', 'documenttag_id'])

        if not db.dry_run:
            Document.objects.sync()

        if connection.vendor == 'sqlite':
            connection.set_autocommit(autocommit)

    def backwards(self, orm):

        # Deleting model 'DocumentPermission'
        db.delete_table('desktop_documentpermission')

        # Remove old m2m fields
        try:
            # Removing M2M table for field users on 'DocumentPermission'
            db.delete_table('desktop_documentpermission_users')

            # Removing M2M table for field groups on 'DocumentPermission'
            db.delete_table('desktop_documentpermission_groups')
        except:
            LOG.exception('failed to delete tables')

        # Remove new m2m fields
        try:
            # Removing M2M table for field users on 'DocumentPermission'
            db.delete_table('documentpermission_users')

            # Removing M2M table for field groups on 'DocumentPermission'
            db.delete_table('documentpermission_groups')
        except:
            LOG.exception('failed to delete tables')

        # Deleting model 'DocumentTag'
        db.delete_table('desktop_documenttag')

        # Deleting model 'Document'
        db.delete_table('desktop_document')

        # Removing M2M table for field tags on 'Document'
        db.delete_table('desktop_document_tags')
    
    
    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 12, 14, 47, 31, 225858)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 9, 12, 14, 47, 31, 225783)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
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
            'name': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc_owner'", 'to': "orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['desktop.DocumentTag']", 'db_index': 'True', 'symmetrical': 'False'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        'desktop.documentpermission': {
            'Meta': {'object_name': 'DocumentPermission'},
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['desktop.Document']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['auth.Group']", 'null': 'True', 'db_table': "'documentpermission_groups'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perms': ('django.db.models.fields.TextField', [], {'default': "'read'"}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': "orm['auth.User']", 'null': 'True', 'db_table': "'documentpermission_users'", 'symmetrical': 'False'})
        },
        'desktop.documenttag': {
            'Meta': {'object_name': 'DocumentTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'tag': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'desktop.settings': {
            'Meta': {'object_name': 'Settings'},
            'collect_usage': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tours_and_tutorials': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True', 'blank': 'True'})
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
