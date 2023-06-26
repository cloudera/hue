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
import sys

import requests

from desktop.lib.conf import Config, UnspecifiedConfigSection, ConfigSection, coerce_bool, coerce_password_from_script
from desktop.lib.idbroker import conf as conf_idbroker
from hadoop.core_site import get_s3a_access_key, get_s3a_secret_key, get_s3a_session_token, get_raz_api_url, get_raz_s3_default_bucket

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _, gettext as _t
else:
  from django.utils.translation import ugettext_lazy as _, ugettext as _t


LOG = logging.getLogger()


DEFAULT_CALLING_FORMAT = 'boto.s3.connection.OrdinaryCallingFormat'
SUBDOMAIN_ENDPOINT_RE = 's3.(?P<region>[a-z0-9-]+).amazonaws.com'
HYPHEN_ENDPOINT_RE = 's3-(?P<region>[a-z0-9-]+).amazonaws.com'
DUALSTACK_ENDPOINT_RE = 's3.dualstack.(?P<region>[a-z0-9-]+).amazonaws.com'
AWS_ACCOUNT_REGION_DEFAULT = 'us-east-1' # Location.USEast
PERMISSION_ACTION_S3 = "s3_access"
REGION_CACHED = None
IS_IAM_CACHED = None
IS_EC2_CACHED = None

def clear_cache():
  global REGION_CACHED, IS_IAM_CACHED, IS_EC2_CACHED
  REGION_CACHED = None
  IS_IAM_CACHED = None
  IS_EC2_CACHED = None

def get_locations():
  return ('EU',  # Ireland
    'af-south-1',
    'ap-east-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-northeast-3',
    'ap-southeast-1',
    'ap-southeast-2',
    'ap-southeast-3',
    'ap-south-1',
    'ca-central-1',
    'cn-north-1',
    'cn-northwest-1',
    'eu-central-1',  # Frankfurt
    'eu-north-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'eu-south-1',
    'me-south-1',
    'sa-east-1',
    'us-east-1',
    'us-east-2',
    'us-gov-east-1',
    'us-gov-west-1',
    'us-west-1',
    'us-west-2')


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


def get_default_session_token():
  """
  Attempt to set AWS secret key from script, else core-site, else None
  """
  return get_s3a_session_token()


def get_default_region():
  return get_region(conf=AWS_ACCOUNTS['default']) if 'default' in AWS_ACCOUNTS else get_region()


def get_default_host():
  '''Returns the S3 host when Raz is configured'''

  if get_raz_api_url():
    endpoint = get_raz_s3_default_bucket()
    if endpoint:
      return endpoint.get('host')

def get_region(conf=None):
  global REGION_CACHED

  if REGION_CACHED is not None:
    return REGION_CACHED
  region = ''

  if conf or get_default_host():
    # First check the host/endpoint configuration
    endpoint = get_default_host() or conf.HOST.get()
    if endpoint:
      if re.search(SUBDOMAIN_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(SUBDOMAIN_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
      elif re.search(HYPHEN_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(HYPHEN_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
      elif re.search(DUALSTACK_ENDPOINT_RE, endpoint, re.IGNORECASE):
        region = re.search(DUALSTACK_ENDPOINT_RE, endpoint, re.IGNORECASE).group('region')
    elif conf.REGION.get():
      region = conf.REGION.get()

  if not region and is_ec2_instance():
    try:
      import boto.utils
      data = boto.utils.get_instance_identity(timeout=1, num_retries=1)
      if data:
        region = data['document']['region']
    except Exception as e:
      LOG.exception("Encountered error when fetching instance identity: %s" % e)

  if not region:
    region = AWS_ACCOUNT_REGION_DEFAULT

  # If the parsed out region is not in the list of supported regions, fallback to the default
  if region not in get_locations():
    LOG.warning("Region, %s, not found in the list of supported regions: %s" % (region, ', '.join(get_locations())))
    region = ''

  REGION_CACHED = region

  return region


def get_key_expiry():
  if 'default' in AWS_ACCOUNTS:
    return AWS_ACCOUNTS['default'].KEY_EXPIRY.get()
  else:
    return 86400


HAS_IAM_DETECTION = Config(
  help=_('Enable the detection of an IAM role providing the credentials automatically. It can take a few seconds.'),
  key='has_iam_detection',
  default=False,
  type=coerce_bool
)

IS_SELF_SIGNING_ENABLED = Config(
  key='is_self_signing_enabled',
  help=_('Skip boto and use self signed URL and requests to make the calls to S3. Used for testing the RAZ integration.'),
  type=coerce_bool,
  private=True,
  default=False,
)

def get_default_get_environment_credentials():
  '''Allow to check if environment credentials are present or not'''
  return not get_raz_api_url()


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
        dynamic_default=get_default_session_token
      ),
      ALLOW_ENVIRONMENT_CREDENTIALS=Config(
        help=_('Allow to use environment sources of credentials (environment variables, EC2 profile).'),
        key='allow_environment_credentials',
        default=True,
        type=coerce_bool
      ),
      REGION=Config(
        key='region',
        default=None,
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
        help=_(
          'The time in seconds before a delegate key is expired. Used when filebrowser/redirect'
          'download is used. Default to 4 Hours.'),
        key='key_expiry',
        default=14400,
        type=int
      ),
    )
  )
)


def is_enabled():
  return ('default' in list(AWS_ACCOUNTS.keys()) and AWS_ACCOUNTS['default'].get_raw() and AWS_ACCOUNTS['default'].ACCESS_KEY_ID.get()) or \
      has_iam_metadata() or \
      conf_idbroker.is_idbroker_enabled('s3a') or \
      is_raz_s3()


def is_ec2_instance():
  # To avoid unnecessary network call, check if Hue is running on EC2 instance.
  # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/identify_ec2_instances.html
  # /sys/hypervisor/uuid doesn't work on m5/c5, but /sys/devices/virtual/dmi/id/product_uuid does
  global IS_EC2_CACHED

  # Detection can be slow and so is disabled by default.
  if not HAS_IAM_DETECTION.get():
    IS_EC2_CACHED = False

  if IS_EC2_CACHED is not None:
    return IS_EC2_CACHED

  try:
    # Low chance of false positive
    IS_EC2_CACHED = (os.path.exists('/sys/hypervisor/uuid') and open('/sys/hypervisor/uuid', 'r').read()[:3].lower() == 'ec2') or \
      (
        os.path.exists('/sys/devices/virtual/dmi/id/product_uuid') and \
        open('/sys/devices/virtual/dmi/id/product_uuid', 'r').read()[:3].lower() == 'ec2'
      )
  except Exception as e:
    LOG.info("Detecting if Hue on an EC2 host, error might be expected: %s" % e)

  if IS_EC2_CACHED is None:
    try:
      resp = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/')  # Definitive way to check
      IS_EC2_CACHED = resp.status_code == 200
    except Exception as e:
      IS_EC2_CACHED = False
      LOG.info("Detecting if Hue on an EC2 host, error might be expected: %s" % e)

  return IS_EC2_CACHED


def has_iam_metadata():
  global IS_IAM_CACHED

  try:
    if IS_IAM_CACHED is not None:
      return IS_IAM_CACHED

    if is_ec2_instance():
      import boto.utils
      metadata = boto.utils.get_instance_metadata(timeout=1, num_retries=1)
      IS_IAM_CACHED = 'iam' in metadata
    else:
      IS_IAM_CACHED = False
  except:
    IS_IAM_CACHED = False
    LOG.exception("Encountered error when checking IAM metadata")
  return IS_IAM_CACHED


def has_s3_access(user):
  from desktop.auth.backend import is_admin

  return user.is_authenticated and user.is_active and (
    is_admin(user) or user.has_hue_permission(action="s3_access", app="filebrowser") or is_raz_s3())


def is_raz_s3():
  from desktop.conf import RAZ  # Must be imported dynamically in order to have proper value

  return (RAZ.IS_ENABLED.get() and 'default' in list(AWS_ACCOUNTS.keys()) and \
          AWS_ACCOUNTS['default'].HOST.get() and AWS_ACCOUNTS['default'].get_raw() and not IS_SELF_SIGNING_ENABLED.get())


def config_validator(user):
  res = []
  import desktop.lib.fsmanager # Circular dependecy

  if is_enabled():
    try:
      conn = desktop.lib.fsmanager.get_client(name='default', fs='s3a')._s3_connection
      conn.get_canonical_user_id()
    except Exception as e:
      LOG.exception('AWS failed configuration check.')
      res.append(('aws', _t('Failed to connect to S3, check your AWS credentials.')))

  return res
