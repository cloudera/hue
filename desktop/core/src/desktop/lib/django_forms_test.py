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
from desktop.lib.django_forms import DependencyAwareForm
from django import forms


def test_dependency_aware_form():
  class Form(DependencyAwareForm):
    cond = forms.BooleanField(required=False)
    if_true = forms.CharField(required=False)
    if_false = forms.CharField(required=False)

    dependencies = [
      ("cond", True, "if_true")
    ]
    dependencies += [
      ("cond", False, "if_false")
    ]

  assert Form({'cond': '', 'if_false': 'hi'}).is_valid()
  assert Form({'cond': 'on', 'if_true': 'hi'}).is_valid()
  assert not Form({}).is_valid()
  # Because 'cond' is a boolean field, if it's not specified,
  # it renders as False in the form.
  f = Form({'if_false': ''})
  assert not f.is_valid()
  # Make sure errors gets populated
  assert 1 == len(f.errors["if_false"])
  assert Form({'if_false': 'foo'}).is_valid()

  a = Form(prefix="prefix")
  assert [('prefix-cond', "True", "prefix-if_true"), ('prefix-cond', 'False', 'prefix-if_false')] == a._calculate_data()
  assert " " not in a.render_dep_metadata()

  # Check that cleaned_data still gets populated.
  f = Form({'if_false': 'foo'})
  f.is_valid()
  assert f.cleaned_data
