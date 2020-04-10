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

from __future__ import absolute_import

from future import standard_library
standard_library.install_aliases()
from builtins import range
import gc
import logging
import multiprocessing
import threading

from datetime import datetime, timedelta
from prometheus_client import Gauge, REGISTRY

from useradmin.models import User

from desktop.conf import ENABLE_PROMETHEUS
from desktop.lib.metrics import global_registry


LOG = logging.getLogger(__name__)

ALLOWED_DJANGO_PROMETHEUS_METRICS = (
    'django_http_requests_latency_including_middlewares_seconds',
    'django_http_requests_total_by_method',
    'django_http_ajax_requests_total',
    'django_http_ajax_requests_created',
    'django_http_responses_body_total_bytes',
    'django_http_responses_total_by_status',
    'django_db'
)

if ENABLE_PROMETHEUS.get():
  django_collectors = set()
  django_metrics_names = [
      name
      for name in REGISTRY._names_to_collectors.keys() if name.startswith('django_') and not name.startswith(ALLOWED_DJANGO_PROMETHEUS_METRICS)
  ]

  for metric_name in django_metrics_names:
    collector_obj = REGISTRY._names_to_collectors[metric_name]
    django_collectors.add(collector_obj)

  for django_collector in django_collectors:
    REGISTRY.unregister(django_collector)


global_registry().gauge_callback(
    name='threads.total',
    callback=lambda: len(threading.enumerate()),
    label='Threads',
    description='The total number of threads',
    numerator='threads',
)

global_registry().gauge_callback(
    name='threads.daemon',
    callback=lambda: sum(1 for thread in threading.enumerate() if thread.isDaemon()),
    label='Daemon Threads',
    description='The number of daemon threads',
    numerator='threads',
)

# ------------------------------------------------------------------------------

global_registry().gauge_callback(
    name='multiprocessing.processes.total',
    callback=lambda: len(multiprocessing.active_children()),
    label='Multiprocessing Processes',
    description='Number of multiprocessing processes',
    numerator='processes',
)

global_registry().gauge_callback(
    name='multiprocessing.processes.daemon',
    callback=lambda: sum(1 for proc in multiprocessing.active_children() if proc.daemon),
    label='Daemon Multiprocessing Processes',
    description='Number of daemon multiprocessing processes',
    numerator='processes',
)

# ------------------------------------------------------------------------------

for i in range(3):
  global_registry().gauge_callback(
      name='python.gc.generation.%s' % i,
      callback=lambda: gc.get_count()[i],
      label='GC Object Count in Generation %s' % i,
      description='Total number of objects in garbage collection generation %s' % i,
      numerator='objects',
  )

global_registry().gauge_callback(
    name='python.gc.objects',
    callback=lambda: sum(gc.get_count()),
    label='GC Object Count',
    description='Total number of objects in the Python process',
    numerator='objects',
)

# ------------------------------------------------------------------------------

active_requests = global_registry().counter(
    name='requests.active',
    label='Active Requests',
    description='Number of currently active requests',
    numerator='requests',
    treat_counter_as_gauge=True,
)

request_exceptions = global_registry().counter(
    name='requests.exceptions',
    label='Request Exceptions',
    description='Number requests that resulted in an exception',
    numerator='requests',
)

response_time = global_registry().timer(
    name='requests.response-time',
    label='Request Response Time',
    description='Time taken to respond to requests across all Hue endpoints',
    numerator='seconds',
    counter_numerator='requests',
    rate_denominator='seconds',
)

# ------------------------------------------------------------------------------

def user_count():
  users = 0
  try:
    users = User.objects.count()
  except:
    LOG.exception('Metrics: Failed to get number of user accounts')
  return users

user_count = global_registry().gauge_callback(
    name='users',
    callback=user_count,
    label='Users',
    description='Total number of user accounts',
    numerator='users',
)

# ------------------------------------------------------------------------------

ldap_authentication_time = global_registry().timer(
    name='auth.ldap.auth-time',
    label='LDAP Authentication Time',
    description='The time spent waiting for LDAP to authenticate a user',
    numerator='seconds',
    counter_numerator='authentications',
    rate_denominator='seconds',
)

pam_authentication_time = global_registry().timer(
    name='auth.pam.auth-time',
    label='PAM Authentication Time',
    description='The time spent waiting for PAM to authenticate a user',
    numerator='seconds',
    counter_numerator='authentications',
    rate_denominator='seconds',
)

spnego_authentication_time = global_registry().timer(
    name='auth.spnego.auth-time',
    label='SPNEGO Authentication Time',
    description='The time spent waiting for SPNEGO to authenticate a user',
    numerator='seconds',
    counter_numerator='authentications',
    rate_denominator='seconds',
)

# ------------------------------------------------------------------------------

def num_of_queries():
  from desktop.models import Document2 # Avoid circular dependency
  try:
    count = Document2.objects.filter(
      type__istartswith='query-',
      is_history=True,
      last_modified__gt=datetime.now() - timedelta(minutes=10)
    ).count()
  except:
    LOG.exception('Could not get num_of_queries')
    count = 0
  return count

global_registry().gauge_callback(
    name='queries.number',
    callback=num_of_queries,
    label='number of queries',
    description='Number of queries were executed in last 10 minutes',
    numerator='users',
)

prometheus_queries_numbers = Gauge('hue_queries_numbers', 'Hue - numbers of queries')
prometheus_queries_numbers.set_function(num_of_queries)
