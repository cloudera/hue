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
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from desktop.lib.metrics import global_registry

global_registry().gauge_callback(
    name='python.threads.count',
    callback=lambda: len(threading.enumerate()),
    label='Thread count',
    description='Number of threads',
)

global_registry().gauge_callback(
    name='python.threads.active',
    callback=lambda: threading.active_count(),
    label='Active thread count',
    description='Number of active threads',
)

global_registry().gauge_callback(
    name='python.threads.daemon',
    callback=lambda: sum(1 for thread in threading.enumerate() if thread.isDaemon()),
    label='Daemon thread count',
    description='Number of daemon threads',
)

# ------------------------------------------------------------------------------

global_registry().gauge_callback(
    name='python.multiprocessing.count',
    callback=lambda: len(multiprocessing.active_children()),
    label='Process count',
    description='Number of multiprocessing processes',
)

global_registry().gauge_callback(
    name='python.multiprocessing.active',
    callback=lambda: sum(1 for proc in multiprocessing.active_children() if proc.is_alive()),
    label='Active multiprocessing processes',
    description='Number of active multiprocessing processes',
)

global_registry().gauge_callback(
    name='python.multiprocessing.daemon',
    callback=lambda: sum(1 for proc in multiprocessing.active_children() if proc.daemon),
    label='Daemon processes count',
    description='Number of daemon multiprocessing processes',
)

# ------------------------------------------------------------------------------

for i in xrange(3):
  global_registry().gauge_callback(
      name='python.gc.collection.count%s' % i,
      callback=lambda: gc.get_count()[i],
      label='GC collection count %s' % i,
      description='Current collection counts',
  )

global_registry().gauge_callback(
    name='python.gc.objects.count',
    callback=lambda: len(gc.get_objects()),
    label='GC tracked object count',
    description='Number of objects being tracked by the garbage collector',
)

global_registry().gauge_callback(
    name='python.gc.referrers.count',
    callback=lambda: len(gc.get_referrers()),
    label='GC tracked object referrers',
    description='Number of objects that directly refer to any objects',
)

global_registry().gauge_callback(
    name='python.gc.referents.count',
    callback=lambda: len(gc.get_referrers()),
    label='GC tracked object referents',
    description='Number of objects that directly referred to any objects',
)

# ------------------------------------------------------------------------------

active_requests = global_registry().counter(
    name='desktop.requests.active.count',
    label='Active requests',
    description='Number of currently active requests',
)

request_exceptions = global_registry().counter(
    name='desktop.requests.exceptions.count',
    label='Request exceptions',
    description='Number requests that resulted in an exception',
)

response_time = global_registry().timer(
    name='desktop.requests.aggregate-response-time',
    label='Request aggregate response time',
    description='Time taken to respond to requests'
)

# ------------------------------------------------------------------------------

user_count = global_registry().gauge(
    name='desktop.users.count',
    label='User count',
    description='Total number of users',
)

# Initialize with the current user count.
user_count.set_value(User.objects.all().count())

@receiver(post_save, sender=User)
def user_post_save_handler(sender, **kwargs):
  if 'created' in kwargs:
    user_count.set_value(User.objects.all().count())

@receiver(post_delete, sender=User)
def user_post_delete_handler(sender, **kwargs):
  user_count.set_value(User.objects.all().count())

logged_in_users = global_registry().counter(
    name='desktop.users.logged-in.count',
    label='Number of logged in users',
    description='Number of logged in users',
)

@receiver(user_logged_in)
def user_logged_in_handler(sender, **kwargs):
  logged_in_users.inc()

@receiver(user_logged_out)
def user_logged_out_handler(sender, **kwargs):
  logged_in_users.dec()

# ------------------------------------------------------------------------------

ldap_authentication_time = global_registry().timer(
    name='desktop.auth.ldap.authentication-time',
    label='LDAP Authentication time',
    description='Time taken to authenticate a user with LDAP',
)

oauth_authentication_time = global_registry().timer(
    name='desktop.auth.oauth.authentication-time',
    label='OAUTH Authentication time',
    description='Time taken to authenticate a user with OAUTH',
)

pam_authentication_time = global_registry().timer(
    name='desktop.auth.pam.authentication-time',
    label='PAM Authentication time',
    description='Time taken to authenticate a user with PAM',
)

spnego_authentication_time = global_registry().timer(
    name='desktop.auth.spnego.authentication-time',
    label='SPNEGO Authentication time',
    description='Time taken to authenticate a user with SPNEGO',
)
