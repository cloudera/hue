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


from desktop.lib import thrift_util

from beeswax import conf
from beeswax.models import HIVE_SERVER2
from beeswax.server.beeswax_lib import BeeswaxClient
from beeswax.server.dbms import get_query_server_config
from beeswax.conf import SERVER_INTERFACE


def get(user, query_server=None):
  # Avoid circular dependency
  from ImpalaService import ImpalaHiveServer2Service, ImpalaService

  if query_server is None:
    query_server = get_query_server_config(name='impala')

  if SERVER_INTERFACE.get() == HIVE_SERVER2:
    return ImpalaServerClient(ImpalaHiveServer2Service, query_server, user)
  else:
    return ImpalaServerClient(ImpalaService, query_server, user)


class ImpalaServerClient:
  """Only support ResetCatalog()"""

  def __init__(self, client_class, query_server, user):
    self.query_server = query_server
    self.user = user

    use_sasl, kerberos_principal_short_name = BeeswaxClient.get_security(query_server)

    self._client = thrift_util.get_client(client_class.Client,
                                          query_server['server_host'],
                                          query_server['server_port'],
                                          service_name='Impala',
                                          kerberos_principal=kerberos_principal_short_name,
                                          use_sasl=use_sasl,
                                          timeout_seconds=conf.BEESWAX_SERVER_CONN_TIMEOUT.get())
  def resetCatalog(self):
    return self._client.ResetCatalog()
