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

from __future__ import absolute_import

from desktop.lib import fs


def test_splitpath():
  s = fs.splitpath

  assert s('s3a://') == ['s3a://']
  assert s('s3a://bucket') == ['s3a://', 'bucket']
  assert s('s3a://bucket/key') == ['s3a://', 'bucket', 'key']
  assert s('s3a://bucket/key/') == ['s3a://', 'bucket', 'key']
  assert s('s3a://bucket/bar/foo') == ['s3a://', 'bucket', 'bar', 'foo']
  assert (s('s3a://bucket/bar/foo?I-have-a-questionmark-in-the-folder-name/me?to') == \
    ['s3a://', 'bucket', 'bar', 'foo?I-have-a-questionmark-in-the-folder-name', 'me?to'])
  assert (s(u"s3a://bucket/all%20% ~@$&()*!+=;.?'Tжейкоб-åäö-你好") == \
    ['s3a://', 'bucket', u"all%20% ~@$&()*!+=;.?'Tжейкоб-åäö-你好"])
  

  assert s('/') == ['/']
  assert s('/dir') == ['/', 'dir']
  assert s('/dir/file') == ['/', 'dir', 'file']
  assert s('/dir/file/') == ['/', 'dir', 'file']
  assert (s('/dir/file/foo?I-have-a-questionmark-in-the-folder-name/me?to') == \
    ['/', 'dir', 'file', 'foo?I-have-a-questionmark-in-the-folder-name', 'me?to'])
  assert (s(u"/dir/all%20% ~@$&()*!+=;.?'Tжейкоб-åäö-你好") == \
    ['/', 'dir', u"all%20% ~@$&()*!+=;.?'Tжейкоб-åäö-你好"])