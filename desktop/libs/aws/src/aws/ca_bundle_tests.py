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

"""
Guards for the CA bundle used by Hue's S3 (boto) connections after the eMudhra CA incident.

The compromised eMudhra (emSign) CA was removed from certifi in 2026.10.19. boto 2 used to ship its own,
unmaintained CA list; it now has to use certifi's bundle instead.
"""

import importlib

import boto.connection
import certifi
import pytest

# First certifi release without the compromised eMudhra CA.
MIN_CERTIFI_VERSION = (2026, 10, 19)


class TestCaBundle(object):
  def test_boto_defaults_to_certifi_ca_bundle(self):
    assert boto.connection.DEFAULT_CA_CERTS_FILE == certifi.where()

  def test_boto_does_not_ship_its_own_ca_bundle(self):
    with pytest.raises(ImportError):
      importlib.import_module("boto.cacerts")

  def test_certifi_is_not_older_than_the_emudhra_fix(self):
    installed_version = tuple(int(part) for part in certifi.__version__.split("."))

    assert installed_version >= MIN_CERTIFI_VERSION, certifi.__version__
