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

from builtins import object
import logging
import pytest

from django import forms
from beeswax.forms import _clean_terminator


LOG = logging.getLogger()


class TestCreateTable(object):

  def test_custom_delimiter(self):
    # Any thing is good
    assert '\x01' == _clean_terminator('\001')
    with pytest.raises(forms.ValidationError):
      _clean_terminator('')
