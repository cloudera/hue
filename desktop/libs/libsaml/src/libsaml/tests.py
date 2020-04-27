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

from nose.tools import assert_equal, assert_true, assert_false

from libsaml.conf import xmlsec

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
