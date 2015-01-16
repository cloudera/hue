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

from django.conf.urls import patterns, url
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import query, CharField, SmallIntegerField

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.models import DocumentTag , Document
from pig.models import PigScript
from useradmin.models import get_default_user_group
from desktop.api import massaged_documents_for_json, _get_docs


class TestDocModelTags():

  def setUp(self):
    self.client = make_logged_in_client(username="tag_user", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_tag_user", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="tag_user")
    self.user_not_me = User.objects.get(username="not_tag_user")

    grant_access(self.user.username, self.user.username, "desktop")
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

  def add_tag(self, name):
    response = self.client.post("/desktop/api/tag/add_tag", {'name': name})
    assert_equal(0, json.loads(response.content)['status'], response.content)
    return json.loads(response.content)['id']

  def add_doc(self, name):
    script = PigScript.objects.create(owner=self.user)
    doc = Document.objects.link(script, owner=script.owner, name=name)
    return script, doc

  def test_add_tag(self):
    response = self.client.get("/desktop/api/tag/add_tag")
    assert_equal(-1, json.loads(response.content)['status'])

    tag_id = self.add_tag('my_tag')

    assert_true(DocumentTag.objects.filter(id=tag_id, owner=self.user, tag='my_tag').exists())

  def test_add_duplicate_tag(self):
    tag_name = 'test_add_duplicate_tag'
    n = DocumentTag.objects.filter(owner=self.user, tag=tag_name).count()

    tag_id = self.add_tag(tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

    tag_id = self.add_tag(tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

  def test_add_and_clean_duplicate_tag(self):
    tag_name = 'test_add_and_clean_duplicate_tag'
    script, doc = self.add_doc('test-pig')
    n = DocumentTag.objects.filter(owner=self.user, tag=tag_name).count()

    tag_id = self.add_tag(tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

    DocumentTag.objects.create(owner=self.user, tag=tag_name)
    assert_equal(n + 2, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

    tag_id = DocumentTag.objects.tag(self.user, doc.id, tag_name=tag_name)
    assert_equal(n + 1, DocumentTag.objects.filter(owner=self.user, tag=tag_name).count())

  def test_remove_tags(self):
    response = self.client.post("/desktop/api/tag/add_tag", {'name': 'my_tag'})
    tag_id = json.loads(response.content)['id']

    response = self.client.get("/desktop/api/tag/remove_tag")
    assert_equal(-1, json.loads(response.content)['status'])

    response = self.client_not_me.post("/desktop/api/tag/remove_tag", {'tag_id': tag_id})
    assert_equal(-1, json.loads(response.content)['status'], response.content)

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

  def test_tag(self):
    script, doc = self.add_doc('tag_pig')

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
      ], content['doc']['tags'])

    # No perms
    response = self.client_not_me.post("/desktop/api/doc/update_tags", {'data': json.dumps({'doc_id': doc.id, 'tag_ids': [tag1_id, tag2_id]})})
    content = json.loads(response.content)

    assert_equal(-1, content['status'])

    # todo no default tag on test user?



class TestDocModelPermissions():

  def setUp(self):
    self.client = make_logged_in_client(username="perm_user", groupname="default", recreate=True, is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username="perm_user")
    self.user_not_me = User.objects.get(username="not_perm_user")

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
    response = self.client.get('/home')
    assert_equal({}, json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_equal({}, json.loads(response.context['json_documents']))

    # Add doc
    script, doc = self._add_doc('test_update_permissions')
    doc_id = '%s' % doc.id

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_false(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_false(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_false(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_false(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))

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

    response = self.client.get('/home')
    assert_true(doc_id in json.loads(response.context['json_documents']))
    response = self.client_not_me.get('/home')
    assert_false(doc_id in json.loads(response.context['json_documents']))
