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
import sys

from desktop import conf
from desktop.lib.raz.clients import AdlsRazClient
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.exceptions_renderable import PopupException

if sys.version_info[0] > 2:
  from django.utils.translation import gettext as _
else:
  from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class RazHttpClient(HttpClient):

  def __init__(self, username, base_url, exc_class=None, logger=None):
    super(RazHttpClient, self).__init__(base_url, exc_class, logger)
    self.username = username

  def execute(self, http_method, path, params=None, data=None, headers=None, allow_redirects=False, urlencode=True,
              files=None, stream=False, clear_cookies=False, timeout=conf.REST_CONN_TIMEOUT.get(), retry=1):
    """
    From an object URL we get back the SAS token as a GET param string, e.g.:
    https://{storageaccountname}.dfs.core.windows.net/{container}/{path}
    -->
    https://{storageaccountname}.dfs.core.windows.net/{container}/{path}?sv=2014-02-14&sr=b&
    sig=pJL%2FWyed41tptiwBM5ymYre4qF8wzrO05tS5MCjkutc%3D&st=2015-01-02T01%3A40%3A51Z&se=2015-01-02T02%3A00%3A51Z&sp=r
    """

    url = self._make_url(path, params)

    # For root stats, the root path needs to end with '/' before adding the query params.
    if params and 'action' in params and params['action'] == 'getAccessControl':
      partition_url = list(url.partition('?'))
      partition_url[0] += '/'
      url = ''.join(partition_url)

    sas_token = self.get_sas_token(http_method, self.username, url, params, headers)

    signed_url = url + ('?' if '?' not in url else '&') + sas_token

    # self._make_url is called in base class execute method as well,
    # so we remove https://{storageaccountname}.dfs.core.windows.net from the signed url here.
    signed_path = signed_url.partition('.dfs.core.windows.net')[2]

    try:
      # Sometimes correct call with SAS token fails, so we retry some operations once again.
      if retry >= 0:
        return super(RazHttpClient, self).execute(
            http_method=http_method,
            path=signed_path,
            data=data,
            headers=headers,
            allow_redirects=allow_redirects,
            urlencode=False,
            files=files,
            stream=stream,
            clear_cookies=clear_cookies,
            timeout=timeout
        )
    except Exception as e:
      LOG.debug('ABFS Exception: ' + str(e))

      # Only retrying safe operations once.
      if http_method in ('HEAD', 'GET') and e.code == 403: 
        LOG.debug('Retrying same operation again for path: %s' % path)
        retry -= 1
        return self.execute(
            http_method=http_method, 
            path=path, 
            params=params, 
            data=data, 
            headers=headers, 
            allow_redirects=allow_redirects, 
            urlencode=urlencode, 
            files=files, 
            stream=stream, 
            clear_cookies=clear_cookies, 
            timeout=timeout, 
            retry=retry
        )
      else:
        # Re-raise all other exceptions to be handled later for other operations such as rename.
        raise e

  def get_sas_token(self, http_method, username, url, params=None, headers=None):
    raz_client = AdlsRazClient(username=username)
    response = raz_client.get_url(action=http_method, path=url, headers=headers)

    if response and response.get('token'):
      return response.get('token')
    else:
      raise PopupException(_('No SAS token in RAZ response'), error_code=403)
