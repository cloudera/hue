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

from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException
from desktop.lib.rest.http_client import HttpClient, RestException
from desktop.lib.rest import resource

from metadata.conf import OPTIMIZER


LOG = logging.getLogger(__name__)


_JSON_CONTENT_TYPE = 'application/json'


def is_optimizer_enabled():
  return OPTIMIZER.API_URL.get() and OPTIMIZER.PRODUCT_NAME.get()


class OptimizerApiException(Exception):
  pass


class OptimizerApi(object):

  def __init__(self, api_url=None, product_name=None, product_secret=None, ssl_cert_ca_verify=OPTIMIZER.SSL_CERT_CA_VERIFY.get(), product_auth_secret=None):
    self._api_url = (api_url or OPTIMIZER.API_URL.get()).strip('/')
    self._product_name = product_name if product_name else OPTIMIZER.PRODUCT_NAME.get()
    self._product_secret = product_secret if product_secret else OPTIMIZER.PRODUCT_SECRET.get()
    self._product_auth_secret = product_auth_secret if product_auth_secret else OPTIMIZER.PRODUCT_AUTH_SECRET.get()

    self._client = HttpClient(self._api_url, logger=LOG)
    self._client.set_verify(ssl_cert_ca_verify)

    self._root = resource.Resource(self._client)

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


  def add_email_to_product(self, email):
    try:
      data = {
          'productName': self._product_name,
          'productSecret': self._product_secret,
          'email': '',
          'password': ''
      }
      return self._root.post('/api/addEmailToProduct', data)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def authenticate(self):
    try:
      data = {
          'productName': self._product_name,
          'productSecret': self._product_secret,
      }
      return self._root.post('/api/createProduct', data)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def delete_workload(self):
    try:
      data = {
          'email': email,
          'token': token,
      }
      return self._root.post('/api/deleteWorkload', data)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def get_status(self):
    try:
      data = {
          'email': email,
          'token': token,
      }
      return self._root.post('/api/getStatus', data)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))


  def upload(self):
    try:
      data = {
          'email': email,
          'token': token,
          'sourcePlatform': 'generic',
          'file': 'file'
      }
      return self._root.post('/api/upload', data)
    except RestException, e:
      raise PopupException(e, title=_('Error while accessing Optimizer'))
