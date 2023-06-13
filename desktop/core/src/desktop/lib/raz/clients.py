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

from desktop.conf import RAZ
from desktop.lib.raz.raz_client import get_raz_client


LOG = logging.getLogger()


class S3RazClient():

  def __init__(self, username):
    self.username = username

  def get_url(self, action='GET', path=None, headers=None, data=None):
    '''
    Example of headers:
    {
      u'x-amz-content-sha256': u'UNSIGNED-PAYLOAD',
      u'Host': u'prakashmowdev1.s3-us-west-2.amazonaws.com',
      u'X-Amz-Security-Token': u'IQoJb3JpZ2luX2Vj...C',
      u'X-Amz-Date': u'20210604T102022Z',
      u'Authorization': u'AWS4-HMAC-SHA256 Credential=ASIAYO3P24NAOAYMMDNN/20210604/us-west-2/s3/aws4_request, 
                          SignedHeaders=host;user-agent;x-amz-content-sha256;x-amz-date;x-amz-security-token, 
                          Signature=d341a194c2998c64b6fc726b69d0c3c2b97d520265f80df7e1bc1ac59a21ef94',
      u'User-Agent': u'user:csso_romain'
    }
    '''
    c = get_raz_client(
      raz_url=RAZ.API_URL.get(),
      username=self.username,
      auth=RAZ.API_AUTHENTICATION.get(),
      service='s3',
    )

    return c.check_access(method=action, url=path, headers=headers, data=data)


class AdlsRazClient():

  def __init__(self, username):
    self.username = username

  def get_url(self, action='GET', path=None, headers=None):
    c = get_raz_client(
      raz_url=RAZ.API_URL.get(),
      username=self.username,
      auth=RAZ.API_AUTHENTICATION.get(),
      service='adls',
    )

    # We need to sign the header source path separately for rename operation
    if headers.get('x-ms-rename-source'):
      partition_path = path.partition('.dfs.core.windows.net')
      source_path = partition_path[0] + partition_path[1] + headers.get('x-ms-rename-source')

      sas_token = c.check_access(method=action, url=source_path, headers=None)
      headers['x-ms-rename-source'] += '?' + sas_token.get('token')

    return c.check_access(method=action, url=path, headers=headers)
