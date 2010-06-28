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
"""
Mix-in implementations for the "forms" functionality.
"""
import copy
import logging
import simplejson

from django.template.loader import render_to_string
from django import forms
from jobsub.parameterization import find_variables, substitute_variables

LOG = logging.getLogger(__name__)

class DjangoFormBasedEditForm(object):
  """
  A mix-in for JobSubForms that manages edits that 
  are controlled with a django form, which is
  accessed via self.DjangoForm.

  Stores the cleaned_data of the form in self.data
  """
  def serialize_to_string(self):
    return simplejson.dumps(self.data)

  def deserialize_from_string(self, data):
    self.data = simplejson.loads(data)
    self.django_form = self.DjangoForm()
    for key, value in self.data.iteritems():
      self.django_form.initial[key] = value

  def is_valid_edit(self, post_data):
    self.django_form = self.DjangoForm(post_data)
    if self.django_form.is_valid():
      self.data = self.django_form.cleaned_data
      return True
    else:
      return False

class BasicParameterizationForm(object):
  """
  A mix-in for JobSubForms that implements simple, default parameterization
  on self.data.
  """
  @staticmethod
  def _parameterization_form(data):
    """
    Returns a Django form appropriate to parameterizing data.
    """
    variables = find_variables(data)
    
    class Form(forms.Form):
      # These are special-cased, since we have help-text available for them.
      if "input" in variables:
        input = forms.CharField(required=True, help_text="Path to input.")
      if "output" in variables:
        output = forms.CharField(required=True, help_text="Must be a non-existant directory.")
      
      for name in sorted(variables.difference(set(["intput", "output"]))):
        locals()[name]= forms.CharField(required=True)

    return Form

  def is_valid_parameterization(self, post_data):
    self.parameterization_form = self._parameterization_form(self.data)(post_data)
    if self.parameterization_form.is_valid():
      self.parameterization_data = self.parameterization_form.cleaned_data
      self.parameterized_data = substitute_variables(copy.deepcopy(self.data),
        self.parameterization_data)
      return True
    else:
      return False

  def render_parameterization(self):
    if not hasattr(self, "parameterization_form"):
      self.parameterization_form = self._parameterization_form(self.data)()
    return render_to_string("forms/basic_parameterization.html", dict(form=self.parameterization_form))
