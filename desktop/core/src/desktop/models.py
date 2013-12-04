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

import logging
from itertools import chain

from django.db import models
from django.db.models import Q
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
    # For now, the only shared tag is from 'sample' user and is named 'example'
    # Tag permissions will come later.
    # Share Tag from shared document will come later.
    tags = self

    try:
      sample_user = auth_models.User.objects.get(username=SAMPLE_USERNAME)
      tags = tags.filter(Q(owner=user) | Q(owner=sample_user, tag=DocumentTag.EXAMPLE))
    except:
      tags = tags.filter(owner=user)

    return tags.distinct()

  def create_tag(self, owner, tag_name):
    if tag_name in DocumentTag.RESERVED:
      raise Exception(_("Can't add %s: it is a reserved tag.") % tag_name)
    else:
      tag, created = DocumentTag.objects.get_or_create(tag=tag_name, owner=owner)
      return tag

  def get_default_tag(self, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=DocumentTag.DEFAULT)
    return tag

  def get_trash_tag(self, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=DocumentTag.TRASH)
    return tag

  def get_history_tag(self, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=DocumentTag.HISTORY)
    return tag

  def get_example_tag(self, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=DocumentTag.EXAMPLE)
    return tag

  def tag(self, owner, doc_id, tag_name='', tag_id=None):
    try:
      tag = DocumentTag.objects.get(id=tag_id, owner=owner)
      if tag.tag in DocumentTag.RESERVED:
        raise Exception(_("Can't add %s: it is a reserved tag.") % tag)
    except DocumentTag.DoesNotExist:
      tag = DocumentTag.objects.create(tag=tag_name, owner=owner)

    doc = Document.objects.get_doc(doc_id, owner)
    doc.add_tag(tag)
    return tag

  def untag(self, tag_id, owner, doc_id):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)

    if tag.tag in DocumentTag.RESERVED:
      raise Exception(_("Can't remove %s: it is a reserved tag.") % tag)

    doc = Document.objects.get_doc(doc_id, owner=owner)
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
    return Document.objects.filter(Q(owner=user) | Q(documentpermission__users=user) | Q(documentpermission__groups__in=user.groups.all()))

  def get_docs(self, user, model_class=None, extra=None):
    docs = Document.objects.documents(user).exclude(name='pig-app-hue-script').exclude(name='spark-app-hue-script')

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

  def available_docs(self, model_class, user):
    trash = DocumentTag.objects.get_trash_tag(user=user)
    history = DocumentTag.objects.get_history_tag(user=user)

    return Document.objects.get_docs(user, model_class).exclude(tags__in=[trash, history]).order_by('-last_modified')

  def available(self, model_class, user):
    docs = self.available_docs(model_class, user)

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
        if doc.content_type is None:
          doc.delete()
    except Exception, e:
      LOG.warn(force_unicode(e))


class Document(models.Model):
  owner = models.ForeignKey(auth_models.User, db_index=True, verbose_name=_t('Owner'), help_text=_t('User who can own the job.'), related_name='doc_owner')
  name = models.TextField(default='')
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
    default_tag = DocumentTag.objects.get_default_tag(user=self.owner)
    self.tags.remove(default_tag)

  def share_to_default(self):
    DocumentPermission.objects.share_to_default(self)

  def can_read(self, user):
    return user.is_superuser or self.owner == user or Document.objects.get_docs(user).filter(id=self.id).exists()

  def can_write(self, user):
    return user.is_superuser or self.owner == user

  def can_read_or_exception(self, user, exception_class=PopupException):
    if self.can_read(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to read this document.') % user)

  def can_write_or_exception(self, user, exception_class=PopupException):
    if self.can_write(user):
      return True
    else:
      raise exception_class(_('Only superusers and %s are allowed to modify this document.') % user)

  def copy(self, name=None, owner=None):
    copy_doc = self

    tags = self.tags.all()

    copy_doc.pk = None
    copy_doc.id = None
    if name is not None:
      copy_doc.name = name
    if owner is not None:
      copy_doc.owner = owner
    copy_doc.save()

    tags = filter(lambda tag: tag.tag != DocumentTag.EXAMPLE, tags)
    if not tags:
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
        return '/static/art/favicon.png'
    except Exception, e:
      LOG.warn(force_unicode(e))
      return '/static/art/favicon.png'

  def share(self, users, groups, name='read'):
    DocumentPermission.objects.update(document=self, name=name, users=users, groups=groups, add=True)

  def unshare(self, users, groups, name='read'):
    DocumentPermission.objects.update(document=self, name=name, users=users, groups=groups, add=False)

  def sync_permissions(self, perms_dict):
    """
    Example of input: {'read': {'user_ids': [1, 2, 3], 'group_ids': [1, 2, 3]}}
    """
    for name, perm in perms_dict.iteritems():
      users = groups = None

      if perm.get('user_ids'):
        users = auth_models.User.objects.in_bulk(perm.get('user_ids'))

      if perm.get('group_ids'):
        groups = auth_models.Group.objects.in_bulk(perm.get('group_ids'))

      DocumentPermission.objects.sync(document=self, name=name, users=users, groups=groups)

  def list_permissions(self):
    return DocumentPermission.objects.list(document=self)


class DocumentPermissionManager(models.Manager):

  def share_to_default(self, document):
    from useradmin.models import get_default_user_group # Remove build dependency
    perm, created = DocumentPermission.objects.get_or_create(doc=document)
    default_group = get_default_user_group()

    if default_group:
      perm.groups.add(default_group)

  def update(self, document, name='read', users=None, groups=None, add=True):
    if name != DocumentPermission.READ_PERM:
      raise PopupException(_('Only %s permissions is supported, not %s.') % (DocumentPermission.READ_PERM, name))

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
    if name != DocumentPermission.READ_PERM:
      raise PopupException(_('Only %s permissions is supported, not %s.') % (DocumentPermission.READ_PERM, name))

    perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=name)

    if users is not None:
      perm.users = []
      perm.users = users

    if groups is not None:
      perm.groups = []
      perm.groups = groups

    if not perm.users and not perm.groups:
      perm.delete()

  def list(self, document):
    perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=DocumentPermission.READ_PERM)
    return perm


class DocumentPermission(models.Model):
  READ_PERM = 'read'

  doc = models.ForeignKey(Document)

  users = models.ManyToManyField(auth_models.User, db_index=True)
  groups = models.ManyToManyField(auth_models.Group, db_index=True)
  perms = models.TextField(
      default='read', choices=((READ_PERM, 'read'),),)


  objects = DocumentPermissionManager()
  #unique_together = ('doc', 'perms')


# HistoryTable
# VersionTable
