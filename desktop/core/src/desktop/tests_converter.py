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

from nose.tools import assert_equal, assert_false, assert_true
from django.contrib.auth.models import User

from desktop.converters import DocumentConverter
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Directory, Document, Document2, DocumentPermission, Document2Permission, DocumentTag
from librdbms.design import SQLdesign

from beeswax.models import SavedQuery
from beeswax.design import hql_query
from pig.models import create_or_update_script, PigScript
from useradmin.models import get_default_user_group


class TestDocumentConverter(object):

  def setUp(self):
    self.client = make_logged_in_client(username="doc2", groupname="doc2", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="doc2")
    grant_access("doc2", "doc2", "beeswax")
    grant_access("doc2", "doc2", "pig")

    # This creates the user directories for the new user
    response = self.client.get('/desktop/api2/doc/')
    data = json.loads(response.content)
    assert_equal('/', data['document']['path'], data)

    self.home_dir = Document2.objects.get_home_directory(user=self.user)


  def test_convert_hive_query(self):
    sql = 'SELECT * FROM sample_07'
    settings = [
        {'key': 'hive.exec.scratchdir', 'value': '/tmp/mydir'},
        {'key': 'hive.querylog.location', 'value': '/tmp/doc2'}
    ]
    file_resources = [{'type': 'jar', 'path': '/tmp/doc2/test.jar'}]
    functions = [{'name': 'myUpper', 'class_name': 'org.hue.udf.MyUpper'}]
    design = hql_query(sql, settings=settings, file_resources=file_resources, functions=functions)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['hql'],
        owner=self.user,
        data=design.dumps(),
        name='Hive query',
        desc='Test Hive query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-hive').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-hive')

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])

      # Verify session type
      assert_equal('hive', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])

      # Verify snippet properties
      assert_equal(settings, doc2.data_dict['snippets'][0]['properties']['settings'])
      assert_equal(file_resources, doc2.data_dict['snippets'][0]['properties']['files'])
      assert_equal(functions, doc2.data_dict['snippets'][0]['properties']['functions'])
    finally:
      query.delete()


  def test_convert_impala_query(self):
    sql = 'SELECT * FROM sample_07'
    settings = [
        {'key': 'EXPLAIN_LEVEL', 'value': '2'},
        {'key': 'ABORT_ON_ERROR', 'value': '1'}
    ]
    design = hql_query(sql, settings=settings)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['impala'],
        owner=self.user,
        data=design.dumps(),
        name='Impala query',
        desc='Test Impala query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-impala').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-impala')

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])

      # Verify session type
      assert_equal('impala', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])

      # Verify snippet properties
      assert_equal(settings, doc2.data_dict['snippets'][0]['properties']['settings'])
    finally:
      query.delete()


  def test_convert_rdbms_query(self):
    sql = 'SELECT * FROM auth_user'
    data = {
        'query': {
            'query': sql,
            'server': 'sqlite',
            'type': 'rdbms',
            'database': 'desktop/desktop.db'
        },
        'VERSION': '0.0.1'
    }
    data_json = json.dumps(data)
    design = SQLdesign.loads(data_json)
    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['rdbms'],
        owner=self.user,
        data=design.dumps(),
        name='SQLite query',
        desc='Test SQLite query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-sqlite').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-sqlite')

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])

      # Verify session type
      assert_equal('sqlite', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])
    finally:
      query.delete()


  def test_convert_workflow(self):
    # TODO: write me
    pass


  def test_convert_pig_script(self):
    attrs = {
      'user': self.user,
      'id': 1000,
      'name': 'Test',
      'script': 'A = LOAD "$data"; STORE A INTO "$output";',
      'parameters': [],
      'resources': [],
      'hadoopProperties': []
    }
    pig_script = create_or_update_script(**attrs)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='link-pigscript').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='link-pigscript')

      # Verify absolute_url
      response = self.client.get(doc2.get_absolute_url())
      assert_equal(200, response.status_code)
    finally:
      pig_script.delete()


  def test_import_project(self):
    # Test that when importing a Document that is tagged with a project, we create a directory with that tag name and
    # place the document within it
    sql = 'SELECT * FROM sample_07'
    design = hql_query(sql)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['impala'],
        owner=self.user,
        data=design.dumps(),
        name='Impala query',
        desc='Test Impala query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)
    default_tag = DocumentTag.objects.get_default_tag(self.user)
    custom_tag = DocumentTag.objects.create_tag(self.user, 'sample_07')
    doc.add_tag(default_tag)
    doc.add_tag(custom_tag)

    try:
      converter = DocumentConverter(self.user)
      converter.convert()

      # Should have a directory named after custom tag
      assert_true(Directory.objects.filter(owner=self.user, name=custom_tag.tag, parent_directory=self.home_dir).exists())

      # But ignore reserved tags (default)
      assert_false(Directory.objects.filter(owner=self.user, name=default_tag.tag, parent_directory=self.home_dir).exists())

      # Document should exist under custom directory
      project_dir = Directory.objects.get(owner=self.user, name=custom_tag.tag, parent_directory=self.home_dir)
      assert_true(Document2.objects.filter(owner=self.user, name='Impala query', parent_directory=project_dir).exists())
    finally:
      query.delete()


  def test_import_permissions(self):
    make_logged_in_client(username="other_user", groupname="default", recreate=True, is_superuser=False)

    other_user = User.objects.get(username="other_user")
    test_group = get_default_user_group()

    # Test that when importing a Document with permissions, the corresponding permissions are created for the Doc2
    sql = 'SELECT * FROM sample_07'
    design = hql_query(sql)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['impala'],
        owner=self.user,
        data=design.dumps(),
        name='Impala query',
        desc='Test Impala query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)
    read_perm = DocumentPermission.objects.create(doc=doc, perms='read')
    read_perm.users.add(other_user)
    read_perm.groups.add(test_group)
    write_perm = DocumentPermission.objects.create(doc=doc, perms='write')
    write_perm.users.add(other_user)

    try:
      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, name=query.name)
      # Test that doc2 has same read permissions
      assert_true(other_user in doc2.get_permission('read').users.all())
      assert_true(test_group in doc2.get_permission('read').groups.all())
      # Test that doc2 has same write permissions
      assert_true(other_user in doc2.get_permission('write').users.all())
    finally:
      query.delete()
