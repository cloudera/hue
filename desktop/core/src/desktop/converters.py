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

import json
import logging
import re
import time

from django.db import transaction
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, DocumentPermission, DocumentTag, Document2, Directory, Document2Permission, \
  DOC2_NAME_INVALID_CHARS
from notebook.api import _historify
from notebook.models import import_saved_beeswax_query


LOG = logging.getLogger(__name__)


class DocumentConverter(object):
  """
  Given a user, converts any existing Document objects to Document2 objects
  """

  def __init__(self, user):
    self.user = user
    # If user does not have a home directory, we need to create one and import any orphan documents to it
    self.home_dir = Document2.objects.create_user_directories(self.user)
    self.imported_tag = DocumentTag.objects.get_imported2_tag(user=self.user)
    self.imported_docs = []


  def convert(self):
    # Convert SavedQuery documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery).filter(extra__in=[HQL, IMPALA, RDBMS])
      for doc in docs:
        if doc.content_object:
          notebook = import_saved_beeswax_query(doc.content_object)
          data = notebook.get_data()

          if doc.is_historic():
            data['isSaved'] = False

          doc2 = self._create_doc2(
              document=doc,
              doctype=data['type'],
              name=data['name'],
              description=data['description'],
              data=notebook.get_json()
          )

          if doc.is_historic():
            doc2.is_history = False

          self.imported_docs.append(doc2)
    except ImportError:
      LOG.warn('Cannot convert Saved Query documents: beeswax app is not installed')

    # Convert SQL Query history documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery, with_history=True).filter(extra__in=[HQL, IMPALA, RDBMS]).order_by('-last_modified')

      for doc in docs:
        if doc.content_object:
          notebook = import_saved_beeswax_query(doc.content_object)
          data = notebook.get_data()

          data['isSaved'] = False
          data['snippets'][0]['lastExecuted'] = time.mktime(doc.last_modified.timetuple()) * 1000

          doc2 = _historify(data, self.user)
          doc2.last_modified = doc.last_modified

          # save() updates the last_modified to current time. Resetting it using update()
          doc2.save()
          Document2.objects.filter(id=doc2.id).update(last_modified=doc.last_modified)

          self.imported_docs.append(doc2)

          # Tag for not re-importing
          Document.objects.link(
            doc2,
            owner=doc2.owner,
            name=doc2.name,
            description=doc2.description,
            extra=doc.extra
          )

          doc.add_tag(self.imported_tag)
          doc.save()
    except ImportError, e:
      LOG.warn('Cannot convert Saved Query documents: beeswax app is not installed')


    # Convert Job Designer documents
    try:
      from oozie.models import Workflow

      # TODO: Change this logic to actually embed the workflow data in Doc2 instead of linking to old job design
      docs = self._get_unconverted_docs(Workflow)
      for doc in docs:
        if doc.content_object:
          data = doc.content_object.data_dict
          data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
          doc2 = self._create_doc2(
              document=doc,
              doctype='link-workflow',
              description=doc.description,
              data=json.dumps(data)
          )
          self.imported_docs.append(doc2)
    except ImportError, e:
      LOG.warn('Cannot convert Job Designer documents: oozie app is not installed')

    # Convert PigScript documents
    try:
      from pig.models import PigScript

      # TODO: Change this logic to actually embed the pig data in Doc2 instead of linking to old pig script
      docs = self._get_unconverted_docs(PigScript)
      for doc in docs:
        if doc.content_object:
          data = doc.content_object.dict
          data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
          doc2 = self._create_doc2(
              document=doc,
              doctype='link-pigscript',
              description=doc.description,
              data=json.dumps(data)
          )
          self.imported_docs.append(doc2)
    except ImportError, e:
      LOG.warn('Cannot convert Pig documents: pig app is not installed')

    # Add converted docs to root directory
    if self.imported_docs:
      LOG.info('Successfully imported %d documents' % len(self.imported_docs))


  def _get_unconverted_docs(self, content_type, with_history=False):
    docs = Document.objects.get_docs(self.user, content_type).filter(owner=self.user)

    tags = [
      DocumentTag.objects.get_trash_tag(user=self.user), # No trashed docs
      DocumentTag.objects.get_example_tag(user=self.user), # No examples
      self.imported_tag # No already imported docs
    ]

    if not with_history:
      tags.append(DocumentTag.objects.get_history_tag(user=self.user)) # No history yet

    return docs.exclude(tags__in=tags)


  def _get_parent_directory(self, document):
    """
    Returns the parent directory object that should be used for a given document. If the document is tagged with a
        project name (non-RESERVED DocumentTag), a Directory object with the first project tag found is returned.
        Otherwise, the owner's home directory is returned.
    """
    parent_dir = self.home_dir
    project_tags = document.tags.exclude(tag__in=DocumentTag.RESERVED)
    if project_tags.exists():
      first_tag = project_tags[0]
      parent_dir, created = Directory.objects.get_or_create(
          owner=self.user,
          name=first_tag.tag,
          parent_directory=self.home_dir
      )
    return parent_dir


  def _sync_permissions(self, document, document2):
    """
    Syncs (creates) Document2Permissions based on the DocumentPermissions found for a given document.
    """
    doc_permissions = DocumentPermission.objects.filter(doc=document)
    for perm in doc_permissions:
      doc2_permission, created = Document2Permission.objects.get_or_create(doc=document2, perms=perm.perms)
      if perm.users:
        doc2_permission.users.add(*perm.users.all())
      if perm.groups:
        doc2_permission.groups.add(*perm.groups.all())


  def _create_doc2(self, document, doctype, name=None, description=None, data=None):
    try:
      with transaction.atomic():
        name = name if name else document.name
        name = re.sub(DOC2_NAME_INVALID_CHARS, '', name)

        document2 = Document2.objects.create(
          owner=self.user,
          parent_directory=self._get_parent_directory(document),
          name=name,
          type=doctype,
          description=description,
          data=data
        )
        self._sync_permissions(document, document2)

        # Create a doc1 copy and link it for backwards compatibility
        Document.objects.link(
          document2,
          owner=document2.owner,
          name=document2.name,
          description=document2.description,
          extra=document.extra
        )

        document.add_tag(self.imported_tag)
        document.save()
        return document2
    except Exception, e:
      raise PopupException(_("Failed to convert Document object: %s") % e)
