# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Job'
        db.create_table('oozie_job', (
            ('is_shared', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('parameters', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('deployment_dir', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('schema_version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('oozie', ['Job'])

        # Adding model 'Workflow'
        db.create_table('oozie_workflow', (
            ('job_xml', self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True)),
            ('end', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='end_workflow', null=True, to=orm['oozie.Node'])),
            ('is_single', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('job_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Job'], unique=True, primary_key=True)),
            ('job_properties', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('start', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='start_workflow', null=True, to=orm['oozie.Node'])),
        ))
        db.send_create_signal('oozie', ['Workflow'])

        # Adding model 'Link'
        db.create_table('oozie_link', (
            ('comment', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(related_name='child_node', to=orm['oozie.Node'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='parent_node', to=orm['oozie.Node'])),
        ))
        db.send_create_signal('oozie', ['Link'])

        # Adding model 'Node'
        db.create_table('oozie_node', (
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Workflow'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('node_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('oozie', ['Node'])

        # Adding model 'Mapreduce'
        db.create_table('oozie_mapreduce', (
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('job_xml', self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True)),
            ('jar_path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('job_properties', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True)),
            ('prepares', self.gf('django.db.models.fields.TextField')(default='[]')),
        ))
        db.send_create_signal('oozie', ['Mapreduce'])

        # Adding model 'Streaming'
        db.create_table('oozie_streaming', (
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('mapper', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('reducer', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('job_properties', self.gf('django.db.models.fields.TextField')(default='[{"name":"oozie.use.system.libpath","value":"true"}]')),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('oozie', ['Streaming'])

        # Adding model 'Java'
        db.create_table('oozie_java', (
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('job_xml', self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True)),
            ('jar_path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('java_opts', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('args', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('job_properties', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('prepares', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
            ('main_class', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('oozie', ['Java'])

        # Adding model 'Pig'
        db.create_table('oozie_pig', (
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('job_xml', self.gf('django.db.models.fields.CharField')(default='', max_length=512, blank=True)),
            ('job_properties', self.gf('django.db.models.fields.TextField')(default='[{"name":"oozie.use.system.libpath","value":"true"}]')),
            ('params', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
            ('prepares', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('script_path', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('oozie', ['Pig'])

        # Adding model 'Start'
        db.create_table('oozie_start', (
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True)),
        ))
        db.send_create_signal('oozie', ['Start'])

        # Adding model 'End'
        db.create_table('oozie_end', (
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('oozie', ['End'])

        # Adding model 'Kill'
        db.create_table('oozie_kill', (
            ('message', self.gf('django.db.models.fields.CharField')(default='Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]', max_length=256)),
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('oozie', ['Kill'])

        # Adding model 'Fork'
        db.create_table('oozie_fork', (
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('oozie', ['Fork'])

        # Adding model 'Join'
        db.create_table('oozie_join', (
            ('node_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Node'], unique=True, primary_key=True)),
        ))
        db.send_create_signal('oozie', ['Join'])

        # Adding model 'Coordinator'
        db.create_table('oozie_coordinator', (
            ('end', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 7, 15, 12, 23, 992784))),
            ('concurrency', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('frequency_number', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Workflow'], null=True)),
            ('job_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Job'], unique=True, primary_key=True)),
            ('frequency_unit', self.gf('django.db.models.fields.CharField')(default='days', max_length=20)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 4, 15, 12, 23, 992735))),
            ('timeout', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='America/Los_Angeles', max_length=24)),
            ('throttle', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('execution', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
        ))
        db.send_create_signal('oozie', ['Coordinator'])

        # Adding model 'Dataset'
        db.create_table('oozie_dataset', (
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True)),
            ('frequency_number', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Coordinator'])),
            ('frequency_unit', self.gf('django.db.models.fields.CharField')(default='days', max_length=20)),
            ('uri', self.gf('django.db.models.fields.CharField')(default='/data/${YEAR}${MONTH}${DAY}', max_length=1024)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 9, 4, 15, 12, 23, 993608))),
            ('timezone', self.gf('django.db.models.fields.CharField')(default='America/Los_Angeles', max_length=24)),
            ('done_flag', self.gf('django.db.models.fields.CharField')(default='', max_length=64, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('oozie', ['Dataset'])

        # Adding model 'DataInput'
        db.create_table('oozie_datainput', (
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Coordinator'])),
            ('dataset', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Dataset'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('oozie', ['DataInput'])

        # Adding model 'DataOutput'
        db.create_table('oozie_dataoutput', (
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Coordinator'])),
            ('dataset', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['oozie.Dataset'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('oozie', ['DataOutput'])

        # Adding model 'History'
        db.create_table('oozie_history', (
            ('submission_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, db_index=True, blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oozie.Job'])),
            ('properties', self.gf('django.db.models.fields.TextField')()),
            ('oozie_job_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('submitter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('oozie', ['History'])


    def backwards(self, orm):

        # Deleting model 'Job'
        db.delete_table('oozie_job')

        # Deleting model 'Workflow'
        db.delete_table('oozie_workflow')

        # Deleting model 'Link'
        db.delete_table('oozie_link')

        # Deleting model 'Node'
        db.delete_table('oozie_node')

        # Deleting model 'Mapreduce'
        db.delete_table('oozie_mapreduce')

        # Deleting model 'Streaming'
        db.delete_table('oozie_streaming')

        # Deleting model 'Java'
        db.delete_table('oozie_java')

        # Deleting model 'Pig'
        db.delete_table('oozie_pig')

        # Deleting model 'Start'
        db.delete_table('oozie_start')

        # Deleting model 'End'
        db.delete_table('oozie_end')

        # Deleting model 'Kill'
        db.delete_table('oozie_kill')

        # Deleting model 'Fork'
        db.delete_table('oozie_fork')

        # Deleting model 'Join'
        db.delete_table('oozie_join')

        # Deleting model 'Coordinator'
        db.delete_table('oozie_coordinator')

        # Deleting model 'Dataset'
        db.delete_table('oozie_dataset')

        # Deleting model 'DataInput'
        db.delete_table('oozie_datainput')

        # Deleting model 'DataOutput'
        db.delete_table('oozie_dataoutput')

        # Deleting model 'History'
        db.delete_table('oozie_history')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'oozie.coordinator': {
            'Meta': {'object_name': 'Coordinator', '_ormbases': ['oozie.Job']},
            'concurrency': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 7, 15, 12, 23, 992784)'}),
            'execution': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'frequency_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'frequency_unit': ('django.db.models.fields.CharField', [], {'default': "'days'", 'max_length': '20'}),
            'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 4, 15, 12, 23, 992735)'}),
            'throttle': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timeout': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/Los_Angeles'", 'max_length': '24'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Workflow']", 'null': 'True'})
        },
        'oozie.datainput': {
            'Meta': {'object_name': 'DataInput'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Coordinator']"}),
            'dataset': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Dataset']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'oozie.dataoutput': {
            'Meta': {'object_name': 'DataOutput'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Coordinator']"}),
            'dataset': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Dataset']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'})
        },
        'oozie.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Coordinator']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'done_flag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '64', 'blank': 'True'}),
            'frequency_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'frequency_unit': ('django.db.models.fields.CharField', [], {'default': "'days'", 'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 4, 15, 12, 23, 993608)'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/Los_Angeles'", 'max_length': '24'}),
            'uri': ('django.db.models.fields.CharField', [], {'default': "'/data/${YEAR}${MONTH}${DAY}'", 'max_length': '1024'})
        },
        'oozie.end': {
            'Meta': {'object_name': 'End'},
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        'oozie.fork': {
            'Meta': {'object_name': 'Fork'},
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        'oozie.history': {
            'Meta': {'object_name': 'History'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Job']"}),
            'oozie_job_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'properties': ('django.db.models.fields.TextField', [], {}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'oozie.java': {
            'Meta': {'object_name': 'Java'},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'args': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'java_opts': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'main_class': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        'oozie.job': {
            'Meta': {'object_name': 'Job'},
            'deployment_dir': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_shared': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'parameters': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'schema_version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'oozie.join': {
            'Meta': {'object_name': 'Join'},
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        'oozie.kill': {
            'Meta': {'object_name': 'Kill'},
            'message': ('django.db.models.fields.CharField', [], {'default': "'Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]'", 'max_length': '256'}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'})
        },
        'oozie.link': {
            'Meta': {'object_name': 'Link'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_node'", 'to': "orm['oozie.Node']"}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'child_node'", 'to': "orm['oozie.Node']"})
        },
        'oozie.mapreduce': {
            'Meta': {'object_name': 'Mapreduce'},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True'}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"})
        },
        'oozie.node': {
            'Meta': {'object_name': 'Node'},
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'parents'", 'symmetrical': 'False', 'through': "orm['oozie.Link']", 'to': "orm['oozie.Node']"}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'node_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['oozie.Workflow']"})
        },
        'oozie.pig': {
            'Meta': {'object_name': 'Pig'},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': '\'[{"name":"oozie.use.system.libpath","value":"true"}]\''}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'prepares': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'script_path': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'oozie.start': {
            'Meta': {'object_name': 'Start'},
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True'})
        },
        'oozie.streaming': {
            'Meta': {'object_name': 'Streaming'},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': '\'[{"name":"oozie.use.system.libpath","value":"true"}]\''}),
            'mapper': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'node_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Node']", 'unique': 'True', 'primary_key': 'True'}),
            'reducer': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'oozie.workflow': {
            'Meta': {'object_name': 'Workflow', '_ormbases': ['oozie.Job']},
            'end': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'end_workflow'", 'null': 'True', 'to': "orm['oozie.End']"}),
            'is_single': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['oozie.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'job_xml': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '512', 'blank': 'True'}),
            'start': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'start_workflow'", 'null': 'True', 'to': "orm['oozie.Start']"})
        }
    }

    complete_apps = ['oozie']
