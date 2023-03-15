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

import boto
import logging
import requests
import sys
import xml.sax

if sys.version_info[0] > 2:
  from urllib.parse import unquote, urlparse as lib_urlparse, parse_qs, urlencode
else:
  from urllib import unquote, urlencode
  from urlparse import urlparse as lib_urlparse, parse_qs

from boto.connection import HTTPRequest
from boto.exception import BotoClientError
from boto.regioninfo import connect
from boto.resultset import ResultSet
from boto.s3 import S3RegionInfo
from boto.s3.bucket import Bucket, Key
from boto.s3.connection import S3Connection, NoHostProvided
from boto.s3.prefix import Prefix

from desktop.conf import RAZ
from desktop.lib.raz.clients import S3RazClient
from aws.conf import IS_SELF_SIGNING_ENABLED


LOG = logging.getLogger(__name__)


class SignedUrlS3Connection(S3Connection):
  """
  Contact S3 via a presigned Url of the resource hence not requiring any S3 credentials.

  This is a client replacing the building of the Http Request of the S3 resource via asking a third party providing for a presigned Urls.
  The request information is then injected into the regular boto HTTPRequest as the format is the same. Raw calls via the requests
  lib would work but the unmarshalling back from XML to boto2 Python object is tedious.

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
    anon = RAZ.IS_ENABLED.get() and not IS_SELF_SIGNING_ENABLED.get()

    super(SignedUrlS3Connection, self).__init__(
      aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                is_secure=is_secure, port=port, proxy=proxy, proxy_port=proxy_port,
                proxy_user=proxy_user, proxy_pass=proxy_pass,
                host=host, debug=debug, https_connection_factory=https_connection_factory,
                calling_format=calling_format, path=path,
                provider=provider, bucket_class=bucket_class, security_token=security_token,
                suppress_consec_slashes=suppress_consec_slashes, anon=anon,
                validate_certs=validate_certs, profile_name=profile_name)


class RazS3Connection(SignedUrlS3Connection):
  """
  Class asking a RAZ server presigned Urls for all the operations on S3 resources.
  Some operations can be denied depending on the privileges of the users in Ranger.

  Then fill-up the boto HttpRequest with the presigned Url data and lets boto executes the request as usual,
  so that we get the XML unmarshalling for free.

  Flow:
    1. signed_url = self.get_signed_url(/bucket/dir/key)
    2. request = http_request(signed_url)
    3. return self._mexe(requests)
  """

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
        qs_parsed = parse_qs(query_args) # all strings will be unquoted
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


class SelfSignedUrlS3Connection(SignedUrlS3Connection):
  """
  Test class self generating presigned Urls so that the Http Client using signed Urls instead
  of direct boto calls to S3 can be tested.
  """
  def make_request(self, method, bucket='', key='', headers=None, data='',
                    query_args=None, sender=None, override_num_retries=None,
                    retry_handler=None):
    if isinstance(bucket, self.bucket_class):
      bucket = bucket.name
    if isinstance(key, Key):
      key = key.name
    path = self.calling_format.build_path_base(bucket, key)
    boto.log.debug('path=%s' % path)
    auth_path = self.calling_format.build_auth_path(bucket, key)
    boto.log.debug('auth_path=%s' % auth_path)
    host = self.calling_format.build_host(self.server_name(), bucket)
    if query_args:
      path += '?' + query_args
      boto.log.debug('path=%s' % path)
      auth_path += '?' + query_args
      boto.log.debug('auth_path=%s' % auth_path)

    params = {}
    http_request = self.build_base_http_request(method, path, auth_path,
                                                params, headers, data, host)

    # Actual override starts here
    LOG.debug('Overriding: %s, %s, %s, %s, %s, %s, %s' % (method, path, auth_path, params, headers, data, host))
    LOG.debug('Overriding: %s' % http_request)

    p = http_request.path.split('/')
    bucket = (p[1] + '/') or ''
    key = '/'.join(p[2:]) if len(p) >= 3 else ''

    kwargs = {
        'bucket': bucket,
        'key': key
    }

    # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.connection.S3Connection.generate_url
    signed_url = self.generate_url(1000, method, **kwargs)
    LOG.debug('Generated url: %s' % signed_url)

    http_request.path = signed_url.replace(http_request.protocol + '://' + http_request.host.split(':')[0], '')
    p, h = http_request.path.split('?')
    http_request.path = unquote(p)
    http_request.headers = dict([a.split('=') for a in h.split('&')])

    LOG.debug('Overriden: %s' % http_request)

    return self._mexe(http_request, sender, override_num_retries,
                      retry_handler=retry_handler)


def url_client_connect_to_region(region_name, **kw_params):
  if 'host' in kw_params:
    host = kw_params.pop('host')
    if host not in ['', None]:
      region = S3RegionInfo(
          name='custom',
          endpoint=host,
          connection_cls=SelfSignedUrlS3Connection  # Override S3Connection class in connect_to_region of boto/s3/__init__.py
      )
      return region.connect(**kw_params)

  return connect('s3', region_name, region_cls=S3RegionInfo,
                   connection_cls=SelfSignedUrlS3Connection, **kw_params)



# --------------------------------------------------------------------------------
# Deprecated Client: to remove at v1
#
# This clients re-implement S3Connection methods via a PreSignedUrl either
# provided by a RAZ server or another Boto lib. Request to S3 are then made via
# requests and the raw XML is unmarshalling back to boto2 Python objects.
#
# Note: hooking-in the get/generate URL directly into S3Connection#make_request()
# was found to be simpler and possible as boto itself sends signed Urls.
# Handling various operations is relatively simple as defined by HTTP action and
# paths. Most of the security is handled via header parameters.
# --------------------------------------------------------------------------------

class SignedUrlClient():
  """
  Share the unmarshalling from XML to boto Python objects from the requests calls.
  """

  def get_all_buckets(self, headers=None):
    LOG.debug('get_all_buckets: %s' % headers)
    kwargs = {'action': 'GET'}

    signed_url = self.get_url_request(**kwargs)
    LOG.debug(signed_url)

    response = requests.get(signed_url)

    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Bucket', UrlBucket)])
    h = boto.handler.XmlHandler(rs, None)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs



class RazSignedUrlClient(SignedUrlClient):

  def __init__(self):
    self.raz = S3RazClient()

  def get_url_request(self, action='GET', bucket_name=None, object_name=None, expiration=3600):
    self.raz.get_url(bucket_name, object_name)



class UrlKey(Key):

  def open_read(self, headers=None, query_args='', override_num_retries=None, response_headers=None):
    LOG.debug('open_read: %s' % self.name)

    # Similar to Key.get_key('GET')
    # data = self.resp.read(self.BufferSize)
    # For seek: headers={"Range": "bytes=%d-" % pos}

    if self.resp is None:
      self.resp = self.bucket.get_key(key_name=self.name, validate=False, action='GET')


  def read(self, size=0):
    return self.resp.read(size) if self.resp else ''


  def get_url_request(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    signed_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.key.Key.generate_url
      signed_url = self.generate_url(self.expiration, action, **kwargs)
      LOG.debug('Generated url: %s' % signed_url)
    except BotoClientError as e:
      LOG.error(e)
      if signed_url is None:
        from aws.s3.s3fs import S3FileSystemException
        raise S3FileSystemException("Resource does not exist or permission missing : '%s'" % kwargs)

    return signed_url


class UrlBucket(Bucket):

  def list(self, prefix='', delimiter='', marker='', headers=None, encoding_type=None):
    params = {
      'prefix': prefix,
      'delimiter': delimiter
    }
    return self.get_all_keys(**params)


  def get_key(self, key_name, headers=None, version_id=None, response_headers=None, validate=True, action='HEAD'):
    LOG.debug('key name: %s %s' % (self.name, key_name))
    kwargs = {'bucket': self.name, 'key': key_name}

    # TODO: if GET --> max length to add

    signed_url = self.connection.generate_url(3000, action, **kwargs)
    LOG.debug('Generated url: %s' % signed_url)

    if action == 'HEAD':
      response = requests.head(signed_url)
    else:
      response = requests.get(signed_url)

    LOG.debug(response)
    LOG.debug(response.content)

    response.getheader = response.headers.get
    response.getheaders = lambda: response.headers

    # Copied from boto2 bucket.py _get_key_internal()
    if response.status_code / 100 == 2:
      k = self.key_class(self)
      provider = self.connection.provider
      # k.metadata = boto.utils.get_aws_metadata(response.msg, provider)
      for field in Key.base_fields:
        k.__dict__[field.lower().replace('-', '_')] = \
          response.getheader(field)
      # the following machinations are a workaround to the fact that
      # apache/fastcgi omits the content-length header on HEAD
      # requests when the content-length is zero.
      # See http://goo.gl/0Tdax for more details.
      clen = response.getheader('content-length')
      if clen:
        k.size = int(response.getheader('content-length'))
      else:
        k.size = 0
      k.name = key_name
      k.handle_version_headers(response)
      k.handle_encryption_headers(response)
      k.handle_restore_headers(response)
      k.handle_addl_headers(response.getheaders())

      class MockResponse():
        def __init__(self, resp):
          self.resp = resp
        def read(self, size):
          return self.resp.content

      k.resp = MockResponse(response)
    else:
      # Currently needed as 404 on directories via stats_key()
      k = self.key_class(self, key_name)

    return k


  def get_all_keys(self, headers=None, **params):
    kwargs = {'bucket': self.name, 'key': '', 'response_headers': params}

    signed_url = self.connection.generate_url(3000, 'GET', **kwargs)
    LOG.debug('Generated url: %s' % signed_url)

    response = requests.get(signed_url)

    LOG.debug('get_all_keys %s' % kwargs)
    LOG.debug(params)
    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Contents', UrlKey), ('CommonPrefixes', Prefix)])
    h = boto.handler.XmlHandler(rs, self)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs


  def get_url_request(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    signed_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.bucket.Bucket.generate_url
      signed_url = self.generate_url(self.expiration, action, **kwargs)
      LOG.debug('Generated url: %s' % signed_url)
    except BotoClientError as e:
      LOG.error(e)
      if signed_url is None:
        raise IOError("Resource does not exist or permission missing : '%s'" % kwargs)

    return signed_url


class SelfSignedUrlClient(SignedUrlClient):

  def __init__(self, connection):
    self.connection = connection
    self.expiration = 3600

    self.connection.make_request = None  # We make sure we never call via regular boto connection directly
    self.connection.set_bucket_class(UrlBucket)  # Use our bucket class to keep overriding any direct call to S3 made from list buckets


  def get_url_request(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    signed_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.connection.S3Connection.generate_url
      signed_url = self.connection.generate_url(self.expiration, action, **kwargs)
      LOG.debug('Generated url: %s' % signed_url)
    except BotoClientError as e:
      LOG.error(e)
      if signed_url is None:
        raise IOError("Resource does not exist or permission missing : '%s'" % kwargs)

    return signed_url


  def get_bucket(self, bucket_name, validate=True, headers=None):
    LOG.debug('get_bucket: %s' % bucket_name)
    kwargs = {'action': 'GET', 'bucket': bucket_name}

    signed_url = self.get_url_request(**kwargs)

    response = requests.get(signed_url)

    LOG.debug(response)
    LOG.debug(response.content)

    rs = self.connection.bucket_class(self.connection, bucket_name, key_class=UrlKey)  # Using content?
    LOG.debug(rs)

    return rs
