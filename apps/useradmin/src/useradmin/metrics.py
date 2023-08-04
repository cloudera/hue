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

import logging

from datetime import datetime, timedelta
from prometheus_client import Gauge

from desktop.lib.metrics import global_registry
from desktop.lib.security_util import get_localhost_name

LOG = logging.getLogger()

def active_users():
  from useradmin.models import UserProfile
  try:
    count = UserProfile.objects.filter(
        last_activity__gt=datetime.now() - timedelta(hours=1),
        first_login=False,
        hostname__isnull=False
    ).count()
  except:
    LOG.exception('Could not get active_users')
    count = 0
  return count

global_registry().gauge_callback(
    name='users.active.total',
    callback=active_users,
    label='Active Users',
    description='Number of users that were active in the last hour in all instances',
    numerator='users',
)

prometheus_active_users = Gauge('hue_active_users', 'Hue Active Users in All Instances')
prometheus_active_users.set_function(active_users)

def active_users_per_instance():
  from useradmin.models import UserProfile
  try:
    count = UserProfile.objects.filter(last_activity__gt=datetime.now() - timedelta(hours=1), hostname=get_localhost_name()).count()
  except:
    LOG.exception('Could not get active_users per instance')
    count = 0
  return count

global_registry().gauge_callback(
    name='users.active',
    callback=active_users_per_instance,
    label='Active Users per Instance',
    description='Number of users that were active in the last hour on specific instance',
    numerator='users',
)

prometheus_active_users_instance = Gauge('hue_local_active_users', 'Hue Active Users in Local Instance')
prometheus_active_users_instance.set_function(active_users_per_instance)
