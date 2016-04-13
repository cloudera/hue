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

from django.forms import util
from django.forms import fields
from django import forms
import json

class JsonFormField(fields.CharField):
  """
  Django field for validation JSON data.

  Note that this is a form field that defines validation routines,
  not a Model Field.
  
  See http://docs.djangoproject.com/en/1.0/ref/forms/validation/ for details.

  The Hampi DataFlowForm class has example usage.
  """

  widget = forms.Textarea

  default_error_messages = {
    'malformed_json': u'Unable to validate JSON'
    }
  
  def clean(self, value):
    value = super(JsonFormField, self).clean(value)
    try:
      json.loads(value)
    except ValueError, e:
      raise util.ValidationError(e)
    return value
  
