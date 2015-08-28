# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Node.name'
        db.alter_column(u'oozie_node', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'Job.name'
        db.alter_column(u'oozie_job', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

    def backwards(self, orm):

        # Changing field 'Node.name'
        db.alter_column(u'oozie_node', 'name', self.gf('django.db.models.fields.CharField')(max_length=40))

        # Changing field 'Job.name'
        db.alter_column(u'oozie_job', 'name', self.gf('django.db.models.fields.CharField')(max_length=40))

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
        u'oozie.bundle': {
            'Meta': {'object_name': 'Bundle', '_ormbases': [u'oozie.Job']},
            'coordinators': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['oozie.Coordinator']", 'through': u"orm['oozie.BundledCoordinator']", 'symmetrical': 'False'}),
            u'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'kick_off_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 8, 28, 0, 0)'})
        },
        u'oozie.bundledcoordinator': {
            'Meta': {'object_name': 'BundledCoordinator'},
            'bundle': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Bundle']"}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Coordinator']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parameters': ('django.db.models.fields.TextField', [], {'default': '\'[{"name":"oozie.use.system.libpath","value":"true"}]\''})
        },
        u'oozie.coordinator': {
            'Meta': {'object_name': 'Coordinator', '_ormbases': [u'oozie.Job']},
            'concurrency': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 8, 31, 0, 0)'}),
            'execution': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'frequency_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'frequency_unit': ('django.db.models.fields.CharField', [], {'default': "'days'", 'max_length': '20'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            u'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 8, 28, 0, 0)'}),
            'throttle': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/Los_Angeles'", 'max_length': '24'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Workflow']", 'null': 'True'})
        },
        u'oozie.datainput': {
            'Meta': {'object_name': 'DataInput'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Coordinator']"}),
            'dataset': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Dataset']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'oozie.dataoutput': {
            'Meta': {'object_name': 'DataOutput'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Coordinator']"}),
            'dataset': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Dataset']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        u'oozie.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'advanced_end_instance': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '128', 'blank': 'True'}),
            'advanced_start_instance': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '128'}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Coordinator']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'done_flag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'frequency_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'frequency_unit': ('django.db.models.fields.CharField', [], {'default': "'days'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instance_choice': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 8, 28, 0, 0)'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/Los_Angeles'", 'max_length': '24'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': "'/data/${YEAR}${MONTH}${DAY}'", 'max_length': '1024'})
        },
        u'oozie.decision': {
            'Meta': {'object_name': 'Decision'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.decisionend': {
            'Meta': {'object_name': 'DecisionEnd'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.distcp': {
            'Meta': {'object_name': 'DistCp'},
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        u'oozie.email': {
            'Meta': {'object_name': 'Email'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'cc': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'to': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'oozie.end': {
            'Meta': {'object_name': 'End'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.fork': {
            'Meta': {'object_name': 'Fork'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.fs': {
            'Meta': {'object_name': 'Fs'},
            'chmods': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'blank': 'True'}),
            'deletes': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'blank': 'True'}),
            'mkdirs': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'blank': 'True'}),
            'moves': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'touchzs': ('django.db.models.fields.TextField', [], {'default': "'[]'", 'blank': 'True'})
        },
        u'oozie.generic': {
            'Meta': {'object_name': 'Generic'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'xml': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        u'oozie.history': {
            'Meta': {'object_name': 'History'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Job']"}),
            'oozie_job_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'properties': ('django.db.models.fields.TextField', [], {}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'oozie.hive': {
            'Meta': {'object_name': 'Hive'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "'hive-config.xml'", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'script_path': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'oozie.java': {
            'Meta': {'object_name': 'Java'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'args': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'capture_output': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'java_opts': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'main_class': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        u'oozie.job': {
            'Meta': {'object_name': 'Job'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            'deployment_dir': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_shared': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'is_trashed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'parameters': ('django.db.models.fields.TextField', [], {'default': '\'[{"name":"oozie.use.system.libpath","value":"true"}]\''}),
            'schema_version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'oozie.join': {
            'Meta': {'object_name': 'Join'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.kill': {
            'Meta': {'object_name': 'Kill'},
            'message': ('django.db.models.fields.CharField', [], {'default': "'Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]'", 'max_length': '256'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.link': {
            'Meta': {'object_name': 'Link'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_node'", 'to': u"orm['oozie.Node']"}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_node'", 'to': u"orm['oozie.Node']"})
        },
        u'oozie.mapreduce': {
            'Meta': {'object_name': 'Mapreduce'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        u'oozie.node': {
            'Meta': {'object_name': 'Node'},
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parents'", 'symmetrical': 'False', 'through': u"orm['oozie.Link']", 'to': u"orm['oozie.Node']"}),
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'", 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'node_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oozie.Workflow']"})
        },
        u'oozie.pig': {
            'Meta': {'object_name': 'Pig'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'script_path': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'oozie.shell': {
            'Meta': {'object_name': 'Shell'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'capture_output': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'command': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        u'oozie.sqoop': {
            'Meta': {'object_name': 'Sqoop'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'script_path': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        u'oozie.ssh': {
            'Meta': {'object_name': 'Ssh'},
            'capture_output': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'command': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'host': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'oozie.start': {
            'Meta': {'object_name': 'Start'},
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'oozie.streaming': {
            'Meta': {'object_name': 'Streaming'},
            'archives': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'files': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'mapper': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'reducer': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'oozie.subworkflow': {
            'Meta': {'object_name': 'SubWorkflow'},
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            u'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'propagate_configuration': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sub_workflow': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['oozie.Workflow']", 'null': 'True', 'blank': 'True'})
        },
        u'oozie.workflow': {
            'Meta': {'object_name': 'Workflow', '_ormbases': [u'oozie.Job']},
            'end': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'end_workflow'", 'null': 'True', 'to': u"orm['oozie.End']"}),
            'is_single': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            u'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['oozie.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'managed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'start': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'start_workflow'", 'null': 'True', 'to': u"orm['oozie.Start']"})
        }
    }

    complete_apps = ['oozie']