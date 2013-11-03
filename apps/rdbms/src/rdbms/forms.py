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

from django import forms
from django.utils.translation import ugettext_lazy as _t


class SQLForm(forms.Form):
  query = forms.CharField(label=_t("Query Editor"),
                          required=True,
                          widget=forms.Textarea(attrs={'class': 'beeswax_query'}))
  is_parameterized = forms.BooleanField(required=False, initial=True)
  email_notify = forms.BooleanField(required=False, initial=False)
  type = forms.IntegerField(required=False, initial=0)
  server = forms.ChoiceField(required=False,
                             label='',
                             choices=(('default', 'default'),),
                             initial=0,
                             widget=forms.widgets.Select(attrs={'class': 'input-medium'}))
  database = forms.ChoiceField(required=False,
                           label='',
                           choices=(('default', 'default'),),
                           initial=0,
                           widget=forms.widgets.Select(attrs={'class': 'input-medium'}))
