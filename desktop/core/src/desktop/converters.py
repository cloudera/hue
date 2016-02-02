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

from django.db import transaction

from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS
from desktop.models import Document2, Document, Directory, DocumentTag, FilesystemException, import_saved_beeswax_query
from oozie.models import Workflow
from pig.models import PigScript


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
    docs = self._get_unconverted_docs(SavedQuery).filter(extra__in=[HQL, IMPALA, RDBMS])
    for doc in docs:
      if doc.content_object:
        notebook = import_saved_beeswax_query(doc.content_object)
        data = notebook.get_data()
        doc2 = self._create_doc2(
            document=doc,
            parent=self._get_parent_directory(doc),
            name=data['name'],
            doctype=data['type'],
            description=data['description'],
            data=notebook.get_json()
        )
        self.imported_docs.append(doc2)

    # Convert Workflow documents
    docs = self._get_unconverted_docs(Workflow)
    for doc in docs:
      if doc.content_object:
        data = doc.content_object.data_dict
        data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
        doc2 = self._create_doc2(
            document=doc,
            parent=self._get_parent_directory(doc),
            name=doc.name,
            doctype='link-workflow',
            description=doc.description,
            data=json.dumps(data)
        )
        self.imported_docs.append(doc2)

    # Convert PigScript documents
    docs = self._get_unconverted_docs(PigScript)
    for doc in docs:
      if doc.content_object:
        data = doc.content_object.dict
        data.update({'content_type': doc.content_type.model, 'object_id': doc.object_id})
        doc2 = self._create_doc2(
            document=doc,
            parent=self._get_parent_directory(doc),
            name=doc.name,
            doctype='link-pigscript',
            description=doc.description,
            data=json.dumps(data)
        )
        self.imported_docs.append(doc2)

    # Add converted docs to root directory
    if self.imported_docs:
      LOG.info('Successfully imported %d documents' % len(self.imported_docs))


  def _get_unconverted_docs(self, content_type):
    docs = Document.objects.get_docs(self.user, content_type).filter(owner=self.user)
    docs = docs.exclude(tags__in=[
      DocumentTag.objects.get_trash_tag(user=self.user), # No trashed docs
      DocumentTag.objects.get_history_tag(user=self.user), # No history yet
      DocumentTag.objects.get_example_tag(user=self.user), # No examples
      self.imported_tag # No already imported docs
    ])
    return docs


  def _get_parent_directory(self, document):
    parent_dir = self.home_dir
    project_tags = document.tags.exclude(tag__in=DocumentTag.RESERVED)
    if project_tags.exists():
      first_tag = project_tags[0]
      parent_dir = Directory.objects.get_or_create(owner=self.user, name=first_tag.tag, parent_directory=self.home_dir)
    return parent_dir


  def _create_doc2(self, document, parent, name, doctype, description=None, data=None):
    with transaction.atomic():
      doc2 = Document2.objects.create(
        owner=self.user,
        parent_directory=parent,
        name=name,
        type=doctype,
        description=description,
        data=data
      )
      document.add_tag(self.imported_tag)
      document.save()
      return doc2
