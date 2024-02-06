#!/usr/bin/env python
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
import re

from boto.gs.key import Key
from boto.gs.connection import GSConnection
from boto.s3.connection import SubdomainCallingFormat

from desktop.conf import RAZ
from desktop.lib.raz.clients import GSRazClient


LOG = logging.getLogger()


class RazGSConnection(GSConnection):
  """
  Class asking a RAZ server presigned URLs for all the operations on GS resources hence not requiring any GS credentials.
  Some operations can be denied depending on the privileges of the users in Ranger.

  This client replaces the building of the Http Request of the GS resource via asking RAZ for presigned URLs.
  The request information is then injected into the regular boto HTTPRequest as the format is the same. Raw calls via the requests
  lib would work but the unmarshalling back from XML to boto2 Python object is tedious.

  Then fill-up the boto HttpRequest with the presigned Url data and lets boto executes the request as usual,
  so that we get the XML unmarshalling for free.

  Flow:
    1. signed_url = self.get_signed_url(/bucket/dir/key)
    2. request = http_request(signed_url)
    3. return self._mexe(requests)
  
  The main logic consists in some light overrides in GSConnection#make_request() and AWSAuthConnection#make_request() so that we
  send an updated HTTPRequest.

  https://github.com/boto/boto/blob/develop/boto/gs/connection.py
  https://github.com/boto/boto/blob/develop/boto/connection.py
  """
  def __init__(self, username, gs_access_key_id=None, gs_secret_access_key=None,
                is_secure=True, port=None, proxy=None, proxy_port=None,
                proxy_user=None, proxy_pass=None,
                host=GSConnection.DefaultHost, debug=0, https_connection_factory=None,
                calling_format=SubdomainCallingFormat(), path='/',
                suppress_consec_slashes=True, anon=False):

    self.username = username

    # No auth handler with RAZ
    anon = RAZ.IS_ENABLED.get()

    super(RazGSConnection, self).__init__(
      gs_access_key_id=gs_access_key_id, gs_secret_access_key=gs_secret_access_key,
      is_secure=is_secure, port=port, proxy=proxy, proxy_port=proxy_port,
      proxy_user=proxy_user, proxy_pass=proxy_pass,
      host=host, debug=debug, https_connection_factory=https_connection_factory,
      calling_format=calling_format, path=path,
      suppress_consec_slashes=suppress_consec_slashes, anon=anon
    )


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
      # Call to RAZ for getting the signed headers does not expect the 'generation' argument in the query_args
      # This might be done to make their side RAZ-GS implementation similar to S3

      # Using regex to remove the 'generation' arg and its value from the query string
      query_args = re.sub(r'&?generation=[^&]*', '', query_args)
      query_args = query_args.lstrip('&') # Remove any leading '&' if 'generation' is at the beginning

      path += '?' + query_args
      LOG.debug('path=%s' % path)
      auth_path += '?' + query_args
      LOG.debug('auth_path=%s' % auth_path)

    params = {}
    # GS expects only one type of headers, either all x-amz-* or all x-goog-*, and the signed headers returned from RAZ are of x-amz-* type
    # So, we are converting all x-goog-* headers to x-amz-* headers before sending the final request to GS from Hue
    if headers:
      updated_headers = {'x-amz-' + key[7:]: value for key, value in headers.items() if key.startswith('x-goog-')}
      headers.update(updated_headers)

      for key in list(headers.keys()):
        if key.startswith('x-goog-'):
          del headers[key]

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
      raise Exception('Aborting operation: We got back empty header from Raz for the request %s' % http_request)

    LOG.debug('Overriden: %s' % http_request)

    return self._mexe(http_request, sender, override_num_retries,
                      retry_handler=retry_handler)


  def get_signed_url(self, action='GET', url=None, headers=None, data=None):
    raz_client = GSRazClient(username=self.username)

    return raz_client.get_url(action, url, headers, data)
