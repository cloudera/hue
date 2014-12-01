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

import json
import logging

from desktop.lib.django_util import render
from desktop.models import Document2

from spark.decorators import view_error_handler
from spark.models import Notebook

LOG = logging.getLogger(__name__)


@view_error_handler
def editor(request):
  notebook_id = request.GET.get('notebook')
  
  if notebook_id:
    notebook = Notebook(document=Document2.objects.get(id=notebook_id)) # Todo perms
  else:
    notebook = Notebook()
    
  return render('editor.mako', request, {
      'notebooks_json': json.dumps([notebook.get_data()])
  })


def list_notebooks(request):
  notebooks = Document2.objects.filter(type='notebook', owner=request.user)

  return render('list_notebooks.mako', request, {
      'notebooks': notebooks
  })