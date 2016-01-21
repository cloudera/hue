#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from nose.tools import assert_equal, assert_true
from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import import_saved_beeswax_query, Directory, Document2

from beeswax.models import SavedQuery
from beeswax.design import hql_query



class TestDocument2(object):

  def setUp(self):
    self.client = make_logged_in_client(username="doc2", groupname="doc2", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="doc2")
    grant_access("doc2", "doc2", "beeswax")

    # Setup Home dir this way currently
    response = self.client.get('/desktop/api2/docs/')
    data = json.loads(response.content)

    assert_equal('/', data['path'], data)


  def test_document_create(self):
    sql = 'SELECT * FROM sample_07'

    design = hql_query(sql)

    # is_auto
    # is_trashed
    # is_redacted
    old_query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['hql'],
        owner=self.user,
        data=design.dumps(),
        name='See examples',
        desc='Example of old format'
    )

    try:
      new_query = import_saved_beeswax_query(old_query)
      new_query_data = new_query.get_data()

      assert_equal('query-hive', new_query_data['type'])
      assert_equal('See examples', new_query_data['name'])
      assert_equal('Example of old format', new_query_data['description'])

      assert_equal('ready', new_query_data['snippets'][0]['status'])
      assert_equal('See examples', new_query_data['snippets'][0]['name'])
      assert_equal('SELECT * FROM sample_07', new_query_data['snippets'][0]['statement_raw'])

      assert_equal([], new_query_data['snippets'][0]['properties']['settings'])
      assert_equal([], new_query_data['snippets'][0]['properties']['files'])
      assert_equal([], new_query_data['snippets'][0]['properties']['functions'])
    finally:
      old_query.delete()


  def test_directory_create(self):
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_path': json.dumps('/'), 'name': json.dumps('test_mkdir')})
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)


  def test_directory_move(self):
    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_path': json.dumps('/'), 'name': json.dumps('test_mv')})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    response = self.client.post('/desktop/api2/doc/mkdir', {'parent_path': json.dumps('/'), 'name': json.dumps('test_mv_dst')})
    data = json.loads(response.content)
    assert_equal(0, data['status'], data)

    response = self.client.post('/desktop/api2/doc/move', {
        'source_doc_id': json.dumps(Directory.objects.get(owner=self.user, name='/test_mv').id),
        'destination_doc_id': json.dumps(Directory.objects.get(owner=self.user, name='/test_mv_dst').id)
    })
    data = json.loads(response.content)

    assert_equal(0, data['status'], data)

    assert_true(Directory.objects.filter(owner=self.user, name='/test_mv_dst/test_mv').exists())


  def test_directory_documents(self):
    home_dir = Directory.objects.get(owner=self.user, name='/')

    dir1 = Directory.objects.create(name='/test_dir1', owner=self.user)
    dir2 = Directory.objects.create(name='/test_dir2', owner=self.user)
    query1 = Document2.objects.create(name='query1', type='query-hive', owner=self.user, data={})
    query2 = Document2.objects.create(name='query2', type='query-hive', owner=self.user, data={})
    children = [dir1, dir2, query1, query2]

    home_dir.dependencies.add(*children)

    # Test that all children directories and documents are returned
    documents, count = home_dir.documents()
    assert_equal(4, count, documents)

    # Test filter type
    documents, count = home_dir.documents(types=['directory'])
    assert_equal(2, count, documents)
    assert_true(all(doc.type == 'directory' for doc in documents))

    # Test search text
    documents, count = home_dir.documents(search_text='query')
    assert_equal(2, count, documents)
    assert_true(all(doc.name.startswith('query') for doc in documents))

    # Test pagination with limit
    documents, count = home_dir.documents(page=2, limit=2)
    assert_equal(4, count, documents)
    assert_equal(2, len(documents))
