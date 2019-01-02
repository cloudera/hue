# encoding: utf-8
from south.db import db
from south.v2 import DataMigration
from django.db import connection
from django.db import models

from useradmin.models import UserProfile


class Migration(DataMigration):

    def forwards(self, orm):
        """
        This migration has been customized to support upgrades from Cloudera
        Enterprise 3.5, as well as Hue 1.2
        """
        # These will be removed if upgrading from a previous version of
        # Cloudera Enterprise
        if 'userman_groupadministrator' in connection.introspection.table_names():
          db.delete_table('userman_groupadministrator')
        if 'userman_grouprelations' in connection.introspection.table_names():
          db.delete_table('userman_grouprelations')

        if 'userman_userprofile' in connection.introspection.table_names():
          db.rename_table('userman_userprofile', 'useradmin_userprofile')
          db.delete_column('useradmin_userprofile', 'primary_group_id')
          db.create_index('useradmin_userprofile', ['user_id'])

          db.alter_column('useradmin_userprofile', 'creation_method', models.CharField(editable=True, null=False, max_length=64, default=UserProfile.CreationMethod.HUE))
          for up in UserProfile.objects.all():
            # From when CreationMethod was not an Enum
            # LDAP == 1
            # HUE == 0
            if up.creation_method == '1':
              up.creation_method = UserProfile.CreationMethod.EXTERNAL.name
            elif up.creation_method == '0':
              up.creation_method = UserProfile.CreationMethod.HUE
            up.save()
        else:
          # Adding model 'UserProfile'
          db.create_table('useradmin_userprofile', (
              ('home_directory', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True)),
              ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
              ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
          ))
          db.commit_transaction()
          db.start_transaction()
          db.send_create_signal('useradmin', ['UserProfile'])

        if 'userman_grouppermission' in connection.introspection.table_names():
          db.rename_table('userman_grouppermission', 'useradmin_grouppermission')
          db.rename_column('useradmin_grouppermission', 'desktop_permission_id', 'hue_permission_id')
          db.create_index('useradmin_grouppermission', ['group_id'])
          db.create_index('useradmin_grouppermission', ['hue_permission_id'])
        else:
          # Adding model 'GroupPermission'
          db.create_table('useradmin_grouppermission', (
              ('hue_permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['useradmin.HuePermission'])),
              ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
              ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
          ))
          db.commit_transaction()
          db.start_transaction()
          db.send_create_signal('useradmin', ['GroupPermission'])

        if 'userman_desktoppermission' in connection.introspection.table_names():
          db.rename_table('userman_desktoppermission', 'useradmin_huepermission')
        else:
          # Adding model 'HuePermission'
          db.create_table('useradmin_huepermission', (
              ('action', self.gf('django.db.models.fields.CharField')(max_length=100)),
              ('app', self.gf('django.db.models.fields.CharField')(max_length=30)),
              ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
              ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
          ))
          db.commit_transaction()
          db.start_transaction()
          db.send_create_signal('useradmin', ['HuePermission'])

    def backwards(self, orm):

        # Deleting model 'UserProfile'
        db.delete_table('useradmin_userprofile')

        # Deleting model 'GroupPermission'
        db.delete_table('useradmin_grouppermission')

        # Deleting model 'HuePermission'
        db.delete_table('useradmin_huepermission')


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
        'useradmin.huepermission': {
            'Meta': {'object_name': 'HuePermission'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'app': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'through': "orm['useradmin.GroupPermission']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'useradmin.grouppermission': {
            'Meta': {'object_name': 'GroupPermission'},
            'hue_permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['useradmin.HuePermission']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'useradmin.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'home_directory': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['useradmin']
