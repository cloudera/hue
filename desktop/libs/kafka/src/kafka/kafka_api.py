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

from django.http import Http404
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from metadata.manager_client import ManagerApi

from kafka.conf import has_kafka_api
from kafka.kafka_client import KafkaApi, KafkaApiException


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    status = 500
    response = {
      'message': ''
    }

    try:
      return view_fn(*args, **kwargs)
    except KafkaApiException, e:
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


@error_handler
def list_topics(request):
  return JsonResponse({
    'status': 0,
    'topics': [{'name': topic} for topic in get_topics()]
  })


@error_handler
def list_topic(request):
  name = request.POST.get('name')

  topic = get_topic(name)
  topic['name'] = name
  topic['type'] = 'topic'

  return JsonResponse({
    'status': 0,
    'topic': topic
  })


@error_handler
def create_topic(request):
  name = request.POST.get('name')
  partitions = request.POST.get('partitions', 1)
  replication_factor = request.POST.get('replication_factor', 1)

  status = KafkaApi().create_topic(name, partitions, replication_factor)

  return JsonResponse({
    'status': status,
    'topic': {
      'name': name,
      'partitions': partitions,
      'replication_factor': replication_factor
    }
  })


def get_topics():
  if has_kafka_api():
    return KafkaApi().topics()
  else:
    try:
      manager = ManagerApi()
      broker_host = manager.get_kafka_brokers().split(',')[0].split(':')[0]
      return [name for name in manager.get_kafka_topics(broker_host).keys() if not name.startswith('__')]
    except Exception, e:
      print e
      return ["traffic", "hueAccessLogs"]


def get_topic(name):
  if has_kafka_api():
    pass
  else:
    manager = ManagerApi()
    broker_host = manager.get_kafka_brokers().split(',')[0].split(':')[0]
    return manager.get_kafka_topics(broker_host)[name]
