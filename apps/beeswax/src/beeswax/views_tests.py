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

import sys
import json
import logging
from unittest.mock import patch

import pytest
from django.urls import reverse

from desktop.lib.django_test_util import make_logged_in_client
from useradmin.models import User

LOG = logging.getLogger()


@pytest.mark.django_db
class TestInstallExamples():

  def setup_method(self):
    self.client = make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=True, is_admin=True)
    self.user = User.objects.get(username="test")

  def test_install_via_insert_mysql(self):

    with patch('beeswax.views.beeswax_install_examples.SampleTable') as SampleTable:
      with patch('beeswax.views.beeswax_install_examples.SampleQuery') as SampleQuery:

        resp = self.client.post(reverse('beeswax:install_examples'), {'db_name': 'default'})
        data = json.loads(resp.content)

        assert 0 == data['status'], data
        assert '' == data['message'], data

        SampleTable.assert_called()
        SampleQuery.assert_called()
