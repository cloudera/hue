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

import re
import json
from builtins import object
from unittest.mock import MagicMock, Mock, patch

import pytest

from beeswax.conf import HIVE_SERVER_HOST
from desktop.api2 import _setup_hive_impala_examples, _setup_notebook_examples, _setup_search_examples, install_app_examples
from desktop.conf import ENABLE_GIST_PREVIEW
from desktop.lib.django_test_util import make_logged_in_client
from desktop.models import Directory, Document2
from useradmin.models import User, get_default_user_group


@pytest.mark.django_db
class TestApi2(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="api2_user", groupname="default", recreate=True, is_superuser=False)
    self.user = User.objects.get(username="api2_user")

  def test_import_document_with_forward_ref(self, client=None):
    if client is None:
      client = self.client

    doc = '''[
{
  "model": "desktop.document2",
  "pk": 20,
  "fields": {
    "owner": [
      "admin"
    ],
    "name": "schd1",
    "description": "",
    "uuid": "fa08942c-edf7-f712-921f-c0fb891d1fc4",
    "type": "oozie-coordinator2",
    "connector": null,
    "data": "{}",
    "extra": "",
    "search": null,
    "last_modified": "2023-01-05T23:08:44.548",
    "version": 1,
    "is_history": false,
    "is_managed": false,
    "is_trashed": false,
    "parent_directory": [
      "117db535-78b6-42e5-92bf-dbafcae015a7",
      1,
      false
    ],
    "dependencies": [
      [
        "92a7dd47-d8c8-b2d8-2895-440ccbc94198",
        1,
        false
      ]
    ]
  }
},
{
  "model": "desktop.document2",
  "pk": 21,
  "fields": {
    "owner": [
      "admin"
    ],
    "name": "wf2",
    "description": "",
    "uuid": "92a7dd47-d8c8-b2d8-2895-440ccbc94198",
    "type": "oozie-workflow2",
    "connector": null,
    "data": "{}",
    "extra": "",
    "search": null,
    "last_modified": "2023-01-05T23:08:27.853",
    "version": 1,
    "is_history": false,
    "is_managed": false,
    "is_trashed": false,
    "parent_directory": [
      "117db535-78b6-42e5-92bf-dbafcae015a7",
      1,
      false
    ],
    "dependencies": []
  }
}
]'''

    response = client.post("/desktop/api2/doc/import", {'documents': json.dumps(doc)})
    status = json.loads(response.content)['status']
    assert status == 0

  def test_search_entities_interactive_xss(self):
    query = Document2.objects.create(
      name='<script>alert(5)</script>', description='<script>alert(5)</script>', type='query-hive', owner=self.user
    )

    try:
      response = self.client.post(
        '/desktop/api/search/entities_interactive/', data={'sources': json.dumps(['documents']), 'query_s': json.dumps('alert')}
      )
      results = json.loads(response.content)['results']
      assert results
      result_json = json.dumps(results)
      assert not re.match('<(?!em)', result_json), result_json
      assert not re.match('(?!em)>', result_json), result_json
      assert '<script>' not in result_json, result_json
      assert '</script>' not in result_json, result_json
      assert '&lt;' in result_json, result_json
      assert '&gt;' in result_json, result_json
    finally:
      query.delete()

  def test_get_hue_config(self):
    client = make_logged_in_client(username="api2_superuser", groupname="default", recreate=True, is_superuser=True)
    user = User.objects.get(username="api2_superuser")

    response = client.get('/desktop/api2/get_hue_config', data={})

    # It should have multiple config sections in json
    config = json.loads(response.content)['config']
    assert len(config) > 1

    # It should only allow superusers
    client_not_me = make_logged_in_client(username='not_me', is_superuser=False, groupname='test')

    response = client_not_me.get('/desktop/api2/get_hue_config', data={})
    assert b"You must be a superuser" in response.content, response.content

    # It should contain a config parameter
    CANARY = b"abracadabra"
    clear = HIVE_SERVER_HOST.set_for_testing(CANARY)
    try:
      response = client.get('/desktop/api2/get_hue_config', data={})
      assert CANARY in response.content, response.content
    finally:
      clear()

  def test_get_hue_config_private(self):
    client = make_logged_in_client(username="api2_superuser", groupname="default", recreate=True, is_superuser=True)
    user = User.objects.get(username="api2_superuser")

    # Not showing private if not asked for
    response = client.get('/desktop/api2/get_hue_config', data={})
    assert b'bind_password' not in response.content

    # Masking passwords if private
    private_response = client.get('/desktop/api2/get_hue_config', data={'private': True})
    assert b'bind_password' in private_response.content
    config_json = json.loads(private_response.content)
    desktop_config = [conf for conf in config_json['config'] if conf['key'] == 'desktop']
    ldap_desktop_config = [val for conf in desktop_config for val in conf['values'] if val['key'] == 'ldap']
    assert any(val['value'] == '**********' for conf in ldap_desktop_config for val in conf['values'] if val['key'] == 'bind_password'), (
      ldap_desktop_config
    )

    # There should be more private than non-private
    assert len(response.content) < len(private_response.content)

  def test_url_password_hiding(self):
    client = make_logged_in_client(username="api2_superuser", groupname="default", recreate=True, is_superuser=True)
    user = User.objects.get(username="api2_superuser")

    data_to_escape = b"protocol://user:very_secret_password@host:1234/some/url"
    clear = HIVE_SERVER_HOST.set_for_testing(data_to_escape)
    try:
      response = client.get('/desktop/api2/get_hue_config', data={})
      assert b"protocol://user:**********@host:1234/some/url" in response.content, response.content
    finally:
      clear()

  def test_get_config(self):
    response = self.client.get('/desktop/api2/get_config')

    assert 200 == response.status_code
    config = json.loads(response.content)

    assert 'types' in config['documents']
    assert 'is_admin' in config['hue_config']
    assert 'is_yarn_enabled' in config['hue_config']
    assert 'query-TestApi2.test_get_config' not in config['documents']['types'], config

    doc = Document2.objects.create(name='Query xxx', type='query-TestApi2.test_get_config', owner=self.user)
    doc2 = Document2.objects.create(name='Query xxx 2', type='query-TestApi2.test_get_config', owner=self.user)

    try:
      response = self.client.get('/desktop/api2/get_config')

      assert 200 == response.status_code
      config = json.loads(response.content)

      assert 'query-TestApi2.test_get_config' in config['documents']['types'], config
      assert 1 == len([t for t in config['documents']['types'] if t == 'query-TestApi2.test_get_config'])
    finally:
      doc.delete()


@pytest.mark.django_db
class TestDocumentApiSharingPermissions(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

  def _add_doc(self, name):
    return Document2.objects.create(name=name, type='query-hive', owner=self.user)

  def share_doc(self, doc, permissions, client=None):
    if client is None:
      client = self.client

    return client.post("/desktop/api2/doc/share", {'uuid': json.dumps(doc.uuid), 'data': json.dumps(permissions)})

  def share_link_doc(self, doc, perm, client=None):
    if client is None:
      client = self.client

    return client.post("/desktop/api2/doc/share/link", {'uuid': json.dumps(doc.uuid), 'perm': json.dumps(perm)})

  def test_update_permissions(self):
    doc = self._add_doc('test_update_permissions')

    response = self.share_doc(doc, {'read': {'user_ids': [self.user_not_me.id], 'group_ids': []}})

    assert 0 == json.loads(response.content)['status'], response.content

  def test_share_document_permissions(self):
    # No doc
    response = self.client.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    # Add doc
    doc = self._add_doc('test_update_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    # Share by user
    response = self.share_doc(
      doc, {'read': {'user_ids': [self.user_not_me.id], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}}
    )

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    # Un-share
    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    # Share by group
    default_group = get_default_user_group()

    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': [default_group.id]}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    # Un-share
    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    # Modify by other user
    response = self.share_doc(
      doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [self.user_not_me.id], 'group_ids': []}}
    )

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    # Un-share
    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

    # Modify by group
    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': [default_group.id]}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    # Un-share
    response = self.share_doc(doc, {'read': {'user_ids': [], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}})

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert not json.loads(response.content)['documents']

  def test_update_permissions_cannot_escalate_privileges(self):
    doc = self._add_doc('test_update_permissions_cannot_escape_privileges')

    # Share read permissions
    response = self.share_doc(
      doc, {'read': {'user_ids': [self.user_not_me.id], 'group_ids': []}, 'write': {'user_ids': [], 'group_ids': []}}
    )

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    # Try, and fail to escalate privileges.
    response = self.share_doc(
      doc,
      {
        'read': {'user_ids': [self.user_not_me.id], 'group_ids': []},
        'write': {
          'user_ids': [
            self.user_not_me.id,
          ],
          'group_ids': [],
        },
      },
      self.client_not_me,
    )

    content = json.loads(response.content)
    assert content['status'] == -1
    assert "Document does not exist or you don't have the permission to access it." in content['message'], content['message']

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

  def test_link_sharing_permissions(self):
    # Add doc
    doc = self._add_doc('test_link_sharing_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert -1 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    # Share by read link
    response = self.share_link_doc(doc, perm='read')

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)

    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']  # Link sharing does not list docs in Home, only provides direct access

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    # Un-share
    response = self.share_link_doc(doc, perm='off')

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert -1 == json.loads(response.content)['status'], response.content

    # Share by write link
    response = self.share_link_doc(doc, perm='write')

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert doc.can_read(self.user_not_me)
    assert doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    # Demote to read link
    response = self.share_link_doc(doc, perm='read')

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)

    assert doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)  # Back to false

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']  # Link sharing does not list docs in Home, only provides direct access

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    # Un-share
    response = self.share_link_doc(doc, perm='off')

    assert 0 == json.loads(response.content)['status'], response.content

    assert doc.can_read(self.user)
    assert doc.can_write(self.user)
    assert not doc.can_read(self.user_not_me)
    assert not doc.can_write(self.user_not_me)

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert json.loads(response.content)['documents']

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert not json.loads(response.content)['documents']

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert 0 == json.loads(response.content)['status'], response.content

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert -1 == json.loads(response.content)['status'], response.content


@pytest.mark.django_db
class TestDocumentGist(object):
  def setup_method(self):
    self.client = make_logged_in_client(username="gist_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="other_gist_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="gist_user")
    self.user_not_me = User.objects.get(username="other_gist_user")

  def _create_gist(self, statement, doc_type, name='', description='', client=None):
    if client is None:
      client = self.client

    return client.post(
      "/desktop/api2/gist/create",
      {
        'statement': statement,
        'doc_type': doc_type,
        'name': name,
        'description': description,
      },
    )

  def _get_gist(self, uuid, client=None, is_crawler_bot=False):
    if client is None:
      client = self.client

    if is_crawler_bot:
      headers = {'HTTP_USER_AGENT': 'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)'}
    else:
      headers = {}

    return client.get(
      "/desktop/api2/gist/open",
      {
        'uuid': uuid,
      },
      **headers,
    )

  def test_create(self):
    assert not Document2.objects.filter(type='gist', name='test_gist_create')

    response = self._create_gist(
      statement='SELECT 1',
      doc_type='hive-query',
      name='test_gist_create',
    )
    gist = json.loads(response.content)

    assert Document2.objects.filter(type='gist', name='test_gist_create')
    assert Document2.objects.filter(type='gist', uuid=gist['uuid'])
    assert 'SELECT 1' == json.loads(Document2.objects.get(type='gist', uuid=gist['uuid']).data)['statement_raw']

    response2 = self._create_gist(
      statement='SELECT 2',
      doc_type='hive-query',
      name='test_gist_create2',
    )
    gist2 = json.loads(response2.content)

    assert Document2.objects.filter(type='gist', name='test_gist_create2')
    assert Document2.objects.filter(type='gist', uuid=gist2['uuid'])
    assert 'SELECT 2' == json.loads(Document2.objects.get(type='gist', uuid=gist2['uuid']).data)['statement_raw']

  def test_multiple_gist_dirs_on_gist_create(self):
    home_dir = Directory.objects.get_home_directory(self.user)

    gist_dir1 = Directory.objects.create(name=Document2.GIST_DIR, owner=self.user, parent_directory=home_dir)
    gist_dir2 = Directory.objects.create(name=Document2.GIST_DIR, owner=self.user, parent_directory=home_dir)
    gist_child = Document2.objects.create(
      name='test_gist_child',
      data=json.dumps({'statement': 'SELECT 123'}),
      owner=self.user,
      type='gist',
      parent_directory=gist_dir2,
    )

    assert 2 == Directory.objects.filter(name=Document2.GIST_DIR, type='directory', owner=self.user).count()

    # get_gist_directory merges all duplicate gist directories into one
    response = self._create_gist(
      statement='SELECT 12345',
      doc_type='hive-query',
      name='test_gist_create',
    )
    gist_uuid = json.loads(response.content)['uuid']
    gist_home = Document2.objects.get(uuid=gist_uuid).parent_directory

    assert 1 == Directory.objects.filter(name=Document2.GIST_DIR, type='directory', owner=self.user).count()
    assert Directory.objects.filter(name=Document2.GIST_DIR, type='directory', uuid=gist_home.uuid).exists()
    assert gist_dir1.uuid == gist_home.uuid
    assert Document2.objects.get(name='test_gist_child', type='gist', owner=self.user).parent_directory == gist_home

  def test_get(self):
    response = self._create_gist(
      statement='SELECT 1',
      doc_type='hive-query',
      name='test_gist_get',
    )
    gist = json.loads(response.content)

    response = self._get_gist(uuid=gist['uuid'])
    assert 302 == response.status_code
    assert '/hue/editor?gist=%(uuid)s&type=hive-query' % gist == response.url

    response = self._get_gist(uuid=gist['uuid'], client=self.client_not_me)
    assert 302 == response.status_code
    assert '/hue/editor?gist=%(uuid)s&type=hive-query' % gist == response.url

  def test_gist_directory_creation(self):
    home_dir = Directory.objects.get_home_directory(self.user)

    assert not home_dir.children.filter(name=Document2.GIST_DIR, owner=self.user).exists()

    Document2.objects.get_gist_directory(self.user)

    assert home_dir.children.filter(name=Document2.GIST_DIR, owner=self.user).exists()

  def test_get_unfurl(self):
    # Unfurling on
    f = ENABLE_GIST_PREVIEW.set_for_testing(True)

    try:
      response = self._create_gist(
        statement='SELECT 1',
        doc_type='hive-query',
        name='test_gist_get',
      )
      gist = json.loads(response.content)

      response = self._get_gist(uuid=gist['uuid'], is_crawler_bot=True)

      assert 200 == response.status_code
      assert b'<meta name="twitter:card" content="summary">' in response.content, response.content
      assert b'<meta property="og:description" content="SELECT 1"/>' in response.content, response.content
    finally:
      f()

    # Unfurling off
    f = ENABLE_GIST_PREVIEW.set_for_testing(False)

    try:
      response = self._get_gist(uuid=gist['uuid'], is_crawler_bot=True)

      assert 302 == response.status_code
      assert '/hue/editor?gist=%(uuid)s&type=hive-query' % gist == response.url
    finally:
      f()


class TestInstallAppExampleAPI:
  def test_install_app_examples_missing_app_name(self):
    request = Mock(method='POST', POST={}, user=Mock())
    response = install_app_examples(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing parameter: app_name is required.'

  def test_install_app_examples_unsupported_app_name(self):
    request = Mock(method='POST', POST={'app_name': 'test_app'}, user=Mock())
    response = install_app_examples(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Unsupported app name: test_app'

  def test_install_app_examples_non_admin_user(self):
    with patch('desktop.api2.is_admin') as mock_is_admin:
      mock_is_admin.return_value = False

      request = Mock(method='POST', POST={'app_name': 'hive'}, user=Mock())
      response = install_app_examples(request)

      assert response.status_code == 403
      assert response.content.decode('utf-8') == 'You must be a Hue admin to access this endpoint.'

  def test_install_app_examples_success_hive(self):
    with patch('desktop.api2.is_admin') as mock_is_admin:
      with patch('desktop.api2._setup_hive_impala_examples') as mock_setup_hive_impala_examples:
        mock_is_admin.return_value = True
        mock_setup_hive_impala_examples.return_value = None

        request = Mock(method='POST', POST={'app_name': 'hive'}, user=Mock())
        response = install_app_examples(request)

        assert response.status_code == 200
        assert response.content.decode('utf-8') == 'Successfully installed examples for hive.'

  def test_install_app_examples_success_impala(self):
    with patch('desktop.api2.is_admin') as mock_is_admin:
      with patch('desktop.api2._setup_hive_impala_examples') as mock_setup_hive_impala_examples:
        mock_is_admin.return_value = True
        mock_setup_hive_impala_examples.return_value = None

        request = Mock(method='POST', POST={'app_name': 'impala'}, user=Mock())
        response = install_app_examples(request)

        assert response.status_code == 200
        assert response.content.decode('utf-8') == 'Successfully installed examples for impala.'

  def test_setup_hive_impala_examples_invalid_dialect(self):
    request = Mock(method='POST', POST={'app_name': 'impala', 'dialect': 'test_dialect'})
    response = _setup_hive_impala_examples(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == "Invalid dialect: Must be 'hive' or 'impala'"

  def test_setup_hive_impala_examples_calls_command(self):
    with patch('desktop.api2.common.find_compute') as mock_find_compute:
      with patch('desktop.api2.beeswax_install_examples.Command.handle') as mock_command:
        mock_find_compute.return_value = 'mock_interpreter'
        request = Mock(method='POST', POST={'app_name': 'impala', 'dialect': 'impala', 'database_name': 'test_db'}, user=Mock())
        _setup_hive_impala_examples(request)

        mock_command.assert_called_once_with(
          dialect='impala', db_name='test_db', user=request.user, request=request, interpreter='mock_interpreter'
        )

  def test_setup_notebook_examples_missing_connector_id(self):
    request = Mock(method='POST', POST={}, user=Mock())

    response = _setup_notebook_examples(request)

    assert response.status_code == 400
    assert response.content.decode('utf-8') == 'Missing parameter: connector_id is required.'

  def test_setup_notebook_examples_existing_connector(self):
    with patch('desktop.api2.Connector.objects.get') as mock_get_connector:
      with patch('desktop.api2.beeswax_install_examples.Command.handle') as mock_command:
        with patch('desktop.api2.get_interpreter') as mock_get_interpreter:
          request = Mock(method='POST', POST={'app_name': 'notebook', 'database_name': 'test_db', 'connector_id': '1'}, user=Mock())
          mock_get_connector.return_value = Mock(to_dict=Mock(return_value={'type': 'test_type'}), dialect='spark')
          mock_get_interpreter.return_value = 'mock_interpreter'

          _setup_notebook_examples(request)

          mock_command.assert_called_once_with(
            dialect='spark', db_name='test_db', user=request.user, interpreter='mock_interpreter', request=request
          )

  def test_setup_notebook_examples_connector_none(self):
    with patch('desktop.api2.Connector.objects.get') as mock_get_connector:
      with patch('desktop.api2.beeswax_install_examples.Command.handle') as mock_beeswax_install_command:
        with patch('desktop.api2.notebook_setup.Command.handle') as mock_notebook_setup_command:
          request = Mock(method='POST', POST={'app_name': 'notebook', 'dialect': 'spark', 'connector_id': '1'}, user=Mock())
          mock_get_connector.return_value = None

          _setup_notebook_examples(request)

          assert not mock_beeswax_install_command.called
          mock_notebook_setup_command.assert_called_once_with(dialect='spark', user=request.user)

  def test_setup_search_examples_with_log_analytics_demo(self):
    with patch('desktop.api2.search_setup.Command.handle') as mock_search_setup_command:
      with patch('desktop.api2.indexer_setup.Command.handle') as mock_indexer_setup_command:
        request = Mock(method='POST', POST={'data': 'log_analytics_demo'}, user=Mock())

        _setup_search_examples(request)

        mock_indexer_setup_command.assert_called_once_with(data='log_analytics_demo')
        mock_search_setup_command.assert_called_once()

  def test_setup_search_examples_without_log_analytics_demo(self):
    with patch('desktop.api2.search_setup.Command.handle') as mock_search_setup_command:
      with patch('desktop.api2.indexer_setup.Command.handle') as mock_indexer_setup_command:
        request = Mock(method='POST', POST={'data': 'twitter_demo'}, user=Mock())

        _setup_search_examples(request)

        mock_indexer_setup_command.assert_called_once_with(data='twitter_demo')
        assert not mock_search_setup_command.called
