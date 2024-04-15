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

import logging
import pytest
import unittest

from django.test import TestCase
from desktop.lib import i18n

from hadoop import pseudo_hdfs4
from hadoop.fs.fsutils import remove_header, do_overwrite_save


LOG = logging.getLogger()


@pytest.mark.requires_hadoop
@pytest.mark.integration
class FsUtilsTests(TestCase):

  @classmethod
  def setup_class(cls):
    cls.cluster = pseudo_hdfs4.shared_cluster()

  def setup_method(self, method):
    self.cluster.fs.setuser('test')

  def teardown_method(self, method):
    try:
      self.cluster.fs.purge_trash()
    except Exception as e:
      LOG.error('Could not clean up trash: %s', e)

  def test_remove_header(self):
    fs = self.cluster.fs

    path = "/tmp/test_remove_header.txt"
    data_header = "destination\trank"
    data_body = """thailand\t10
costarica\t?
curacao\t?"""
    data = data_header + '\n' + data_body

    f = fs.open(path, "w")
    f.write("hello")
    f.close()

    encoding = i18n.get_site_encoding()
    do_overwrite_save(fs, path, data.encode(encoding))

    assert data_body != fs.open(path).read()

    remove_header(fs, path)

    assert data_body == fs.open(path).read()
