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
import time

from django.db import transaction
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.models import Document, DocumentPermission, DocumentTag, Document2, Directory, Document2Permission
from notebook.api import _historify
from notebook.models import import_saved_beeswax_query, import_saved_java_job, import_saved_mapreduce_job, \
  import_saved_pig_script, import_saved_shell_job


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
    self.imported_doc_count = 0
    self.failed_doc_ids = []


  def convert(self):
    self._convert_saved_queries()

    self._convert_query_histories()

    self._convert_job_designs()

    self._convert_pig_scripts()

    # Add converted docs to root directory
    if self.imported_doc_count:
      LOG.info('Successfully imported %d documents for user: %s' % (self.imported_doc_count, self.user.username))

    # Log docs that failed to import
    if self.failed_doc_ids:
      LOG.error('Failed to import %d document(s) for user: %s - %s' % (len(self.failed_doc_ids), self.user.username, self.failed_doc_ids))

    # Set is_trashed field for old documents with is_trashed=None
    docs = Document2.objects.filter(owner=self.user, is_trashed=None).exclude(is_history=True)
    for doc in docs:
      try:
        if doc.path and doc.path != '/.Trash':
          doc_last_modified = doc.last_modified
          doc.is_trashed = doc.path.startswith('/.Trash')
          doc.save()

          # save() updates the last_modified to current time. Resetting it using update()
          Document2.objects.filter(id=doc.id).update(last_modified=doc_last_modified)
      except Exception, e:
        LOG.exception("Failed to set is_trashed field with exception: %s" % e)


  def _convert_saved_queries(self):
    # Convert SavedQuery documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery).filter(extra__in=[HQL, IMPALA, RDBMS])
      for doc in docs:
        try:
          if doc.content_object:
            notebook = import_saved_beeswax_query(doc.content_object)
            data = notebook.get_data()

            doc2 = self._create_doc2(
              document=doc,
              doctype=data['type'],
              name=data['name'],
              description=data['description'],
              data=notebook.get_json()
            )

            self.imported_doc_count += 1
        except Exception, e:
          self.failed_doc_ids.append(doc.id)
          LOG.exception('Failed to import SavedQuery document id: %d' % doc.id)
    except ImportError:
      LOG.warn('Cannot convert Saved Query documents: beeswax app is not installed')


  def _convert_query_histories(self):
    # Convert SQL Query history documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery, only_history=True).filter(extra__in=[HQL, IMPALA, RDBMS]).order_by(
        '-last_modified')

      for doc in docs:
        try:
          if doc.content_object:
            notebook = import_saved_beeswax_query(doc.content_object)
            data = notebook.get_data()

            data['isSaved'] = False
            data['snippets'][0]['lastExecuted'] = time.mktime(doc.last_modified.timetuple()) * 1000

            with transaction.atomic():
              doc2 = _historify(data, self.user)
              doc2.last_modified = doc.last_modified

              # save() updates the last_modified to current time. Resetting it using update()
              doc2.save()
              Document2.objects.filter(id=doc2.id).update(last_modified=doc.last_modified)

              self.imported_doc_count += 1

              doc.add_tag(self.imported_tag)
              doc.save()
        except Exception, e:
          self.failed_doc_ids.append(doc.id)
          LOG.exception('Failed to import history document id: %d' % doc.id)
    except ImportError, e:
      LOG.warn('Cannot convert history documents: beeswax app is not installed')


  def _convert_job_designs(self):
    # Convert Job Designer documents
    try:
      from oozie.models import Workflow

      docs = self._get_unconverted_docs(Workflow)
      for doc in docs:
        try:
          if doc.content_object:
            node = doc.content_object.start.get_child('to')
            notebook = None

            if node.node_type == 'mapreduce':
              notebook = import_saved_mapreduce_job(doc.content_object)
            elif node.node_type == 'shell':
              notebook = import_saved_shell_job(doc.content_object)
            elif node.node_type == 'java':
              notebook = import_saved_java_job(doc.content_object)

            if notebook:
              data = notebook.get_data()
              doc2 = self._create_doc2(
                document=doc,
                doctype=data['type'],
                name=doc.name,
                description=data['description'],
                data=notebook.get_json()
              )
            else:
              data = doc.content_object.data_dict
              data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
              doc2 = self._create_doc2(
                document=doc,
                doctype='link-workflow',
                name=doc.name,
                description=doc.description,
                data=json.dumps(data)
              )
            self.imported_doc_count += 1
        except Exception, e:
          self.failed_doc_ids.append(doc.id)
          LOG.exception('Failed to import Job Designer document id: %d' % doc.id)
    except ImportError, e:
      LOG.warn('Cannot convert Job Designer documents: oozie app is not installed')


  def _convert_pig_scripts(self):
    # Convert PigScript documents
    try:
      from pig.models import PigScript

      docs = self._get_unconverted_docs(PigScript)

      for doc in docs:
        try:
          if doc.content_object:
            notebook = import_saved_pig_script(doc.content_object)
            data = notebook.get_data()

            doc2 = self._create_doc2(
              document=doc,
              doctype=data['type'],
              name=data['name'],
              description=data['description'],
              data=notebook.get_json()
            )

            self.imported_doc_count += 1
        except Exception, e:
          self.failed_doc_ids.append(doc.id)
          LOG.exception('Failed to import Pig document id: %d' % doc.id)
    except ImportError, e:
      LOG.warn('Cannot convert Pig documents: pig app is not installed')


  def _get_unconverted_docs(self, content_type, only_history=False):
    docs = Document.objects.get_docs(self.user, content_type).filter(owner=self.user)

    tags = [
      DocumentTag.objects.get_trash_tag(user=self.user),  # No trashed docs
      DocumentTag.objects.get_example_tag(user=self.user),  # No examples
      self.imported_tag  # No already imported docs
    ]

    if only_history:
      docs = docs.filter(tags__in=[DocumentTag.objects.get_history_tag(user=self.user)])
    else:  # Exclude history docs by default
      tags.append(DocumentTag.objects.get_history_tag(user=self.user))

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
      document2 = None
      with transaction.atomic():
        name = name if name else document.name

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

        # save() updates the last_modified to current time. Resetting it using update()
        Document2.objects.filter(id=document2.id).update(last_modified=document.last_modified)

        document.add_tag(self.imported_tag)
        document.save()
        return document2
    except Exception, e:
      # Just to be sure we delete Doc2 object incase of exception.
      # Possible when there are mixed InnoDB and MyISAM tables
      if document2 and Document2.objects.filter(id=document2.id).exists():
        document2.delete()
      raise PopupException(_("Failed to convert Document object: %s") % e)
