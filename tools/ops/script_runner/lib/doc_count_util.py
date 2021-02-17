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
import re
import sys

from django.db import transaction

from desktop.models import Document, DocumentPermission, DocumentTag, Document2, Directory, Document2Permission

LOG = logging.getLogger(__name__)

class DocumentCounts(object):
  """
  Given a user, prints the count of doc1 and doc2 documents 
  """

  def __init__(self, user, differ=False):
    LOG.info("Sai")
    self.user = user
    self.differ = differ
    self.home_dir = Document2.objects.create_user_directories(self.user)
    sys.stdout = open('counts.txt', 'a')
    

  def printCounts(self):
    LOG.info("HI")
    # Convert SavedQuery documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery).filter(extra__in=[HQL, IMPALA, RDBMS])
      self.saved_query_doc1 = len(docs)

      docs = Document2.objects.filter(owner=self.user, type__startswith='query-').filter(is_history=False)
      self.saved_query_doc2 = len(docs)
    except:
      LOG.info('Cannot convert Saved Query documents: beeswax app is not installed')
      pass

    # Convert SQL Query history documents
    try:
      from beeswax.models import SavedQuery, HQL, IMPALA, RDBMS

      docs = self._get_unconverted_docs(SavedQuery, with_history=True).filter(extra__in=[HQL, IMPALA, RDBMS]).order_by('-last_modified')
      self.query_history_doc1 = len(docs)

      docs = Document2.objects.filter(owner=self.user,type__startswith='query-').filter(is_history=True)
      self.query_history_doc2 = len(docs)

    except:
      LOG.info('Cannot convert Saved Query documents: beeswax app is not installed')
      pass
    
    if self.differ:
      if self.saved_query_doc2 != self.saved_query_doc1 or self.query_history_doc2 != self.query_history_doc1:
        print("%-20s  %s/%s \t  %s/%s" %(self.user.username, self.saved_query_doc2, self.saved_query_doc1, self.query_history_doc2, self.query_history_doc1))
    else: 
      print("%-20s  %s/%s \t  %s/%s" %(self.user.username, self.saved_query_doc2, self.saved_query_doc1, self.query_history_doc2, self.query_history_doc1))
    sys.stdout.close()


  def _get_unconverted_docs(self, content_type, with_history=False):
    docs = Document.objects.get_docs(self.user, content_type).filter(owner=self.user)

    tags = [
      DocumentTag.objects.get_trash_tag(user=self.user), # No trashed docs
      DocumentTag.objects.get_example_tag(user=self.user), # No examples
#      self.imported_tag # No already imported docs
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
