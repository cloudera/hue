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

import logging

from desktop.lib.raz.ranger.model.ranger_raz import RangerRazRequest, ResourceAccess
from desktop.lib.raz.ranger.clients.ranger_raz_client import RangerRazClient


LOG = logging.getLogger()


class RangerRazS3:
  def __init__(self, url, auth):
    self.razClient = RangerRazClient(url, auth)

  def get_signed_url(self, region, bucket, relative_path, action="read"):
    req = RangerRazRequest()

    # endpoint_prefix="s3",
    # service_name="s3",
    # endpoint=endpoint, # https://s3-us-west-1.amazonaws.com
    # http_method=self.request.method,
    # headers=headers,
    # parameters=allparams,
    # resource_path=resource_path,
    # time_offset=0

    req.serviceType = "s3"
    req.operation = ResourceAccess(
      # TODO: parameters for S3
      {
        "resource": {
          "storageaccount": region,
          "container": bucket,
          "relativepath": relative_path,
        },
        "action": action,
      }
    )

    res = self.razClient.check_privilege(req)

    # TODO: Check if no access inside RangerRazResult and raise exception, cf. res["operResult"]["result"]=="ALLOWED":

    return res.operResult.additionalInfo["S3_SIGN_RESPONSE"]
