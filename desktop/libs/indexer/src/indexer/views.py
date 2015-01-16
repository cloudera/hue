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

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse, render

from indexer.management.commands import indexer_setup


LOG = logging.getLogger(__name__)


def collections(request, is_redirect=False):
  return render('collections.mako', request, {})


def install_examples(request, is_redirect=False):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      indexer_setup.Command().handle_noargs()
      result['status'] = 0
    except Exception, e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
