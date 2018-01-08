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

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises
from nose.plugins.skip import SkipTest

from django.contrib.auth.models import User

from desktop.api import massaged_documents_for_json, _get_docs
from desktop.conf import USE_NEW_EDITOR
from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import DocumentTag , Document

from pig.models import PigScript
from useradmin.models import get_default_user_group


class TestDocModelTags():

  def setUp(self):
    self.client = make_logged_in_client(username="tag_user", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_tag_user", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="tag_user")
    self.user_not_me = User.objects.get(username="not_tag_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

  def add_tag(self, name, expected_status=0):
    response = self.client.post("/desktop/api/tag/add_tag", {'name': name})
    content = json.loads(response.content)
    assert_equal(content['status'], expected_status, content)

    return content.get('id')

  def add_doc(self, name):
    script = PigScript.objects.create(owner=self.user)
    doc = Document.objects.link(script, owner=script.owner, name=name)
    return script, doc

  def share_doc(self, doc, permissions):
    response = self.client.post("/desktop/api/doc/update_permissions", {
        'doc_id': doc.id,
        'data': json.dumps(*permissions)
    })

  def share_doc_read_only(self, doc):
    return self.share_doc(doc, {
      'read': {
        'user_ids': [
          self.user.id
        ],
        'group_ids': []
      },
      'write': {
        'user_ids': [],
        'group_ids': []
      }
    })

  def test_add_tag(self):
    raise SkipTest
    response = self.client.get("/desktop/api/tag/add_tag")
    assert_equal(response.status_code, 405)

    response = self.client.post("/desktop/api/tag/add_tag")
    content = json.loads(response.content)
    assert_equal(content['status'], -1, content)
    assert_equal(content['message'], "Form is missing 'name' field", content)

    tag_id = self.add_tag('my_tag')

    assert_true(DocumentTag.objects.filter(id=tag_id, owner=self.user, tag='my_tag').exists())

  def test_add_duplicate_tag(self):
    tag_name = 'test_add_duplicate_tag'
    n = DocumentTag.objects.filter(owner=self.user, tag=tag_name).count()

    tag_id = self.add_tag(tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

    tag_id = self.add_tag(tag_name, expected_status=-1)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

  def test_add_and_clean_duplicate_tag(self):
    tag_name = 'test_add_and_clean_duplicate_tag'
    script, doc = self.add_doc('test-pig')
    n = DocumentTag.objects.filter(owner=self.user, tag=tag_name).count()

    tag_id = self.add_tag(tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

    tag_id = DocumentTag.objects.tag(self.user, doc.id, tag_name=tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

  def test_remove_tags(self):
    response = self.client.post("/desktop/api/tag/add_tag", {'name': 'my_tag'})
    tag_id = json.loads(response.content)['id']

    response = self.client.get("/desktop/api/tag/remove_tag")
    assert_equal(response.status_code, 405)

    # Only the owner can remove tags.
    response = self.client_not_me.post("/desktop/api/tag/remove_tag", {'tag_id': tag_id})
    content = json.loads(response.content)
    assert_equal(content['status'], -1, content)
    assert_equal(content['message'], "DocumentTag matching query does not exist.", content)

    response = self.client.post("/desktop/api/tag/remove_tag", {'tag_id': tag_id})
    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_false(DocumentTag.objects.filter(id=tag_id).exists())

  def test_massaged_documents_for_json(self):
    docs = _get_docs(self.user)
    assert_equal({}, massaged_documents_for_json(docs, self.user))

    tag_name = 'test_massaged_documents_for_json'
    script, doc = self.add_doc('test_massaged_documents_for_json')

    docs = _get_docs(self.user)
    assert_not_equal({}, massaged_documents_for_json(docs, self.user))

  def test_tag_errors(self):
    script, doc = self.add_doc('tag_pig_errors')

    # Users without permission cannot see docs.
    response = self.client_not_me.post("/desktop/api/doc/tag", {'data': json.dumps({'doc_id': doc.id, 'tag': 'pig'})})
    content = json.loads(response.content)
    assert_equal(content['status'], -1, content)
    assert_equal(content['message'], "Document matching query does not exist.", content)

    # Users with permission cannot tag docs.
    self.share_doc_read_only(doc)

    response = self.client_not_me.post("/desktop/api/doc/tag", {'data': json.dumps({'doc_id': doc.id, 'tag': 'pig'})})
    content = json.loads(response.content)
    assert_equal(content['status'], -1, content)
    assert_equal(content['message'], "Document matching query does not exist.", content)

  def test_tag(self):
    script, doc = self.add_doc('tag_pig')

    # Owners can add tags.
    response = self.client.post("/desktop/api/doc/tag", {'data': json.dumps({'doc_id': doc.id, 'tag': 'pig'})})
    assert_equal(0, json.loads(response.content)['status'], response.content)

    tag2_id = self.add_tag('pig2')

    response = self.client.post("/desktop/api/doc/tag", {'data': json.dumps({'doc_id': doc.id, 'tag_id': tag2_id})})
    assert_equal(0, json.loads(response.content)['status'], response.content)

  def test_update_tags(self):
    script, doc = self.add_doc('update_tags')
    default_tag = DocumentTag.objects.get_default_tag(self.user)

    tag1_id = self.add_tag('update_tags_1')
    tag2_id = self.add_tag('update_tags_2')

    response = self.client.post("/desktop/api/doc/update_tags", {'data': json.dumps({'doc_id': doc.id, 'tag_ids': [tag1_id, tag2_id]})})
    content = json.loads(response.content)

    assert_equal(0, content['status'], content)
    assert_equal([
        {"id": default_tag.id, "name": "default"},
        {"id": tag1_id, "name": "update_tags_1"},
        {"id": tag2_id, "name": "update_tags_2"}
      ], sorted(content['doc']['tags'], key=lambda t: t['id']))

    # Only the owner can update tags.
    response = self.client_not_me.post("/desktop/api/doc/update_tags", {'data': json.dumps({'doc_id': doc.id, 'tag_ids': [tag1_id, tag2_id]})})
    content = json.loads(response.content)
    assert_equal(content['status'], -1, response.content)
    assert_equal(content['message'], "Document matching query does not exist.", content)

    # todo no default tag on test user?


class TestDocModelPermissions():

  def setUp(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

    self.old_home_path = '/home2' if USE_NEW_EDITOR.get() else '/home'

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    PigScript.objects.filter(owner=self.user).delete()
    Document.objects.filter(owner=self.user).delete()

  def _add_doc(self, name):
    script, created = PigScript.objects.get_or_create(owner=self.user)
    doc = Document.objects.link(script, owner=script.owner, name=name)
    return script, doc

  def test_update_permissions(self):
    script, doc = self._add_doc('test_update_permissions')

    response = self.client.post("/desktop/api/doc/update_permissions", {
        'doc_id': doc.id,
        'data': json.dumps({'read': {'user_ids': [self.user.id, self.user_not_me.id], 'group_ids': []}})
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

  def test_share_document_permissions(self):
    # No doc
    response = self.client.get(self.old_home_path)
    assert_equal({}, json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_equal({}, json.loads(response.context[0]['json_documents']))

    # Add doc
    script, doc = self._add_doc('test_update_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_false(doc_id in json.loads(response.context[0]['json_documents']))

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # Share by user
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id,
            self.user_not_me.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))

    # Un-share
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_false(doc_id in json.loads(response.context[0]['json_documents']))

    # Share by group
    default_group = get_default_user_group()

    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': [
            default_group.id
          ]
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))

    # Un-share
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_false(doc_id in json.loads(response.context[0]['json_documents']))

    # Modify by user
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [
            self.user_not_me.id
          ],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))

    # Un-share
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_false(doc_id in json.loads(response.context[0]['json_documents']))

    # Modify by group
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': [
            default_group.id
          ]
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_true(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))

    # Un-share
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_false(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    response = self.client.get(self.old_home_path)
    assert_true(doc_id in json.loads(response.context[0]['json_documents']))
    response = self.client_not_me.get(self.old_home_path)
    assert_false(doc_id in json.loads(response.context[0]['json_documents']))

  def test_update_permissions_cannot_escalate_privileges(self):
    script, doc = self._add_doc('test_update_permissions_cannot_escape_privileges')

    # Share read permissions
    response = self.client.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id,
            self.user_not_me.id,
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [
            self.user.id,
          ],
          'group_ids': []
        }
      })
    })

    assert_equal(0, json.loads(response.content)['status'], response.content)

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # Try, and fail to escalate privileges.
    response = self.client_not_me.post("/desktop/api/doc/update_permissions", {
      'doc_id': doc.id,
      'data': json.dumps({
        'read': {
          'user_ids': [
            self.user.id,
            self.user_not_me.id,
          ],
          'group_ids': []
        },
        'write': {
          'user_ids': [
            self.user_not_me.id,
            self.user_not_me.id,
          ],
          'group_ids': []
        }
      })
    })

    content = json.loads(response.content)
    assert_equal(content['status'], -1)
    assert_equal(content['message'], "Document does not exist or you don\'t have the permission to access it.")

    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))
