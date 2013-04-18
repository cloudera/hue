# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Facet'
        db.create_table('search_facet', (
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('search', ['Facet'])

        # Adding model 'Result'
        db.create_table('search_result', (
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('search', ['Result'])

        # Adding model 'Sorting'
        db.create_table('search_sorting', (
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('search', ['Sorting'])

        # Adding model 'Core'
        db.create_table('search_core', (
            ('sorting', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Sorting'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('facets', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Facet'])),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['search.Result'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('properties', self.gf('django.db.models.fields.TextField')(default='[]')),
        ))
        db.send_create_signal('search', ['Core'])


    def backwards(self, orm):

        # Deleting model 'Facet'
        db.delete_table('search_facet')

        # Deleting model 'Result'
        db.delete_table('search_result')

        # Deleting model 'Sorting'
        db.delete_table('search_sorting')

        # Deleting model 'Core'
        db.delete_table('search_core')


    models = {
        'search.core': {
            'Meta': {'object_name': 'Core'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'facets': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.Facet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
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
