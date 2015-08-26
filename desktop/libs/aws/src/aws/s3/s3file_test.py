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

import os

from nose.tools import eq_

from aws.s3 import s3file
from aws.s3.s3test_utils import S3TestBase


QUOTE_EN = 'a journey of a thousand miles begins with a single step'
QUOTE_CH = u'千里之行，始於足下'


class S3FileTest(S3TestBase):
  def test_basic_read(self):
    path = self.get_test_path('test_basic_read.txt')
    key = self.get_key(path)
    with self.cleaning(path):
      key.set_contents_from_string(QUOTE_EN)
      eq_(QUOTE_EN, s3file.open(key, 'r').read())
      eq_(QUOTE_EN[:4], s3file.open(key, 'r').read(length=4))

  def test_unicode_read(self):
    path = self.get_test_path('test_unicode_read.txt')
    key = self.get_key(path)
    with self.cleaning(path):
      key.set_contents_from_string(QUOTE_CH)
      eq_(QUOTE_CH.encode('utf-8'), s3file.open(key, 'r').read())
      eq_(QUOTE_CH.encode('utf-8')[:4], s3file.open(key, 'r').read(length=4))

  def test_seek(self):
    path = self.get_test_path('test_seek.txt')
    key = self.get_key(path)
    with self.cleaning(path):
      key.set_contents_from_string(QUOTE_EN)
      f = s3file.open(key, 'r')
      f.seek(0, os.SEEK_SET)
      eq_(QUOTE_EN[:2], f.read(2))
      f.seek(1, os.SEEK_SET)
      eq_(QUOTE_EN[1:][:2], f.read(2))
      f.seek(-1, os.SEEK_END)
      eq_(QUOTE_EN[-1:], f.read())
      f.seek(0, os.SEEK_SET)
      f.seek(2, os.SEEK_CUR)
      eq_(QUOTE_EN[2:][:2], f.read(2))
