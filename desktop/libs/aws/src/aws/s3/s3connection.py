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
from urllib.parse import parse_qs, unquote, urlencode

import boto
from boto.connection import HTTPRequest
from boto.exception import BotoClientError
from boto.regioninfo import connect
from boto.resultset import ResultSet
from boto.s3 import S3RegionInfo
from boto.s3.bucket import Bucket, Key
from boto.s3.connection import NoHostProvided, S3Connection
from boto.s3.prefix import Prefix

from desktop.conf import RAZ
from desktop.lib.raz.clients import S3RazClient

LOG = logging.getLogger()


class RazS3Connection(S3Connection):
  """
  Class asking a RAZ server presigned Urls for all the operations on S3 resources hence not requiring any S3 credentials.
  Some operations can be denied depending on the privileges of the users in Ranger.

  This client replaces the building of the Http Request of the S3 resource via asking RAZ for presigned URLs.
  The request information is then injected into the regular boto HTTPRequest as the format is the same. Raw calls via the requests
  lib would work but the unmarshalling back from XML to boto2 Python object is tedious.

  It fills-up the boto HttpRequest with the presigned URL data and lets boto executes the request as usual,
  so that we get the XML unmarshalling for free.

  Flow:
    1. signed_url = self.get_signed_url(/bucket/dir/key)
    2. request = http_request(signed_url)
    3. return self._mexe(requests)

  The main logic consists in some light overrides in S3Connection#make_request() and AWSAuthConnection#make_request() so that we
  send an updated HTTPRequest.

  https://github.com/boto/boto/blob/develop/boto/s3/connection.py
  https://github.com/boto/boto/blob/develop/boto/connection.py

  Example of a presigned S3 Url declaring a `list all buckets` call:
  https://s3-us-west-1.amazonaws.com/?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA23E77ZX2HVY76YGL%2F20210505%2Fus-west-1%2Fs3%2Faws4_request&X-Amz-Date=20210505T171457Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=994d0ec2ca19a00aa2925fe62cab0e727591b1951a8a47504b2b9124facbd6cf
  """
  def __init__(self, username, aws_access_key_id=None, aws_secret_access_key=None,
                is_secure=True, port=None, proxy=None, proxy_port=None,
                proxy_user=None, proxy_pass=None,
                host=NoHostProvided, debug=0, https_connection_factory=None,
                calling_format=S3Connection.DefaultCallingFormat, path='/',
                provider='aws', bucket_class=Bucket, security_token=None,
                suppress_consec_slashes=True, anon=False,
                validate_certs=None, profile_name=None):

    self.username = username

    # No auth handler with RAZ
    anon = RAZ.IS_ENABLED.get()

    super(RazS3Connection, self).__init__(
      aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                is_secure=is_secure, port=port, proxy=proxy, proxy_port=proxy_port,
                proxy_user=proxy_user, proxy_pass=proxy_pass,
                host=host, debug=debug, https_connection_factory=https_connection_factory,
                calling_format=calling_format, path=path,
                provider=provider, bucket_class=bucket_class, security_token=security_token,
                suppress_consec_slashes=suppress_consec_slashes, anon=anon,
                validate_certs=validate_certs, profile_name=profile_name)

  def make_request(self, method, bucket='', key='', headers=None, data='',
                    query_args=None, sender=None, override_num_retries=None,
                    retry_handler=None):

    if isinstance(bucket, self.bucket_class):
      bucket = bucket.name
    if isinstance(key, Key):
      key = key.name

    path = self.calling_format.build_path_base(bucket, key)
    LOG.debug('path=%s' % path)

    auth_path = self.calling_format.build_auth_path(bucket, key)
    LOG.debug('auth_path=%s' % auth_path)

    host = self.calling_format.build_host(self.server_name(), bucket)

    if query_args:
      # Clean prefix to remove s3a%3A//[S3_BUCKET]/ for sending correct relative path to RAZ
      if 'prefix=s3a%3A//' in query_args:
        qs_parsed = parse_qs(query_args)  # all strings will be unquoted
        prefix_relative_path = qs_parsed['prefix'][0].partition(bucket + '/')[2]
        qs_parsed['prefix'][0] = prefix_relative_path

        query_args = unquote(urlencode(qs_parsed, doseq=True))

      path += '?' + query_args
      LOG.debug('path=%s' % path)
      auth_path += '?' + query_args
      LOG.debug('auth_path=%s' % auth_path)

    params = {}
    http_request = self.build_base_http_request(method, path, auth_path, params, headers, data, host)

    # Actual override starts here
    LOG.debug('http_request: %s, %s, %s, %s, %s, %s, %s' % (method, path, auth_path, params, headers, data, host))
    LOG.debug('http_request object: %s' % http_request)

    url = 'https://%(host)s%(path)s' % {'host': host, 'path': path}

    # Do not send the xml data for signing for upload operation
    xml_data = '' if query_args and 'uploadId=' in query_args else data

    raz_headers = self.get_signed_url(action=method, url=url, headers=headers, data=xml_data)
    LOG.debug('Raz returned those headers: %s' % raz_headers)

    if raz_headers is not None:
      http_request.headers.update(raz_headers)
    else:
      LOG.error('We got back empty header from Raz for the request %s' % http_request)

    LOG.debug('Overriden: %s' % http_request)

    return self._mexe(http_request, sender, override_num_retries,
                      retry_handler=retry_handler)

  def get_signed_url(self, action='GET', url=None, headers=None, data=None):
    raz_client = S3RazClient(username=self.username)

    return raz_client.get_url(action, url, headers, data)

  def _required_auth_capability(self):
    """
    Force AnonAuthHandler when Raz is enabled

    We want to always use AnonAuthHandler when Raz is enabled and that is what gets used in most cases,
    except for some regions.

    S3Connection._required_auth_capability() has a decorator @detect_potential_s3sigv4 that overrides
    the default func (which works correctly) for certain regions (boto.auth.SIGV4_DETECT). This breaks
    Raz regions cn-*, eu-central, ap-northeast-2, ap-south-1, us-east-2, ca-central and eu-west-2.
    We end up using auth.S3HmacAuthV4Handler rather than AnonAuthHandler for these regions and therefore fail.

    This function overrides skips the @detect_potential_s3sigv4 decorator from S3Connection super class
    and forces the use of AnonAuthHandler.
    """
    return ['anon']
