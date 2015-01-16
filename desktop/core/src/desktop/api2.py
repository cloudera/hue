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

import itertools
import logging
import json
import time

from collections import defaultdict

from django.core.urlresolvers import reverse

from django.utils import html
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from desktop.models import Document2, DocumentTag


LOG = logging.getLogger(__name__)


def get_document(request):
  if request.GET.get('id'):
    doc = Document2.objects.get(id=request.GET['id'])
  else:
    doc = Document2.objects.get(uuid=request.GET['uuid'])

  response = _massage_doc_for_json(doc, request.user, with_data=request.GET.get('with_data'))

  return JsonResponse(response)


def _massage_doc_for_json(document, user, with_data=False):

  massaged_doc = {
    'id': document.id,
    'uuid': document.uuid,
    
    'owner': document.owner.username,
    'type': html.conditional_escape(document.type),    
    'name': html.conditional_escape(document.name),
    'description': html.conditional_escape(document.description),    

    'isMine': document.owner == user,
    'lastModified': document.last_modified.strftime("%x %X"),
    'lastModifiedInMillis': time.mktime(document.last_modified.timetuple()),
    'version': document.version,
    'is_history': document.is_history,
    
    # tags
    # dependencies
  }
  
  if with_data:
    massaged_doc['data'] = document.data_dict

  return massaged_doc
