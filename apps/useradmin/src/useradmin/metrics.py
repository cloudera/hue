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

from desktop.lib.metrics import global_registry

LOG = logging.getLogger(__name__)

def active_users():
  from useradmin.models import UserProfile
  try:
    count = UserProfile.objects.filter(last_activity__gt=datetime.now() - timedelta(hours=1)).count()
  except:
    LOG.exception('Could not get active_users')
    count = 0
  return count

global_registry().gauge_callback(
    name='users.active',
    callback=active_users,
    label='Active Users',
    description='Number of users that were active in the last hour',
    numerator='users',
)
