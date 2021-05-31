#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import json
import logging
import socket
import sys
import uuid

import requests
import requests_kerberos

from datetime import datetime, timedelta

from desktop.lib.exceptions_renderable import PopupException
import desktop.lib.raz.signer_protos_pb2 as raz_signer

if sys.version_info[0] > 2:
  from urllib.parse import urlparse as lib_urlparse
else:
  from urlparse import urlparse as lib_urlparse


LOG = logging.getLogger(__name__)


class RazToken:

  def __init__(self, raz_url, auth_handler):
    self.raz_url = raz_url
    self.auth_handler = auth_handler
    self.init_time = datetime.now()
    self.raz_token = None
    o = lib_urlparse(self.raz_url)
    self.raz_hostname, self.raz_port = o.netloc.split(':')
    self.scheme = o.scheme

  def get_delegation_token(self, user):
    ip_address = socket.gethostbyname(self.raz_hostname)
    GET_PARAMS = {"op": "GETDELEGATIONTOKEN", "service": "%s:%s" % (ip_address, self.raz_port), "renewer": user}
    r = requests.get(self.raz_url, GET_PARAMS, auth=self.auth_handler, verify=False)
    self.raz_token = json.loads(r.text)['Token']['urlString']
    return self.raz_token

  def renew_delegation_token(self, user):
    if self.raz_token is None:
        self.raz_token = self.get_delegation_token(user=user)
    if (self.init_time - timedelta(hours=8)) > datetime.now():
        r = requests.put("%s?op=RENEWDELEGATIONTOKEN&token=%s"%(self.raz_url, self.raz_token), auth=self.auth_handler, verify=False)
    return self.raz_token


class RazClient(object):

  def __init__(self, raz_url, raz_token, username, service='s3', service_name='cm_s3', cluster_name='myCluster'):
    self.raz_url = raz_url.strip('/')
    self.raz_token = raz_token
    self.username = username
    if service == 's3' or True:  # True until ABFS option
      self.service_params = {
        'endpoint_prefix': 's3',
        'service_name': 's3',
        'serviceType': 's3'
      }
    self.service_name = service_name
    self.cluster_name = cluster_name
    self.requestid = str(uuid.uuid4())

  def check_access(self, method, url, params=None, headers=None):
    path = lib_urlparse(url)
    url_params = dict([p.split('=') for p in path.query.split('&') if path.query])
    params = params if params is not None else {}
    headers = headers if headers is not None else {}

    allparams = [raz_signer.StringListStringMapProto(key=key, value=val) for key, val in url_params.items()]
    allparams.extend([raz_signer.StringListStringMapProto(key=key, value=val) for key, val in params.items()])
    headers = [raz_signer.StringStringMapProto(key=key, value=val) for key, val in headers.items()]
    endpoint = "%s://%s" % (path.scheme, path.netloc)
    resource_path = path.path.lstrip("/")

    LOG.debug(
      "Preparing sign request with http_method: {%s}, header: {%s}, parameters: {%s}, endpoint: {%s}, resource_path: {%s}" %
      (method, headers, allparams, endpoint, resource_path)
    )
    raz_req = raz_signer.SignRequestProto(
        endpoint_prefix=self.service_params['endpoint_prefix'],
        service_name=self.service_params['service_name'],
        endpoint=endpoint,
        http_method=method,
        headers=headers,
        parameters=allparams,
        resource_path=resource_path,
        time_offset=0
    )
    raz_req_serialized = raz_req.SerializeToString()
    signed_request = base64.b64encode(raz_req_serialized)

    request_data = {
      "requestId": self.requestid,
      "serviceType": self.service_params['serviceType'],
      "serviceName": self.service_name,
      "user": self.username,
      "userGroups": [],
      "accessTime": "",
      "clientIpAddress": "",
      "clientType": "",
      "clusterName": self.cluster_name,
      "clusterType": "",
      "sessionId": "",
      "context": {
        "S3_SIGN_REQUEST": signed_request
      }
    }
    headers = {"Content-Type":"application/json", "Accept-Encoding":"gzip,deflate"}
    rurl = "%s/api/authz/s3/access?delegation=%s" % (self.raz_url, self.raz_token)

    LOG.debug("Sending access check headers: {%s} request_data: {%s}" % (headers, request_data))
    raz_req = requests.post(rurl, headers=headers, json=request_data, verify=False)

    s3_sign_response = None
    signed_response = None

    if raz_req.ok:
      result = raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]

      if result == "NOT_DETERMINED":
        msg = "Failure %s" % raz_req.json()
        LOG.error(msg)
        raise PopupException(msg)

      if result != "ALLOWED":
        msg = "Permission missing %s" % raz_req.json()
        raise PopupException(msg, error_code=401)

      if result == "ALLOWED":
        LOG.debug('Received allowed response %s' % raz_req.json())
        s3_sign_response = raz_req.json()["operResult"]["additionalInfo"]["S3_SIGN_RESPONSE"]

      if s3_sign_response:
        raz_response_proto = raz_signer.SignResponseProto()
        signed_response = raz_response_proto.FromString(base64.b64decode(s3_sign_response))
        LOG.debug("Received signed Response %s" % signed_response)

      # Currently returning signed headers "only"
      if signed_response:
        return dict([(i.key, i.value) for i in signed_response.signer_generated_headers])


def get_raz_client(raz_url, username, auth='kerberos', service='s3', service_name='cm_s3', cluster_name='myCluster'):
  if auth == 'kerberos' or True:  # True until ABFS option
    auth_handler = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)

  raz = RazToken(raz_url, auth_handler)
  raz_token = raz.get_delegation_token(user=username)

  return RazClient(raz_url, raz_token, username, service=service, service_name=service_name, cluster_name=cluster_name)
