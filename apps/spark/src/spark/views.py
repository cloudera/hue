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

from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.lib.json_utils import JSONEncoderForHTML
from desktop.models import Document2

from spark.conf import LANGUAGES
from spark.models import Notebook, get_api

LOG = logging.getLogger(__name__)


def editor(request):
  notebook_id = request.GET.get('notebook')
  
  if notebook_id:
    notebook = Notebook(document=Document2.objects.get(id=notebook_id)) # Todo perms
  else:
    notebook = Notebook()
    
  return render('editor.mako', request, {
      'notebooks_json': json.dumps([notebook.get_data()]),
      'options_json': json.dumps({
          'languages': LANGUAGES.get(),
          'snippet_placeholders' : {
              'scala': _('Example: 1 + 1, or press CTRL + space'),
              'python': _('Example: 1 + 1, or press CTRL + space'),
              'impala': _('Example: SELECT * FROM tablename, or press CTRL + space'),
              'hive': _('Example: SELECT * FROM tablename, or press CTRL + space'),
          }
      })
  })


def new(request):
  return editor(request)
  

def notebooks(request):
  notebooks = [d.to_dict() for d in Document2.objects.filter(type='notebook', owner=request.user)]

  return render('notebooks.mako', request, {
      'notebooks_json': json.dumps(notebooks, cls=JSONEncoderForHTML)
  })


def download(request):
  notebook = json.loads(request.POST.get('notebook', '{}'))
  snippet = json.loads(request.POST.get('snippet', '{}'))
  file_format = request.POST.get('format', 'csv')

  return get_api(request.user, snippet).download(notebook, snippet, file_format)

