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

import os
import shutil
import tempfile

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster

from libzookeeper.models import ZookeeperClient
from libzookeeper.conf import zkensemble


class TestWithZooKeeper:
  requires_hadoop = True

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest()

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "libzookeeper")

    # Create a ZKNode namespace
    cls.namespace = 'TestWithZooKeeper'

    # Create temporary test directory and file with contents
    cls.local_directory = tempfile.mkdtemp()
    # Create subdirectory
    cls.subdir_name = 'subdir'
    subdir_path = '%s/%s' % (cls.local_directory, cls.subdir_name)
    os.mkdir(subdir_path, 0755)
    # Create file
    cls.filename = 'test.txt'
    file_path = '%s/%s' % (subdir_path, cls.filename)
    cls.file_contents = "This is a test"
    file = open(file_path, 'w+')
    file.write(cls.file_contents)
    file.close()

  @classmethod
  def teardown_class(cls):
    # Don't want directories laying around
    shutil.rmtree(cls.local_directory)

  def test_get_children_data(self):
    client = ZookeeperClient(hosts=zkensemble())
    db = client.get_children_data(namespace='')
    assert_true(len(db) > 0)

  def test_copy_and_delete_path(self):
    root_node = '%s/%s' % (TestWithZooKeeper.namespace, 'test_copy_and_delete_path')
    client = ZookeeperClient(hosts=zkensemble(), read_only=False)

    # Delete the root_node first just in case it wasn't cleaned up in previous run
    client.zk.start()
    client.zk.delete(root_node, recursive=True)
    client.zk.stop()

    # Test copy_path
    client.copy_path(root_node, TestWithZooKeeper.local_directory)

    client.zk.start()
    assert_true(client.zk.exists('%s' % root_node))
    assert_true(client.zk.exists('%s/%s' % (root_node, TestWithZooKeeper.subdir_name)))
    assert_true(client.zk.exists('%s/%s/%s' % (root_node, TestWithZooKeeper.subdir_name, TestWithZooKeeper.filename)))
    contents, stats = client.zk.get('%s/%s/%s' % (root_node, TestWithZooKeeper.subdir_name, TestWithZooKeeper.filename))
    assert_equal(contents, TestWithZooKeeper.file_contents)
    client.zk.stop()

    # Test delete_path
    client.delete_path(root_node)

    client.zk.start()
    assert_equal(client.zk.exists('%s' % root_node), None)
    assert_equal(client.zk.exists('%s/%s' % (root_node, TestWithZooKeeper.subdir_name)), None)
    assert_equal(client.zk.exists('%s/%s/%s' % (root_node, TestWithZooKeeper.subdir_name, TestWithZooKeeper.filename)), None)
