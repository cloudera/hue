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

from itertools import chain

from django.db import models
from django.db.models import Q
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.i18n import force_unicode
from desktop.lib.exceptions_renderable import PopupException

from useradmin.models import get_default_user_group



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


class DocumentTag(models.Model):
  owner = models.ForeignKey(auth_models.User, db_index=True)
  tag = models.SlugField()

  DEFAULT = 'default'
  TRASH = 'trash'

  unique_together = ('owner', 'tag')

  def __unicode__(self):
    return force_unicode('%s') % (self.tag,)

  @classmethod
  def get_trash_tag(cls, user):
    tag, created = DocumentTag.objects.get_or_create(owner=user, tag=DocumentTag.TRASH)
    return tag
  
  @classmethod
  def add_or_create_tag(cls, owner, doc_id, tag_name, tag_id=None):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)
    if tag.id == DocumentTag.get_trash_tag(owner):
      raise Exception(_("Can't add trash tag. Please trash the document from instead."))
        
    if tag_id is not None:
      tag = DocumentTag.objects.create(tag=tag_name, owner=owner)  
      
    doc = Document.objects.get_doc(doc_id, owner=owner)
    doc.add(tag)


  @classmethod
  def remove_tag(cls, tag_id, owner, doc_id):
    tag = DocumentTag.objects.get(id=tag_id, owner=owner)
    if tag.id == DocumentTag.get_trash_tag(owner):
      raise Exception(_("Can't remove trash tag. Please restore the document from the trash instead."))

    doc = Document.objects.get_doc(doc_id, owner=owner)
    doc.remove(tag)
    if tag.tag != DocumentTag.TRASH and not tag.document_set.exists():
      tag.delete()    


class DocumentManager(models.Manager):

  def documents(self, user):
    return Document.objects.filter(Q(owner=user) | Q(documentpermission__users=user) | Q(documentpermission__groups__in=user.groups.all()))
  
  def get_docs(self, user):
    return Document.objects.documents(user).exclude(name='pig-app-hue-script')
    
  def get_doc(self, doc_id, user):
    return Document.objects.documents(user).get(id=doc_id)  
  
  def trashed_docs(self, model_class, user):
    ct = ContentType.objects.get_for_model(model_class)
    tag = DocumentTag.get_trash_tag(user=user)
    
    return Document.objects.get_docs(user).filter(content_type=ct).filter(tags__in=[tag]).order_by('-last_modified')

  def trashed(self, model_class, user):
    docs = self.trashed_docs(model_class, user)
    
    return [job.content_object for job in docs if job.content_object]
  
  def available_docs(self, model_class, user):
    ct = ContentType.objects.get_for_model(model_class)
    tag = DocumentTag.get_trash_tag(user=user)
    
    return Document.objects.get_docs(user).filter(content_type=ct).exclude(tags__in=[tag]).order_by('-last_modified')
          
  def available(self, model_class, user):
    docs = self.available_docs(model_class, user)
    
    return [job.content_object for job in docs if job.content_object]
  
  def is_accessible_or_exception(self, user, doc_class, doc_id, exception_class=PopupException):
    if doc_id is None:
      return
    try:
      ct = ContentType.objects.get_for_model(doc_class)
      doc = Document.objects.get(object_id=doc_id, content_type=ct)
      if doc.is_accessible(user):
        return doc
      else:
        message = _("Permission denied. %(username)s does not have the permissions required to access document %(id)s") % \
            {'username': user.username, 'id': doc.id}
        raise exception_class(message)

    except Document.DoesNotExist:
      raise exception_class(_('Document %(id)s does not exist') % {'id': doc_id})

  def is_accessible(self, user, doc_class, doc_id):
    ct = ContentType.objects.get_for_model(doc_class)    
    doc = Document.objects.get(object_id=doc_id, content_type=ct)

    return doc.is_accessible(user)
  
  def link(self, content_object, owner, name='', description='', extra=''):
    doc = Document.objects.create(
              content_object=content_object,
              owner=owner,
              name=name,
              description=description,
              extra=extra
          )

    tag, created = DocumentTag.objects.get_or_create(owner=owner, tag=DocumentTag.DEFAULT)
    doc.tags.add(tag)

    return doc

  def sync(self):
    try:
      from oozie.models import Workflow, Coordinator, Bundle

      for job in list(chain(Workflow.objects.all(), Coordinator.objects.all(), Bundle.objects.all())):
        if not job.doc.exists():
          doc = Document.objects.link(job, owner=job.owner, name=job.name, description=job.description)
          tag, created = DocumentTag.objects.get_or_create(owner=job.owner, tag='default')
          doc.tags.add(tag)
          if job.is_trashed:
            doc.send_to_trash()
          if job.is_shared:
            DocumentPermission.share_to_default(doc)
    except Exception, e:
      print e
       
       
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
      
  def send_to_trash(self):
    tag = DocumentTag.get_trash_tag(user=self.owner)
    self.tags.add(tag)

  def restore_from_trash(self):
    tag = DocumentTag.get_trash_tag(user=self.owner)
    self.tags.remove(tag)

  def is_accessible(self, user):
    return user.is_superuser or self.owner == user or Document.objects.get_doc(self.id, user) 

  def can_read(self, user):
    return user.is_superuser or self.owner == user or Document.objects.get_doc(self.id, user)

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

  def copy(self):
    copy_doc = self

    tags = self.tags.all()

    copy_doc.pk = None
    copy_doc.id = None
    copy_doc.save()
    
    copy_doc.tags.add(*tags)
    
    return copy_doc 



class DocumentPermission(models.Model):
  doc = models.ForeignKey(Document)
  
  users = models.ManyToManyField(auth_models.User, db_index=True)
  groups = models.ManyToManyField(auth_models.Group, db_index=True) 
  perms = models.TextField(
      default='read', choices=(('read', 'read'),),)    

  @classmethod
  def share_to_default(cls, document):
    perm, created = DocumentPermission.objects.get_or_create(doc=document)
    default_group = get_default_user_group()
    if default_group:
      perm.groups.add(default_group)

# HistoryTable
# VersionTable
