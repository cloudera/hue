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
Views & controls for creating tables
"""

import logging

from django.urls import reverse

from desktop.lib import django_mako
from desktop.lib.django_util import render

from beeswax.design import hql_query
from beeswax.forms import CreateDatabaseForm
from beeswax.views import execute_directly


LOG = logging.getLogger(__name__)


def create_database(request):

  if request.method == "POST":
    data = request.POST.copy()
    data.setdefault("use_default_location", False)
    form = CreateDatabaseForm(data)

    if form.is_valid():
      proposed_query = django_mako.render_to_string("create_database_statement.mako", {
        'database': form.cleaned_data,
      })
      query = hql_query(proposed_query)
      return execute_directly(request, query, on_success_url=reverse('metastore:databases'))
  else:
    form = CreateDatabaseForm()

  return render("create_database.mako", request, {
    'database_form': form,
  })
