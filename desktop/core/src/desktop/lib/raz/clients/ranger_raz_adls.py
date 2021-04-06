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

from desktop.lib.raz.clients.model.ranger_raz         import RangerRazRequest, RangerRazResult, ResourceAccess
from desktop.lib.raz.clients.client.ranger_raz_client import RangerRazClient
from apache_ranger.utils                    import *

LOG = logging.getLogger(__name__)

class RangerRazAdls:
    def __init__(self, url, auth):
        self.razClient = RangerRazClient(url, auth)

    def get_raz_client(self):
        return self.razClient

    def get_dsas_token(self, storage_account, container, relative_path, action):
        req = RangerRazRequest()

        req.serviceType = 'adls'
        req.operation   = ResourceAccess({'resource': {'storageaccount': storage_account, 'container': container, 'relativepath': relative_path}, 'action': action})

        res = self.razClient.check_privilege(req)

        return res.operResult.additionalInfo["ADLS_DSAS"]

'''
#
# Sample usage
#
from apache_ranger.client.ranger_raz_adls import RangerRazAdls
from requests_kerberos                    import HTTPKerberosAuth

razAdls = RangerRazAdls('https://<raz_server_host>:<raz_port>', HTTPKerberosAuth())

# disable HTTPS certificate validation; not recommended for production use
razAdls.razClient.session.verify = False

dsas = razAdls.get_dsas_token('<storage_account>', '<container>>', '<relative_path>', 'read')

print(dsas)
'''
