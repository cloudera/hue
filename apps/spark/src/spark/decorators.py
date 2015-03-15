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

from django.http import Http404
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import force_unicode

from spark.models import QueryExpired, QueryError, SessionExpired
from desktop.models import Document2, Document


LOG = logging.getLogger(__name__)


def check_document_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      notebook_id = request.GET.get('notebook')
      if not notebook_id:
        notebook_id = json.loads(request.POST.get('notebook', '{}')).get('id')

      try:
        if notebook_id:
          document = Document2.objects.get(id=notebook_id)
          document.doc.get().can_read_or_exception(request.user)
      except Document2.DoesNotExist:
        raise PopupException(_('Document %(id)s does not exist') % {'id': notebook_id})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_document_modify_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      notebook = json.loads(request.POST.get('notebook', '{}'))

      try:
        if notebook.get('id'):
          doc2 = Document2.objects.get(id=notebook['id'])
          doc2.doc.get().can_write_or_exception(request.user)
      except Document.DoesNotExist:
        raise PopupException(_('Job %(id)s does not exist') % {'id': notebook.get('id')})

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def api_error_handler(func):
  def decorator(*args, **kwargs):
    response = {}
    
    try:
      return func(*args, **kwargs)
    except SessionExpired, e:
      response['status'] = -2    
    except QueryExpired, e:
      response['status'] = -3
    except QueryError, e:
      response['status'] = 1
      response['message'] = force_unicode(str(e))
    except Exception, e:
      response['status'] = -1
      response['message'] = force_unicode(str(e))
    finally:
      if response:
        return JsonResponse(response)

  return decorator


def json_error_handler(view_fn):
  def decorator(*args, **kwargs):
    try:
      return view_fn(*args, **kwargs)
    except Http404, e:
      raise e
    except Exception, e:
      response = {
        'error': str(e)
      }
      return JsonResponse(response, status=500)
  return decorator
