# -*- coding: utf-8 -*-
import datetime
from django.utils.translation import ugettext as _
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'JobDesign.data'
        db.alter_column('jobsub_jobdesign', 'data', self.gf('django.db.models.fields.TextField')())
        db.alter_column('jobsub_ooziejavaaction', 'args', self.gf('django.db.models.fields.TextField')(blank=True))

    def backwards(self, orm):

        # Changing field 'JobDesign.data'
        # db.alter_column('jobsub_jobdesign', 'data', self.gf('django.db.models.fields.CharField')(max_length=4096))
        # db.alter_column('jobsub_ooziejavaaction', 'data', self.gf('django.db.models.fields.CharField')(max_length=4096, blank=True))
        raise RuntimeError(_("Cannot backwards migrate this change."))

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
        'jobsub.checkforsetup': {
            'Meta': {'object_name': 'CheckForSetup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'setup_run': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'jobsub.jobdesign': {
            'Meta': {'object_name': 'JobDesign'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'jobsub.jobhistory': {
            'Meta': {'object_name': 'JobHistory'},
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieDesign']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'jobsub.oozieaction': {
            'Meta': {'object_name': 'OozieAction'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jobsub.ooziedesign': {
            'Meta': {'object_name': 'OozieDesign'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'root_action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieAction']"})
        },
        'jobsub.ooziejavaaction': {
            'Meta': {'object_name': 'OozieJavaAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'args': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'java_opts': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'main_class': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziemapreduceaction': {
            'Meta': {'object_name': 'OozieMapreduceAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziestreamingaction': {
            'Meta': {'object_name': 'OozieStreamingAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'mapper': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'}),
            'reducer': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['jobsub']
