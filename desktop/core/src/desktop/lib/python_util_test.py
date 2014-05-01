# Tests for django_util
# Some parts based on http://www.djangosnippets.org/snippets/1044/
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

import datetime

from nose.tools import assert_true, assert_equal, assert_not_equal

from desktop.lib.python_util import CaseInsensitiveDict, force_dict_to_strings, force_list_to_strings


class TestPythonUtil(object):
  def test_case_insensitive_dictionary(self):
    d = CaseInsensitiveDict()
    d["Test"] = "Test"
    assert_true("Test" in d)
    assert_true("test" in d)
    assert_equal("Test", d['Test'])
    assert_equal("Test", d['test'])
    assert_not_equal("test", d['Test'])
    assert_not_equal("test", d['test'])

  def test_force_dict_to_strings(self):
    unicode_dict = {u'test': u'test'}
    string_dict = {'test': 'test'}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

    # Embedded
    unicode_dict = {u'test': {u'test': u'test'}}
    string_dict = {'test': {'test': 'test'}}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

    # Embedded list
    unicode_dict = {u'test': [{u'test': u'test'}]}
    string_dict = {'test': [{'test': 'test'}]}
    transformed_dict = force_dict_to_strings(unicode_dict)
    assert_equal(string_dict, transformed_dict)

  def test_force_list_to_strings(self):
    unicode_list = [u'test', {u'test': u'test'}]
    string_list = ['test', {'test': 'test'}]
    transformed_list = force_list_to_strings(unicode_list)
    assert_equal(string_list, transformed_list)
