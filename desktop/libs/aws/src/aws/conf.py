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

from boto.regioninfo import get_regions

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_bool


AWS_ACCOUNTS = UnspecifiedConfigSection(
  'aws_accounts',
  help='One entry for each AWS account',
  each=ConfigSection(
    help='Information about single AWS account',
    members=dict(
      ACCESS_KEY_ID=Config(
        key='access_key_id',
        type=str,
        private=True
      ),
      SECRET_ACCESS_KEY=Config(
        key='secret_access_key',
        type=str,
        private=True
      ),
      ALLOW_ENVIRONMENT_CREDENTIALS=Config(
        help='Allow to use environment sources of credentials (environment variables, EC2 profile).',
        key='allow_environment_credentials',
        default=True,
        type=coerce_bool
      ),
      REGION=Config(
        key='region',
        default='us-east-1',
        type=str
      )
    )
  )
)


def is_enabled():
  return 'default' in AWS_ACCOUNTS.keys() and AWS_ACCOUNTS['default'].get_raw()


def is_default_configured():
  return is_enabled() and AWS_ACCOUNTS['default'].ACCESS_KEY_ID.get() is not None


def config_validator(user):
  res = []

  if is_enabled():
    if not is_default_configured():  # Make a redundant call to is_enabled so that we only check default if it's non-empty
      res.append(('aws.aws_accounts', 'Default AWS account is not configured'))

    regions = get_regions('s3')  # S3 is only supported service so far
    region_names = [r.name for r in regions]

    for name in AWS_ACCOUNTS.keys():
      region_name = AWS_ACCOUNTS[name].REGION.get()
      if region_name not in region_names:
        res.append(('aws.aws_accounts.%s.region' % name, 'Unknown region %s' % region_name))

  return res