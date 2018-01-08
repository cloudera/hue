# Tests for ThriftField.
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

import os
import sys
sys.path.insert(1, os.path.join(os.path.dirname(__file__), "gen-py"))
from djangothrift_test_gen.ttypes import TestStruct
import unittest

from django_test_util import configure_django_for_test, create_tables

configure_django_for_test()

from django.db import models
from djangothrift import ThriftField

from desktop.lib import django_util

class ThriftTestModel(models.Model):
  class Meta:
    app_label = "TEST_THRIFT_APP"

  my_int = models.IntegerField()
  my_struct = ThriftField(TestStruct)

class TestThriftField(unittest.TestCase):
  def test_store_and_retrieve(self):
    create_tables(ThriftTestModel)
    struct = TestStruct()
    struct.a = "hello world"
    struct.b = 12345
    x = ThriftTestModel()
    x.my_int = 3
    x.my_struct = struct
    x.save()

    y = ThriftTestModel.objects.all()[0]
    self.assertEqual(x.my_int, y.my_int)
    self.assertEqual(django_util.encode_json(x.my_struct), y.my_struct)
    y.delete()

if __name__ == '__main__':
  unittest.main()
