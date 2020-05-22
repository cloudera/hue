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

from past.builtins import basestring
import json
import logging
import math
import re

from django.forms import ValidationError
from django.http import Http404
from django.utils.functional import wraps
from django.utils.translation import ugettext as _

from dashboard.models import extract_solr_exception_message
from desktop.lib.django_util import JsonResponse
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.i18n import smart_unicode
from desktop.lib.rest.http_client import RestException
from desktop.models import Document2, Document, FilesystemException

from notebook.conf import check_has_missing_permission, ENABLE_NOTEBOOK_2
from notebook.connectors.base import QueryExpired, QueryError, SessionExpired, AuthenticationRequired, OperationTimeout, \
  OperationNotSupported
from notebook.models import _get_editor_type


LOG = logging.getLogger(__name__)


def check_editor_access_permission():
  def inner(view_func):
    def decorate(request, *args, **kwargs):
      editor_id = request.GET.get('editor')
      editor_type = request.GET.get('type', 'hive')
      gist_id = request.POST.get('gist')

      if editor_type == 'gist' or gist_id: # Gist don't have permissions currently
        pass
      else:
        if editor_id:  # Open existing saved editor document
          try:
            editor_type = _get_editor_type(editor_id)
          except Document2.DoesNotExist:
            raise PopupException(_('Query id %s can not be found, please open a new editor') % editor_id)

        if check_has_missing_permission(request.user, editor_type):
          raise PopupException(_('Missing permission to access the %s Editor' % editor_type), error_code=401)

      return view_func(request, *args, **kwargs)
    return wraps(view_func)(decorate)
  return inner


def check_document_access_permission(f):
  @wraps(f)
  def wrapper(request, *args, **kwargs):
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

    return f(request, *args, **kwargs)
  return wrapper


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


def api_error_handler(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    response = {}

    try:
      return f(*args, **kwargs)
    except SessionExpired as e:
      response['status'] = -2
    except QueryExpired as e:
      if ENABLE_NOTEBOOK_2.get():
        response['query_status'] = {'status': 'expired'}
        response['status'] = 0
      else:
        response['status'] = -3
      if e.message and isinstance(e.message, basestring):
        response['message'] = e.message
    except AuthenticationRequired as e:
      response['status'] = 401
      if e.message and isinstance(e.message, basestring):
        response['message'] = e.message
    except ValidationError as e:
      LOG.exception('Error validation %s' % f)
      response['status'] = -1
      response['message'] = e.message
    except OperationTimeout as e:
      response['status'] = -4
    except FilesystemException as e:
      response['status'] = 2
      response['message'] = e.message or 'Query history not found'
    except QueryError as e:
      LOG.exception('Error running %s' % f.__name__)
      response['status'] = 1
      response['message'] = smart_unicode(e)
      if response['message'].index("max_row_size"):
        size = re.search(r"(\d+.?\d*) (.B)", response['message'])
        if size and size.group(1):
          response['help'] = {
            'setting': {
              'name': 'max_row_size',
              'value': str(int(_closest_power_of_2(_to_size_in_bytes(size.group(1), size.group(2)))))
            }
          }
      if e.handle:
        response['handle'] = e.handle
      if e.extra:
        response.update(e.extra)
    except OperationNotSupported as e:
      response['status'] = 5
      response['message'] = e.message
    except RestException as e:
      message = extract_solr_exception_message(e)
      response['status'] = 1
      response['message'] = message.get('error')
    except Exception as e:
      LOG.exception('Error running %s' % f.__name__)
      response['status'] = -1
      response['message'] = smart_unicode(e)
    finally:
      if response:
        return JsonResponse(response)

  return wrapper


def ssh_error_handler(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except Exception as e:
      if has_missing_ssh(message=str(e)):
        LOG.info('Opening SSH tunnel')
        from notebook.conf import _connector_to_iterpreter
        from desktop.lib.connectors.models import _augment_connector_properties

        if hasattr(args[0], 'POST'):
          if args[0].POST.get('session'):
            connector_c = args[0].POST['session']
          else:
            connector_c = args[0].POST.get('snippet')
          connector_json_data = json.loads(connector_c)
        else:
          connector_json_data = args[1]  # Task Server


        if connector_json_data.get('type') == 'hello':
          connector = connector_json_data['interpreter']
          idle_time = 10
        else:
          connector_id = int(connector_json_data.get('type'))
          connector_data = _get_installed_connectors(connector_id=connector_id)[0]
          connector = _connector_to_iterpreter(
            _augment_connector_properties(connector_data)
          )
          idle_time = 1800

        if not connector['options'].get('has_ssh'):
          raise e

        ssh_options = connector['options'].copy()

        ssh_options['idle_time'] = idle_time

        if connector['interface'] in ('sqlalchemy', 'ksql', 'flink'):
          ssh_url = rewrite_ssh_api_url(ssh_options['url'])

          ssh_options['server_host'] = ssh_url['server_host']
          ssh_options['server_port'] = ssh_url['server_port']

        if '@' in ssh_options['ssh_server_host']:
          ssh_options['ssh_server_user'], ssh_options['ssh_server_host'] = ssh_options['ssh_server_host'].rsplit('@')
        else:
          ssh_options['ssh_server_user'] = 'gethue'

        # Docs: https://gist.github.com/scy/6781836
        # TODO: local server_port needs to be dynamic (first server_port)
        # TODO: "Could not request local forwarding" not bubbled up
        # TODO: grep: no sleep 10: No such file or directory?
        ssh = "ssh -f -L %(server_port)s:%(server_host)s:%(server_port)s %(ssh_server_user)s@%(ssh_server_host)s -o ExitOnForwardFailure=yes" % ssh_options
        ssh += ' -4'
        ssh += ' -o StrictHostKeyChecking=no'
        ssh += ' sleep %(idle_time)s' % ssh_options

        LOG.info(ssh)

        if len(list(os.popen('ps -ef | grep "%s"' % ssh))) < 3:
          FNULL = open(os.devnull, 'w')
          subprocess.Popen(ssh.split(' '), stdout=FNULL, stderr=FNULL)

          retries = 0

          while retries < 5:
            try:
              return f(*args, **kwargs)
            except Exception as e2:
              if has_missing_ssh(message=str(e2)):
                time.sleep(1)
                retries += 1
              else:
                raise e2
          raise e
        else:
          raise e
      else:
        raise e
  return wrapper


def has_missing_ssh(message):
  return 'Connection refused' in message or 'Could not connect' in message or 'No route to host' in message \
      or 'Missing SSH tunnel' in message


def rewrite_ssh_api_url(url):
  m = re.search('(?:.*://|@)?(?P<host>[^:/ ]+).?(?P<port>[0-9]*).*', url)
  server_host = m.group('host')
  server_port = m.group('port')

  if not server_host:
    raise QueryError('Hostname of %(url)s could not be found.' % url)
  if not server_port:
    raise QueryError('Port of %(url)s could not be found.' % url)

  return {
    'server_host': server_host,
    'server_port': server_port,
    'url': re.sub(server_host, '127.0.0.1', url)
  }


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
    except Http404 as e:
      raise e
    except Exception as e:
      response = {
        'error': str(e)
      }
      return JsonResponse(response, status=500)
  return decorator
