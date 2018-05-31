# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Nonce'
        db.create_table(u'oidc_auth_nonce', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issuer_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('redirect_url', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'oidc_auth', ['Nonce'])

        # Adding model 'OpenIDProvider'
        db.create_table(u'oidc_auth_openidprovider', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issuer', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('authorization_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('token_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('userinfo_endpoint', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('jwks_uri', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('signing_alg', self.gf('django.db.models.fields.CharField')(default='HS256', max_length=5)),
            ('client_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('client_secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'oidc_auth', ['OpenIDProvider'])

        # Adding model 'OpenIDUser'
        db.create_table(u'oidc_auth_openiduser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sub', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('issuer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['oidc_auth.OpenIDProvider'])),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='oidc_account', unique=True, to=orm['auth.User'])),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('refresh_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'oidc_auth', ['OpenIDUser'])


    def backwards(self, orm):
        # Deleting model 'Nonce'
        db.delete_table(u'oidc_auth_nonce')

        # Deleting model 'OpenIDProvider'
        db.delete_table(u'oidc_auth_openidprovider')

        # Deleting model 'OpenIDUser'
        db.delete_table(u'oidc_auth_openiduser')


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
        u'oidc_auth.nonce': {
            'Meta': {'object_name': 'Nonce'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'redirect_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        u'oidc_auth.openidprovider': {
            'Meta': {'object_name': 'OpenIDProvider'},
            'authorization_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'client_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'client_secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'jwks_uri': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'signing_alg': ('django.db.models.fields.CharField', [], {'default': "'HS256'", 'max_length': '5'}),
            'token_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'userinfo_endpoint': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'oidc_auth.openiduser': {
            'Meta': {'object_name': 'OpenIDUser'},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issuer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['oidc_auth.OpenIDProvider']"}),
            'refresh_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sub': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'oidc_account'", 'unique': 'True', 'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['oidc_auth']