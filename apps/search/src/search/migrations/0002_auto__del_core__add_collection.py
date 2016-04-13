# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting model 'Core'
        db.delete_table('search_core')

        # Adding model 'Collection'
        db.create_table('search_collection', (
            ('properties', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('sorting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Sorting'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('facets', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Facet'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('is_core_only', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Result'])),
            ('cores', self.gf('django.db.models.fields.TextField')(default='{}')),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('search', ['Collection'])


    def backwards(self, orm):

        # Adding model 'Core'
        db.create_table('search_core', (
            ('sorting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Sorting'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40, unique=True)),
            ('facets', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Facet'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Result'])),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('properties', self.gf('django.db.models.fields.TextField')(default='[]')),
        ))
        db.send_create_signal('search', ['Core'])

        # Deleting model 'Collection'
        db.delete_table('search_collection')


    models = {
        'search.collection': {
            'Meta': {'object_name': 'Collection'},
            'cores': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'facets': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Facet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_core_only': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'properties': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Result']"}),
            'sorting': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Sorting']"})
        },
        'search.facet': {
            'Meta': {'object_name': 'Facet'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'search.result': {
            'Meta': {'object_name': 'Result'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'search.sorting': {
            'Meta': {'object_name': 'Sorting'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['search']
