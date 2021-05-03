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
import xml.sax

from boto.exception import BotoClientError
from boto.resultset import ResultSet
from boto.s3.bucket import Bucket, Key
from boto.s3.bucketlistresultset import BucketListResultSet
from boto.s3.prefix import Prefix

from desktop.lib.raz.clients import S3RazClient
from aws.s3.s3fs import S3FileSystemException


LOG = logging.getLogger(__name__)


# Note: Connection means more "Client" but we currently follow boto2 terminology
# To split in 3 modules at some point s3_url_client, s3_raz_client, s3_self_signing_client,


class UrlConnection():
  """
  Share the unmarshalling from XML to boto Python objects from the requests calls.
  """
  def _get_all_buckets(self, signed_url):
    LOG.debug(signed_url)

    response = requests.get(signed_url)

    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Bucket', UrlBucket)])
    h = boto.handler.XmlHandler(rs, None)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs


class RazUrlConnection(UrlConnection):

  def __init__(self):
    self.raz = S3RazClient()

  def get_all_buckets(self, headers=None):
    url = self._generate_url()
    return self._get_all_buckets(url)

  def get_bucket(self, bucket_name, validate=True, headers=None):
    pass

  def get_key(self, key_name, headers=None, version_id=None, response_headers=None, validate=True):
    pass

  def get_all_keys(self, headers=None, **params):
    pass

  def _generate_url(self, bucket_name=None, object_name=None, expiration=3600):
    self.raz.get_url(bucket_name, object_name)


class UrlKey(Key):

  def open_read(self, headers=None, query_args='', override_num_retries=None, response_headers=None):

    # Similar to Bucket.get_key()
    # data = self.resp.read(self.BufferSize)
    # For seek: headers={"Range": "bytes=%d-" % pos}

    return

  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    tmp_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.key.Key.generate_url
      tmp_url = self.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      if tmp_url is None:
        raise S3FileSystemException("Resource does not exist or permission missing : '%s'" % kwargs)

    return tmp_url


class UrlBucket(Bucket):

  def list(self, prefix='', delimiter='', marker='', headers=None, encoding_type=None):
    params = {
      'prefix': prefix,
      'delimiter': delimiter
    }
    return self.get_all_keys(**params)


  def get_key(self, key_name, headers=None, version_id=None, response_headers=None, validate=True):
    # Note: in current FS API we get file even if we don't need the content, hence why it can be slow.
    # To check if we should give a length in read() to mitigate.
    LOG.debug('key name: %s' % key_name)
    kwargs = {'bucket': self.name, 'key': key_name}

    tmp_url = self.connection.generate_url(3000, 'GET', **kwargs)

    response = requests.get(tmp_url)
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
    else:
      # Currently needed as 404 on directories via stats_key()
      k = self.key_class(self, key_name)

    return k


  def get_all_keys(self, headers=None, **params):
    kwargs = {'bucket': self.name, 'key': '', 'response_headers': params}

    tmp_url = self.connection.generate_url(3000, 'GET', **kwargs)

    response = requests.get(tmp_url)

    LOG.debug('get_all_keys %s' % kwargs)
    LOG.debug(params)
    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Contents', UrlKey), ('CommonPrefixes', Prefix)])  # Or BucketListResultSet?
    h = boto.handler.XmlHandler(rs, self)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs


  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    tmp_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.bucket.Bucket.generate_url
      tmp_url = self.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      if tmp_url is None:
        raise S3FileSystemException("Resource does not exist or permission missing : '%s'" % kwargs)

    return tmp_url


class BotoUrlConnection(UrlConnection):

  def __init__(self, connection):
    self.connection = connection
    self.expiration = 3600

    self.connection.make_request = None  # We make sure we never call via regular boto connection directly
    self.connection.set_bucket_class(UrlBucket)  # Use our bucket class to keep overriding any direct call to S3 made from list buckets


  def get_all_buckets(self, headers=None):
    LOG.debug('get_all_buckets: %s' % headers)
    kwargs = {'action': 'GET'}

    signed_url = self._generate_url(**kwargs)

    return self._get_all_buckets(signed_url)


  def get_bucket(self, bucket_name, validate=True, headers=None):
    LOG.debug('get_bucket: %s' % bucket_name)
    kwargs = {'action': 'GET', 'bucket': bucket_name}

    signed_url = self._generate_url(**kwargs)

    response = requests.get(signed_url)

    LOG.debug(response)
    LOG.debug(response.content)

    rs = self.connection.bucket_class(self.connection, bucket_name, key_class=UrlKey)  # Using content?
    LOG.debug(rs)

    return rs


  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    tmp_url = None

    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.connection.S3Connection.generate_url
      tmp_url = self.connection.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      if tmp_url is None:
        raise S3FileSystemException("Resource does not exist or permission missing : '%s'" % kwargs)

    return tmp_url
