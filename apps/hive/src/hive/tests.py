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

import sys

import aws

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal, assert_raises

from desktop.lib.django_test_util import make_logged_in_client



if sys.version_info[0] > 2:
  from unittest.mock import patch, Mock
else:
  from mock import patch, Mock


def test_config_check():
  with patch('beeswax.hive_site.get_metastore_warehouse_dir') as get_metastore_warehouse_dir:
    with patch('aws.s3.s3fs.S3FileSystem._stats') as s3_stat:
      with patch('aws.conf.is_enabled') as is_s3_enabled:
        reset = aws.conf.AWS_ACCOUNTS.set_for_testing({
            'default': {
                'region': 'us-east-1',
                'access_key_id': 'access_key_id',
                'secret_access_key':'secret_access_key'
            }
        }),
        warehouse = 's3a://yingsdx0602/data1/warehouse/tablespace/managed/hive'
        get_metastore_warehouse_dir.return_value = warehouse
        is_s3_enabled.return_value = True
        s3_stat.return_value = Mock(
            DIR_MODE=16895,
            FILE_MODE=33206,
            aclBit=False,
            atime=None,
            group='',
            isDir=True,
            mode=16895,
            mtime=None,
            name='hive',
            path='s3a://yingchensdx/data1/warehouse/tablespace/managed/hive/',
            size=0,
            type='DIRECTORY',
            user=''
        )

        try:
          cli = make_logged_in_client()
          resp = cli.get('/desktop/debug/check_config')
          s3_stat.assert_called()
          err_msg = 'Failed to access Hive warehouse: %s' % warehouse
          if not isinstance(err_msg, bytes):
            err_msg = err_msg.encode('utf-8')
          assert_false(err_msg in resp.content, resp)
        finally:
          for old_conf in reset:
            old_conf()

