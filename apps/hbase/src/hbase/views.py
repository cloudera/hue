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

from future import standard_library
standard_library.install_aliases()
from builtins import str
import base64
import json
import logging
import re
import io
import urllib.request, urllib.parse, urllib.error

from avro import datafile, io

from django.utils.translation import ugettext as _

from desktop.lib.django_util import JsonResponse, render

from hbase import conf
from hbase.hbase_site import is_impersonation_enabled
from hbase.settings import DJANGO_APPS
from hbase.api import HbaseApi
from hbase.management.commands import hbase_setup
from hbase.server.hbase_lib import get_thrift_type

from desktop.auth.backend import is_admin

LOG = logging.getLogger(__name__)


def has_write_access(user):
  return is_admin(user) or user.has_hue_permission(action="write", app=DJANGO_APPS[0]) or is_impersonation_enabled()

def app(request):
  return render('app.mako', request, {
    'can_write': has_write_access(request.user),
    'is_embeddable': request.GET.get('is_embeddable', False),
  })

# action/cluster/arg1/arg2/arg3...
def api_router(request, url): # On split, deserialize anything

  def safe_json_load(raw):
    try:
      return json.loads(re.sub(r'(?:\")([0-9]+)(?:\")', r'\1', str(raw)))
    except:
      LOG.debug('Failed to parse input as JSON, falling back to raw input.')
      return raw

  def deserialize(data):
    if type(data) == dict:
      special_type = get_thrift_type(data.pop('hue-thrift-type', ''))
      if special_type:
        return special_type(data)

    if hasattr(data, "__iter__"):
      for i, item in enumerate(data):
        data[i] = deserialize(item) # Sets local binding, needs to set in data
    return data

  decoded_url_params = [urllib.parse.unquote(arg) for arg in re.split(r'(?<!\\)/', url.strip('/'))]
  url_params = [safe_json_load((arg, request.POST.get(arg[0:16], arg))[arg[0:15] == 'hbase-post-key-'])
                for arg in decoded_url_params] # Deserialize later

  if request.POST.get('dest', False):
    url_params += [request.FILES.get(request.GET.get('dest'))]

  return api_dump(HbaseApi(request.user).query(*url_params))

def api_dump(response):
  ignored_fields = ('thrift_spec', '__.+__')
  trunc_limit = conf.TRUNCATE_LIMIT.get()

  def clean(data):
    try:
      json.dumps(data)
      return data
    except:
      LOG.debug('Failed to dump data as JSON, falling back to raw data.')
      cleaned = {}
      lim = [0]
      if isinstance(data, str): # Not JSON dumpable, meaning some sort of bytestring or byte data
        #detect if avro file
        if(data[:3] == '\x4F\x62\x6A'):
          #write data to file in memory
          output = io.StringIO()
          output.write(data)

          #read and parse avro
          rec_reader = io.DatumReader()
          df_reader = datafile.DataFileReader(output, rec_reader)
          return json.dumps(clean([record for record in df_reader]))
        return base64.b64encode(data)

      if hasattr(data, "__iter__"):
        if type(data) is dict:
          for i in data:
            cleaned[i] = clean(data[i])
        elif type(data) is list:
          cleaned = []
          for i, item in enumerate(data):
            cleaned += [clean(item)]
        else:
          for i, item in enumerate(data):
            cleaned[i] = clean(item)
      else:
        for key in dir(data):
          value = getattr(data, key)
          if value is not None and not hasattr(value, '__call__') and sum([int(bool(re.search(ignore, key)))
                                                                           for ignore in ignored_fields]) == 0:
            cleaned[key] = clean(value)
      return cleaned

  return JsonResponse({
    'data': clean(response),
    'truncated': True,
    'limit': trunc_limit,
    })


def install_examples(request):
  result = {'status': -1, 'message': ''}

  if request.method != 'POST':
    result['message'] = _('A POST request is required.')
  else:
    try:
      hbase_setup.Command().handle(user=request.user)
      result['status'] = 0
    except Exception as e:
      LOG.exception(e)
      result['message'] = str(e)

  return JsonResponse(result)
