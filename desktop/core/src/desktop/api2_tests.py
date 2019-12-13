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

from builtins import object
import json
import re

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from useradmin.models import get_default_user_group, User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import Document2


class TestApi2(object):

  def setUp(self):
    self.client = make_logged_in_client(username="api2_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="api2_user")

    grant_access(self.user.username, self.user.username, "desktop")

  def test_search_entities_interactive_xss(self):
    query = Document2.objects.create(
        name='<script>alert(5)</script>',
        description='<script>alert(5)</script>',
        type='query-hive',
        owner=self.user
    )

    try:
      response = self.client.post('/desktop/api/search/entities_interactive/', data={
        'sources': json.dumps(['documents']),
        'query_s': json.dumps('alert')
      })
      results = json.loads(response.content)['results']
      assert_true(results)
      result_json = json.dumps(results)
      assert_false(re.match('<(?!em)', result_json), result_json)
      assert_false(re.match('(?!em)>', result_json), result_json)
      assert_false('<script>' in result_json, result_json)
      assert_false('</script>' in result_json, result_json)
      assert_true('&lt;' in result_json, result_json)
      assert_true('&gt;' in result_json, result_json)
    finally:
      query.delete()


class TestDocumentApiSharingPermissions(object):

  def setUp(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")


  def _add_doc(self, name):
    return Document2.objects.create(
        name=name,
        type='query-hive',
        owner=self.user
    )

  def share_doc(self, doc, permissions, client=None):
    if client is None:
      client = self.client

    return client.post("/desktop/api2/doc/share", {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps(permissions)
    })

  def share_link_doc(self, doc, perm, is_on=False, client=None):
    if client is None:
      client = self.client

    return client.post("/desktop/api2/doc/share/link", {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps({'name': 'link_%s' % perm, 'is_link_on': is_on})
    })

  def test_update_permissions(self):
    doc = self._add_doc('test_update_permissions')

    response = self.share_doc(
        doc,
        {
          'read': {
            'user_ids': [self.user_not_me.id],
            'group_ids': []
          }
        }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

  def test_share_document_permissions(self):
    # No doc
    response = self.client.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    # Add doc
    doc = self._add_doc('test_update_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # Share by user
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
            self.user_not_me.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    # Un-share
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    # Share by group
    default_group = get_default_user_group()

    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': [default_group.id]
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    # Un-share
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    # Modify by other user
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [self.user_not_me.id],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    # Un-share
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])

    # Modify by group
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': [default_group.id]
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    # Un-share
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/')
    assert_false(json.loads(response.content)['documents'])


  def test_update_permissions_cannot_escalate_privileges(self):
    doc = self._add_doc('test_update_permissions_cannot_escape_privileges')

    # Share read permissions
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
            self.user_not_me.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      }
    )

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # Try, and fail to escalate privileges.
    response = self.share_doc(doc, {
        'read': {
          'user_ids': [
            self.user_not_me.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [
            self.user_not_me.id,
          ],
          'group_ids': []
        }
      },
      self.client_not_me
    )

    content = json.loads(response.content)
    assert_equal(content['status'], -1)
    assert_true("Document does not exist or you don\'t have the permission to access it." in content['message'], content['message'])

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))


  def test_link_sharing_permissions(self):
    # Add doc
    doc = self._add_doc('test_link_sharing_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_false(json.loads(response.content)['documents'])

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(-1, json.loads(response.content)['status'], response.content)


    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # Share by read link
    response = self.share_link_doc(doc, perm='read', is_on=True)

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_false(json.loads(response.content)['documents'])  #  Link sharing does not list docs in Home, only provides direct access

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    # Un-share
    response = self.share_link_doc(doc, perm='read', is_on=False)

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_false(json.loads(response.content)['documents'])

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(-1, json.loads(response.content)['status'], response.content)

    # Share by write link
    response = self.share_link_doc(doc, perm='write', is_on=True)

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_false(json.loads(response.content)['documents'])

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    # Un-share
    response = self.share_link_doc(doc, perm='write', is_on=False)

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_true(json.loads(response.content)['documents'])

    response = self.client_not_me.get('/desktop/api2/docs/?text=test_link_sharing_permissions')
    assert_false(json.loads(response.content)['documents'])

    response = self.client.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(0, json.loads(response.content)['status'], response.content)

    response = self.client_not_me.get('/desktop/api2/doc/?uuid=%s' % doc_id)
    assert_equal(-1, json.loads(response.content)['status'], response.content)
