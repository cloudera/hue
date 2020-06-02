#!/usr/bin/env python
## -*- coding: utf-8 -*-
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

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from libsaml.conf import xmlsec, REQUIRED_GROUPS, REQUIRED_GROUPS_ATTRIBUTE


if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


def test_xmlsec_dynamic_default_no_which():

  with patch('libsaml.conf.subprocess') as subprocess:
    subprocess.Popen = Mock(
      side_effect = OSError('No such file or directory. `which` command is not present')
    )

    assert_equal('/usr/local/bin/xmlsec1', xmlsec())


class TestLibSaml():

  def setUp(self):
    try:
      from djangosaml2 import views as djangosaml2_views
      from libsaml import views as libsaml_views
    except ImportError:
      raise SkipTest('djangosaml2 or libsaml modules not found')

  def test_is_authorized_groups(self):
    from libsaml.backend import SAML2Backend

    # Single group
    attributes = {'groups': ['analyst']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['analyst']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_true(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()

    attributes = {'groups': ['analyst', 'finance']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['analyst']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_true(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()


    # Multi groups
    attributes = {'groups': ['analyst', 'sales', 'engineering']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['analyst', 'sales']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_true(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()


  def test_is_non_authorized_groups(self):
    from libsaml.backend import SAML2Backend

    # Single group
    attributes = {'groups': ['intern']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['sales']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_false(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()

    attributes = {'groups': ['intern', 'finance']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['sales']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_false(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()

    # Multi groups
    attributes = {'groups': ['intern', 'sales']}
    attribute_mapping = {}

    resets = [
      REQUIRED_GROUPS.set_for_testing(['sales', 'engineering']),
      REQUIRED_GROUPS_ATTRIBUTE.set_for_testing('groups'),
    ]

    try:
      assert_false(SAML2Backend().is_authorized(attributes, attribute_mapping))
    finally:
      for reset in resets:
        reset()
