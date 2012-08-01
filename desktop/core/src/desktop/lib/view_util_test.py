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

from nose.tools import *

from desktop.lib.view_util import big_filesizeformat, format_time_diff, format_duration_in_millis

import datetime

def test_big_filesizeformat():
  assert_equal("N/A", big_filesizeformat(None))
  assert_equal("N/A", big_filesizeformat(""))
  assert_equal("0 B", big_filesizeformat(0))
  assert_equal("17 B", big_filesizeformat(17))
  assert_equal("1.0 KB", big_filesizeformat(1024))
  assert_equal("1.0 MB", big_filesizeformat(1024*1024))
  assert_equal("1.1 GB", big_filesizeformat(int(1.1*1024*1024*1024)))
  assert_equal("2.0 TB", big_filesizeformat(2*1024*1024*1024*1024))
  assert_equal("1.5 PB", big_filesizeformat(3*1024*1024*1024*1024*1024/2))

def test_format_time_diff():
  assert_equal("1h:0m:0s", format_time_diff(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(60*60*1)))
  assert_equal("0s", format_time_diff(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(0)))
  assert_equal("1d:12h:24m:32s", format_time_diff(datetime.datetime.fromtimestamp(0), datetime.datetime.fromtimestamp(131072)))

def test_format_duration_in_millis():
    assert_equal("1h:0m:0s", format_duration_in_millis(60*60*1000))
    assert_equal("0s", format_duration_in_millis(0))
    assert_equal("1d:12h:24m:32s", format_duration_in_millis(24*60*60*1000 + 12*60*60*1000 + 24*60*1000 + 32*1000))
