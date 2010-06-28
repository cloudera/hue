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
The ReportDesign class can (de)serialize a design to/from a QueryDict.
"""

import logging
import simplejson
import django.http

from desktop.lib.django_forms import MultiForm

from beeswax.design import denormalize_form_dict
from beeswax.design import denormalize_formset_dict
from beeswax.design import normalize_form_dict
from beeswax.design import normalize_formset_dict
from beeswax.design import SERIALIZATION_VERSION

from beeswax.report import report_gen_views


LOG = logging.getLogger(__name__)

class ReportDesign(object):
  """
  Represents a report design, with methods to perform (de)serialization.
  """
  _COLUMN_ATTRS = [ 'display', 'source', 'agg', 'distinct', 'constant', 'table', 'table_alias',
                    'col', 'col_alias', 'sort', 'sort_order', 'group_order' ]
  _COND_ATTRS = [ 'l_source', 'l_table', 'l_col', 'l_constant', 'op',
                  'r_source', 'r_table', 'r_col', 'r_constant' ]
  _BOOL_ATTRS = [ 'bool' ]

  def __init__(self, form):
    """Initialize the design from form data. The form may be invalid."""
    assert isinstance(form, MultiForm)
    self._data_dict = dict(
        columns = normalize_formset_dict(form.columns, ReportDesign._COLUMN_ATTRS))
    self._data_dict['union'] = self._normalize_union_mform(form.union)


  def _normalize_union_mform(self, union_mform):
    """
    Normalize the subunions in the MultiForm recursively.
    Returns a data dict.
    """
    data_dict = dict(
        bools = normalize_form_dict(union_mform.bool, ReportDesign._BOOL_ATTRS),
        conds = normalize_formset_dict(union_mform.conds, ReportDesign._COND_ATTRS))

    subunion_list = [ ]
    for name, subform in union_mform.get_subforms():
      if name.startswith(report_gen_views.SUB_UNION_PREFIX):
        dic = self._normalize_union_mform(subform)
        subunion_list.append(dic)
    data_dict['subunions'] = subunion_list
    return data_dict


  def dumps(self):
    """Returns the serialized form of the design in a string"""
    dic = self._data_dict.copy()
    dic['VERSION'] = SERIALIZATION_VERSION
    return simplejson.dumps(dic)


  def get_query_dict(self):
    """get_query_dict() -> QueryDict"""
    # We construct the mform to use its structure and prefix. We don't actually bind
    # data to the forms.
    mform = report_gen_views.report_form()
    mform.bind()

    res = django.http.QueryDict('', mutable=True)
    res.update(denormalize_formset_dict(
                self._data_dict['columns'], mform.columns, ReportDesign._COLUMN_ATTRS))
    res.update(self._denormalize_union_mform(self._data_dict['union'], mform.union))
    return res


  def _denormalize_union_mform(self, data_dict, mform):
    """Returns a QueryDict"""
    res = django.http.QueryDict('', mutable=True)
    res.update(denormalize_form_dict(data_dict['bools'], mform.bool, ReportDesign._BOOL_ATTRS))
    res.update(denormalize_formset_dict(data_dict['conds'], mform.conds, ReportDesign._COND_ATTRS))

    subunion_dict_list = data_dict['subunions']
    for i, subunion_dict in enumerate(subunion_dict_list):
      # Make a subform on the fly and denormalize that recursively
      name = '%s%d' % (report_gen_views.SUB_UNION_PREFIX, i)
      mform.add_subform(name, report_gen_views.UnionMultiForm)
      res.update(self._denormalize_union_mform(subunion_dict, getattr(mform, name)))

    res[mform.mgmt.add_prefix('next_form_id')] = str(len(subunion_dict_list))
    return res


  @staticmethod
  def loads(data):
    """Returns an HQLdesign from the serialized form"""
    dic = simplejson.loads(data)
    if dic['VERSION'] != SERIALIZATION_VERSION:
      LOG.error('Report design version mismatch. Found %s; expect %s' %
                (dic['VERSION'], SERIALIZATION_VERSION))
      return None
    del dic['VERSION']

    design = ReportDesign.__new__(ReportDesign)
    design._data_dict = dic
    return design
