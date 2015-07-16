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
import os

from kazoo.client import KazooClient

from hadoop import cluster
from libzookeeper.conf import ENSEMBLE, PRINCIPAL_NAME


LOG = logging.getLogger(__name__)


class ReadOnlyClientException(Exception):
  pass


class ZookeeperConfigurationException(Exception):
  pass


class ZookeeperClient(object):

  def __init__(self, hosts=None, read_only=True):
    self.hosts = hosts if hosts else ENSEMBLE.get()
    self.read_only = read_only

    hdfs = cluster.get_hdfs()

    if hdfs is None:
      raise ZookeeperConfigurationException('No [hdfs] configured in hue.ini.')

    if hdfs.security_enabled:
      self.sasl_server_principal = PRINCIPAL_NAME.get()
    else:
      self.sasl_server_principal = None

    self.zk = KazooClient(hosts=self.hosts,
                          read_only=self.read_only,
                          sasl_server_principal=self.sasl_server_principal)


  def get_children_data(self, namespace):
    children_data = []
    try:
      self.zk.start()

      children = self.zk.get_children(namespace)

      for node in children:
        data, stat = self.zk.get("%s/%s" % (namespace, node))
        children_data.append(data)
    finally:
      self.zk.stop()

    return children_data


  def copy_path(self, namespace, filepath):
    if self.read_only:
      raise ReadOnlyClientException('Cannot execute copy_path when read_only is set to True.')

    try:
      self.zk.start()

      self.zk.ensure_path(namespace)
      for dir, subdirs, files in os.walk(filepath):
        path = dir.replace(filepath, '').strip('/')
        if path:
          node_path = '%s/%s' % (namespace, path)
          self.zk.create(path=node_path, value='', makepath=True)
        for filename in files:
          node_path = '%s/%s/%s' % (namespace, path, filename)
          with open(os.path.join(dir, filename), 'r') as f:
            file_content = f.read()
            self.zk.create(path=node_path, value=file_content, makepath=True)
    finally:
      self.zk.stop()


  def delete_path(self, namespace):
    if self.read_only:
      raise ReadOnlyClientException('Cannot execute delete_path when read_only is set to True.')

    try:
      self.zk.start()

      self.zk.delete(namespace, recursive=True)
    finally:
      self.zk.stop()
