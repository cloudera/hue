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

from kazoo.client import KazooClient

from hadoop import cluster
from desktop.lib.exceptions_renderable import PopupException

from libzookeeper.conf import PRINCIPAL_NAME


def get_children_data(ensemble, namespace, read_only=True):
  hdfs = cluster.get_hdfs()
  if hdfs is None:
    raise PopupException(_('No [hdfs] configured in hue.ini.'))

  if hdfs.security_enabled:
    sasl_server_principal = PRINCIPAL_NAME.get()
  else:
    sasl_server_principal = None

  zk = KazooClient(hosts=ensemble, read_only=read_only, sasl_server_principal=sasl_server_principal)

  zk.start()

  children_data = []

  children = zk.get_children(namespace)

  for node in children:
    data, stat = zk.get("%s/%s" % (namespace, node))
    children_data.append(data)

  zk.stop()

  return children_data
