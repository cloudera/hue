# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'QueryHistory.is_cleared'
        db.add_column(u'beeswax_queryhistory', 'is_cleared',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'QueryHistory.is_cleared'
        db.delete_column(u'beeswax_queryhistory', 'is_cleared')


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
        u'beeswax.metainstall': {
            'Meta': {'object_name': 'MetaInstall'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installed_example': ('django.db.models.fields.BooleanField', [], {})
        },
        u'beeswax.queryhistory': {
            'Meta': {'ordering': "['-submission_date']", 'object_name': 'QueryHistory'},
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['beeswax.SavedQuery']", 'null': 'True'}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'has_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_cleared': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_redacted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'log_context': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'modified_row_count': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'notify': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'operation_type': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'query_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'server_guid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '1024', 'null': 'True'}),
            'server_host': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'server_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'server_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'server_port': ('django.db.models.fields.PositiveIntegerField', [], {'default': '10000'}),
            'server_type': ('django.db.models.fields.CharField', [], {'default': "'beeswax'", 'max_length': '128'}),
            'statement_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'beeswax.savedquery': {
            'Meta': {'ordering': "['-mtime']", 'object_name': 'SavedQuery'},
            'data': ('django.db.models.fields.TextField', [], {'max_length': '65536'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_auto': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_redacted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        u'beeswax.session': {
            'Meta': {'object_name': 'Session'},
            'application': ('django.db.models.fields.CharField', [], {'default': "'beeswax'", 'max_length': '128'}),
            'guid': ('django.db.models.fields.TextField', [], {'max_length': "'100'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_used': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'properties': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'secret': ('django.db.models.fields.TextField', [], {'max_length': "'100'"}),
            'server_protocol_version': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status_code': ('django.db.models.fields.PositiveSmallIntegerField', [], {})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['beeswax']