# -*- coding: utf-8 -*-
import logging
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, transaction

from desktop.models import Document2


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Unfortunately before this change it was possible to have multiple
        # documents that shared the same (uuid, version, is_history). However,
        # as opposed to before we can't just delete the records as Document2
        # documents contain user data. So instead what we'll do is identify
        # what's the most recent document, and manipulate the other document
        # version numbers to be negative. This keeps the duplicates linked
        # together.

        # We'll start off by first finding all the duplicate documents.
        # Ideally we'd do this in one pass, but Django's aggregates don't seem
        # to support doing a GROUP BY without grouping all the selected fields
        # together. So we'll do this in a few phases. First we'll just find the
        # duplicates.
        #
        # Note we reset the `order_by` to make sure that if a default ordering
        # is ever added, it's never included in the group by.
        duplicated_records = Document2.objects \
            .values('uuid', 'version', 'is_history') \
            .annotate(id_count=models.Count('id')) \
            .filter(id_count__gt=1) \
            .order_by()

        for record in duplicated_records:
            # We found some duplicates, now actually fetch the duplicated
            # documents for these values.
            docs = Document2.objects \
                .filter(
                    uuid=record['uuid'],
                    version=record['version'],
                    is_history=record['is_history'],
                ) \
                .order_by('-version', '-last_modified')

            # Grab all but the first document, which we're preserving as the
            # current version.
            docs = list(docs[1:])

            logging.warn('Modifying version number of these duplicated docs %s' %
                [doc.id for doc in docs])

            # Update all these document's version numbers. To be safe, we want
            # to give them a unique negative number so there's no collision and
            # also so they're easily discoverable.
            version = Document2.objects \
                .values_list('version') \
                .filter(uuid=record['uuid']) \
                .earliest('version')[0]

            version = min(0, version) - 1

            # Finally, update the version numbers.
            for doc in docs:
              doc.version = version

              if not db.dry_run:
                doc.save()

              version -= 1

        # Adding unique constraint on 'Document2', fields ['uuid', 'version', 'is_history']
        db.create_unique(u'desktop_document2', ['uuid', 'version', 'is_history'])


    def backwards(self, orm):
        # Removing unique constraint on 'Document2', fields ['uuid', 'version', 'is_history']
        db.delete_unique(u'desktop_document2', ['uuid', 'version', 'is_history'])


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
        u'desktop.document': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'Document'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc_owner'", 'to': u"orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['desktop.DocumentTag']", 'db_index': 'True', 'symmetrical': 'False'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'})
        },
        u'desktop.document2': {
            'Meta': {'unique_together': "(('uuid', 'version', 'is_history'),)", 'object_name': 'Document2'},
            'data': ('django.db.models.fields.TextField', [], {'default': "'{}'"}),
            'dependencies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'dependencies_rel_+'", 'db_index': 'True', 'to': u"orm['desktop.Document2']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'extra': ('django.db.models.fields.TextField', [], {'default': "''"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_history': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'doc2_owner'", 'to': u"orm['auth.User']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tags_rel_+'", 'db_index': 'True', 'to': u"orm['desktop.Document2']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'db_index': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'default': "'c5b98d36-a9da-42ff-8cc9-c5d956899d05'", 'max_length': '36', 'db_index': 'True'}),
            'version': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'desktop.documentpermission': {
            'Meta': {'unique_together': "(('doc', 'perms'),)", 'object_name': 'DocumentPermission'},
            'doc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['desktop.Document']"}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': u"orm['auth.Group']", 'db_table': "'documentpermission_groups'", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'perms': ('django.db.models.fields.CharField', [], {'default': "'read'", 'max_length': '10'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'db_index': 'True', 'to': u"orm['auth.User']", 'db_table': "'documentpermission_users'", 'symmetrical': 'False'})
        },
        u'desktop.documenttag': {
            'Meta': {'unique_together': "(('owner', 'tag'),)", 'object_name': 'DocumentTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'tag': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'desktop.settings': {
            'Meta': {'object_name': 'Settings'},
            'collect_usage': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tours_and_tutorials': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        u'desktop.userpreferences': {
            'Meta': {'object_name': 'UserPreferences'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'value': ('django.db.models.fields.TextField', [], {'max_length': '4096'})
        }
    }

    complete_apps = ['desktop']
