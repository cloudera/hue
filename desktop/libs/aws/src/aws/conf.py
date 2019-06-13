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

import logging
import os
import re

import boto.utils
from boto.s3.connection import Location

from django.utils.translation import ugettext_lazy as _, ugettext as _t

import aws
from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_bool, coerce_password_from_script
from hadoop.core_site import get_s3a_access_key, get_s3a_secret_key

LOG = logging.getLogger(__name__)


DEFAULT_CALLING_FORMAT = 'boto.s3.connection.OrdinaryCallingFormat'
SUBDOMAIN_ENDPOINT_RE = 's3.(?P<region>[a-z0-9-]+).amazonaws.com'
HYPHEN_ENDPOINT_RE = 's3-(?P<region>[a-z0-9-]+).amazonaws.com'
DUALSTACK_ENDPOINT_RE = 's3.dualstack.(?P<region>[a-z0-9-]+).amazonaws.com'
AWS_ACCOUNT_REGION_DEFAULT = 'us-east-1' # Location.USEast


def get_locations():
  return ('EU',  # Ireland
    'eu-central-1',  # Frankfurt
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'ca-central-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
    'sa-east-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-northeast-3',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-south-1',
    'cn-north-1',
    'cn-northwest-1')


def get_default_access_key_id():
  """
  Attempt to set AWS access key ID from script, else core-site, else None
  """
  access_key_id_script = AWS_ACCOUNTS['default'].ACCESS_KEY_ID_SCRIPT.get()
  return access_key_id_script or get_s3a_access_key()


def get_default_secret_key():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  secret_access_key_script = AWS_ACCOUNTS['default'].SECRET_ACCESS_KEY_SCRIPT.get()
  return secret_access_key_script or get_s3a_secret_key()


def get_default_region():
  region = ''

  if 'default' in AWS_ACCOUNTS:
    # First check the host/endpoint configuration
    if AWS_ACCOUNTS['default'].HOST.get():
      endpoint = AWS_ACCOUNTS['default'].HOST.get()
      if re.search(SUBDOMAIN_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(SUBDOMAIN_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
      elif re.search(HYPHEN_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(HYPHEN_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
      elif re.search(DUALSTACK_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(DUALSTACK_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
    elif AWS_ACCOUNTS['default'].REGION.get():
      region = AWS_ACCOUNTS['default'].REGION.get()

    # If the parsed out region is not in the list of supported regions, fallback to the default
    if region not in get_locations():
      LOG.warn("Region, %s, not found in the list of supported regions: %s" % (region, ', '.join(get_locations())))
      region = ''

  return region

def get_key_expiry():
  if 'default' in AWS_ACCOUNTS:
    return AWS_ACCOUNTS['default'].KEY_EXPIRY.get()
  else:
    return 86400


AWS_ACCOUNTS = UnspecifiedConfigSection(
  'aws_accounts',
  help=_('One entry for each AWS account'),
  each=ConfigSection(
    help=_('Information about single AWS account'),
    members=dict(
      ACCESS_KEY_ID=Config(
        key='access_key_id',
        type=str,
        dynamic_default=get_default_access_key_id
      ),
      ACCESS_KEY_ID_SCRIPT=Config(
        key='access_key_id_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS access key ID.")),
      SECRET_ACCESS_KEY=Config(
        key='secret_access_key',
        type=str,
        private=True,
        dynamic_default=get_default_secret_key
      ),
      SECRET_ACCESS_KEY_SCRIPT=Config(
        key='secret_access_key_script',
        default=None,
        private=True,
        type=coerce_password_from_script,
        help=_("Execute this script to produce the AWS secret access key.")
      ),
      SECURITY_TOKEN=Config(
        key='security_token',
        type=str,
        private=True,
      ),
      ALLOW_ENVIRONMENT_CREDENTIALS=Config(
        help=_('Allow to use environment sources of credentials (environment variables, EC2 profile).'),
        key='allow_environment_credentials',
        default=True,
        type=coerce_bool
      ),
      REGION=Config(
        key='region',
        default=AWS_ACCOUNT_REGION_DEFAULT,
        type=str
      ),
      HOST=Config(
        help=_('Alternate address for the S3 endpoint.'),
        key='host',
        default=None,
        type=str
      ),
      PROXY_ADDRESS=Config(
        help=_('Proxy address to use for the S3 connection.'),
        key='proxy_address',
        default=None,
        type=str
      ),
      PROXY_PORT=Config(
        help=_('Proxy port to use for the S3 connection.'),
        key='proxy_port',
        default=8080,
        type=int
      ),
      PROXY_USER=Config(
        help=_('Proxy user to use for the S3 connection.'),
        key='proxy_user',
        default=None,
        type=str
      ),
      PROXY_PASS=Config(
        help=_('Proxy password to use for the S3 connection.'),
        key='proxy_pass',
        default=None,
        type=str
      ),
      CALLING_FORMAT=Config(
        key='calling_format',
        default=DEFAULT_CALLING_FORMAT,
        type=str
      ),
      IS_SECURE=Config(
        key='is_secure',
        default=True,
        type=coerce_bool
      ),
      KEY_EXPIRY=Config(
        help=_('The time in seconds before a delegate key is expired. Used when filebrowser/redirect_download is used. Default to 4 Hours.'),
        key='key_expiry',
        default=14400,
        type=int
      )
    )
  )
)


def is_enabled():
  return ('default' in AWS_ACCOUNTS.keys() and AWS_ACCOUNTS['default'].get_raw() and AWS_ACCOUNTS['default'].ACCESS_KEY_ID.get()) or has_iam_metadata()


def has_iam_metadata():
  try:
    # To avoid unnecessary network call, check if Hue is running on EC2 instance
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
    if os.path.exists('/sys/hypervisor/uuid') and open('/sys/hypervisor/uuid', 'read').read()[:3] == 'ec2':
      metadata = boto.utils.get_instance_metadata(timeout=1, num_retries=1)
      return 'iam' in metadata
  except Exception, e:
    LOG.exception("Encountered error when checking IAM metadata: %s" % e)
  return False


def has_s3_access(user):
  from desktop.auth.backend import is_admin
  return user.is_authenticated() and user.is_active and (is_admin(user) or user.has_hue_permission(action="s3_access", app="filebrowser"))


def config_validator(user):
  res = []

  if is_enabled():
    try:
      conn = aws.get_client('default').get_s3_connection()
      conn.get_canonical_user_id()
    except Exception, e:
      LOG.exception('AWS failed configuration check.')
      res.append(('aws', _t('Failed to connect to S3, check your AWS credentials.')))

  return res
