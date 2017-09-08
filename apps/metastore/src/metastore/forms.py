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
from django.utils.translation import ugettext as _, ugettext_lazy as _t

from desktop.lib.django_forms import simple_formset_factory, DependencyAwareForm
from desktop.lib.django_forms import ChoiceOrOtherField, MultiForm, SubmitButton
from filebrowser.forms import PathField

from beeswax import common
from beeswax.models import SavedQuery


class DbForm(forms.Form):
  """For 'show tables'"""
  database = forms.ChoiceField(required=False,
                           label='',
                           choices=(('default', 'default'),),
                           initial=0,
                           widget=forms.widgets.Select(attrs={'class': 'input-medium'}))

  def __init__(self, *args, **kwargs):
    databases = kwargs.pop('databases')
    super(DbForm, self).__init__(*args, **kwargs)
    self.fields['database'].choices = ((db, db) for db in databases)


class LoadDataForm(forms.Form):
  """Form used for loading data into an existing table."""
  path = PathField(label=_t("Path"))
  overwrite = forms.BooleanField(required=False, initial=False, label=_t("Overwrite?"))
  is_embeddable = forms.BooleanField(required=False, initial=False)

  def __init__(self, table_obj, *args, **kwargs):
    """
    @param table_obj is a hive_metastore.thrift Table object,
    used to add fields corresponding to partition keys.
    """
    super(LoadDataForm, self).__init__(*args, **kwargs)
    self.partition_columns = dict()
    for i, column in enumerate(table_obj.partition_keys):
      # We give these numeric names because column names
      # may be unpleasantly arbitrary.
      name = "partition_%d" % i
      char_field = forms.CharField(required=True, label=_t("%(column_name)s (partition key with type %(column_type)s)") % {'column_name': column.name, 'column_type': column.type})
      self.fields[name] = char_field
      self.partition_columns[name] = column.name
