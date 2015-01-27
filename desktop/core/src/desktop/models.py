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
import logging
import json
import uuid

from itertools import chain

from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.i18n import force_unicode
from desktop.lib.exceptions_renderable import PopupException

from desktop import appmanager


LOG = logging.getLogger(__name__)


SAMPLE_USERNAME = 'sample'


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
    try:
      tag, created = DocumentTag.objects.get_or_create(owner=user, tag=name)
    except DocumentTag.MultipleObjectsReturned, ex:
      # We can delete duplicate tags of a user
      dups = DocumentTag.objects.filter(owner=user, tag=name)
      tag = dups[0]
      for dup in dups[1:]:
        LOG.warn('Deleting duplicate %s' % dup)
        dup.delete()
    return tag

  def get_default_tag(self, user):
    return self._get_tag(user, DocumentTag.DEFAULT)

  def get_trash_tag(self, user):
    return self._get_tag(user, DocumentTag.TRASH)

  def get_history_tag(self, user):
    return self._get_tag(user, DocumentTag.HISTORY)

  def get_example_tag(self, user):
    return self._get_tag(user, DocumentTag.EXAMPLE)

  def tag(self, owner, doc_id, tag_name='', tag_id=None):
    try:
      tag = DocumentTag.objects.get(id=tag_id, owner=owner)
      if tag.tag in DocumentTag.RESERVED:
        raise Exception(_("Can't add %s: it is a reserved tag.") % tag)
    except DocumentTag.DoesNotExist:
      tag = self._get_tag(user=owner, name=tag_name)

    doc = Document.objects.get_doc(doc_id, owner)
    doc.add_tag(tag)
    return tag

  def untag(self, tag_id, owner, doc_id):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)

    if tag.tag in DocumentTag.RESERVED:
      raise Exception(_("Can't remove %s: it is a reserved tag.") % tag)

    doc = Document.objects.get_doc(doc_id, owner=owner)
    doc.can_write_or_exception(owner)
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
    doc = Document.objects.get_doc(doc_id, owner)
    doc.can_write_or_exception(owner)

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

  RESERVED = (DEFAULT, TRASH, HISTORY, EXAMPLE)

  objects = DocumentTagManager()
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

  def get_docs(self, user, model_class=None, extra=None):
    docs = Document.objects.documents(user).exclude(name='pig-app-hue-script')

    if model_class is not None:
      ct = ContentType.objects.get_for_model(model_class)
      docs = docs.filter(content_type=ct)

    if extra is not None:
      docs = docs.filter(extra=extra)

    return docs

  def get_doc(self, doc_id, user):
    return Document.objects.documents(user).get(id=doc_id)

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

  def sync(self):

    try:
      from oozie.models import Workflow, Coordinator, Bundle

      for job in list(chain(Workflow.objects.all(), Coordinator.objects.all(), Bundle.objects.all())):
        if job.doc.count() > 1:
          LOG.warn('Deleting duplicate document %s for %s' % (job.doc.all(), job))
          job.doc.all().delete()

        if not job.doc.exists():
          doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.description)
          tag = DocumentTag.objects.get_example_tag(user=job.owner)
          doc.tags.add(tag)
          if job.is_trashed:
            doc.send_to_trash()
          if job.is_shared:
            doc.share_to_default()
          if hasattr(job, 'managed'):
            if not job.managed:
              doc.extra = 'jobsub'
              doc.save()
        if job.owner.username == SAMPLE_USERNAME:
          job.doc.get().share_to_default()
    except Exception, e:
      LOG.warn(force_unicode(e))

    try:
      from beeswax.models import SavedQuery

      for job in SavedQuery.objects.all():
        if job.doc.count() > 1:
          LOG.warn('Deleting duplicate document %s for %s' % (job.doc.all(), job))
          job.doc.all().delete()

        if not job.doc.exists():
          doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.desc, extra=job.type)
          tag = DocumentTag.objects.get_example_tag(user=job.owner)
          doc.tags.add(tag)
          if job.is_trashed:
            doc.send_to_trash()
        if job.owner.username == SAMPLE_USERNAME:
          job.doc.get().share_to_default()
    except Exception, e:
      LOG.warn(force_unicode(e))

    try:
      from pig.models import PigScript

      for job in PigScript.objects.all():
        if job.doc.count() > 1:
          LOG.warn('Deleting duplicate document %s for %s' % (job.doc.all(), job))
          job.doc.all().delete()

        if not job.doc.exists():
          doc = Document.objects.link(job, owner=job.owner, name=job.dict['name'], description='')
          tag = DocumentTag.objects.get_example_tag(user=job.owner)
          doc.tags.add(tag)
        if job.owner.username == SAMPLE_USERNAME:
          job.doc.get().share_to_default()
    except Exception, e:
      LOG.warn(force_unicode(e))

    # Make sure doc have at least a tag
    try:
      for doc in Document.objects.filter(tags=None):
        default_tag = DocumentTag.objects.get_default_tag(doc.owner)
        doc.tags.add(default_tag)
    except Exception, e:
      LOG.warn(force_unicode(e))

    # For now remove the default tag from the examples
    try:
      for doc in Document.objects.filter(tags__tag=DocumentTag.EXAMPLE):
        default_tag = DocumentTag.objects.get_default_tag(doc.owner)
        doc.tags.remove(default_tag)
    except Exception, e:
      LOG.warn(force_unicode(e))

    # Delete documents with no object
    try:
      for doc in Document.objects.all():
        if doc.content_type is None or doc.content_object is None:
          doc.delete()
    except Exception, e:
      LOG.warn(force_unicode(e))


UTC_TIME_FORMAT = "%Y-%m-%dT%H:%MZ"


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
  content_object = generic.GenericForeignKey('content_type', 'object_id')

  objects = DocumentManager()
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
    return user.is_superuser or self.owner == user or Document.objects.get_docs(user).filter(id=self.id).exists()

  def can_write(self, user):
    perm = self.list_permissions('write')
    return user.is_superuser or self.owner == user or perm.groups.filter(id__in=user.groups.all()).exists() or user in perm.users.all()

  def can_read_or_exception(self, user, exception_class=PopupException):
    if self.can_read(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to read this document.') % user)

  def can_write_or_exception(self, user, exception_class=PopupException):
    if self.can_write(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to write this document.') % user)

  def copy(self, name=None, owner=None):
    copy_doc = self

    copy_doc.pk = None
    copy_doc.id = None
    if name is not None:
      copy_doc.name = name
    if owner is not None:
      copy_doc.owner = owner
    copy_doc.save()

    # Don't copy tags
    default_tag = DocumentTag.objects.get_default_tag(copy_doc.owner)
    tags = [default_tag]
    copy_doc.tags.add(*tags)

    return copy_doc

  @property
  def icon(self):
    apps = appmanager.get_apps_dict()

    try:
      if self.content_type.app_label == 'beeswax':
        if self.extra == '0':
          return apps['beeswax'].icon_path
        elif self.extra == '3':
          return apps['spark'].icon_path
        else:
          return apps['impala'].icon_path
      elif self.content_type.app_label == 'oozie':
        if self.extra == 'jobsub':
          return apps['jobsub'].icon_path
        else:
          return self.content_type.model_class().ICON
      elif self.content_type.app_label in apps:
        return apps[self.content_type.app_label].icon_path
      else:
        return '/static/art/icon_hue_48.png'
    except Exception, e:
      LOG.warn(force_unicode(e))
      return '/static/art/icon_hue_48.png'

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
      'uuid': None,
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
    try:
      perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=perm)
    except DocumentPermission.MultipleObjectsReturned:
      # We can delete duplicate perms of a document
      dups = DocumentPermission.objects.filter(doc=document, perms=perm)
      perm = dups[0]
      for dup in dups[1:]:
        LOG.warn('Deleting duplicate %s' % dup)
        dup.delete()
    return perm


class DocumentPermission(models.Model):
  READ_PERM = 'read'
  WRITE_PERM = 'write'

  doc = models.ForeignKey(Document)

  users = models.ManyToManyField(auth_models.User, db_index=True, db_table='documentpermission_users')
  groups = models.ManyToManyField(auth_models.Group, db_index=True, db_table='documentpermission_groups')
  perms = models.TextField(default=READ_PERM, choices=( # one perm
    (READ_PERM, 'read'),
    (WRITE_PERM, 'write'),
  ))


  objects = DocumentPermissionManager()
  unique_together = ('doc', 'perms')



class Document2Manager(models.Manager):
  def get_by_natural_key(self, uuid, version, is_history):
    return self.get(uuid=uuid, version=version, is_history=is_history)


def uuid_default():
    return uuid.uuid4().hex


class Document2(models.Model):    
  owner = models.ForeignKey(auth_models.User, db_index=True, verbose_name=_t('Owner'), help_text=_t('Creator.'), related_name='doc2_owner')
  name = models.CharField(default='', max_length=255)
  description = models.TextField(default='')
  uuid = models.CharField(default=uuid_default, max_length=32, db_index=True)
  type = models.CharField(default='', max_length=32, db_index=True, help_text=_t('Type of document, e.g. Hive query, Oozie workflow, Search Dashboard...'))

  data = models.TextField(default='{}')
  extra = models.TextField(default='')

  last_modified = models.DateTimeField(auto_now=True, db_index=True, verbose_name=_t('Time last modified'))
  version = models.SmallIntegerField(default=1, verbose_name=_t('Document version'), db_index=True) 
  is_history = models.BooleanField(default=False, db_index=True)

  tags = models.ManyToManyField('self', db_index=True)
  dependencies = models.ManyToManyField('self', db_index=True)
  doc = generic.GenericRelation(Document, related_name='doc_doc') # Compatibility with Hue 3
  
  objects = Document2Manager()
  unique_together = ('uuid', 'version', 'is_history')
  
  def natural_key(self):
    return (self.uuid, self.version, self.is_history)
  
  @property
  def data_dict(self):
    if not self.data:
      self.data = json.dumps({})
    data_python = json.loads(self.data)

    return data_python

  def update_data(self, post_data):
    data_dict = self.data_dict

    data_dict.update(post_data)

    self.data = json.dumps(data_dict)

  def get_absolute_url(self):
    if self.type == 'oozie-coordinator2':
      return reverse('oozie:edit_coordinator') + '?coordinator=' + str(self.id)
    elif self.type == 'oozie-bundle2':
      return reverse('oozie:edit_bundle') + '?bundle=' + str(self.id)    
    else:
      return reverse('oozie:edit_workflow') + '?workflow=' + str(self.id)
    
  def to_dict(self):
    return {
      'owner': self.owner.username,
      'name': self.name,
      'description': self.description,
      'uuid': self.uuid,
      'id': self.id,
      'doc1_id': self.doc.get().id if self.doc.exists() else -1,
      'type': self.type,
      'last_modified': self.last_modified.strftime(UTC_TIME_FORMAT),
      'last_modified_ts': calendar.timegm(self.last_modified.utctimetuple()),
      'isSelected': False
    }

