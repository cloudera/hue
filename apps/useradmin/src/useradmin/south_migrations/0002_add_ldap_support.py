# encoding: utf-8
from south.db import db
from south.v2 import DataMigration

from django.contrib.auth.models import User
from django.db import connection
from useradmin.models import create_profile_for_user
from useradmin.models import UserProfile

class Migration(DataMigration):

    def forwards(self, orm):
        """
        This migration has been customized to support upgrades from Cloudera
        Enterprise 3.5, as well as Hue 1.2
        """
        if 'userman_ldapgroup' in connection.introspection.table_names():
          db.rename_table('userman_ldapgroup', 'useradmin_ldapgroup')
          db.delete_column('useradmin_ldapgroup', 'hidden')
        else:
          # Adding model 'LdapGroup'
          db.create_table('useradmin_ldapgroup', (
              ('group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='group', to=orm['auth.Group'])),
              ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
          ))
          db.send_create_signal('useradmin', ['LdapGroup'])

        # Adding field 'UserProfile.creation_method'
        try:
          db.add_column('useradmin_userprofile', 'creation_method', self.gf('django.db.models.fields.CharField')(max_length=64, default=UserProfile.CreationMethod.HUE.name), keep_default=False)
        except Exception:
          # It's possible that we could run into an error here, because this
          # table may have been migrated from Cloudera Enterprise, in which case
          # this column would already exist.
          pass

        for user in User.objects.all():
          try:
            orm.UserProfile.objects.get(user=user)
          except orm.UserProfile.DoesNotExist:
            create_profile_for_user(user)


    def backwards(self, orm):

        # Deleting model 'LdapGroup'
        db.delete_table('useradmin_ldapgroup')

        # Deleting field 'UserProfile.creation_method'
        db.delete_column('useradmin_userprofile', 'creation_method')


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
        'useradmin.grouppermission': {
            'Meta': {'object_name': 'GroupPermission'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'hue_permission': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['useradmin.HuePermission']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'useradmin.huepermission': {
            'Meta': {'object_name': 'HuePermission'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'app': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'through': "orm['useradmin.GroupPermission']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'useradmin.ldapgroup': {
            'Meta': {'object_name': 'LdapGroup'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'useradmin.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'creation_method': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'home_directory': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['useradmin']
