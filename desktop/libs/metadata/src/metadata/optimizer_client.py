#!/usr/bin/env python
# -- coding: utf-8 --
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

import json
import logging
import uuid

from django.utils.translation import ugettext as _

from desktop.lib import export_csvxls
from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from metadata.conf import OPTIMIZER, get_optimizer_url


LOG = logging.getLogger(__name__)


_JSON_CONTENT_TYPE = 'application/json'


def is_optimizer_enabled():
  return get_optimizer_url() and OPTIMIZER.PRODUCT_NAME.get()


class OptimizerApiException(Exception):
  pass


class OptimizerApi(object):

  def __init__(self, api_url=None, product_name=None, product_secret=None, ssl_cert_ca_verify=OPTIMIZER.SSL_CERT_CA_VERIFY.get(), product_auth_secret=None):
    self._api_url = (api_url or get_optimizer_url()).strip('/')
    self._product_name = product_name if product_name else OPTIMIZER.PRODUCT_NAME.get()
    self._product_secret = product_secret if product_secret else OPTIMIZER.PRODUCT_SECRET.get()
    self._product_auth_secret = product_auth_secret if product_auth_secret else OPTIMIZER.PRODUCT_AUTH_SECRET.get()
    self._email = OPTIMIZER.EMAIL.get()
    self._email_password = OPTIMIZER.EMAIL_PASSWORD.get()

    self._client = HttpClient(self._api_url, logger=LOG)
    self._client.set_verify(ssl_cert_ca_verify)

    self._root = resource.Resource(self._client)
    self._token = None


  def _authenticate(self, force=False):
    if self._token is None or force:
      self._token = self.authenticate()['token']

    return self._token


  def create_product(self, product_name=None, product_secret=None, authCode=None):
    try:
      data = {
          'productName': product_name if product_name is not None else self._product_name,
          'productSecret': product_secret if product_secret is not None else self._product_secret,
          'authCode': authCode if authCode is not None else self._product_auth_secret
      }
      return self._root.post('/api/createProduct', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def add_email_to_product(self, email=None, email_password=None):
    try:
      data = {
          'productName': self._product_name,
          'productSecret': self._product_secret,
          'email': email if email is not None else self._email,
          'password': email_password if email_password is not None else self._email_password
      }
      return self._root.post('/api/addEmailToProduct', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def authenticate(self):
    try:
      data = {
          'productName': self._product_name,
          'productSecret': self._product_secret,
      }
      return self._root.post('/api/authenticate', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def delete_workload(self, token, email=None):
    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
      }
      return self._root.post('/api/deleteWorkload', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def get_status(self, token, email=None):
    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
      }
      return self._root.post('/api/getStatus', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def upload(self, queries, token=None, email=None, source_platform='generic'):
    if token is None:
      token = self._authenticate()

    try:      
      content_generator = OptimizerDataAdapter(queries)
      queries_csv = export_csvxls.create_generator(content_generator, 'csv')

      data = {
          'email': email if email is not None else self._email,
          'token': token,
          'sourcePlatform': source_platform,
      }
      return self._root.post('/api/upload', data=data, files = {'file': ('hue-report.csv', list(queries_csv)[0])})

    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def top_tables(self, token=None, email=None):
    if token is None:
      token = self._authenticate()

    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
      }
      return self._root.post('/api/topTables', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def table_details(self, table_name, token=None, email=None):
    if token is None:
      token = self._authenticate()

    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
          'tableName': table_name
      }
      return self._root.post('/api/tableDetails', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def query_compatibility(self, source_platform, target_platform, query, token=None, email=None):
    if token is None:
      token = self._authenticate()

    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
          'sourcePlatform': source_platform,
          'targetPlatform': target_platform,
          'query': query
      }
      return self._root.post('/api/queryCompatibility', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def similar_queries(self, source_platform, query, token=None, email=None):
    if token is None:
      token = self._authenticate()

    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
          'sourcePlatform': source_platform,
          'query': query
      }
      return self._root.post('/api/similarQueries', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def popular_filter_values(self, table_name, column_name=None, token=None, email=None):
    if token is None:
      token = self._authenticate()

    try:
      data = {
          'email': email if email is not None else self._email,
          'token': token,
          'tableName': table_name
      }
      if column_name:
        data['columnName'] = column_name
      return self._root.post('/api/getPopularFilterValues', data=json.dumps(data), contenttype=_JSON_CONTENT_TYPE)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))



def OptimizerDataAdapter(queries):
  headers = ['SQL_ID', 'ELAPSED_TIME', 'SQL_FULLTEXT']
  if queries and len(queries[0]) == 3:
    rows = queries
  else:  
    rows = ([str(uuid.uuid4()), 1000, q] for q in queries)

  yield headers, rows
