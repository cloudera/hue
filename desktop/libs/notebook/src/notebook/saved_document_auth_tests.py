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

import pytest

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import grant_access
from desktop.models import Document2
from notebook.saved_document_auth import get_writable_document_for_update
from useradmin.models import User


@pytest.mark.django_db
class TestSavedDocumentAuth(object):
  def setup_method(self):
    make_logged_in_client(username="save_doc_owner", recreate=True, is_superuser=False)
    make_logged_in_client(username="save_doc_other", recreate=True, is_superuser=False)
    make_logged_in_client(username="save_doc_admin", recreate=True, is_superuser=True)
    grant_access("save_doc_owner", "save_doc_owner", "desktop")
    grant_access("save_doc_other", "save_doc_other", "desktop")
    self.owner = User.objects.get(username="save_doc_owner")
    self.other = User.objects.get(username="save_doc_other")
    self.admin = User.objects.get(username="save_doc_admin")

  def test_get_writable_document_for_update_returns_none_for_new_document(self):
    assert get_writable_document_for_update({"name": "new", "uuid": "abc"}, self.owner) is None

  def test_get_writable_document_for_update_allows_owner_by_id(self):
    doc = Document2.objects.create(name="mine", uuid="owner-doc-uuid", type="pipeline", owner=self.owner)
    resolved = get_writable_document_for_update({"id": doc.id}, self.owner)
    assert resolved.id == doc.id

  def test_get_writable_document_for_update_denies_other_user_by_id(self):
    doc = Document2.objects.create(name="victim", uuid="victim-doc-uuid", type="pipeline", owner=self.owner)
    with pytest.raises(PopupException):
      get_writable_document_for_update({"id": doc.id}, self.other)

  def test_get_writable_document_for_update_parent_uuid_requires_write(self):
    parent = Document2.objects.create(name="parent", uuid="parent-uuid", type="query-hive", owner=self.owner)
    with pytest.raises(PopupException):
      get_writable_document_for_update({"parentSavedQueryUuid": parent.uuid}, self.other)

  def test_get_writable_document_for_update_allows_admin_for_other_users_private_document(self):
    doc = Document2.objects.create(name="private", uuid="private-doc-uuid", type="query-hive", owner=self.owner)
    resolved = get_writable_document_for_update({"id": doc.id}, self.admin)
    assert resolved.id == doc.id

  def test_get_writable_document_for_update_missing_and_denied_documents_share_one_message(self):
    doc = Document2.objects.create(name="victim", uuid="probe-doc-uuid", type="pipeline", owner=self.owner)
    with pytest.raises(PopupException) as denied:
      get_writable_document_for_update({"id": doc.id}, self.other)
    with pytest.raises(PopupException) as missing:
      get_writable_document_for_update({"id": doc.id + 100000}, self.other)
    assert denied.value.message == missing.value.message
