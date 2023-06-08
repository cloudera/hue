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

import json
import logging
import os

from requests import Session, Response
from desktop.lib.raz.ranger.model.ranger_raz import RangerRazResult
from apache_ranger.utils import *


LOG = logging.getLogger()


class RangerRazClient:
  def __init__(self, url, auth):
    self.url = url
    self.session = Session()
    self.session.auth = auth

    logging.getLogger("requests").setLevel(logging.WARNING)

  def get_delegation_token(self, renewer, dtServiceName=None, doAsUser=None):
    resp = None

    if self.__is_kerberos_authenticated():
      resp = self.__call_api(
        RangerRazClient.GET_DELEGATION_TOKEN,
        self.__get_query_params(
          {
            RangerRazClient.PARAM_OP: RangerRazClient.GET_DELEGATION_TOKEN,
            RangerRazClient.PARAM_RENEWER: renewer,
            RangerRazClient.PARAM_DT_SERVICENAME: dtServiceName,
          },
          doAsUser,
        ),
      )
    else:
      LOG.error("Kerberos Authentication is required to get RAZ delegation token")

    return resp

  def renew_delegation_token(self, delegation_token, doAsUser=None):
    resp = None

    if self.__is_kerberos_authenticated():
      resp = self.__call_api(
        RangerRazClient.RENEW_DELEGATION_TOKEN,
        self.__get_query_params(
          {
            RangerRazClient.PARAM_OP: RangerRazClient.RENEW_DELEGATION_TOKEN,
            RangerRazClient.PARAM_TOKEN: delegation_token,
          },
          doAsUser,
        ),
      )
    else:
      LOG.error(
        "Kerberos Authentication is required to renew RAZ delegation token"
      )

    return resp

  def cancel_delegation_token(self, delegation_token, doAsUser=None):
    resp = None

    if self.__is_kerberos_authenticated():
      resp = self.__call_api(
        RangerRazClient.CANCEL_DELEGATION_TOKEN,
        self.__get_query_params(
          {
            RangerRazClient.PARAM_OP: RangerRazClient.CANCEL_DELEGATION_TOKEN,
            RangerRazClient.PARAM_TOKEN: delegation_token,
          },
          doAsUser,
        ),
      )
    else:
      LOG.error(
        "Kerberos Authentication is required to cancel RAZ delegation token"
      )

    return resp

  def check_privilege(self, raz_request, doAsUser=None):
    resp = self.__call_api(
      RangerRazClient.CHECK_PRIVILEGE.format_path(
        {"serviceType": raz_request.serviceType}
      ),
      query_params=self.__get_query_params(None, doAsUser),
      request_data=raz_request,
    )

    return type_coerce(resp, RangerRazResult)

  def check_privileges(self, raz_requests, doAsUser=None):
    resp = self.__call_api(
      RangerRazClient.CHECK_PRIVILEGES.format_path(
        {"serviceType": raz_requests.serviceType}
      ),
      query_params=self.__get_query_params(None, doAsUser),
      request_data=raz_requests,
    )

    return type_coerce_list(resp, RangerRazResult)

  def __is_kerberos_authenticated(self):
    from requests_kerberos import HTTPKerberosAuth

    return isinstance(self.session.auth, HTTPKerberosAuth)

  def __get_query_params(self, query_params, doAsUser=None):
    if doAsUser is not None:
      query_params = query_params or {}

      query_params[RangerRazClient.PARAM_DOAS] = doAsUser

    return query_params

  def __call_api(self, api, query_params=None, request_data=None):
    ret = None
    params = {"headers": {"Accept": api.consumes, "Content-type": api.produces}}

    if query_params:
      params["params"] = query_params

    if request_data:
      params["data"] = json.dumps(request_data)

    path = os.path.join(self.url, api.path)

    if LOG.isEnabledFor(logging.DEBUG):
      LOG.debug("------------------------------------------------------")
      LOG.debug("Call         : %s %s", api.method, path)
      LOG.debug("Content-type : %s", api.consumes)
      LOG.debug("Accept       : %s", api.produces)

    response = None

    if api.method == HttpMethod.GET:
      response = self.session.get(path, **params)
    elif api.method == HttpMethod.POST:
      response = self.session.post(path, **params)
    elif api.method == HttpMethod.PUT:
      response = self.session.put(path, **params)
    elif api.method == HttpMethod.DELETE:
      response = self.session.delete(path, **params)

    if LOG.isEnabledFor(logging.DEBUG):
      LOG.debug("HTTP Status: %s", response.status_code if response else "None")

    if response is None:
      ret = None
    elif response.status_code == api.expected_status:
      try:
        if response.content is not None:
          if LOG.isEnabledFor(logging.DEBUG):
            LOG.debug(
              "<== __call_api(%s, %s, %s), result=%s",
              vars(api),
              params,
              request_data,
              response,
            )

            LOG.debug(response.json())

          ret = response.json()
        else:
          ret = None
      except Exception as e:
        print(e)

        LOG.exception(
          "Exception occurred while parsing response with msg: %s", e
        )

        raise RangerRazException(api, response)
    elif response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
      LOG.error(
        "Ranger Raz server unavailable. HTTP Status: %s",
        HTTPStatus.SERVICE_UNAVAILABLE,
      )

      ret = None
    else:
      raise RangerRazException(api, response)

    return ret

  # URIs
  PARAM_OP = "op"
  PARAM_RENEWER = "renewer"
  PARAM_TOKEN = "token"
  PARAM_DELEGATION = "delegation"
  PARAM_DOAS = "doAs"
  PARAM_DT_SERVICENAME = "service"
  OP_GETDELEGATIONTOKEN = "GETDELEGATIONTOKEN"
  OP_RENEWDELEGATIONTOKEN = "RENEWDELEGATIONTOKEN"
  OP_CANCELDELEGATIONTOKEN = "CANCELDELEGATIONTOKEN"
  URI_DELEGATION_TOKEN = ""
  URI_CHECK_PRIVILEGE = "api/authz/{serviceType}/access"
  URI_CHECK_PRIVILEGES = "api/authz/{serviceType}/accesses"

  # APIs
  GET_DELEGATION_TOKEN = API(URI_DELEGATION_TOKEN, HttpMethod.GET, HTTPStatus.OK)
  RENEW_DELEGATION_TOKEN = API(URI_DELEGATION_TOKEN, HttpMethod.PUT, HTTPStatus.OK)
  CANCEL_DELEGATION_TOKEN = API(URI_DELEGATION_TOKEN, HttpMethod.PUT, HTTPStatus.OK)
  CHECK_PRIVILEGE = API(URI_CHECK_PRIVILEGE, HttpMethod.POST, HTTPStatus.OK)
  CHECK_PRIVILEGES = API(URI_CHECK_PRIVILEGES, HttpMethod.POST, HTTPStatus.OK)


class RangerRazException(Exception):
  """Exception raised for errors in API calls.

  Attributes:
    api      -- api endpoint which caused the error
    response -- response from the server
  """

  def __init__(self, api, response):
    self.method = api.method.name
    self.path = api.path
    self.expected_status = api.expected_status
    self.statusCode = -1
    self.msgDesc = None
    self.messageList = None

    print(response)

    if api is not None and response is not None:
      self.statusCode = response.status_code
      self.message = response.content

    Exception.__init__(
      self,
      "{} {} failed: expected_status={}, status={}, message={}".format(
        self.method,
        self.path,
        self.expected_status,
        self.statusCode,
        self.message,
      ),
    )
