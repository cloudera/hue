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

import gc
import multiprocessing
import threading

from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

from desktop.lib.metrics import global_registry

global_registry().gauge_callback(
    name='python.threads.total',
    callback=lambda: len(threading.enumerate()),
    label='Thread count',
    description='Number of threads',
    numerator='threads',
)

global_registry().gauge_callback(
    name='python.threads.active',
    callback=lambda: threading.active_count(),
    label='Active thread count',
    description='Number of active threads',
    numerator='threads',
)

global_registry().gauge_callback(
    name='python.threads.daemon',
    callback=lambda: sum(1 for thread in threading.enumerate() if thread.isDaemon()),
    label='Daemon thread count',
    description='Number of daemon threads',
    numerator='threads',
)

# ------------------------------------------------------------------------------

global_registry().gauge_callback(
    name='python.multiprocessing.total',
    callback=lambda: len(multiprocessing.active_children()),
    label='Process count',
    description='Number of multiprocessing processes',
    numerator='processes',
)

global_registry().gauge_callback(
    name='python.multiprocessing.active',
    callback=lambda: sum(1 for proc in multiprocessing.active_children() if proc.is_alive()),
    label='Active multiprocessing processes',
    description='Number of active multiprocessing processes',
    numerator='processes',
)

global_registry().gauge_callback(
    name='python.multiprocessing.daemon',
    callback=lambda: sum(1 for proc in multiprocessing.active_children() if proc.daemon),
    label='Daemon processes count',
    description='Number of daemon multiprocessing processes',
    numerator='processes',
)

# ------------------------------------------------------------------------------

for i in xrange(3):
  global_registry().gauge_callback(
      name='python.gc.collection.count%s' % i,
      callback=lambda: gc.get_count()[i],
      label='GC collection count %s' % i,
      description='Current collection counts',
      numerator='collections',
  )

global_registry().gauge_callback(
    name='python.gc.objects',
    callback=lambda: len(gc.get_objects()),
    label='GC tracked object count',
    description='Number of objects being tracked by the garbage collector',
    numerator='objects',
)

global_registry().gauge_callback(
    name='python.gc.referrers',
    callback=lambda: len(gc.get_referrers()),
    label='GC tracked object referrers',
    description='Number of objects that directly refer to any objects',
    numerator='referrers',
)

global_registry().gauge_callback(
    name='python.gc.referents',
    callback=lambda: len(gc.get_referrers()),
    label='GC tracked object referents',
    description='Number of objects that directly referred to any objects',
    numerator='referents',
)

# ------------------------------------------------------------------------------

active_requests = global_registry().counter(
    name='requests.active',
    label='Active requests',
    description='Number of currently active requests',
    numerator='active requests',
)

request_exceptions = global_registry().counter(
    name='requests.exceptions',
    label='Request exceptions',
    description='Number requests that resulted in an exception',
    numerator='failed requests',
)

response_time = global_registry().timer(
    name='requests.aggregate-response-time',
    label='Request aggregate response time',
    description='Time taken to respond to requests',
    numerator='seconds',
    counter_numerator='requests',
    rate_denominator='seconds',
)

# ------------------------------------------------------------------------------

user_count = global_registry().gauge_callback(
    name='users.total',
    callback=lambda: User.objects.count(),
    label='User count',
    description='Total number of users',
    numerator='users',
)

logged_in_users = global_registry().counter(
    name='users.logged-in',
    label='Number of logged in users',
    description='Number of logged in users',
    numerator='logged in users',
)

@receiver(user_logged_in)
def user_logged_in_handler(sender, **kwargs):
  logged_in_users.inc()

@receiver(user_logged_out)
def user_logged_out_handler(sender, **kwargs):
  logged_in_users.dec()

# ------------------------------------------------------------------------------

ldap_authentication_time = global_registry().timer(
    name='ldap.authentication-time',
    label='LDAP Authentication time',
    description='Time taken to authenticate a user with LDAP',
    numerator='seconds',
    counter_numerator='auths',
    rate_denominator='seconds',
)

oauth_authentication_time = global_registry().timer(
    name='auth.oauth.authentication-time',
    label='OAUTH Authentication time',
    description='Time taken to authenticate a user with OAUTH',
    numerator='seconds',
    counter_numerator='auths',
    rate_denominator='seconds',
)

pam_authentication_time = global_registry().timer(
    name='auth.pam.authentication-time',
    label='PAM Authentication time',
    description='Time taken to authenticate a user with PAM',
    numerator='seconds',
    counter_numerator='auths',
    rate_denominator='seconds',
)

spnego_authentication_time = global_registry().timer(
    name='auth.spnego.authentication-time',
    label='SPNEGO Authentication time',
    description='Time taken to authenticate a user with SPNEGO',
    numerator='seconds',
    counter_numerator='auths',
    rate_denominator='seconds',
)
