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

LOG = logging.getLogger(__name__)

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'MetaInstall'
        try:
            db.create_table('beeswax_metainstall', (
                ('installed_example', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ))
            db.send_create_signal('beeswax', ['MetaInstall'])
        except:
            LOG.exception("Initial db creation being skipped, likely because table already exists.")
            return

        # Adding model 'QueryHistory'
        db.create_table('beeswax_queryhistory', (
            ('submission_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_state', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('server_id', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True)),
            ('log_context', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True)),
            ('design', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['beeswax.SavedQuery'], null=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('query', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('has_results', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))

        db.send_create_signal('beeswax', ['QueryHistory'])

        # Adding model 'SavedQuery'
        db.create_table('beeswax_savedquery', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('is_auto', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('data', self.gf('django.db.models.fields.TextField')(max_length=65536)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('desc', self.gf('django.db.models.fields.TextField')(max_length=1024)),
        ))
        db.send_create_signal('beeswax', ['SavedQuery'])


    def backwards(self, orm):

        # Deleting model 'QueryHistory'
        db.delete_table('beeswax_queryhistory')

        # Deleting model 'SavedQuery'
        db.delete_table('beeswax_savedquery')

        # Deleting model 'MetaInstall'
        db.delete_table('beeswax_metainstall')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'beeswax.metainstall': {
            'Meta': {'object_name': 'MetaInstall'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installed_example': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'beeswax.queryhistory': {
            'Meta': {'object_name': 'QueryHistory'},
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['beeswax.SavedQuery']", 'null': 'True'}),
            'has_results': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_state': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'log_context': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'query': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'server_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'beeswax.savedquery': {
            'Meta': {'object_name': 'SavedQuery'},
            'data': ('django.db.models.fields.TextField', [], {'max_length': '65536'}),
            'desc': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_auto': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['beeswax']
