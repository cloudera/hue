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


from desktop import conf
from desktop.lib.fs.ozone.client import _make_ofs_client


class TestOFSClient(object):

  @classmethod
  def setup_class(cls):
    cls._resets = [
      conf.OZONE['default'].FS_DEFAULTFS.set_for_testing('ofs://ozone1'),
      conf.OZONE['default'].LOGICAL_NAME.set_for_testing('test-logical-name'),
      conf.OZONE['default'].WEBHDFS_URL.set_for_testing('http://gethue-ozone:9778/webhdfs/v1'),
      conf.OZONE['default'].SECURITY_ENABLED.set_for_testing(True),
      conf.OZONE['default'].SSL_CERT_CA_VERIFY.set_for_testing(True),
      conf.OZONE['default'].TEMP_DIR.set_for_testing('/tmp')
    ]

    cls.ofs_client = _make_ofs_client('default')


  def test_client_attributes(self):
    assert self.ofs_client._url == 'http://gethue-ozone:9778/webhdfs/v1'
    assert self.ofs_client._superuser == None
    assert self.ofs_client._security_enabled == True
    assert self.ofs_client._ssl_cert_ca_verify == True
    assert self.ofs_client._temp_dir == '/tmp'
    assert self.ofs_client._umask == 530
    assert self.ofs_client._fs_defaultfs == 'ofs://ozone1'
    assert self.ofs_client._logical_name == 'test-logical-name'
    assert self.ofs_client._supergroup == None
    assert self.ofs_client._scheme == 'ofs'
    assert self.ofs_client._netloc == 'ozone1'
    assert self.ofs_client._is_remote == True
    assert self.ofs_client._has_trash_support == False
    assert self.ofs_client.expiration == None
    assert self.ofs_client._filebrowser_action == 'ofs_access'


  def test_strip_normpath(self):
    test_path = self.ofs_client.strip_normpath('ofs://ozone1/vol1/buk1/key')
    assert test_path == '/vol1/buk1/key'

    test_path = self.ofs_client.strip_normpath('ofs:/ozone1/vol1/buk1/key')
    assert test_path == '/vol1/buk1/key'

    test_path = self.ofs_client.strip_normpath('/ozone1/vol1/buk1/key')
    assert test_path == '/ozone1/vol1/buk1/key'


  def test_normpath(self):
    test_path = self.ofs_client.normpath('ofs://')
    assert test_path == 'ofs://'

    test_path = self.ofs_client.normpath('ofs://ozone1/vol1/buk1/key')
    assert test_path == 'ofs://ozone1/vol1/buk1/key'

    test_path = self.ofs_client.normpath('ofs://ozone1/vol1/buk1/key/')
    assert test_path == 'ofs://ozone1/vol1/buk1/key'

    test_path = self.ofs_client.normpath('ofs://ozone1/vol1/buk1/key//')
    assert test_path == 'ofs://ozone1/vol1/buk1/key'

    test_path = self.ofs_client.normpath('ofs://ozone1/vol1/buk1//key//')
    assert test_path == 'ofs://ozone1/vol1/buk1/key'


  def test_isroot(self):
    is_root = self.ofs_client.isroot('ofs://ozone1/vol1/buk1/key')
    assert is_root == False

    is_root = self.ofs_client.isroot('ofs://ozone1')
    assert is_root == False

    is_root = self.ofs_client.isroot('ofs://')
    assert is_root == True


  def test_parent_path(self):
    parent_path = self.ofs_client.parent_path('ofs://')
    assert parent_path == 'ofs://'

    parent_path = self.ofs_client.parent_path('ofs://ozone1/vol1/buk1/dir1/file1.csv')
    assert parent_path == 'ofs://ozone1/vol1/buk1/dir1'

    parent_path = self.ofs_client.parent_path('ofs://ozone1/vol1/buk1/key')
    assert parent_path == 'ofs://ozone1/vol1/buk1'

    parent_path = self.ofs_client.parent_path('ofs://ozone1/vol1/buk1')
    assert parent_path == 'ofs://ozone1/vol1'

    parent_path = self.ofs_client.parent_path('ofs://ozone1/vol1')
    assert parent_path == 'ofs://ozone1/'

    parent_path = self.ofs_client.parent_path('ofs://ozone1')
    assert parent_path == 'ofs://'


  def test_listdir_stats_for_serviceid_path(self):
    serviceid_stat = self.ofs_client.listdir_stats('ofs://')
    assert (
      serviceid_stat[0].to_json_dict() ==
      {'path': 'ofs://ozone1', 'size': 0, 'atime': 0, 'mtime': 0, 'mode': 16895, 'user': '', 'group': '', 'blockSize': 0, 'replication': 0})


  def test_stats_for_serviceid_path(self):
    serviceid_stat = self.ofs_client.stats('ofs://')
    assert (
      serviceid_stat.to_json_dict() ==
      {'path': 'ofs://ozone1', 'size': 0, 'atime': 0, 'mtime': 0, 'mode': 16895, 'user': '', 'group': '', 'blockSize': 0, 'replication': 0})


  @classmethod
  def teardown_class(cls):
    for reset in cls._resets:
      reset()


