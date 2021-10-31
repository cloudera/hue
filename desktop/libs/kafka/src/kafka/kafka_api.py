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
import sys

from desktop.lib.django_util import JsonResponse
from desktop.lib.i18n import force_unicode
from metadata.manager_client import ManagerApi
from notebook.models import _get_notebook_api

from kafka.conf import has_kafka_api
from kafka.kafka_client import KafkaApi, KafkaApiException, SchemaRegistryApi

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


def error_handler(view_fn):
  def decorator(*args, **kwargs):
    status = 500
    response = {
      'message': ''
    }

    try:
      return view_fn(*args, **kwargs)
    except KafkaApiException as e:
      try:
        response['message'] = json.loads(e.message)
      except Exception:
        response['message'] = force_unicode(e.message)
    except Exception as e:
      message = force_unicode(e)
      response['message'] = message
      LOG.exception(message)

    return JsonResponse(response, status=status)
  return decorator


@error_handler
def list_topics(request):
  return JsonResponse({
    'status': 0,
    'topics': [
      {'name': topic} for topic in get_topics(request.user)
    ]
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


def get_topics(user):
  if has_kafka_api():
    return KafkaApi().topics()
  else:
    data = {
      'snippet': {},
      'database': 'topics'
    }

    from desktop.api_public import _get_interpreter_from_dialect  # Avoid circular import
    interpreter = _get_interpreter_from_dialect('ksql', user)
    api = _get_notebook_api(user, connector_id=interpreter['type'])

    return [
      topic['name']
      for topic in api.autocomplete(**data)['tables_meta']
      if not topic['name'].startswith('__')
    ]


def get_topic_data(user, name):
  if has_kafka_api():
    print(
      SchemaRegistryApi().subjects()
    )
    print(
      SchemaRegistryApi().subject(name='Kafka-value')
    )
    data = {
      'full_headers': [{'name': 'message', 'type': 'string'}],
      'rows': [
        ['This is rider 894 and I am at 38.1952, -123.1723'],
        ['This is rider 98 and I am at 39.2531, -121.9547'],
        ['This is rider 564 and I am at 22.3431, -111.7670']
      ]
    }
  else:
    from desktop.api_public import _get_interpreter_from_dialect  # Avoid circular import
    interpreter = _get_interpreter_from_dialect('ksql', user)
    api = _get_notebook_api(user, connector_id=interpreter['type'])

    data = api.get_sample_data(snippet={})

  print(data)

  return data


def get_topic(name):
  if has_kafka_api():
    pass
  else:
    manager = ManagerApi()
    broker_host = manager.get_kafka_brokers().split(',')[0].split(':')[0]
    return manager.get_kafka_topics(broker_host)[name]
