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

import logging
import json

from functools import wraps

from django.utils.translation import ugettext as _
from django.urls import reverse

from desktop.context_processors import get_app_name
from desktop.models import Document
from desktop.lib.django_util import render

from librdbms import conf
from librdbms.design import SQLdesign

from beeswax import models as beeswax_models
from beeswax.views import safe_get_design


LOG = logging.getLogger(__name__)


def index(request):
  return execute_query(request)


def configuration_error(request, *args, **kwargs):
  return render('error.mako', request, {})


"""
Decorators
"""
def ensure_configuration(view_func):
  def _decorator(*args, **kwargs):
    if conf.DATABASES.get():
      return view_func(*args, **kwargs)
    else:
      return configuration_error(*args, **kwargs)
  return wraps(view_func)(_decorator)


"""
Queries Views
"""
@ensure_configuration
def execute_query(request, design_id=None, query_history_id=None):
  """
  View function for executing an arbitrary synchronously query.
  """
  action = request.path
  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)

  return render('execute.mako', request, {
    'action': action,
    'doc_id': json.dumps(design.id and design.doc.get().id or -1),
    'design': design,
    'autocomplete_base_url': reverse('rdbms:api_autocomplete_databases', kwargs={}),
    'can_edit_name': design.id and not design.is_auto,
  })


@ensure_configuration
def save_design(request, save_form, query_form, type_, design, explicit_save=False):
  """
  save_design(request, save_form, query_form, type_, design, explicit_save) -> SavedQuery

  A helper method to save the design:
    * If ``explicit_save``, then we save the data in the current design.
    * If the user clicked the submit button, we do NOT overwrite the current
      design. Instead, we create a new "auto" design (iff the user modified
      the data). This new design is named after the current design, with the
      AUTO_DESIGN_SUFFIX to signify that it's different.

  Need to return a SavedQuery because we may end up with a different one.
  Assumes that form.saveform is the SaveForm, and that it is valid.
  """

  if type_ == beeswax_models.RDBMS:
    design_cls = SQLdesign
  else:
    raise ValueError(_('Invalid design type %(type)s') % {'type': type_})

  old_design = design
  design_obj = design_cls(query_form)
  new_data = design_obj.dumps()

  # Auto save if (1) the user didn't click "save", and (2) the data is different.
  # Don't generate an auto-saved design if the user didn't change anything
  if explicit_save:
    design.name = save_form.cleaned_data['name']
    design.desc = save_form.cleaned_data['desc']
    design.is_auto = False
  elif new_data != old_design.data:
    # Auto save iff the data is different
    if old_design.id is not None:
      # Clone iff the parent design isn't a new unsaved model
      design = old_design.clone()
      if not old_design.is_auto:
        design.name = old_design.name + beeswax_models.SavedQuery.AUTO_DESIGN_SUFFIX
    else:
      design.name = beeswax_models.SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.is_auto = True

  design.name = design.name[:64]
  design.type = type_
  design.data = new_data

  design.save()

  LOG.info('Saved %s design "%s" (id %s) for %s' % (design.name and '' or 'auto ', design.name, design.id, design.owner))

  if design.doc.exists():
    design.doc.update(name=design.name, description=design.desc)
  else:
    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)

  if design.is_auto:
    design.doc.get().add_to_history()

  return design
