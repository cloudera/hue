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

import desktop.lib.raz.ranger.model.signer_protos_pb2 as raz_signer


if sys.version_info[0] > 2:
  from urllib.parse import unquote, urlparse as lib_urlparse
else:
  from urllib import unquote
  from urlparse import urlparse as lib_urlparse


LOG = logging.getLogger(__name__)


class RazToken(object):
    def __init__(self, raz_url, kerberos_auth):
        self.raz_url = raz_url
        self.kerberos_auth = kerberos_auth
        self.init_time = datetime.now()
        self.raz_token = None
        tstamp=(self.init_time + timedelta(minutes=3)).strftime("%Y%m%dT%H%M%SZ")
        # ParseResult(scheme='https', netloc='s3-us-west-1.amazonaws.com', path='/', params='', query='X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA23E77ZX2HVY76YGL%2F20210513%2Fus-west-1%2Fs3%2Faws4_request&X-Amz-Date=20210513T225608Z&X-Amz-Expires=1000&X-Amz-SignedHeaders=host&X-Amz-Signature=edb051e1d6af35fadbf4eeb189f4f8fee342fbeb1af36216cdede253cdddbb74', fragment='')
        o = urlsplit(self.raz_url)
        self.raz_port = o.port
        self.raz_hostname = o.hostname
        self.scheme = o.scheme

    def get_delegation_token(self, user="csso_ranade"):
        ip_address = socket.gethostbyname(self.raz_hostname)
        GET_PARAMS = {"op": "GETDELEGATIONTOKEN", "service": "%s:%s" % (ip_address, self.raz_port), "renewer": user}
        r = requests.get(self.raz_url, GET_PARAMS, auth=self.kerberos_auth, verify=False)
        self.raz_token = json.loads(r.text)['Token']['urlString']
        return self.raz_token

    def renew_delegation_token(self, user="csso_ranade"):
        if self.raz_token==None:
            self.raz_token = self.get_delegation_token(user=user)
        if (self.init_time + timedelta(hours=8)) > datetime.now():
            r = requests.put("%s?op=RENEWDELEGATIONTOKEN&token=%s"%(self.raz_url, self.raz_token), auth=self.kerberos_auth, verify=False)
        return self.raz_token


class RazToken(object):
    def __init__(self, raz_url, kerberos_auth):
        self.raz_url = raz_url
        self.kerberos_auth = kerberos_auth
        self.init_time = datetime.now()
        self.raz_token = None
        tstamp=(self.init_time + timedelta(minutes=3)).strftime("%Y%m%dT%H%M%SZ")
        o = urlsplit(self.raz_url)
        self.raz_port = o.port
        self.raz_hostname = o.hostname
        self.scheme = o.scheme

    def get_delegation_token(self, user="csso_ranade"):
        ip_address = socket.gethostbyname(self.raz_hostname)
        GET_PARAMS = {"op": "GETDELEGATIONTOKEN", "service": "%s:%s" % (ip_address, self.raz_port), "renewer": user}
        r = requests.get(self.raz_url, GET_PARAMS, auth=self.kerberos_auth, verify=False)
        self.raz_token = json.loads(r.text)['Token']['urlString']
        return self.raz_token

    def renew_delegation_token(self, user="csso_ranade"):
        if self.raz_token==None:
            self.raz_token = self.get_delegation_token(user=user)
        if (self.init_time + timedelta(hours=8)) > datetime.now():
            r = requests.put("%s?op=RENEWDELEGATIONTOKEN&token=%s"%(self.raz_url, self.raz_token), auth=self.kerberos_auth, verify=False)
        return self.raz_token


class RazClient(object):
    def __init__(self, request, raz_url, raz_token, *args, **kwargs):
        LOG.debug("Sign request: {%s}, args: {%s}, kwargs: {%s}"%(request, args, kwargs))
        self.request = request
        self.raz_url = raz_url
        self.raz_token = raz_token
        self.args = args
        self.kwargs = kwargs
        self.requestid = str(uuid.uuid4())

    def check_access(self):
        LOG.debug("inside sign")

        # parsed_url = lib_urlparse(signed_url)

        o = urlsplit(self.request.url)
        params = parse_qs(o.query)

        allparams = [raz_signer.StringListStringMapProto(key=key, value=val) for key, val in params.items()]
        allparams.extend([raz_signer.StringListStringMapProto(key=key, value=val) for key, val in self.request.params.items()])
        headers = [raz_signer.StringStringMapProto(key=key, value=val) for key, val in self.request.headers.items()]
        endpoint = "%s://%s" % (o.scheme, o.netloc)
        resource_path=o.path.lstrip("/")

        LOG.debug(
          "preparing sign request with http_method: {%s}, header: {%s}, parameters: {%s}, endpoint: {%s}, resource_path: {%s}" %
          (self.request.method, headers, allparams, endpoint, resource_path)
        )
        raz_req = raz_signer.SignRequestProto(
            endpoint_prefix="s3",
            service_name="s3",
            endpoint=endpoint,
            http_method=self.request.method,
            headers=headers,
            parameters=allparams,
            resource_path=resource_path,
            time_offset=0
        )
        raz_req_serialized = raz_req.SerializeToString()
        signed_request = base64.b64encode(raz_req_serialized)

        LOG.debug("inside check_access")
        request_data = {
          "requestId":self.requestid,
          "serviceType":"s3",
          "serviceName":"cm_s3",
          "user":"csso_ranade",  # make change to improve KERBEROS USER NAME
          "userGroups":[],
          "accessTime":"",
          "clientIpAddress":"",
          "clientType": "",
          "clusterName":"prakashdb23",
          "clusterType":"",
          "sessionId":"",
          "context":{"S3_SIGN_REQUEST":signed_request}
        }
        headers = {"Content-Type":"application/json", "Accept-Encoding":"gzip,deflate"}

        LOG.debug("sending access check headers: {%s} request_data: {%s}" % (headers, request_data))
        rurl = "%s/api/authz/s3/access?delegation=%s"%(self.raz_url, self.raz_token)
        raz_req = requests.post(rurl, headers=headers, json=request_data, verify=False)

        s3_sign_response = None
        signed_response = None

        if raz_req.ok:
            if raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]=="NOT_DETERMINED":
                LOG.error("failure %s"%(raz_req.json()))
                sys.exit(1)
            if raz_req.json().get("operResult", False) and raz_req.json()["operResult"]["result"]=="ALLOWED":
                s3_sign_response=raz_req.json()["operResult"]["additionalInfo"]["S3_SIGN_RESPONSE"]
            if s3_sign_response:
                raz_response_proto=raz_signer.SignResponseProto()
                signed_response=raz_response_proto.FromString(base64.b64decode(s3_sign_response))
                LOG.debug("Received signed Response %s" % signed_response)
            if signed_response:
                for i in signed_response.signer_generated_headers:
                    self.request.headers[i.key]=i.value
        if not signed_response:
            return False
        return True


def getRazSign(request, *args, **kwargs):
    raz_url="https://prakashdh27-master10.prakashr.xcu2-8y8x.dev.cldr.work:6082"
    kerberos_auth = requests_kerberos.HTTPKerberosAuth(mutual_authentication=requests_kerberos.OPTIONAL)
    raz = RazToken(raz_url, kerberos_auth)
    raz_token = raz.get_delegation_token(user="csso_ranade")

    raz = RazClient(request, raz_url, raz_token, args, kwargs)

    rs = raz.check_access()

    if rs == False:
        return False

# class RangerRazClient:
#   def __init__(self, url, auth):
#     self.url = url
#     self.session = Session()
#     self.session.auth = auth

#     logging.getLogger("requests").setLevel(logging.WARNING)


# class RangerRazS3:
#   def __init__(self, url, auth):
#     self.razClient = RangerRazClient(url, auth)

#   def get_signed_url(self, region, bucket, relative_path, action="read"):
#     req = RangerRazRequest()

    # endpoint_prefix="s3",
    # service_name="s3",
    # endpoint=endpoint, # https://s3-us-west-1.amazonaws.com
    # http_method=self.request.method,
    # headers=headers,
    # parameters=allparams,
    # resource_path=resource_path,
    # time_offset=0

    # req.serviceType = "s3"
    # req.operation = ResourceAccess(
    #   # TODO: parameters for S3
    #   {
    #     "resource": {
    #       "storageaccount": region,
    #       "container": bucket,
    #       "relativepath": relative_path,
    #     },
    #     "action": action,
    #   }
    # )

    # res = self.razClient.check_privilege(req)

    # # TODO: Check if no access inside RangerRazResult and raise exception, cf. res["operResult"]["result"]=="ALLOWED":

    # return res.operResult.additionalInfo["S3_SIGN_RESPONSE"]
