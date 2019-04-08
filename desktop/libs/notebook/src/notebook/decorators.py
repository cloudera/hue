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
import math
import re

from django.forms import ValidationError
from django.http import Http404
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from desktop.models import Document2, Document, FilesystemException
from dashboard.models import extract_solr_exception_message

from notebook.conf import check_permissions
from notebook.connectors.base import QueryExpired, QueryError, SessionExpired, AuthenticationRequired, OperationTimeout,\
  OperationNotSupported


LOG = logging.getLogger(__name__)

def check_editor_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      editor_id = request.GET.get('type', 'hive')

      if check_permissions(request.user, editor_id):
        raise PopupException(_('Missing permission to access the %s Editor' % editor_id), error_code=401)
      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner

def check_document_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      notebook_id = request.GET.get('notebook', request.GET.get('editor'))
      if not notebook_id:
        notebook_id = json.loads(request.POST.get('notebook', '{}')).get('id')

      try:
        if notebook_id:
          if str(notebook_id).isdigit():
            document = Document2.objects.get(id=notebook_id)
            document.can_read_or_exception(request.user)
          else:
            Document2.objects.get_by_uuid(user=request.user, uuid=notebook_id)
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
          doc2 = Document2.objects.get(uuid=notebook['parentSavedQueryUuid']) if notebook.get('parentSavedQueryUuid') else \
            Document2.objects.get(id=notebook['id'])
          doc2.can_write_or_exception(request.user)
      except Document.DoesNotExist:
        raise PopupException(_('Document %(id)s does not exist') % {'id': notebook.get('id')})

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
      if e.message and isinstance(e.message, basestring):
        response['message'] = e.message
    except AuthenticationRequired, e:
      response['status'] = 401
      if e.message and isinstance(e.message, basestring):
        response['message'] = e.message
    except ValidationError, e:
      LOG.exception('Error validation %s' % func)
      response['status'] = -1
      response['message'] = e.message
    except OperationTimeout, e:
      response['status'] = -4
    except FilesystemException, e:
      response['status'] = 2
      response['message'] = e.message
    except QueryError, e:
      LOG.exception('Error running %s' % func.__name__)
      response['status'] = 1
      response['message'] = smart_unicode(e)
      if response['message'].index("max_row_size"):
        size = re.search(r"(\d+.?\d*) (.B)", response['message'])
        if size and size.group(1):
          response['help'] = {
            'setting': {
              'name': 'max_row_size',
              'value':str(int(_closest_power_of_2(_to_size_in_bytes(size.group(1), size.group(2)))))
            }
          }
      if e.handle:
        response['handle'] = e.handle
      if e.extra:
        response.update(e.extra)
    except OperationNotSupported, e:
      response['status'] = 5
      response['message'] = e.message
    except RestException, e:
      message = extract_solr_exception_message(e)
      response['status'] = 1
      response['message'] = message.get('error')
    except Exception, e:
      LOG.exception('Error running %s' % func.__name__)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    finally:
      if response:
        return JsonResponse(response)

  return decorator

def _closest_power_of_2(number):
  return math.pow(2, math.ceil(math.log(number, 2)))

def _to_size_in_bytes(size, unit):
  unit_size = 1
  unit = unit.upper()
  if unit[0] == 'K':
    unit_size = unit_size * 1024
  elif unit[0] == 'M':
    unit_size = unit_size * 1024 * 1024
  elif unit[0] == 'G':
    unit_size = unit_size * 1024 * 1024 * 1024
  elif unit[0] == 'T':
    unit_size = unit_size * 1024 * 1024 * 1024 * 1024

  return float(size) * unit_size

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
