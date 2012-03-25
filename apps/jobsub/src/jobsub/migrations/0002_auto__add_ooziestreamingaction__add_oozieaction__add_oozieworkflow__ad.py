#!/usr/bin/env python
# encoding: utf-8
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.utils import DatabaseError

from desktop.lib.django_db_util import remove_content_type
from jobsub.models import JobDesign, OozieJavaAction, OozieStreamingAction, OozieDesign

LOG = logging.getLogger(__name__)

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'OozieStreamingAction'
        db.create_table('jobsub_ooziestreamingaction', (
            ('oozieaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jobsub.OozieAction'], unique=True, primary_key=True)),
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('mapper', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('reducer', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('job_properties', self.gf('django.db.models.fields.CharField')(default='[]', max_length=32768)),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
        ))
        db.send_create_signal('jobsub', ['OozieStreamingAction'])

        # Adding model 'OozieAction'
        db.create_table('jobsub_oozieaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('jobsub', ['OozieAction'])

        # Adding model 'OozieDesign'
        db.create_table('jobsub_ooziedesign', (
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('root_action', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jobsub.OozieAction'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('jobsub', ['OozieDesign'])

        # Adding model 'JobHistory'
        db.create_table('jobsub_jobhistory', (
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('submission_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('design', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jobsub.OozieDesign'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal('jobsub', ['JobHistory'])

        # Adding model 'OozieMapreduceAction'
        db.create_table('jobsub_ooziemapreduceaction', (
            ('oozieaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jobsub.OozieAction'], unique=True, primary_key=True)),
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('jar_path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('job_properties', self.gf('django.db.models.fields.CharField')(default='[]', max_length=32768)),
        ))
        db.send_create_signal('jobsub', ['OozieMapreduceAction'])

        # Adding model 'OozieJavaAction'
        db.create_table('jobsub_ooziejavaaction', (
            ('oozieaction_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jobsub.OozieAction'], unique=True, primary_key=True)),
            ('files', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('jar_path', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('java_opts', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('args', self.gf('django.db.models.fields.CharField')(max_length=4096, blank=True)),
            ('job_properties', self.gf('django.db.models.fields.CharField')(default='[]', max_length=32768)),
            ('archives', self.gf('django.db.models.fields.CharField')(default='[]', max_length=512)),
            ('main_class', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('jobsub', ['OozieJavaAction'])

        # Adding field 'CheckForSetup.setup_level'
        db.add_column('jobsub_checkforsetup', 'setup_level', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)
    
        # Delete legacy tables. Note that this only applies to Hue 1.x installations
        try:
            db.delete_table('jobsub_submission')
            remove_content_type('jobsub', 'submission')
        except DatabaseError, ex:
            pass    # Table doesn't exist. Ok.

        try:
            db.delete_table('jobsub_serversubmissionstate')
            remove_content_type('jobsub', 'serversubmissionstate')
        except DatabaseError, ex:
            pass    # Table doesn't exist. Ok.

        hue1_to_hue2_data_migration()


    def backwards(self, orm):
        
        # Deleting model 'OozieStreamingAction'
        db.delete_table('jobsub_ooziestreamingaction')

        # Deleting model 'OozieAction'
        db.delete_table('jobsub_oozieaction')

        # Deleting model 'OozieDesign'
        db.delete_table('jobsub_ooziedesign')

        # Deleting model 'JobHistory'
        db.delete_table('jobsub_jobhistory')

        # Deleting model 'OozieMapreduceAction'
        db.delete_table('jobsub_ooziemapreduceaction')

        # Deleting model 'OozieJavaAction'
        db.delete_table('jobsub_ooziejavaaction')

        # Deleting field 'CheckForSetup.setup_level'
        db.delete_column('jobsub_checkforsetup', 'setup_level')
    
    
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
        'jobsub.checkforsetup': {
            'Meta': {'object_name': 'CheckForSetup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'setup_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'setup_run': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'jobsub.jobdesign': {
            'Meta': {'object_name': 'JobDesign'},
            'data': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'jobsub.jobhistory': {
            'Meta': {'object_name': 'JobHistory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieDesign']"})
        },
        'jobsub.oozieaction': {
            'Meta': {'object_name': 'OozieAction'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jobsub.ooziejavaaction': {
            'Meta': {'object_name': 'OozieJavaAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'args': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'java_opts': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '32768'}),
            'main_class': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziemapreduceaction': {
            'Meta': {'object_name': 'OozieMapreduceAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'job_properties': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '32768'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziestreamingaction': {
            'Meta': {'object_name': 'OozieStreamingAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'job_properties': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '32768'}),
            'mapper': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'}),
            'reducer': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'jobsub.ooziedesign': {
            'Meta': {'object_name': 'OozieDesign'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'root_action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieAction']"})
        }
    }
    
    complete_apps = ['jobsub']


#
# Data migration helper
#

def hue1_to_hue2_data_migration():
  """
  Data migration from the JobDesign table to the new Oozie-based models.

  The migration could be incomplete:
  - Jar types, for which the main class wasn't specified.

  We add an `(incomplete)' marker to the design name to alert the user.
  """
  jd_list = JobDesign.objects.all()

  for jd in jd_list:
    if jd.type == 'jar':
      job_design_migration_for_jar(jd)
    elif jd.type == 'streaming':
      job_design_migration_for_streaming(jd)
    else:
      LOG.warn("Unknown JobDesign type '%s' in the old table. Row id: %s" %
               (jd.type, jd.id))


def job_design_migration_for_jar(jd):
  """Migrate one jar type design"""
  data = json.loads(jd.data)
  action = OozieJavaAction(action_type=OozieJavaAction.ACTION_TYPE,
                           jar_path=data['jarfile'],
                           main_class="please.specify.in.the.job.design",
                           args=data['arguments'])
  action.save()

  design = OozieDesign(owner=jd.owner,
                       name=jd.name + ' (incomplete)',
                       description=jd.description,
                       root_action=action)
  design.save()


def job_design_migration_for_streaming(jd):
  """Migrate one streaming type design"""
  data = json.loads(jd.data)

  files = json.dumps(data['cache_files'])
  archives = json.dumps(data['cache_archives'])
  properties = data['hadoop_properties']

  def add_property(key, value):
    if value:
      properties[key] = value

  add_property('mapred.input.dir', ','.join(data['input']))
  add_property('mapred.output.dir', data['output'])
  add_property('mapred.combiner.class', data['combiner_class'])
  add_property('mapred.mapper.class', data['mapper_class'])
  add_property('mapred.reducer.class', data['reducer_class'])
  add_property('mapred.partitioner.class', data['partitioner_class'])
  add_property('mapred.input.format.class', data['inputformat_class'])
  add_property('mapred.output.format.class', data['outputformat_class'])
  add_property('mapred.reduce.tasks', data['num_reduce_tasks'])

  action = OozieStreamingAction(action_type=OozieStreamingAction.ACTION_TYPE,
                                mapper=data['mapper_cmd'],
                                reducer=data['reducer_cmd'],
                                files=files,
                                archives=archives,
                                job_properties=properties)
  action.save()

  design = OozieDesign(owner=jd.owner,
                       name=jd.name,
                       description=jd.description,
                       root_action=action)
  design.save()

