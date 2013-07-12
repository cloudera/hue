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

try:
  import json
except ImportError:
  import simplejson as json
import logging
import re
import base64

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.translation import ugettext as _

from desktop.lib.django_util import render
from desktop.lib.exceptions_renderable import PopupException

from hbase import conf
from hbase.api import HbaseApi
from server.hbase_lib import get_thrift_type

LOG = logging.getLogger(__name__)


def app(request):
  return render('app.mako', request, {})

#action/cluster/arg1/arg2/arg3...
def api_router(request, url): #on split, deserialize anything
  def safe_json_load(raw):
    try:
      return json.loads(re.sub(r'(?:\")([0-9]+)(?:\")', r'\1', str(raw).replace("'", "\"")))
    except:
      return raw
  def deserialize(data):
    if type(data) == dict:
      special_type = get_thrift_type(data.pop('hue-thrift-type', ''))
      if special_type:
        return special_type(data)
    if hasattr(data, "__iter__"):
      for i, item in enumerate(data):
        data[i] = deserialize(item) #sets local binding, needs to set in data
    return data
  url_params = [safe_json_load((arg, request.POST.get(arg[0:16], arg))[arg[0:15] == 'hbase-post-key-']) for arg in re.split(r'(?<!\\)/', url.strip('/'))] #deserialize later
  return api_dump(HbaseApi().query(*url_params))

def api_dump(response):
  ignored_fields = ('thrift_spec', "__.+__")
  HARD_LIMIT = conf.TRUNCATE_LIMIT.get()
  truncateCount = [0]
  truncated = [False]
  def clean(data):
    try:
      json.dumps(data)
      return data
    except:
      cleaned = {}
      lim = [0]
      def step(data):
        lim[0] += 1
        if lim[0] > HARD_LIMIT:
          truncateCount[0] += len(data) - HARD_LIMIT
          truncated[0] = True
          return True
        return False
      if isinstance(data, str): #not JSON dumpable, meaning some sort of bytestring or byte data
        return base64.b64encode(data)
      if hasattr(data, "__iter__"):
        if type(data) is dict:
          for i in data:
            cleaned[i] = clean(data[i])
            if step(data): break
        elif type(data) is list:
          cleaned = []
          for i, item in enumerate(data):
            cleaned += [clean(item)]
            if step(data): break
        else:
          for i, item in enumerate(data):
            cleaned[i] = clean(item)
            if step(data): break
      else:
        for key in dir(data):
          value = getattr(data, key)
          if value is not None and not hasattr(value, '__call__') and sum([int(bool(re.search(ignore, key))) for ignore in ignored_fields]) == 0:
            cleaned[key] = clean(value)
            if step(dir(data)): break
      return cleaned
  return HttpResponse(json.dumps({ 'data': clean(response), 'truncated': truncated[0], 'limit': HARD_LIMIT, 'truncate_count': truncateCount[0] }), content_type="application/json")