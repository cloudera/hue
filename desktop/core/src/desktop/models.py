#!/usr/bin/env python
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

import calendar
import json
import logging
import os
import urllib
import uuid

from collections import OrderedDict
from itertools import chain

from django.contrib.auth import models as auth_models
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse, NoReverseMatch
from django.db import connection, models, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from settings import HUE_DESKTOP_VERSION

from aws.conf import is_enabled as is_s3_enabled, has_s3_access
from azure.conf import is_adls_enabled, has_adls_access
from dashboard.conf import get_engines, HAS_REPORT_ENABLED
from hadoop.conf import has_hdfs_enabled
from kafka.conf import has_kafka
from notebook.conf import SHOW_NOTEBOOKS, get_ordered_interpreters

from desktop import appmanager
from desktop.conf import get_clusters, CLUSTER_ID, IS_MULTICLUSTER_ONLY, IS_EMBEDDED, IS_K8S_ONLY
from desktop.lib.i18n import force_unicode
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.paths import get_run_root, SAFE_CHARACTERS_URI_COMPONENTS
from desktop.redaction import global_redaction_engine
from desktop.settings import DOCUMENT2_SEARCH_MAX_LENGTH
from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)

SAMPLE_USER_ID = 1100713
SAMPLE_USER_INSTALL = 'hue'
SAMPLE_USER_OWNERS = ['hue', 'sample']

UTC_TIME_FORMAT = "%Y-%m-%dT%H:%MZ"
HUE_VERSION = None


def uuid_default():
  return str(uuid.uuid4())

def hue_version():
  global HUE_VERSION

  if HUE_VERSION is None:
    HUE_VERSION = HUE_DESKTOP_VERSION

    p = get_run_root('cloudera', 'cdh_version.properties')
    if os.path.exists(p):
      build_version = _version_from_properties(open(p))
      if build_version:
        HUE_VERSION = '%s - %s' % (HUE_VERSION, build_version)

  return HUE_VERSION

def _version_from_properties(f):
  return dict(line.strip().split('=') for line in f.readlines() if len(line.strip().split('=')) == 2).get('cloudera.cdh.release')


###################################################################################################
# Custom Settings
###################################################################################################

PREFERENCE_IS_WELCOME_TOUR_SEEN = 'is_welcome_tour_seen'

class HueUser(auth_models.User):
  class Meta:
    proxy = True

  def __init__(self, *args, **kwargs):
    self._meta.get_field(
      'username'
    ).validators[0] = UnicodeUsernameValidator()
    super(auth_models.User, self).__init__(*args, **kwargs)


class UserPreferences(models.Model):
  """Holds arbitrary key/value strings."""
  user = models.ForeignKey(auth_models.User)
  key = models.CharField(max_length=20)
  value = models.TextField(max_length=4096)




class Settings(models.Model):
  collect_usage = models.BooleanField(db_index=True, default=True)
  tours_and_tutorials = models.BooleanField(db_index=True, default=True)

  @classmethod
  def get_settings(cls):
    settings, created = Settings.objects.get_or_create(id=1)
    return settings


class DefaultConfigurationManager(models.Manager):

  def get_configuration_for_user(self, app, user):
    """
    :param app: app name
    :param user: User object
    :return: DefaultConfiguration for user, or first group found, or default for app, or None
    """
    try:
      return super(DefaultConfigurationManager, self).get(app=app, user=user)
    except DefaultConfiguration.DoesNotExist:
      pass

    configs = super(DefaultConfigurationManager, self).get_queryset().filter(app=app, groups__in=user.groups.all())
    if configs.count() > 0:
      return configs[0]

    try:
      return super(DefaultConfigurationManager, self).get(app=app, is_default=True)
    except DefaultConfiguration.DoesNotExist:
      pass

    return None


class DefaultConfiguration(models.Model):
  """
  Default values for configuration properties for a given app/editor
  Can be designated as default for all users by is_default flag, or for a specific group or user
  """
  app = models.CharField(max_length=32, null=False, db_index=True, help_text=_t('App that this configuration belongs to.'))
  properties = models.TextField(default='[]', help_text=_t('JSON-formatted default properties values.'))

  is_default = models.BooleanField(default=False, db_index=True)
  groups = models.ManyToManyField(auth_models.Group, db_index=True, db_table='defaultconfiguration_groups')
  user = models.ForeignKey(auth_models.User, blank=True, null=True, db_index=True)

  objects = DefaultConfigurationManager()

  class Meta:
    ordering = ["app", "-is_default", "user"]


  @property
  def properties_list(self):
    """
    :return: Deserialized properties as a list of property objects
    """
    if not self.properties:
      self.properties = json.dumps([])
    return json.loads(self.properties)

  @property
  def properties_dict(self):
    """
    :return: Deserialized properties as a dict of key: value pairs
    """
    if not self.properties:
      self.properties = json.dumps([])
    return dict((prop['key'], prop['value']) for prop in json.loads(self.properties))

  def to_dict(self):
    return {
      'id': self.id,
      'app': self.app,
      'properties': self.properties_list,
      'is_default': self.is_default,
      'group_ids': [group.id for group in self.groups.all()],
      'user': self.user.username if self.user else None
    }


###################################################################################################
# Document1
###################################################################################################
class DocumentTagManager(models.Manager):

  def get_tags(self, user):
    return self.filter(owner=user).distinct()

  def create_tag(self, owner, tag_name):
    if tag_name in DocumentTag.RESERVED:
      raise Exception(_("Can't add %s: it is a reserved tag.") % tag_name)
    else:
      tag, created = DocumentTag.objects.get_or_create(tag=tag_name, owner=owner)
      return tag

  def _get_tag(self, user, name):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=name)
    return tag

  def get_default_tag(self, user):
    return self._get_tag(user, DocumentTag.DEFAULT)

  def get_trash_tag(self, user):
    return self._get_tag(user, DocumentTag.TRASH)

  def get_history_tag(self, user):
    return self._get_tag(user, DocumentTag.HISTORY)

  def get_example_tag(self, user):
    return self._get_tag(user, DocumentTag.EXAMPLE)

  def get_imported2_tag(self, user):
    return self._get_tag(user, DocumentTag.IMPORTED2)

  def tag(self, owner, doc_id, tag_name='', tag_id=None):
    try:
      tag = DocumentTag.objects.get(id=tag_id, owner=owner)
      if tag.tag in DocumentTag.RESERVED:
        raise Exception(_("Can't add %s: it is a reserved tag.") % tag)
    except DocumentTag.DoesNotExist:
      tag = self._get_tag(user=owner, name=tag_name)

    doc = Document.objects.get_doc_for_writing(doc_id, owner)
    doc.add_tag(tag)

    return tag

  def untag(self, tag_id, owner, doc_id):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)

    if tag.tag in DocumentTag.RESERVED:
      raise Exception(_("Can't remove %s: it is a reserved tag.") % tag)

    doc = Document.objects.get_doc_for_writing(doc_id, owner=owner)
    doc.remove_tag(tag)

  def delete_tag(self, tag_id, owner):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)
    default_tag = DocumentTag.objects.get_default_tag(owner)

    if tag.tag in DocumentTag.RESERVED:
      raise Exception(_("Can't remove %s: it is a reserved tag.") % tag)
    else:
      tag.delete()

    for doc in Document.objects.get_docs(owner).filter(tags=None):
      doc.add_tag(default_tag)

  def update_tags(self, owner, doc_id, tag_ids):
    doc = Document.objects.get_doc_for_writing(doc_id, owner)

    for tag in doc.tags.all():
      if tag.tag not in DocumentTag.RESERVED:
        doc.remove_tag(tag)

    for tag_id in tag_ids:
      tag = DocumentTag.objects.get(id=tag_id, owner=owner)
      if tag.tag not in DocumentTag.RESERVED:
        doc.add_tag(tag)

    return doc


class DocumentTag(models.Model):
  """
  Reserved tags can't be manually removed by the user.
  """
  owner = models.ForeignKey(auth_models.User, db_index=True)
  tag = models.SlugField()

  DEFAULT = 'default' # Always there
  TRASH = 'trash' # There when the document is trashed
  HISTORY = 'history' # There when the document is a submission history
  EXAMPLE = 'example' # Hue examples
  IMPORTED2 = 'imported2' # Was imported to document2

  RESERVED = (DEFAULT, TRASH, HISTORY, EXAMPLE, IMPORTED2)

  objects = DocumentTagManager()

  class Meta:
    unique_together = ('owner', 'tag')


  def __unicode__(self):
    return force_unicode('%s') % (self.tag,)


class DocumentManager(models.Manager):

  def documents(self, user):
    return Document.objects.filter(
        Q(owner=user) |
        Q(documentpermission__users=user) |
        Q(documentpermission__groups__in=user.groups.all())
    ).defer('description', 'extra').distinct()

  def get_docs(self, user, model_class=None, extra=None, qfilter=None):
    docs = Document.objects.documents(user).exclude(name='pig-app-hue-script')

    if model_class is not None:
      ct = ContentType.objects.get_for_model(model_class)
      docs = docs.filter(content_type=ct)

    if extra is not None:
      docs = docs.filter(extra=extra)

    if qfilter is not None:
      docs = docs.filter(qfilter)

    return docs

  def get_doc_for_writing(self, doc_id, user):
    """Fetch a document and confirm that this user can write to it."""
    doc = Document.objects.documents(user).get(id=doc_id)
    doc.can_write_or_exception(user)
    return doc

  def trashed_docs(self, model_class, user):
    tag = DocumentTag.objects.get_trash_tag(user=user)

    return Document.objects.get_docs(user, model_class).filter(tags__in=[tag]).order_by('-last_modified')

  def trashed(self, model_class, user):
    docs = self.trashed_docs(model_class, user)

    return [job.content_object for job in docs if job.content_object]

  def available_docs(self, model_class, user, with_history=False):
    exclude = [DocumentTag.objects.get_trash_tag(user=user)]
    if not with_history:
      exclude.append(DocumentTag.objects.get_history_tag(user=user))

    return Document.objects.get_docs(user, model_class).exclude(tags__in=exclude).order_by('-last_modified')

  def history_docs(self, model_class, user):
    include = [DocumentTag.objects.get_history_tag(user=user)]
    exclude = [DocumentTag.objects.get_trash_tag(user=user)]

    return Document.objects.get_docs(user, model_class).filter(tags__in=include).exclude(tags__in=exclude).order_by('-last_modified')

  def available(self, model_class, user, with_history=False):
    docs = self.available_docs(model_class, user, with_history)

    return [doc.content_object for doc in docs if doc.content_object]

  def can_read_or_exception(self, user, doc_class, doc_id, exception_class=PopupException):
    if doc_id is None:
      return
    try:
      ct = ContentType.objects.get_for_model(doc_class)
      doc = Document.objects.get(object_id=doc_id, content_type=ct)
      if doc.can_read(user):
        return doc
      else:
        message = _("Permission denied. %(username)s does not have the permissions required to access document %(id)s") % \
            {'username': user.username, 'id': doc.id}
        raise exception_class(message)

    except Document.DoesNotExist:
      raise exception_class(_('Document %(id)s does not exist') % {'id': doc_id})

  def can_read(self, user, doc_class, doc_id):
    ct = ContentType.objects.get_for_model(doc_class)
    doc = Document.objects.get(object_id=doc_id, content_type=ct)

    return doc.can_read(user)

  def link(self, content_object, owner, name='', description='', extra=''):
    if not content_object.doc.exists():
      doc = Document.objects.create(
                content_object=content_object,
                owner=owner,
                name=name,
                description=description,
                extra=extra
            )

      tag = DocumentTag.objects.get_default_tag(user=owner)
      doc.tags.add(tag)
      return doc
    else:
      LOG.warn('Object %s already has documents: %s' % (content_object, content_object.doc.all()))
      return content_object.doc.all()[0]

  def sync(self, doc2_only=True):

    def find_jobs_with_no_doc(model):
      jobs = model.objects.filter(doc__isnull=True)
      if model == Document2:
        jobs = jobs.exclude(is_history=True)
      return jobs.select_related('owner')

    def find_oozie_jobs_with_no_doc(model):
      return model.objects.filter(doc__isnull=True).exclude(name__exact='').select_related('owner')

    table_names = connection.introspection.table_names()

    try:
      from oozie.models import Workflow, Coordinator, Bundle

      if \
          Workflow._meta.db_table in table_names or \
          Coordinator._meta.db_table in table_names or \
          Bundle._meta.db_table in table_names:
        with transaction.atomic():
          for job in chain(
              find_oozie_jobs_with_no_doc(Workflow),
              find_oozie_jobs_with_no_doc(Coordinator),
              find_oozie_jobs_with_no_doc(Bundle)):
            doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.description)

            if job.is_trashed:
              doc.send_to_trash()

            if job.is_shared:
              doc.share_to_default()

            if hasattr(job, 'managed'):
              if not job.managed:
                doc.extra = 'jobsub'
                doc.save()
    except Exception, e:
      LOG.exception('error syncing oozie')

    try:
      from beeswax.models import SavedQuery

      if SavedQuery._meta.db_table in table_names:
        with transaction.atomic():
          for job in find_jobs_with_no_doc(SavedQuery):
            doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.desc, extra=job.type)
            if job.is_trashed:
              doc.send_to_trash()
    except Exception, e:
      LOG.exception('error syncing beeswax')

    try:
      from pig.models import PigScript

      if PigScript._meta.db_table in table_names:
        with transaction.atomic():
          for job in find_jobs_with_no_doc(PigScript):
            Document.objects.link(job, owner=job.owner, name=job.dict['name'], description='')
    except Exception, e:
      LOG.exception('error syncing pig')

    try:
      from search.models import Collection

      if Collection._meta.db_table in table_names:
        with transaction.atomic():
          for dashboard in Collection.objects.all():
            if 'collection' in dashboard.properties_dict:
              col_dict = dashboard.properties_dict['collection']
              if not 'uuid' in col_dict:
                _uuid = str(uuid.uuid4())
                col_dict['uuid'] = _uuid
                dashboard.update_properties({'collection': col_dict})
                if dashboard.owner is None:
                  from useradmin.models import install_sample_user
                  owner = install_sample_user()
                else:
                  owner = dashboard.owner
                dashboard_doc = Document2.objects.create(name=dashboard.label, uuid=_uuid, type='search-dashboard', owner=owner, description=dashboard.label, data=dashboard.properties)
                Document.objects.link(dashboard_doc, owner=owner, name=dashboard.label, description=dashboard.label, extra='search-dashboard')
                dashboard.save()
    except Exception, e:
      LOG.exception('error syncing search')

    try:
      if Document2._meta.db_table in table_names:
        with transaction.atomic():
          for job in find_jobs_with_no_doc(Document2):
            if job.type == 'oozie-workflow2':
              extra = 'workflow2'
            elif job.type == 'oozie-coordinator2':
              extra = 'coordinator2'
            elif job.type == 'oozie-bundle2':
              extra = 'bundle2'
            elif job.type == 'notebook':
              extra = 'notebook'
            elif job.type == 'search-dashboard':
              extra = 'search-dashboard'
            else:
              extra = ''
            doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.description, extra=extra)
    except Exception, e:
      LOG.exception('error syncing Document2')


    if not doc2_only and Document._meta.db_table in table_names:
      # Make sure doc have at least a tag
      try:
        for doc in Document.objects.filter(tags=None):
          default_tag = DocumentTag.objects.get_default_tag(doc.owner)
          doc.tags.add(default_tag)
      except Exception, e:
        LOG.exception('error adding at least one tag to docs')

      # Make sure all the sample user documents are shared.
      try:
        with transaction.atomic():
          for doc in Document.objects.filter(owner__username__in=SAMPLE_USER_OWNERS):
            doc.share_to_default()

            tag = DocumentTag.objects.get_example_tag(user=doc.owner)
            doc.tags.add(tag)
            doc_last_modified = doc.last_modified

            doc.save()
            Document.objects.filter(id=doc.id).update(last_modified=doc_last_modified)
      except Exception, e:
        LOG.exception('error sharing sample user documents')

      # For now remove the default tag from the examples
      try:
        for doc in Document.objects.filter(tags__tag=DocumentTag.EXAMPLE):
          default_tag = DocumentTag.objects.get_default_tag(doc.owner)
          doc.tags.remove(default_tag)
      except Exception, e:
        LOG.exception('error removing default tags')

      # ------------------------------------------------------------------------

      LOG.info('Looking for documents that have no object')

      # Delete documents with no object.
      try:
        with transaction.atomic():
          # First, delete all the documents that don't have a content type
          docs = Document.objects.filter(content_type=None)

          if docs:
            LOG.info('Deleting %s doc(s) that do not have a content type' % docs.count())
            docs.delete()

          # Next, it's possible that there are documents pointing at a non-existing
          # content_type. We need to do a left join to find these records, but we
          # can't do this directly in django. To get around writing wrap sql (which
          # might not be portable), we'll use an aggregate to count up all the
          # associated content_types, and delete the documents that have a count of
          # zero.
          #
          # Note we're counting `content_type__name` to force the join.
          docs = Document.objects \
              .values('id') \
              .annotate(content_type_count=models.Count('content_type__name')) \
              .filter(content_type_count=0)

          if docs:
            LOG.info('Deleting %s doc(s) that have invalid content types' % docs.count())
            docs.delete()

          # Finally we need to delete documents with no associated content object.
          # This is tricky because of our use of generic foreign keys. So to do
          # this a bit more efficiently, we'll start with a query of all the
          # documents, then step through each content type and and filter out all
          # the documents it's referencing from our document query. Messy, but it
          # works.

          # TODO: This can be several 100k entries for large databases.
          # Need to figure out a better way to handle this scenario.
          docs = Document.objects.all()

          for content_type in ContentType.objects.all():
            model_class = content_type.model_class()

            # Ignore any types that don't have a model.
            if model_class is None:
              continue

            # Ignore types that don't have a table yet.
            if model_class._meta.db_table not in table_names:
              continue

            # Ignore classes that don't have a 'doc'.
            if not hasattr(model_class, 'doc'):
              continue

            # First create a query that grabs all the document ids for this type.
            docs_from_content = model_class.objects.values('doc__id')

            # Next, filter these from our document query.
            docs = docs.exclude(id__in=docs_from_content)

          if docs.exists():
            LOG.info('Deleting %s documents' % docs.count())
            docs.delete()
      except Exception, e:
        LOG.exception('Error in sync while attempting to delete documents with no object: %s' % e)


class Document(models.Model):

  owner = models.ForeignKey(auth_models.User, db_index=True, verbose_name=_t('Owner'), help_text=_t('User who can own the job.'), related_name='doc_owner')
  name = models.CharField(default='', max_length=255)
  description = models.TextField(default='')

  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Last modified'))
  version = models.SmallIntegerField(default=1, verbose_name=_t('Schema version'))
  extra = models.TextField(default='')

  tags = models.ManyToManyField(DocumentTag, db_index=True)

  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  content_object = GenericForeignKey('content_type', 'object_id')

  objects = DocumentManager()

  class Meta:
    unique_together = ('content_type', 'object_id')

  def __unicode__(self):
    return force_unicode('%s %s %s') % (self.content_type, self.name, self.owner)

  def is_editable(self, user):
    """Deprecated by can_read"""
    return self.can_write(user)

  def can_edit_or_exception(self, user, exception_class=PopupException):
    """Deprecated by can_write_or_exception"""
    return self.can_write_or_exception(user, exception_class)

  def add_tag(self, tag):
    self.tags.add(tag)

  def remove_tag(self, tag):
    self.tags.remove(tag)

  def is_trashed(self):
    return DocumentTag.objects.get_trash_tag(user=self.owner) in self.tags.all()

  def is_historic(self):
    return DocumentTag.objects.get_history_tag(user=self.owner) in self.tags.all()

  def send_to_trash(self):
    tag = DocumentTag.objects.get_trash_tag(user=self.owner)
    self.tags.add(tag)

  def restore_from_trash(self):
    tag = DocumentTag.objects.get_trash_tag(user=self.owner)
    self.tags.remove(tag)

  def add_to_history(self):
    tag = DocumentTag.objects.get_history_tag(user=self.owner)
    self.tags.add(tag)

  def remove_from_history(self):
    tag = DocumentTag.objects.get_history_tag(user=self.owner)
    self.tags.remove(tag)

  def share_to_default(self, name='read'):
    DocumentPermission.objects.share_to_default(self, name=name)

  def can_read(self, user):
    return is_admin(user) or self.owner == user or Document.objects.get_docs(user).filter(id=self.id).exists()

  def can_write(self, user):
    perm = self.list_permissions('write')
    return is_admin(user) or self.owner == user or perm.groups.filter(id__in=user.groups.all()).exists() or user in perm.users.all()

  def can_read_or_exception(self, user, exception_class=PopupException):
    if self.can_read(user):
      return True
    else:
      raise exception_class(_("Document does not exist or you don't have the permission to access it."))

  def can_write_or_exception(self, user, exception_class=PopupException):
    if self.can_write(user):
      return True
    else:
      raise exception_class(_("Document does not exist or you don't have the permission to access it."))

  def copy(self, content_object, name, owner, description=None):
    if content_object:
      copy_doc = self

      copy_doc.pk = None
      copy_doc.id = None
      copy_doc.name = name
      copy_doc.owner = owner
      if description:
        copy_doc.description = description

      copy_doc = Document.objects.link(content_object,
                                       owner=copy_doc.owner,
                                       name=copy_doc.name,
                                       description=copy_doc.description,
                                       extra=copy_doc.extra)

      # Update reverse Document relation to new copy
      if content_object.doc.get():
        content_object.doc.get().delete()
      content_object.doc.add(copy_doc)

      return copy_doc
    else:
      raise PopupException(_("Document copy method requires a content_object argument."))

  @property
  def icon(self):
    apps = appmanager.get_apps_dict()

    try:
      if self.extra == 'workflow2':
        return staticfiles_storage.url('oozie/art/icon_oozie_workflow_48.png')
      elif self.extra == 'coordinator2':
        return staticfiles_storage.url('oozie/art/icon_oozie_coordinator_48.png')
      elif self.extra == 'bundle2':
        return staticfiles_storage.url('oozie/art/icon_oozie_bundle_48.png')
      elif self.extra == 'notebook':
        return staticfiles_storage.url('notebook/art/icon_notebook_48.png')
      elif self.extra.startswith('query'):
        if self.extra == 'query-impala':
          return staticfiles_storage.url(apps['impala'].icon_path)
        else:
          return staticfiles_storage.url(apps['beeswax'].icon_path)
      elif self.extra.startswith('search'):
        return staticfiles_storage.url('search/art/icon_search_48.png')
      elif self.content_type.app_label == 'beeswax':
        if self.extra == '0':
          return staticfiles_storage.url(apps['beeswax'].icon_path)
        elif self.extra == '3':
          return staticfiles_storage.url(apps['spark'].icon_path)
        else:
          return staticfiles_storage.url(apps['impala'].icon_path)
      elif self.content_type.app_label == 'oozie':
        if self.extra == 'jobsub':
          return staticfiles_storage.url(apps['jobsub'].icon_path)
        else:
          return staticfiles_storage.url(self.content_type.model_class().ICON)
      elif self.content_type.app_label in apps:
        return staticfiles_storage.url(apps[self.content_type.app_label].icon_path)
      else:
        return staticfiles_storage.url('desktop/art/icon_hue_48.png')
    except Exception, e:
      LOG.warn(force_unicode(e))
      return staticfiles_storage.url('desktop/art/icon_hue_48.png')

  def share(self, users, groups, name='read'):
    DocumentPermission.objects.filter(document=self, name=name).update(users=users, groups=groups, add=True)

  def unshare(self, users, groups, name='read'):
    DocumentPermission.objects.filter(document=self, name=name).update(users=users, groups=groups, add=False)

  def sync_permissions(self, perms_dict):
    """
    Set who else or which other group can interact with the document.

    Example of input: {'read': {'user_ids': [1, 2, 3], 'group_ids': [1, 2, 3]}}
    """
    for name, perm in perms_dict.iteritems():
      users = groups = None
      if perm.get('user_ids'):
        users = auth_models.User.objects.in_bulk(perm.get('user_ids'))
      else:
        users = []

      if perm.get('group_ids'):
        groups = auth_models.Group.objects.in_bulk(perm.get('group_ids'))
      else:
        groups = []

      DocumentPermission.objects.sync(document=self, name=name, users=users, groups=groups)

  def list_permissions(self, perm='read'):
    return DocumentPermission.objects.list(document=self, perm=perm)

  def to_dict(self):
    return {
      'owner': self.owner.username,
      'name': self.name,
      'description': self.description,
      'uuid': None, # no uuid == v1
      'id': self.id,
      'doc1_id': self.id,
      'object_id': self.object_id,
      'type': str(self.content_type),
      'last_modified': self.last_modified.strftime(UTC_TIME_FORMAT),
      'last_modified_ts': calendar.timegm(self.last_modified.utctimetuple()),
      'isSelected': False
    }


class DocumentPermissionManager(models.Manager):

  def _check_perm(self, name):
    perms = (DocumentPermission.READ_PERM, DocumentPermission.WRITE_PERM)
    if name not in perms:
      perms_string = ' and '.join(', '.join(perms).rsplit(', ', 1))
      raise PopupException(_('Only %s permissions are supported, not %s.') % (perms_string, name))


  def share_to_default(self, document, name='read'):
    from useradmin.models import get_default_user_group # Remove build dependency

    self._check_perm(name)

    if name == DocumentPermission.WRITE_PERM:
      perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=DocumentPermission.WRITE_PERM)
    else:
      perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=DocumentPermission.READ_PERM)
    default_group = get_default_user_group()

    if default_group:
      perm.groups.add(default_group)

  def update(self, document, name='read', users=None, groups=None, add=True):
    self._check_perm(name)

    perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=name)

    if users is not None:
      if add:
        perm.users.add(*users)
      else:
        perm.users.remove(*users)

    if groups is not None:
      if add:
        perm.groups.add(*groups)
      else:
        perm.groups.remove(*groups)

    if not perm.users and not perm.groups:
      perm.delete()

  def sync(self, document, name='read', users=None, groups=None):
    self._check_perm(name)

    perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=name)

    if users is not None:
      perm.users = []
      perm.users = users
      perm.save()

    if groups is not None:
      perm.groups = []
      perm.groups = groups
      perm.save()

    if not users and not groups:
      perm.delete()

  def list(self, document, perm='read'):
    perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=perm)
    return perm


class DocumentPermission(models.Model):
  READ_PERM = 'read'
  WRITE_PERM = 'write'

  doc = models.ForeignKey(Document)

  users = models.ManyToManyField(auth_models.User, db_index=True, db_table='documentpermission_users')
  groups = models.ManyToManyField(auth_models.Group, db_index=True, db_table='documentpermission_groups')
  perms = models.CharField(default=READ_PERM, max_length=10, choices=( # one perm
    (READ_PERM, 'read'),
    (WRITE_PERM, 'write'),
  ))

  objects = DocumentPermissionManager()

  class Meta:
    unique_together = ('doc', 'perms')


###################################################################################################
# Document2
###################################################################################################
class FilesystemException(Exception):
  pass


class Document2QueryMixin(object):

  def documents(self, user, perms='both', include_history=False, include_trashed=False, include_managed=False):
    """
    Returns all documents that are owned or shared with the user.
    :param perms: both, shared, owned. Defaults to both.
    :param include_history: boolean flag to return history documents. Defaults to False.
    :param include_trashed: boolean flag to return trashed documents. Defaults to True.
    """
    if perms == 'both':
      docs = self.filter(
        Q(owner=user) |
        Q(document2permission__users=user) |
        Q(document2permission__groups__in=user.groups.all())
      )
    elif perms == 'shared':
      docs = self.filter(
        Q(document2permission__users=user) |
        Q(document2permission__groups__in=user.groups.all())
      )
    else:  # only return documents owned by the user
      docs = self.filter(owner=user)

    if not include_history:
      docs = docs.exclude(is_history=True)

    if not include_managed:
      docs = docs.exclude(is_managed=True)

    if not include_trashed:
      docs = docs.exclude(is_trashed=True)

    return docs.defer('description', 'data', 'extra', 'search').distinct().order_by('-last_modified')


  def search_documents(self, types=None, search_text=None, order_by=None):
    """
    Search for documents based on type filters, search_text or order_by and return a queryset of document objects
    :param types: list of Document2 types (e.g. - query-hive, directory, etc)
    :param search_text: text to search on in the name and description fields
    :param order_by: order by field (e.g. -last_modified, type)
    """
    documents = self

    if types and isinstance(types, list) and types[0] != 'all':
      documents = documents.filter(type__in=types)

    if search_text:
      documents = documents.filter(Q(name__icontains=search_text) | Q(description__icontains=search_text) | Q(search__icontains=search_text))

    if order_by:  # TODO: Validate that order_by is a valid sort parameter
      documents = documents.order_by(order_by)

    return documents


class Document2QuerySet(QuerySet, Document2QueryMixin):
    pass


class Document2Manager(models.Manager, Document2QueryMixin):

  def get_queryset(self):
    return Document2QuerySet(self.model, using=self._db)

  # TODO prevent get() in favor of this
  def document(self, user, doc_id):
    return self.documents(user, include_trashed=True, include_history=True).get(id=doc_id)

  def get_by_natural_key(self, uuid, version, is_history):
    return self.get(uuid=uuid, version=version, is_history=is_history)

  def get_by_uuid(self, user, uuid, perm_type='read'):
    """
    Since UUID is not a unique field, but part of a composite unique key, this returns the latest version by UUID
    This should always be used in place of Document2.objects.get(uuid=) when a single document is expected

    :param user: User to check permissions against
    :param uuid
    :param perm_type: permission type to check against
    """
    docs = self.filter(uuid=uuid).order_by('-last_modified')

    if not docs.exists():
      raise FilesystemException(_('Document with UUID %s not found.') % uuid)

    latest_doc = docs[0]

    if perm_type == 'write':
      latest_doc.can_write_or_exception(user)
    else:
      latest_doc.can_read_or_exception(user)

    return latest_doc

  def get_history(self, user, doc_type, include_trashed=False):
    return self.documents(user, perms='owned', include_history=True, include_trashed=include_trashed).filter(type=doc_type, is_history=True)

  def get_tasks_history(self, user):
    return self.documents(user, perms='owned', include_history=True, include_trashed=False, include_managed=True).filter(is_history=True, is_managed=True).exclude(name='pig-app-hue-script').exclude(type='oozie-workflow2')

  def get_home_directory(self, user):
    try:
      return self.get(owner=user, parent_directory=None, name=Document2.HOME_DIR, type='directory')
    except Document2.DoesNotExist:
      return self.create_user_directories(user)
    except Document2.MultipleObjectsReturned:
      LOG.error('Multiple Home directories detected. Merging all into one.')

      home_dirs = list(self.filter(owner=user, parent_directory=None, name=Document2.HOME_DIR, type='directory').order_by('-last_modified'))
      parent_home_dir = home_dirs.pop()
      for dir in home_dirs:
        dir.children.exclude(name='.Trash').update(parent_directory=parent_home_dir)
        dir.delete()

      return parent_home_dir

  def get_by_path(self, user, path):
    """
    This can be an expensive operation b/c we have to traverse the path tree, so if possible, request a document by UUID
    NOTE: get_by_path only works for the owner's documents since it is based off the user's home directory
    """
    cleaned_path = path.rstrip('/')
    doc = Document2.objects.get_home_directory(user)
    if cleaned_path:
      path_tokens = cleaned_path.split('/')[1:]
      for token in path_tokens:
        try:
          doc = doc.children.get(name=token)
        except Document2.DoesNotExist:
          raise FilesystemException(_('Requested invalid path for user %s: %s') % (user.username, path))
        except Document2.MultipleObjectsReturned:
          raise FilesystemException(_('Duplicate documents found for user %s at path: %s') % (user.username, path))

    doc.can_read_or_exception(user)

    return doc

  def create_user_directories(self, user):
    """
    Creates user home and Trash directories if they do not exist and move any orphan documents to home directory
    :param user: User object
    """
    # Edge-case if the user has a legacy home directory with path-name
    Directory.objects.filter(name='/', owner=user).update(name=Document2.HOME_DIR)

    # Get or create home and Trash directories for all users
    home_dir, created = Directory.objects.get_or_create(name=Document2.HOME_DIR, owner=user)

    if created:
      LOG.info('Successfully created home directory for user: %s' % user.username)

    trash_dir, created = Directory.objects.get_or_create(name=Document2.TRASH_DIR, owner=user, parent_directory=home_dir)

    if created:
      LOG.info('Successfully created trash directory for user: %s' % user.username)

    # For any directories or documents that do not have a parent directory, assign it to home directory
    count = 0
    for doc in Document2.objects.filter(owner=user).filter(parent_directory=None).exclude(id__in=[home_dir.id, trash_dir.id]):
      doc.parent_directory = home_dir
      doc.save()
      count += 1

    LOG.info("Moved %d documents to home directory for user: %s" % (count, user.username))
    return home_dir


class Document2(models.Model):

  HOME_DIR = ''
  TRASH_DIR = '.Trash'
  EXAMPLES_DIR = 'examples'

  owner = models.ForeignKey(auth_models.User, db_index=True, verbose_name=_t('Owner'), help_text=_t('Creator.'), related_name='doc2_owner')
  name = models.CharField(default='', max_length=255)
  description = models.TextField(default='')
  uuid = models.CharField(default=uuid_default, max_length=36, db_index=True)
  type = models.CharField(default='', max_length=32, db_index=True, help_text=_t('Type of document, e.g. Hive query, Oozie workflow, Search Dashboard...'))

  data = models.TextField(default='{}')
  extra = models.TextField(default='')
  search = models.TextField(blank=True, null=True, help_text=_t('Searchable text for the document.'))
  # settings = models.TextField(default='{}') # Owner settings like, can other reshare, can change access

  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))
  version = models.SmallIntegerField(default=1, verbose_name=_t('Document version'), db_index=True)
  is_history = models.BooleanField(default=False, db_index=True)
  is_managed = models.BooleanField(default=False, db_index=True, verbose_name=_t('If managed under the cover by Hue and never by the user')) # Aka isTask
  is_trashed = models.NullBooleanField(default=False, db_index=True, verbose_name=_t('True if trashed'))

  dependencies = models.ManyToManyField('self', symmetrical=False, related_name='dependents', db_index=True)

  parent_directory = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.CASCADE)

  doc = GenericRelation(Document, related_query_name='doc_doc') # Compatibility with Hue 3

  objects = Document2Manager()

  class Meta:
    unique_together = ('uuid', 'version', 'is_history')
    ordering = ["-last_modified", "name"]

  def __unicode__(self):
    res = '%s - %s - %s - %s' % (force_unicode(self.name), self.owner, self.type, self.uuid)
    return force_unicode(res)

  @property
  def data_dict(self):
    if not self.data:
      self.data = json.dumps({})
    data_python = json.loads(self.data)
    return data_python

  @property
  def path(self):
    quoted_name = urllib.quote(self.name.encode('utf-8'))
    if self.parent_directory:
      return '%s/%s' % (self.parent_directory.path, quoted_name)
    else:
      return quoted_name

  @property
  def dirname(self):
    return os.path.dirname(self.path) or '/'

  @property
  def is_directory(self):
    return self.type == 'directory'

  @property
  def is_home_directory(self):
    return self.is_directory and self.parent_directory == None and self.name == self.HOME_DIR

  @property
  def is_trash_directory(self):
    return self.is_directory and self.name == self.TRASH_DIR

  def natural_key(self):
    return (self.uuid, self.version, self.is_history)

  def copy(self, name, owner, description=None):
    copy_doc = self

    copy_doc.pk = None
    copy_doc.id = None
    copy_doc.uuid = uuid_default()
    copy_doc.name = name
    copy_doc.owner = owner
    if description:
      copy_doc.description = description
    copy_doc.save()
    return copy_doc

  def update_data(self, post_data):
    data_dict = self.data_dict
    data_dict.update(post_data)
    self.data = json.dumps(data_dict)

  def get_absolute_url(self):
    url = None
    try:
      if self.type == 'oozie-coordinator2':
        url = reverse('oozie:edit_coordinator') + '?coordinator=' + str(self.id)
      elif self.type == 'oozie-bundle2':
        url = reverse('oozie:edit_bundle') + '?bundle=' + str(self.id)
      elif self.type.startswith('query'):
        url = '/editor' + '?editor=' + str(self.id)
      elif self.type == 'directory':
        url = '/home2' + '?uuid=' + self.uuid
      elif self.type == 'notebook':
        url = reverse('notebook:notebook') + '?notebook=' + str(self.id)
      elif self.type == 'search-dashboard':
        url = reverse('search:index') + '?collection=' + str(self.id)
      elif self.type == 'link-pigscript':
        url = reverse('pig:index') + '#edit/%s' % self.data_dict.get('object_id', '')
      elif self.type == 'link-workflow':
        url = '/jobsub/#edit-design/%s' % self.data_dict.get('object_id', '')
      else:
        url = reverse('oozie:edit_workflow') + '?workflow=' + str(self.id)
    except NoReverseMatch:
      LOG.warn('Could not perform reverse lookup for type %s, app may be blacklisted.' % self.type)
    return url

  def to_dict(self):
    return {
      'owner': self.owner.username,
      'name': self.name,
      'path': self.path or '/',
      'description': self.description,
      'uuid': self.uuid,
      'id': self.id,
      'doc1_id': self.doc.get().id if self.doc.exists() else -1,
      'parent_uuid': self.parent_directory.uuid if self.parent_directory else None,
      'type': self.type,
      'perms': self._massage_permissions(),
      'last_modified': self.last_modified.strftime(UTC_TIME_FORMAT) if self.last_modified else None,
      'last_modified_ts': calendar.timegm(self.last_modified.utctimetuple()) if self.last_modified else None,
      'is_managed': self.is_managed,
      'isSelected': False,
      'absoluteUrl': self.get_absolute_url(),
    }

  def get_history(self):
    return self.dependencies.filter(is_history=True).order_by('-last_modified')

  def add_to_history(self, user, data_dict):
    doc_id = self.id # Need to copy as the clone messes it

    history_doc = self.copy(name=self.name, owner=user)
    history_doc.update_data({'history': data_dict})
    history_doc.is_history = True
    history_doc.last_modified = None
    history_doc.save()

    Document2.objects.get(id=doc_id).dependencies.add(history_doc)
    return history_doc

  def save(self, *args, **kwargs):
    # Set document parent to home directory if parent directory isn't specified
    if not self.parent_directory and not self.is_home_directory and not self.is_trash_directory:
      home_dir = Document2.objects.get_home_directory(self.owner)
      self.parent_directory = home_dir

    # Run validations
    self.validate()

    # Redact query if needed
    self._redact_query()

    if self.search:
      self.search = self.search[:DOCUMENT2_SEARCH_MAX_LENGTH]

    super(Document2, self).save(*args, **kwargs)

    # Inherit shared permissions from parent directory, must be done after save b/c new doc needs ID
    self.inherit_permissions()

  def validate(self):
    # Validate home and Trash directories are only created once per user and cannot be created or modified after
    if self.name in [Document2.HOME_DIR, Document2.TRASH_DIR] and self.type == 'directory' and \
          Document2.objects.filter(name=self.name, owner=self.owner, type='directory').exists():
      raise FilesystemException(_('Cannot create or modify directory with name: %s') % self.name)

    # Validate that parent directory does not create cycle
    if self._contains_cycle():
      raise FilesystemException(_('Cannot save document %s under parent directory %s due to circular dependency') %
                                (self.name, self.parent_directory.uuid))


  def inherit_permissions(self):
    if self.parent_directory is not None:
      parent_perms = Document2Permission.objects.filter(doc=self.parent_directory)
      for perm in parent_perms:
        self.share(self.owner, name=perm.perms, users=perm.users.all(), groups=perm.groups.all())


  def move(self, directory, user):
    if not directory.is_directory:
      raise FilesystemException(_('Target with UUID %s is not a directory') % directory.uuid)

    if directory.can_write_or_exception(user=user):
      # Restore last_modified date after save
      original_last_modified = self.last_modified
      self.parent_directory = directory
      self.save()
      # Use update instead of save() so that last_modified date is not modified automatically
      Document2.objects.filter(id=self.id).update(last_modified=original_last_modified)

    return self

  def trash(self):
    try:
      trash_dir = Directory.objects.get(name=self.TRASH_DIR, owner=self.owner)
      self.move(trash_dir, self.owner)
      self.is_trashed = True
      self.save()

      if self.is_directory:
        children_ids = self._get_child_ids_recursively(self.id)
        Document2.objects.filter(id__in=children_ids).update(is_trashed=True)
    except Document2.MultipleObjectsReturned:
      LOG.error('Multiple Trash directories detected. Merging all into one.')

      trash_dirs = list(Directory.objects.filter(name=self.TRASH_DIR, owner=self.owner).order_by('-last_modified'))
      parent_trash_dir = trash_dirs.pop()
      for dir in trash_dirs:
        dir.children.update(parent_directory=parent_trash_dir)
        dir.delete()

      self.move(parent_trash_dir, self.owner)

  def restore(self):
    # Currently restoring any doucment to /home
    home_dir = Document2.objects.get_home_directory(self.owner)
    self.move(home_dir, self.owner)
    self.is_trashed = False
    self.save()

    if self.is_directory:
      children_ids = self._get_child_ids_recursively(self.id)
      Document2.objects.filter(id__in=children_ids).update(is_trashed=False)

  def _get_child_ids_recursively(self, directory_id):
    """
    Returns the list of all children ids for a given directory id recursively, excluding history documents
    """
    directory = Directory.objects.get(id=directory_id)
    children_ids = []
    for child in directory.children.filter(is_history=False).filter(is_managed=False):
      children_ids.append(child.id)
      if child.is_directory:
        children_ids.extend(self._get_child_ids_recursively(child.id))
    return children_ids

  def can_read(self, user):
    perm = self.get_permission('read')
    has_read_permissions = perm.user_has_access(user) if perm else False
    return is_admin(user) or self.owner == user or self.can_write(user) or has_read_permissions

  def can_read_or_exception(self, user):
    if self.can_read(user):
      return True
    else:
      raise PopupException(_("Document does not exist or you don't have the permission to access it."), error_code=401)

  def can_write(self, user):
    perm = self.get_permission('write')
    has_write_permissions = perm.user_has_access(user) if perm else False
    return is_admin(user) or self.owner == user or has_write_permissions or (self.parent_directory and self.parent_directory.can_write(user))

  def can_write_or_exception(self, user):
    if self.can_write(user):
      return True
    else:
      raise PopupException(_("Document does not exist or you don't have the permission to access it."))

  def get_permission(self, perm='read'):
    try:
      return Document2Permission.objects.get(doc=self, perms=perm)
    except Document2Permission.DoesNotExist:
      return None

  def share(self, user, name='read', users=None, groups=None):
    try:
      with transaction.atomic():
        self.update_permission(user, name, users, groups)
        # For directories, update all children recursively with same permissions
        for child in self.children.all():
          child.share(user, name, users, groups)
    except Exception, e:
      raise PopupException(_("Failed to share document: %s") % e)
    return self

  def update_permission(self, user, name='read', users=None, groups=None):
    # Check if user has access to grant permissions
    if users or groups:
      if name == 'read':
        self.can_read_or_exception(user)
      elif name == 'write':
        self.can_write_or_exception(user)
      else:
        raise ValueError(_('Invalid permission type: %s') % name)

    perm, created = Document2Permission.objects.get_or_create(doc=self, perms=name)

    perm.users = []
    if users is not None:
      perm.users = users

    perm.groups = []
    if groups is not None:
      perm.groups = groups

    perm.save()

  def _get_doc1(self, doc2_type=None):
    if not doc2_type:
      doc2_type = self.type

    try:
      doc = self.doc.get()
    except Exception, e:
      LOG.error('Exception when retrieving document object for saved query: %s' % e)
      doc = Document.objects.link(
        self,
        owner=self.owner,
        name=self.name,
        description=self.description,
        extra=doc2_type
      )

    return doc

  def _massage_permissions(self):
    """
    Returns the permissions for a given document as a dictionary
    """
    permissions = {
      'read': {'users': [], 'groups': []},
      'write': {'users': [], 'groups': []}
    }

    read_perms = self.get_permission(perm='read')
    write_perms = self.get_permission(perm='write')

    if read_perms:
      permissions.update(read_perms.to_dict())
    if write_perms:
      permissions.update(write_perms.to_dict())

    return permissions

  def _redact_query(self):
    """
    Optionally mask out the query from being saved to the database. This is because if the database contains sensitive
    information like personally identifiable information, that information could be leaked into the Hue database and
    logfiles.
    """
    if global_redaction_engine.is_enabled() and (self.type == 'notebook' or self.type.startswith('query')):
      data_dict = self.data_dict
      snippets = data_dict.get('snippets', [])
      for snippet in snippets:
        if snippet['type'] in ('hive', 'impala'):  # TODO: Pull SQL types from canonical lookup
          redacted_statement_raw = global_redaction_engine.redact(snippet['statement_raw'])
          if snippet['statement_raw'] != redacted_statement_raw:
            snippet['statement_raw'] = redacted_statement_raw
            snippet['statement'] = global_redaction_engine.redact(snippet['statement'])
            snippet['is_redacted'] = True
      self.data = json.dumps(data_dict)
      self.search = global_redaction_engine.redact(self.search)

  def _contains_cycle(self):
    """
    Uses Floyd's cycle-detection algorithm to detect a cycle (aka Tortoise and Hare)
    https://en.wikipedia.org/wiki/Cycle_detection#Tortoise_and_hare
    """
    # Test base case where self.uuid == self.parent_directory.uuid first
    if self.parent_directory is not None and self.parent_directory.uuid == self.uuid:
      return True

    slow = self
    fast = self
    while True:
      slow = slow.parent_directory
      if slow and slow.uuid == self.uuid:
        slow = self

      if fast.parent_directory is not None:
        if fast.parent_directory.uuid == self.uuid:
          fast = self.parent_directory.parent_directory
        else:
          fast = fast.parent_directory.parent_directory
      else:
        return False

      if slow is None or fast is None:
        return False

      if slow == fast:
        return True


class DirectoryManager(Document2Manager):

  def get_queryset(self):
    return super(DirectoryManager, self).get_queryset().filter(type='directory')


class Directory(Document2):
  # e.g. name = '/' or '/dir1/dir2/f3'

  objects = DirectoryManager()

  class Meta:
    proxy = True

  def get_children_documents(self):
    """
    Returns the children documents for a given directory, excluding history documents
    """
    documents = self.children.filter(is_history=False).filter(is_managed=False)  # TODO: perms
    return documents

  def get_children_and_shared_documents(self, user):
    """
    Returns the children and shared documents for a given directory, excluding history documents
    """
    # Get documents that are direct children, or shared with but not owned by the current user
    documents = Document2.objects.filter(
        Q(parent_directory=self) |
        ( (Q(document2permission__users=user) | Q(document2permission__groups__in=user.groups.all())) &
          ~Q(owner=user) )
      )

    documents = documents.exclude(is_history=True).exclude(is_managed=True)

    # Excluding all trashed docs across users
    documents = documents.exclude(is_trashed=True)

    # Optimizing roll up for /home by checking only with directories instead of all documents
    # For all other directories roll up is done in _filter_documents()
    directories_all = Document2.objects.filter(type='directory').exclude(id=self.id)
    directories_inside_home = directories_all.filter(
      (Q(document2permission__users=user) | Q(document2permission__groups__in=user.groups.all())) &
        ~Q(owner=user)
    )
    documents = documents.exclude(parent_directory__in=directories_inside_home)

    return documents.defer('description', 'data', 'extra', 'search').distinct().order_by('-last_modified')


  def save(self, *args, **kwargs):
    self.type = 'directory'
    super(Directory, self).save(*args, **kwargs)


class Document2Permission(models.Model):
  """
  Combine either:
   - regular perms (listed)
   - link
  """
  READ_PERM = 'read'
  WRITE_PERM = 'write'
  COMMENT_PERM = 'comment'

  doc = models.ForeignKey(Document2)

  users = models.ManyToManyField(auth_models.User, db_index=True, db_table='documentpermission2_users')
  groups = models.ManyToManyField(auth_models.Group, db_index=True, db_table='documentpermission2_groups')

  perms = models.CharField(default=READ_PERM, max_length=10, db_index=True, choices=( # one perm
    (READ_PERM, 'read'),
    (WRITE_PERM, 'write'),
    (COMMENT_PERM, 'comment'), # PLAYER PERM?
  ))

  # link = models.CharField(default=uuid_default, max_length=255, unique=True) # Short link like dropbox
  # embed

  class Meta:
    unique_together = ('doc', 'perms')

  def to_dict(self):
    return {
      self.perms: {
        'users': [{'id': perm_user.id, 'username': perm_user.username} for perm_user in self.users.all()],
        'groups': [{'id': perm_group.id, 'name': perm_group.name} for perm_group in self.groups.all()]
      }
    }

  def user_has_access(self, user):
    """
    Returns true if the given user has permissions based on users, groups, or all flag
    """
    return self.groups.filter(id__in=user.groups.all()).exists() or user in self.users.all()


def get_cluster_config(user):
  cluster_type = Cluster(user).get_type()
  cluster_config = ClusterConfig(user, cluster_type=cluster_type)

  return cluster_config.get_config()


# Aka 'Atus'
ANALYTIC_DB = 'altus'


class ClusterConfig():
  """
  Configuration of the apps and engines that each individual user sees on the core Hue.
  Fine grained Hue permissions and available apps are leveraged here in order to render the correct UI.

  TODO: rename to HueConfig
  TODO: get list of contexts dynamically
  """
  def __init__(self, user, apps=None, cluster_type='ini'):
    self.user = user
    self.apps = appmanager.get_apps_dict(self.user) if apps is None else apps
    self.cluster_type = cluster_type


  def refreshConfig(self):
    # TODO: reload "some ini sections"
    pass


  def get_config(self):
    app_config = self.get_apps()
    editors = app_config.get('editor')
    main_button_action = self.get_main_quick_action(app_config)

    if main_button_action.get('is_sql'):
      default_sql_interpreter = main_button_action['type']
    else:
      default_sql_interpreter = editors and editors['default_sql_interpreter']

    return {
      'app_config': app_config,
      'main_button_action': main_button_action,
      'button_actions': [
        app for app in [
          editors,
          app_config.get('dashboard'),
          app_config.get('scheduler')
        ] if app is not None
      ],
      'default_sql_interpreter': default_sql_interpreter,
      'cluster_type': self.cluster_type
    }


  def get_apps(self):
    apps = OrderedDict([app for app in [
      ('editor', self._get_editor()),
      ('dashboard', self._get_dashboard()),
      ('catalogs', self._get_catalogs()),
      ('browser', self._get_browser()),
      ('scheduler', self._get_scheduler()),
      ('sdkapps', self._get_sdk_apps()),
      ('home', self._get_home()),
    ] if app[1]])

    return apps


  def get_main_quick_action(self, apps):
    if not apps:
      raise PopupException(_('No permission to any app.'))

    default_app = apps.values()[0]
    default_interpreter = default_app.get('interpreters')

    try:
      user_default_app = json.loads(UserPreferences.objects.get(user=self.user, key='default_app').value)
      if apps.get(user_default_app['app']):
        default_interpreter = []
        default_app = apps[user_default_app['app']]
        if default_app.get('interpreters'):
          interpreters = [interpreter for interpreter in default_app['interpreters'] if interpreter['type'] == user_default_app['interpreter']]
          if interpreters:
            default_interpreter = interpreters
    except UserPreferences.DoesNotExist:
      pass
    except Exception:
      LOG.exception('Could not load back default app')

    if default_interpreter:
      return default_interpreter[0]
    else:
      return default_app


  def _get_home(self):
    return {
      'name': 'home',
      'displayName': _('Home'),
      'buttonName': _('Documents'),
      'interpreters': [],
      'page': '/home'
    }


  def _get_editor(self):
    interpreters = []

    _interpreters = get_ordered_interpreters(self.user)

    if ANALYTIC_DB in self.cluster_type:
      _interpreters = [interpreter for interpreter in _interpreters if interpreter['type'] in ('impala')] #, 'hive', 'spark2', 'pyspark', 'mapreduce')]

    for interpreter in _interpreters:
      if interpreter['interface'] != 'hms':
        interpreters.append({
          'name': interpreter['name'],
          'type': interpreter['type'],
          'displayName': interpreter['name'],
          'buttonName': _('Query'),
          'tooltip': _('%s Query') % interpreter['type'].title(),
          'page': '/editor/?type=%(type)s' % interpreter,
          'is_sql': interpreter['is_sql'],
        })

    if SHOW_NOTEBOOKS.get() and ANALYTIC_DB not in self.cluster_type:
      try:
        first_non_sql_index = [interpreter['is_sql'] for interpreter in interpreters].index(False)
      except ValueError:
        first_non_sql_index = 0
      interpreters.insert(first_non_sql_index, {
        'name': 'notebook',
        'type': 'notebook',
        'displayName': 'Notebook',
        'buttonName': _('Notebook'),
        'tooltip': _('Notebook'),
        'page': '/notebook',
        'is_sql': False,
      })

    if interpreters:
      return {
        'name': 'editor',
        'displayName': _('Editor'),
        'buttonName': _('Query'),
        'interpreters': interpreters,
        'interpreter_names': [interpreter['type'] for interpreter in interpreters],
        'page': interpreters[0]['page'],
        'default_sql_interpreter': next((interpreter['type'] for interpreter in interpreters if interpreter.get('is_sql')), 'hive')
      }
    else:
      return None

  def _get_catalogs(self):
    interpreters = []

    _interpreters = get_ordered_interpreters(self.user)

    for interpreter in _interpreters:
      if interpreter['interface'] == 'hms':
        interpreters.append({
          'name': interpreter['name'],
          'type': interpreter['type'],
          'displayName': interpreter['name'],
          'buttonName': _('Query'),
          'tooltip': _('%s Query') % interpreter['type'].title(),
          'page': '/editor/?type=%(type)s' % interpreter,
          'is_sql': interpreter['is_sql'],
          'is_catalog': interpreter['is_catalog'],
        })

    return interpreters if interpreters else None

  def _get_dashboard(self):
    interpreters = get_engines(self.user)
    _interpreters = []

    if interpreters and ANALYTIC_DB not in self.cluster_type:
      if HAS_REPORT_ENABLED.get():
        _interpreters.append({
          'type': 'report',
          'displayName': 'Report',
          'buttonName': 'Report',
          'page': '/dashboard/new_search?engine=report',
          'tooltip': _('Report'),
          'is_sql': False
        })

      _interpreters.extend([{
          'type': interpreter['type'],
          'displayName': interpreter['type'].title(),
          'buttonName': interpreter['type'].title(),
          'page': '/dashboard/new_search?engine=%(type)s' % interpreter,
          'tooltip': _('%s Dashboard') % interpreter['type'].title(),
          'is_sql': True
        } for interpreter in interpreters
      ])

      return {
        'name': 'dashboard',
        'displayName': _('Dashboard'),
        'buttonName': _('Dashboard'),
        'interpreters': _interpreters,
        'page': '/dashboard/new_search?engine=%(type)s' % interpreters[0]
      }
    else:
      return None

  def _get_browser(self):
    interpreters = []

    if has_hdfs_enabled() and 'filebrowser' in self.apps and ANALYTIC_DB not in self.cluster_type:
      interpreters.append({
        'type': 'hdfs',
        'displayName': _('Files'),
        'buttonName': _('Browse'),
        'tooltip': _('Files'),
        'page': '/filebrowser/' + (not self.user.is_anonymous() and 'view=' + urllib.quote(self.user.get_home_directory().encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS) or '')
      })

    if is_s3_enabled() and 'filebrowser' in self.apps and has_s3_access(self.user) and not IS_EMBEDDED.get():
      interpreters.append({
        'type': 's3',
        'displayName': _('S3'),
        'buttonName': _('Browse'),
        'tooltip': _('S3'),
        'page': '/filebrowser/view=' + urllib.quote('S3A://'.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      })

    if is_adls_enabled() and 'filebrowser' in self.apps and has_adls_access(self.user) and ANALYTIC_DB not in self.cluster_type:
      interpreters.append({
        'type': 'adls',
        'displayName': _('ADLS'),
        'buttonName': _('Browse'),
        'tooltip': _('ADLS'),
        'page': '/filebrowser/view=' + urllib.quote('adl:/'.encode('utf-8'), safe=SAFE_CHARACTERS_URI_COMPONENTS)
      })

    if 'metastore' in self.apps:
      interpreters.append({
        'type': 'tables',
        'displayName': _('Tables'),
        'buttonName': _('Browse'),
        'tooltip': _('Tables'),
        'page': '/metastore/tables'
      })

    if 'search' in self.apps and ANALYTIC_DB not in self.cluster_type:
      interpreters.append({
        'type': 'indexes',
        'displayName': _('Indexes'),
        'buttonName': _('Dashboard'),
        'tooltip': _('Indexes'),
        'page': '/indexer/'
      })

    if 'jobbrowser' in self.apps:
      from hadoop.cluster import get_default_yarncluster # Circular loop

      title =  _('Jobs') if ANALYTIC_DB not in self.cluster_type else _('Queries')

      if get_default_yarncluster():
        interpreters.append({
          'type': 'yarn',
          'displayName': title,
          'buttonName': title,
          'tooltip': title,
          'page': '/jobbrowser/'
        })

    if has_kafka() and ANALYTIC_DB not in self.cluster_type:
      interpreters.append({
        'type': 'kafka',
        'displayName': _('Streams'),
        'buttonName': _('Browse'),
        'tooltip': _('Kafka'),
        'page': '/kafka/'
      })

    if 'hbase' in self.apps and ANALYTIC_DB not in self.cluster_type:
      interpreters.append({
        'type': 'hbase',
        'displayName': _('HBase'),
        'buttonName': _('Browse'),
        'tooltip': _('HBase'),
        'page': '/hbase/'
      })

    if 'security' in self.apps and not IS_EMBEDDED.get():
      interpreters.append({
        'type': 'security',
        'displayName': _('Security'),
        'buttonName': _('Browse'),
        'tooltip': _('Security'),
        'page': '/security/hive'
      })

    if 'sqoop' in self.apps and ANALYTIC_DB not in self.cluster_type:
      from sqoop.conf import IS_ENABLED
      if IS_ENABLED.get():
        interpreters.append({
          'type': 'sqoop',
          'displayName': _('Sqoop'),
          'buttonName': _('Browse'),
          'tooltip': _('Sqoop'),
          'page': '/sqoop'
        })

    if interpreters:
      return {
          'name': 'browser',
          'displayName': _('Browsers'),
          'buttonName': _('Browse'),
          'interpreters': interpreters,
          'interpreter_names': [interpreter['type'] for interpreter in interpreters],
        }
    else:
      return None


  def _get_scheduler(self):
    interpreters = [{
        'type': 'oozie-workflow',
        'displayName': _('Workflow'),
        'buttonName': _('Schedule'),
        'tooltip': _('Workflow'),
        'page': '/oozie/editor/workflow/new/'
      }, {
        'type': 'oozie-coordinator',
        'displayName': _('Schedule'),
        'buttonName': _('Schedule'),
        'tooltip': _('Schedule'),
        'page': '/oozie/editor/coordinator/new/'
      }, {
        'type': 'oozie-bundle',
        'displayName': _('Bundle'),
        'buttonName': _('Schedule'),
        'tooltip': _('Bundle'),
        'page': '/oozie/editor/bundle/new/'
      }
    ]

    if 'oozie' in self.apps and not (self.user.has_hue_permission(action="disable_editor_access", app="oozie") and not is_admin(self.user)) and ANALYTIC_DB not in self.cluster_type:
      return {
          'name': 'oozie',
          'displayName': _('Scheduler'),
          'buttonName': _('Schedule'),
          'interpreters': interpreters,
          'page': interpreters[0]['page']
        }
    else:
      return None


  def _get_sdk_apps(self):
    current_app, other_apps, apps_list = _get_apps(self.user)

    interpreters = []

    for other in other_apps:
      interpreters.append({
        'type': other.display_name,
        'displayName': other.nice_name,
        'buttonName': other.nice_name,
        'tooltip': other.nice_name,
        'page': '/%s' % other.display_name
      })

    if interpreters:
      return {
          'name': 'other',
          'displayName': _('Other Apps'),
          'buttonName': _('Other'),
          'interpreters': interpreters,
        }
    else:
      return None


class Cluster():

  def __init__(self, user):
    self.user = user
    self.clusters = get_clusters(user)

    if len(self.clusters) == 1:
      self.data = self.clusters.values()[0]
    elif IS_K8S_ONLY.get():
      self.data = self.clusters['AltusV2']
      self.data['type'] = 'altus' # To show simplified UI
    elif IS_MULTICLUSTER_ONLY.get():
      self.data = self.clusters['Altus']
    else:
      self.data = self.clusters[CLUSTER_ID.get()]

  def get_type(self):
    return self.data['type']

  def get_config(self, name):
    return self.clusters[name]


def _get_apps(user, section=None):
  current_app = None
  other_apps = []
  if user.is_authenticated():
    apps_list = appmanager.get_apps_dict(user)
    apps = apps_list.values()
    for app in apps:
      if app.display_name not in [
          'beeswax', 'hive', 'impala', 'pig', 'jobsub', 'jobbrowser', 'metastore', 'hbase', 'sqoop', 'oozie', 'filebrowser',
          'useradmin', 'search', 'help', 'about', 'zookeeper', 'proxy', 'rdbms', 'spark', 'indexer', 'security', 'notebook'] and app.menu_index != -1:
        other_apps.append(app)
      if section == app.display_name:
        current_app = app
  else:
    apps_list = []

  return current_app, other_apps, apps_list


def get_user_preferences(user, key=None):
  if key is not None:
    try:
      x = UserPreferences.objects.get(user=user, key=key)
      return {key: x.value}
    except UserPreferences.DoesNotExist:
      return None
  else:
    return dict((x.key, x.value) for x in UserPreferences.objects.filter(user=user))


def set_user_preferences(user, key, value):
  try:
    x = UserPreferences.objects.get(user=user, key=key)
  except UserPreferences.DoesNotExist:
    x = UserPreferences(user=user, key=key)
  x.value = value
  x.save()
  return x


def get_data_link(meta):
  link = None

  if not meta.get('type'):
    pass
  elif meta['type'] == 'hbase':
    link = '/hbase/#Cluster/%(table)s/query/%(row_key)s' % meta
    if 'col' in meta:
      link += '[%(fam)s:%(col)s]' % meta
    elif 'fam' in meta:
      link += '[%(fam)s]' % meta
  elif meta['type'] == 'hdfs':
    link = '/filebrowser/view=%(path)s' % meta # Could add a byte #
  elif meta['type'] == 'link':
    link = meta['link']
  elif meta['type'] == 'hive':
    link = '/metastore/table/%(database)s/%(table)s' % meta # Could also add col=val

  return link
