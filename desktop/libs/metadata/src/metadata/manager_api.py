#!/usr/bin/env python
# -- coding: utf-8 --
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
import os

from django.http import Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.auth.backend import is_admin
from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from libzookeeper.conf import zkensemble
from indexer.conf import config_morphline_path

from metadata.catalog.navigator_client import CatalogApiException
from metadata.conf import has_catalog
from metadata.manager_client import ManagerApi


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    status = 500
    response = {
      'message': ''
    }

    try:
      if has_catalog(args[0].user): # TODO
        return view_fn(*args, **kwargs)
      else:
        raise CatalogApiException('Navigator API is not configured.')
    except CatalogApiException, e:
      try:
        response['message'] = json.loads(e.message)
      except Exception:
        response['message'] = force_unicode(e.message)
    except Exception, e:
      message = force_unicode(e)
      response['message'] = message
      LOG.exception(message)

    return JsonResponse(response, status=status)
  return decorator


def admin_only_handler(view_fn):
  def decorator(*args, **kwargs):
    if is_admin(args[0].user):
      return view_fn(*args, **kwargs)
    else:
      raise CatalogApiException('Manager API is for admins only.')

  return decorator


@error_handler
def hello(request):
  api = ManagerApi(request.user)

  response = api.tools_echo()

  return JsonResponse(response)


@error_handler
def get_hosts(request):
  response = {
    'status': 0
  }
  api = ManagerApi(request.user)

  if request.POST.get('service', '').lower() == 'flume':
    response['hosts'] = api.get_flume_agents()

  return JsonResponse(response)


@error_handler
@admin_only_handler
def update_flume_config(request):
  api = ManagerApi(request.user)

  flume_agent_config = '''tier1.sources = source1
tier1.channels = channel1
tier1.sinks = sink1

tier1.sources.source1.type = exec
tier1.sources.source1.command = tail -F /var/log/hue-httpd/access_log
tier1.sources.source1.channels = channel1

tier1.channels.channel1.type = memory
tier1.channels.channel1.capacity = 10000
tier1.channels.channel1.transactionCapacity = 1000

# Solr Sink configuration
tier1.sinks.sink1.type          = org.apache.flume.sink.solr.morphline.MorphlineSolrSink
tier1.sinks.sink1.morphlineFile = morphlines.conf
tier1.sinks.sink1.morphlineId = hue_accesslogs_no_geo
tier1.sinks.sink1.channel       = channel1'''


  morphline_config = open(os.path.join(config_morphline_path(), 'hue_accesslogs_no_geo.morphline.conf')).read()
  morphline_config = morphline_config.replace(
    '${SOLR_COLLECTION}', 'log_analytics_demo'
  ).replace(
    '${ZOOKEEPER_ENSEMBLE}', '%s/solr' % zkensemble()
  )

  responses = {}

  responses['agent_config_file'] = api.update_flume_config(cluster_name=None, config_name='agent_config_file', config_value=flume_agent_config)
  responses['agent_morphlines_conf_file'] = api.update_flume_config(cluster_name=None, config_name='agent_morphlines_conf_file', config_value=morphline_config)

  responses['refresh_flume'] = api.refresh_flume(cluster_name=None, restart=True)

  return JsonResponse(responses)
