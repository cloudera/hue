# encoding: utf-8
import datetime
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from south.db import db
from south.v2 import DataMigration
from django.db import models
from oozie.importlib.jobdesigner import convert_jobsub_design
from oozie.models import Workflow, Kill, Start, End


class Migration(DataMigration):
    depends_on = (
        # Need to ensure oozie is completely sync'd before jobsub.
        # This migration relies on the existence of the complete oozie model in the DB.
        # If a new oozie schema migration is added, then this will need to be updated as well.
        ("oozie", "0023_auto__add_field_node_data__add_field_job_data"),
    )

    def forwards(self, orm):
        """ Find every design and move them into Oozie. """
        for design in orm.OozieDesign.objects.all():
            action = convert_jobsub_design(design)

            if not action:
                raise RuntimeError(_("Cannot convert %s design into an Oozie action.") % design.name)

            # User is guaranteed to exist since this executes for upgrades only.
            workflow = Workflow.objects.new_workflow(User.objects.get(id=design.owner.pk))
            workflow.name = action.name
            workflow.description = design.description
            # Inform oozie to not manage this workflow.
            workflow.managed = False
            workflow.save()

            workflow.start.workflow = workflow
            workflow.start.save()
            workflow.start = Start.objects.get(id=workflow.start.id)

            workflow.end.workflow = workflow
            workflow.end.save()
            workflow.end = End.objects.get(id=workflow.end.id)

            Kill.objects.create(name='kill', workflow=workflow, node_type=Kill.node_type)

            action.workflow = workflow
            action.save()

            workflow.start.add_node(action)
            action.add_node(workflow.end)

            workflow.save()


    def backwards(self, orm):
        """ Cannot migrate backwards once migrated forwards. """
        raise RuntimeError(_("Cannot backwards migrate this change."))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
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
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
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
            'design': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieDesign']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'submission_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'jobsub.oozieaction': {
            'Meta': {'object_name': 'OozieAction'},
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'jobsub.ooziedesign': {
            'Meta': {'object_name': 'OozieDesign'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'root_action': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['jobsub.OozieAction']"})
        },
        'jobsub.ooziejavaaction': {
            'Meta': {'object_name': 'OozieJavaAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'args': ('django.db.models.fields.CharField', [], {'max_length': '4096', 'blank': 'True'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'java_opts': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'main_class': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziemapreduceaction': {
            'Meta': {'object_name': 'OozieMapreduceAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'jar_path': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'})
        },
        'jobsub.ooziestreamingaction': {
            'Meta': {'object_name': 'OozieStreamingAction', '_ormbases': ['jobsub.OozieAction']},
            'archives': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'files': ('django.db.models.fields.CharField', [], {'default': "'[]'", 'max_length': '512'}),
            'job_properties': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'mapper': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'oozieaction_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['jobsub.OozieAction']", 'unique': 'True', 'primary_key': 'True'}),
            'reducer': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        }
    }

    complete_apps = ['jobsub']
