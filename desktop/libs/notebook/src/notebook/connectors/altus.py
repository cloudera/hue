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
import json
import subprocess

from django.urls import reverse
from django.utils.translation import ugettext as _

from desktop.lib.exceptions_renderable import PopupException


LOG = logging.getLogger(__name__)


def _exec(command, args):
  try:
    data = subprocess.check_output([
        'altus',
        command,
       ] +
       args
    )
  except Exception, e:
    raise PopupException(e, title=_('Error accessing'))

  response = json.loads(data)

  return response


class IAMApi(): pass
# altus iam list-user-assigned-roles --user=crn:altus:ia


class SdxApi():

  def __init__(self, user): pass

  def list_namespaces(self):
    """
    e.g. returns
    [{
      u'status': u'CREATED',
      u'namespaceName': u'cca-5150-ns',
      u'creationDate': u'2018-06-03T23:24:46.125000+00:00',
      u'crn': u'crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:cca-5150-ns/f54461af-b241-4f1d-a521-ab3624e841c4'},
      ...
    ]
    """

    args = ['list-namespaces']
    return _exec('sdx', args)['namespaces']


class AnalyticDbApi():

  def __init__(self, user): pass

  def list_clusters(self):
    """
    e.g. returns
    [{
            "status": "CREATED",
            "namespaceCrn": "crn:altus:sdx:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:namespace:spot-ns/7bdb225f-a7a1-408e-8503-1b3a422cc039",
            "workersGroupSize": 4,
            "clusterName": "spot",
            "environmentType": "AWS",
            "secured": false,
            "environmentCrn": "crn:altus:environments:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:environment:Spot-AWS-dev2/5a6d0ced-c8af-4fa3-9b24-8c5a3ea11cf8",
            "securityConfiguration": {
                "enabled": false
            },
            "creationDate": "2018-06-01T13:14:43.530000+00:00",
            "crn": "crn:altus:analyticdb:us-west-1:12a0079b-1591-4ca0-b721-a446bda74e67:cluster:spot/70595482-6a46-4a9d-b395-56fcabe079e4",
            "instanceType": "r4.4xlarge",
            "cdhVersion": "CDH514"
        },
      ...
    ]
    """

    args = ['list-clusters']
    return _exec('analyticdb', args)['clusters']
