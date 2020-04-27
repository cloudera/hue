#!/usr/bin/env python
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

from future import standard_library
standard_library.install_aliases()
import sys

from desktop.lib.i18n import force_unicode
from nose.tools import assert_equal

from indexer.utils import field_values_from_separated_file


if sys.version_info[0] > 2:
  from io import StringIO as string_io
else:
  from StringIO import StringIO as string_io


def test_get_ensemble():
  # Non ascii
  data = string_io('fieldA\nrel=""nofollow"">Twitter for Péché')
  result = list(field_values_from_separated_file(data, delimiter='\t', quote_character='"'))
  assert_equal(u'rel=""nofollow"">Twitter for Péché', result[0]['fieldA'])

  data = string_io('fieldA\nrel=""nofollow"">Twitter for BlackBerry®')
  result = list(field_values_from_separated_file(data, delimiter='\t', quote_character='"'))
  assert_equal(u'rel=""nofollow"">Twitter for BlackBerry®', result[0]['fieldA'])

  # Bad binary
  test_str = b'fieldA\naaa\x80\x02\x03'
  if sys.version_info[0] > 2:
    data = string_io(force_unicode(test_str, errors='ignore'))
  else:
    data = string_io(test_str)
  result = list(field_values_from_separated_file(data, delimiter='\t', quote_character='"'))
  assert_equal(u'aaa\x02\x03', result[0]['fieldA'])
