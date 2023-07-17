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

"""
Interfaces for ADLS via HttpFs/WebHDFS
"""
from future import standard_library
standard_library.install_aliases()
import logging
import threading

from urllib.parse import urlparse

from hadoop.fs.webhdfs import WebHdfs as HadoopWebHdfs
from hadoop.fs.exceptions import WebHdfsException
from hadoop.hdfs_site import get_umask_mode

from desktop.lib.rest import http_client, resource
from azure.conf import get_default_adls_url, get_default_adls_fs, PERMISSION_ACTION_ADLS


LOG = logging.getLogger()

#Azure has a 30MB block limit on upload.
UPLOAD_CHUCK_SIZE = 30 * 1000 * 1000


class WebHdfs(HadoopWebHdfs):

  def __init__(
      self, url,
      fs_defaultfs,
      logical_name=None,
      hdfs_superuser=None,
      security_enabled=False,
      ssl_cert_ca_verify=True,
      temp_dir="/tmp",
      umask=0o1022,
      hdfs_supergroup=None,
      access_token=None,
      token_type=None,
      expiration=None
    ):
    self._url = url
    self._superuser = hdfs_superuser
    self._security_enabled = security_enabled
    self._ssl_cert_ca_verify = ssl_cert_ca_verify
    self._temp_dir = temp_dir
    self._umask = umask
    self._fs_defaultfs = fs_defaultfs
    self._logical_name = logical_name
    self._supergroup = hdfs_supergroup
    self._access_token = access_token
    self._token_type = token_type
    split = urlparse(fs_defaultfs)
    self._scheme = split.scheme
    self._netloc = split.netloc
    self._is_remote = True
    self._has_trash_support = False
    self._filebrowser_action = PERMISSION_ACTION_ADLS

    self._root = self.get_client(url)
    self.expiration = expiration

    # To store user info
    self._thread_local = threading.local()

    LOG.debug("Initializing Azure ADLS WebHdfs: %s (security: %s, superuser: %s)" % (self._url, self._security_enabled, self._superuser))

  @classmethod
  def from_config(cls, hdfs_config, auth_provider):
    credentials = auth_provider.get_credentials()
    fs_defaultfs = get_default_adls_fs()
    url = get_default_adls_url()

    return cls(
        url=url,
        fs_defaultfs=fs_defaultfs,
        logical_name=None,
        security_enabled=False,
        ssl_cert_ca_verify=False,
        temp_dir=None,
        umask=get_umask_mode(),
        hdfs_supergroup=None,
        access_token=credentials.get('access_token'),
        token_type=credentials.get('token_type'),
        expiration=int(credentials.get('expires_on')) * 1000 if credentials.get('expires_on')  is not None else None
    )

  def get_client(self, url):
    return resource.Resource(http_client.HttpClient(url, exc_class=WebHdfsException, logger=LOG))

  def _getheaders(self):
    return {
      "Authorization": self._token_type + " " + self._access_token,
    }

  def is_web_accessible(self):
    return False # Does not support OP=GETDELEGATIONTOKEN HADOOP-14579

  def get_upload_chuck_size(self):
    return UPLOAD_CHUCK_SIZE

  def filebrowser_action(self):
    return self._filebrowser_action
