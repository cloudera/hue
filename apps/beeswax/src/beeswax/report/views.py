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

from django.core import urlresolvers

from desktop.lib.django_util import render

from beeswaxd.ttypes import BeeswaxException
import beeswax.report.design
from beeswax.report import report_gen_views

from beeswax import models
import beeswax.views

def edit_report(request, design_id=None):
  """View function for the Report Generator."""
  action = request.path
  mform = report_gen_views.report_form()
  design = beeswax.views.safe_get_design(request, models.SavedQuery.REPORT, design_id)
  error_message = None
  log = None

  # Use a loop structure to allow the use of 'break' to get out
  for _ in range(1):
    # Always bind to POST data, and update the design accordingly
    if request.method == 'POST':
      mform.bind(request.POST)
      report_gen_views.fixup_union(mform, subform_name='union', data=request.POST, is_root=True)

      to_submit = request.POST.has_key('button-submit')
      to_advanced = request.POST.has_key('button-advanced')
      # Always validate the saveform, which will tell us whether it needs explicit saving
      if not mform.saveform.is_valid():
        break
      to_save = mform.saveform.cleaned_data['save']
      if to_submit or to_advanced or to_save:
        design = beeswax.views.save_design(
                            request, mform, models.SavedQuery.REPORT, design, to_save)
        action = urlresolvers.reverse(beeswax.views.edit_report, kwargs=dict(design_id=design.id))

      # Submit?
      if (to_advanced or to_submit) and mform.is_valid():
        query_str = report_gen_views.construct_query(mform)
        if to_advanced:
          return beeswax.views.confirm_query(request, query_str)
        elif to_submit:
          query_msg = beeswax.views.make_beeswax_query(request, query_str)
          try:
            return beeswax.views.execute_directly(request, query_msg, design)
          except BeeswaxException, ex:
            error_message, log = beeswax.views.expand_exception(ex)
      # Fall through if just adding a new column.
    else:
      if design.id is not None:
        data = beeswax.report.design.ReportDesign.loads(design.data).get_query_dict()
        mform.bind(data)
        mform.saveform.set_data(design.name, design.desc)
        report_gen_views.fixup_union(mform, subform_name='union', data=data, is_root=True)
      else:
        # New design
        mform.bind()

  return render('report_gen.mako', request, dict(
    action=action,
    design=design,
    mform=mform,
    error_message=error_message,
    log=log,
  ))
