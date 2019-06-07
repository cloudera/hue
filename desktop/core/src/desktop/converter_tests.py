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

from datetime import datetime
import json

from nose.tools import assert_equal, assert_false, assert_true
from django.contrib.auth.models import User

from desktop.converters import DocumentConverter
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Directory, Document, Document2, DocumentPermission, DocumentTag
from librdbms.design import SQLdesign

from beeswax.models import SavedQuery
from beeswax.design import hql_query
from oozie.models import Link, Workflow
from oozie.tests import add_node
from pig.models import create_or_update_script
from useradmin.models import get_default_user_group


class TestDocumentConverter(object):

  def setUp(self):
    self.client = make_logged_in_client(username="doc2", groupname="doc2", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="doc2")
    grant_access("doc2", "doc2", "beeswax")
    grant_access("doc2", "doc2", "pig")
    grant_access("doc2", "doc2", "jobsub")

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
    design = hql_query(sql, database='etl', settings=settings, file_resources=file_resources, functions=functions)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['hql'],
        owner=self.user,
        data=design.dumps(),
        name='Hive query',
        desc='Test Hive query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    # Setting doc.last_modified to older date
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    query2 = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['hql'],
        owner=self.user,
        data=design.dumps(),
        name='Hive query history',
        desc='Test Hive query history',
        is_auto=True
    )
    doch = Document.objects.link(query2, owner=query2.owner, extra=query2.type, name=query2.name, description=query2.desc)
    doch.add_to_history()

    try:
      # Test that corresponding doc2 is created after convert
      assert_equal(0, Document2.objects.filter(owner=self.user, type='query-hive').count())

      converter = DocumentConverter(self.user)
      converter.convert()

      assert_equal(2, Document2.objects.filter(owner=self.user, type='query-hive').count())

      #
      # Query
      #
      doc2 = Document2.objects.get(owner=self.user, type='query-hive', is_history=False)

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])

      # Verify session type
      assert_equal('hive', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])
      assert_equal('etl', doc2.data_dict['snippets'][0]['database'])

      # Verify snippet properties
      assert_equal(settings, doc2.data_dict['snippets'][0]['properties']['settings'])
      assert_equal(file_resources, doc2.data_dict['snippets'][0]['properties']['files'])
      assert_equal(functions, doc2.data_dict['snippets'][0]['properties']['functions'])

      # Verify default properties
      assert_true(doc2.data_dict['isSaved'])
      assert_equal(doc.last_modified.strftime('%Y-%m-%dT%H:%M:%S'), doc2.last_modified.strftime('%Y-%m-%dT%H:%M:%S'))

      #
      # Query History
      #
      doc2 = Document2.objects.get(owner=self.user, type='query-hive', is_history=True)

      # Verify Document2 attributes
      assert_equal(doch.name, doc2.data_dict['name'])
      assert_equal(doch.description, doc2.data_dict['description'])
      assert_equal(doch.last_modified.strftime('%Y-%m-%dT%H:%M:%S'), doc2.last_modified.strftime('%Y-%m-%dT%H:%M:%S'))

      # Verify session type
      assert_false(doc2.data_dict['sessions'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])
      assert_equal('etl', doc2.data_dict['snippets'][0]['database'])

      # Verify snippet properties
      assert_equal(settings, doc2.data_dict['snippets'][0]['properties']['settings'])
      assert_equal(file_resources, doc2.data_dict['snippets'][0]['properties']['files'])
      assert_equal(functions, doc2.data_dict['snippets'][0]['properties']['functions'])

      # Verify default properties
      assert_false(doc2.data_dict['isSaved'])


      #
      # Check that we don't re-import again
      #
      converter = DocumentConverter(self.user)
      converter.convert()

      assert_equal(2, Document2.objects.filter(owner=self.user, type='query-hive').count())
    finally:
      query.delete()
      query2.delete()


  def test_convert_hive_query_with_special_chars(self):
    sql = 'SELECT * FROM sample_07'
    settings = [
      {'key': 'hive.exec.scratchdir', 'value': '/tmp/mydir'},
      {'key': 'hive.querylog.location', 'value': '/tmp/doc2'}
    ]
    file_resources = [{'type': 'jar', 'path': '/tmp/doc2/test.jar'}]
    functions = [{'name': 'myUpper', 'class_name': 'org.hue.udf.MyUpper'}]
    design = hql_query(sql, database='etl', settings=settings, file_resources=file_resources, functions=functions)

    query = SavedQuery.objects.create(
      type=SavedQuery.TYPES_MAPPING['hql'],
      owner=self.user,
      data=design.dumps(),
      name='Test / Hive query',
      desc='Test Hive query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    try:
      # Test that corresponding doc2 is created after convert
      assert_equal(0, Document2.objects.filter(owner=self.user, type='query-hive').count())

      converter = DocumentConverter(self.user)
      converter.convert()

      assert_equal(1, Document2.objects.filter(owner=self.user, type='query-hive').count())

      doc2 = Document2.objects.get(owner=self.user, type='query-hive', is_history=False)

      # Verify name is maintained
      assert_equal('Test / Hive query', doc2.name)

      # Verify Document2 path is stripped of invalid chars
      assert_equal('/Test%20/%20Hive%20query', doc2.path)
    finally:
      query.delete()


  def test_convert_impala_query(self):
    sql = 'SELECT * FROM sample_07'
    settings = [
        {'key': 'EXPLAIN_LEVEL', 'value': '2'},
        {'key': 'ABORT_ON_ERROR', 'value': '1'}
    ]
    design = hql_query(sql, database='etl', settings=settings)

    query = SavedQuery.objects.create(
        type=SavedQuery.TYPES_MAPPING['impala'],
        owner=self.user,
        data=design.dumps(),
        name='Impala query',
        desc='Test Impala query'
    )
    doc = Document.objects.link(query, owner=query.owner, extra=query.type, name=query.name, description=query.desc)

    # Setting doc.last_modified to older date
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-impala').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-impala')

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])
      assert_equal(doc.last_modified.strftime('%Y-%m-%dT%H:%M:%S'), doc2.last_modified.strftime('%Y-%m-%dT%H:%M:%S'))

      # Verify session type
      assert_equal('impala', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])
      assert_equal('etl', doc2.data_dict['snippets'][0]['database'])

      # Verify snippet properties
      assert_equal(settings, doc2.data_dict['snippets'][0]['properties']['settings'])

      # Verify default properties
      assert_true(doc2.data_dict['isSaved'])
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

    # Setting doc.last_modified to older date
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-sqlite').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-sqlite')

      # Verify Document2 attributes
      assert_equal(doc.name, doc2.data_dict['name'])
      assert_equal(doc.description, doc2.data_dict['description'])
      assert_equal(doc.last_modified.strftime('%Y-%m-%dT%H:%M:%S'), doc2.last_modified.strftime('%Y-%m-%dT%H:%M:%S'))

      # Verify session type
      assert_equal('sqlite', doc2.data_dict['sessions'][0]['type'])

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement'])
      assert_equal(sql, doc2.data_dict['snippets'][0]['statement_raw'])
    finally:
      query.delete()


  def test_convert_mapreduce(self):
    wf = Workflow.objects.new_workflow(self.user)
    wf.save()
    Workflow.objects.initialize(wf)
    Link.objects.filter(parent__workflow=wf).delete()
    action = add_node(wf, 'action-name-1', 'mapreduce', [wf.start], {
      'description': 'Test MR job design',
      'files': '[]',
      'jar_path': '/user/hue/oozie/examples/lib/hadoop-examples.jar',
      'job_properties': '[{"name": "sleep.job.map.sleep.time", "value": "5"}, {"name": "sleep.job.reduce.sleep.time", "value": "10"}]',
      'prepares': '[{"value":"${output}","type":"delete"},{"value":"/test","type":"mkdir"}]',
      'archives': '[]',
    })
    Link(parent=action, child=wf.end, name="ok").save()

    # Setting doc.last_modified to older date
    doc = Document.objects.get(id=wf.doc.get().id)
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-mapreduce').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-mapreduce')

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal('/user/hue/oozie/examples/lib/hadoop-examples.jar', doc2.data_dict['snippets'][0]['properties']['app_jar'])
      assert_equal(['sleep.job.map.sleep.time=5', 'sleep.job.reduce.sleep.time=10'], doc2.data_dict['snippets'][0]['properties']['hadoopProperties'])
    finally:
      wf.delete()


  def test_convert_shell(self):
    wf = Workflow.objects.new_workflow(self.user)
    wf.save()
    Workflow.objects.initialize(wf)
    Link.objects.filter(parent__workflow=wf).delete()
    action = add_node(wf, 'action-name-1', 'shell', [wf.start], {
      u'job_xml': 'my-job.xml',
      u'files': '["hello.py"]',
      u'name': 'Shell',
      u'job_properties': '[{"name": "mapred.job.queue.name", "value": "test"}]',
      u'capture_output': True,
      u'command': 'hello.py',
      u'archives': '[{"dummy": "", "name": "test.zip"}]',
      u'prepares': '[]',
      u'params': '[{"type": "argument", "value": "baz"}, {"type": "env-var", "value": "foo=bar"}]',
      u'description': 'Execute a Python script printing its arguments'
    })
    Link(parent=action, child=wf.end, name="ok").save()

    # Setting doc.last_modified to older date
    doc = Document.objects.get(id=wf.doc.get().id)
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-shell').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-shell')

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal('hello.py', doc2.data_dict['snippets'][0]['properties']['command_path'])
      assert_equal(['baz'], doc2.data_dict['snippets'][0]['properties']['arguments'])
      assert_equal(['foo=bar'], doc2.data_dict['snippets'][0]['properties']['env_var'])
      assert_equal(['mapred.job.queue.name=test'], doc2.data_dict['snippets'][0]['properties']['hadoopProperties'])
      assert_equal(['test.zip'], doc2.data_dict['snippets'][0]['properties']['archives'])
      assert_equal([{'type': 'file', 'path': 'hello.py'}], doc2.data_dict['snippets'][0]['properties']['files'])
      assert_equal(True, doc2.data_dict['snippets'][0]['properties']['capture_output'])
    finally:
      wf.delete()


  def test_convert_java(self):
    wf = Workflow.objects.new_workflow(self.user)
    wf.save()
    Workflow.objects.initialize(wf)
    Link.objects.filter(parent__workflow=wf).delete()
    action = add_node(wf, 'action-name-1', 'java', [wf.start], {
      'name': 'MyTeragen',
      "description": "Generate N number of records",
      "main_class": "org.apache.hadoop.examples.terasort.TeraGen",
      "args": "1000 ${output_dir}/teragen",
      "files": '["my_file","my_file2"]',
      "job_xml": "",
      "java_opts": "-Dexample-property=natty",
      "jar_path": "/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
      'job_properties': '[{"name": "mapred.job.queue.name", "value": "test"}]',
      "prepares": '[{"value":"/test","type":"mkdir"}]',
      "archives": '[{"dummy":"","name":"my_archive"},{"dummy":"","name":"my_archive2"}]',
      "capture_output": True,
    })
    Link(parent=action, child=wf.end, name="ok").save()

    # Setting doc.last_modified to older date
    doc = Document.objects.get(id=wf.doc.get().id)
    Document.objects.filter(id=doc.id).update(
      last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-java').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-java')

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal('/user/hue/oozie/workspaces/lib/hadoop-examples.jar', doc2.data_dict['snippets'][0]['properties']['app_jar'])
      assert_equal('org.apache.hadoop.examples.terasort.TeraGen', doc2.data_dict['snippets'][0]['properties']['class'])
      assert_equal('1000 ${output_dir}/teragen', doc2.data_dict['snippets'][0]['properties']['args'])
      assert_equal('-Dexample-property=natty', doc2.data_dict['snippets'][0]['properties']['java_opts'])
      assert_equal(['mapred.job.queue.name=test'], doc2.data_dict['snippets'][0]['properties']['hadoopProperties'])
      assert_equal(['my_archive', 'my_archive2'], doc2.data_dict['snippets'][0]['properties']['archives'])
      assert_equal([{'type': 'file', 'path': 'my_file'}, {'type': 'file', 'path': 'my_file2'}], doc2.data_dict['snippets'][0]['properties']['files'])
      assert_equal(True, doc2.data_dict['snippets'][0]['properties']['capture_output'])
    finally:
      wf.delete()


  def test_convert_pig_script(self):
    attrs = {
      'user': self.user,
      'id': 1000,
      'name': 'Test',
      'script': 'A = LOAD "$data"; STORE A INTO "$output";',
      'hadoopProperties': [
        {u'name': u'mapred.job.queue.name', u'value': u'pig'},
        {u'name': u'mapreduce.task.profile', u'value': u'true'}
      ],
      'parameters': [
        {u'name': u'input', u'value': u'/user/test/data'},
        {u'name': u'verbose', u'value': u'true'}
      ],
      'resources': [
        {u'type': u'file', u'value': u'/user/test/test.txt'},
        {u'type': u'archive', u'value': u'/user/test/test.jar'}
      ],
    }
    pig_script = create_or_update_script(**attrs)
    pig_script.save()

    # Setting doc.last_modified to older date
    doc = Document.objects.get(id=pig_script.doc.get().id)
    Document.objects.filter(id=doc.id).update(last_modified=datetime.strptime('2000-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ'))
    doc = Document.objects.get(id=doc.id)

    try:
      # Test that corresponding doc2 is created after convert
      assert_false(Document2.objects.filter(owner=self.user, type='query-pig').exists())

      converter = DocumentConverter(self.user)
      converter.convert()

      doc2 = Document2.objects.get(owner=self.user, type='query-pig')

      # Verify snippet values
      assert_equal('ready', doc2.data_dict['snippets'][0]['status'])
      assert_equal(attrs['script'], doc2.data_dict['snippets'][0]['statement'], doc2.data_dict)
      assert_equal(attrs['script'], doc2.data_dict['snippets'][0]['statement_raw'])
      assert_equal(['mapred.job.queue.name=pig', 'mapreduce.task.profile=true'], doc2.data_dict['snippets'][0]['properties']['hadoopProperties'])
      assert_equal(['input=/user/test/data', 'verbose=true'], doc2.data_dict['snippets'][0]['properties']['parameters'])
      assert_equal(['/user/test/test.txt', '/user/test/test.jar'], doc2.data_dict['snippets'][0]['properties']['resources'])
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
