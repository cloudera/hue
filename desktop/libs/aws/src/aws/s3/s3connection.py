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


LOG = logging.getLogger(__name__)


# Note: Connection means more "Client" but we follow boto2 terminology


class UrlConnection():

  def get_all_buckets(self, response):
    LOG.debug('get_all_buckets')
    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Bucket', self.connection.bucket_class)])
    h = boto.handler.XmlHandler(rs, self.connection)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)


class RazUrlConnection():

  def __init__(self):
    self.raz = S3RazClient()

  def _generate_url(self, bucket_name=None, object_name=None, expiration=3600):
    self.raz.get_url(bucket_name, object_name)

  def get_all_buckets(self, headers=None):
    url = self._generate_url()

  def get_bucket(self, bucket_name, validate=True, headers=None):
    pass

  def get_key(self, key_name, headers=None, version_id=None, response_headers=None, validate=True):
    pass

  def get_all_keys(self, headers=None, **params):
    pass


class UrlKey(Key):

  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.key.Key.generate_url
      tmp_url = self.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      return None

    return tmp_url


class UrlBucket(Bucket):

  def list(self, prefix='', delimiter='', marker='', headers=None, encoding_type=None):
    LOG.debug('prefix')
    LOG.debug(prefix)
    return self.get_all_keys()  # TODO: unsure yet how to generate URL with key prefix filtering


  def get_key(self, key_name, headers=None, version_id=None, response_headers=None, validate=True):
    LOG.debug('key name: %s' % key_name)
    kwargs = {'bucket': self.name, 'key': key_name}

    tmp_url = self.connection.generate_url(3000, 'GET', **kwargs)
    # tmp_url = self.generate_url(1000, 'GET', self.name, key_name, headers, version_id, response_headers, validate)

    response = requests.get(tmp_url)
    LOG.debug(response)
    LOG.debug(response.content)

    k = self.key_class(self, key_name)

    return k


  def get_all_keys(self, headers=None, **params):
    # delimiter=/&prefix=data/
    kwargs = {'bucket': self.name, 'key': ''} # data/

    tmp_url = self.connection.generate_url(3000, 'GET', **kwargs)

    response = requests.get(tmp_url)

    LOG.debug('get_all_keys %s' % kwargs)
    LOG.debug(params)
    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Contents', Key), ('CommonPrefixes', Prefix)])  # Or BucketListResultSet?
    h = boto.handler.XmlHandler(rs, self)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs


  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.bucket.Bucket.generate_url
      tmp_url = self.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      return None

    return tmp_url


class BotoUrlConnection():

  def __init__(self, connection):
    self.connection = connection
    self.expiration = 3600

    self.connection.make_request = None  # We make sure we never call directly
    self.connection.set_bucket_class(UrlBucket)  # We use our bucket class to override any direct call to S3


  def get_all_buckets(self, headers=None):
    kwargs = {'action': 'GET'}
    try:
      tmp_url = self._generate_url(**kwargs)
    except BotoClientError as e:
      LOG.error(e)
      return None

    response = requests.get(tmp_url)

    LOG.debug('get_all_buckets')
    LOG.debug(response)
    LOG.debug(response.content)

    rs = ResultSet([('Bucket', self.connection.bucket_class)])
    h = boto.handler.XmlHandler(rs, self.connection)
    xml.sax.parseString(response.content, h)
    LOG.debug(rs)

    return rs


  def get_bucket(self, bucket_name, validate=True, headers=None):
    kwargs = {'action': 'GET', 'bucket': bucket_name}

    tmp_url = self._generate_url(**kwargs)

    response = requests.get(tmp_url)

    LOG.debug('get_bucket')
    LOG.debug(response)
    LOG.debug(response.content)

    rs = self.connection.bucket_class(self.connection, bucket_name, key_class=UrlKey)  # Using content?
    LOG.debug(rs)

    return rs


  def _generate_url(self, action='GET', **kwargs):
    LOG.debug(kwargs)
    try:
      # http://boto.cloudhackers.com/en/latest/ref/s3.html#boto.s3.connection.S3Connection.generate_url
      tmp_url = self.connection.generate_url(self.expiration, action, **kwargs)
    except BotoClientError as e:
      LOG.error(e)
      return None

    return tmp_url
