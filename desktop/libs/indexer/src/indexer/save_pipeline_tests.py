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

import pytest

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.test_utils import grant_access
from desktop.models import Document, Document2
from indexer.models import _save_pipeline
from useradmin.models import User


@pytest.mark.django_db
class TestSavePipeline(object):
  def setup_method(self):
    self.owner_client = make_logged_in_client(username="pipeline_owner", recreate=True, is_superuser=False)
    self.attacker_client = make_logged_in_client(username="pipeline_attacker", recreate=True, is_superuser=False)
    grant_access("pipeline_owner", "pipeline_owner", "desktop")
    grant_access("pipeline_attacker", "pipeline_attacker", "desktop")
    self.owner = User.objects.get(username="pipeline_owner")
    self.attacker = User.objects.get(username="pipeline_attacker")

  def _minimal_pipeline(self, **overrides):
    payload = {
      "name": "Importer pipeline",
      "description": "Original description",
      "type": "pipeline",
      "uuid": "pipeline-test-uuid",
      "isSaved": False,
    }
    payload.update(overrides)
    return payload

  def test_save_pipeline_denies_cross_user_overwrite_via_model(self):
    victim_doc = Document2.objects.create(
      name="Victim pipeline",
      uuid="victim-pipeline-uuid",
      type="pipeline",
      owner=self.owner,
      description="trusted content",
    )
    Document.objects.link(victim_doc, owner=self.owner, name=victim_doc.name, description=victim_doc.description, extra="pipeline")
    victim_doc.update_data({"steps": []})
    victim_doc.save()

    attacker_payload = self._minimal_pipeline(
      id=victim_doc.id,
      name="Malicious pipeline",
      description="attacker controlled",
    )

    with pytest.raises(PopupException):
      _save_pipeline(attacker_payload, self.attacker)

    victim_doc.refresh_from_db()
    assert victim_doc.owner_id == self.owner.id
    assert victim_doc.name == "Victim pipeline"
    assert victim_doc.description == "trusted content"

  def test_save_pipeline_allows_owner_update_via_model(self):
    doc = Document2.objects.create(
      name="My pipeline",
      uuid="owner-pipeline-uuid",
      type="pipeline",
      owner=self.owner,
      description="before",
    )
    Document.objects.link(doc, owner=self.owner, name=doc.name, description=doc.description, extra="pipeline")
    doc.update_data({"steps": []})
    doc.save()

    payload = self._minimal_pipeline(id=doc.id, name="Updated pipeline", description="after")
    updated_doc, save_as = _save_pipeline(payload, self.owner)

    assert not save_as
    assert updated_doc.id == doc.id
    assert updated_doc.name == "Updated pipeline"
    assert updated_doc.description == "after"

  def test_save_pipeline_http_denies_cross_user(self):
    victim_doc = Document2.objects.create(
      name="HTTP victim",
      uuid="http-victim-uuid",
      type="pipeline",
      owner=self.owner,
    )
    Document.objects.link(victim_doc, owner=self.owner, name=victim_doc.name, description="", extra="pipeline")
    victim_doc.update_data({})
    victim_doc.save()

    notebook_json = json.dumps(self._minimal_pipeline(id=victim_doc.id, name="HTTP attack"))
    response = self.attacker_client.post("/indexer/api/importer/save", {"notebook": notebook_json})
    data = json.loads(response.content)

    assert data["status"] == -1
    victim_doc.refresh_from_db()
    assert victim_doc.name == "HTTP victim"

  def test_save_pipeline_http_allows_owner(self):
    doc = Document2.objects.create(
      name="HTTP owner doc",
      uuid="http-owner-uuid",
      type="pipeline",
      owner=self.owner,
    )
    Document.objects.link(doc, owner=self.owner, name=doc.name, description="", extra="pipeline")
    doc.update_data({})
    doc.save()

    notebook_json = json.dumps(self._minimal_pipeline(id=doc.id, name="HTTP updated"))
    response = self.owner_client.post("/indexer/api/importer/save", {"notebook": notebook_json})
    data = json.loads(response.content)

    assert data["status"] == 0
    doc.refresh_from_db()
    assert doc.name == "HTTP updated"

  def test_save_pipeline_creates_new_document_for_owner(self):
    payload = self._minimal_pipeline(uuid="brand-new-pipeline-uuid")
    doc, save_as = _save_pipeline(payload, self.owner)

    assert save_as
    assert doc.owner_id == self.owner.id
    assert doc.name == "Importer pipeline"
