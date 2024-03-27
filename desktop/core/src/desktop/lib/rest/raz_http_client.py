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
import posixpath

from django.utils.translation import gettext as _
from django.utils.encoding import iri_to_uri

from desktop import conf
from desktop.lib.raz.clients import AdlsRazClient
from desktop.lib.rest.http_client import HttpClient
from desktop.lib.exceptions_renderable import PopupException

from urllib.parse import quote, urlencode


LOG = logging.getLogger()


class RazHttpClient(HttpClient):
  """
  A custom HTTP client that adds support for generating Shared Access Signature (SAS) tokens for ABFS.

  This class extends :class:`desktop.lib.rest.http_client.HttpClient`. The main difference is the addition of the `execute` method,
  which generates a SAS token based on the given parameters and appends it to the URL before making the actual request using the
  parent class's `execute` method to ABFS for performing the user action.

  Args:
    username (str): The name of the user associated with the object URL. Used to generate the SAS token.
    base_url (str): Base URL for the REST API endpoint. Must include protocol (HTTP or HTTPS) and hostname.
    exc_class (type, optional): An exception type used by this instance when raising errors. Defaults to None.
    logger (logging.Logger, optional): A logger instance. If not provided, uses the default logger. Defaults to None.
  """

  def __init__(self, username, base_url, exc_class=None, logger=None):
    super(RazHttpClient, self).__init__(base_url, exc_class, logger)
    self.username = username

  def execute(self, http_method, path, params=None, data=None, headers=None, allow_redirects=False, urlencode=True,
              files=None, stream=False, clear_cookies=False, timeout=conf.REST_CONN_TIMEOUT.get(), retry=1):
    """
    Overrides the parent class's `execute` method. Before making the request, generates a SAS token based on the given parameters and
    appends it to the URL. Then calls the parent class's `execute` method with the modified URL to send the user action request to ABFS.

    Eg: https://{storageaccountname}.dfs.core.windows.net/{container}/{path}
        -->
        https://{storageaccountname}.dfs.core.windows.net/{container}/{path}?sv=2014-02-14&sr=b&
        sig=pJL%2FWyed41tptiwBM5ymYre4qF8wzrO05tS5MCjkutc%3D&st=2015-01-02T01%3A40%3A51Z&se=2015-01-02T02%3A00%3A51Z&sp=r

    Returns:
      Any: The result returned by the parent class's `execute` method after performing the user action to ABFS.

    Raises:
      PopupException: When no SAS token is present in the RAZ response.
    """
    url = self._make_url(quote(path), params)

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
    """
    Request a SAS token from the RAZ service for the specified resource.

    Calls the RAZ client's `get_url` method and returns the received token if available. Otherwise, raises
    a PopupException indicating a missing token.

    Returns:
      str: The generated SAS token if successful; otherwise, raises an exception.

    Raises:
      PopupException: When no SAS token is present in the RAZ response.
    """
    raz_client = AdlsRazClient(username=username)
    response = raz_client.get_url(action=http_method, path=url, headers=headers)

    if response and response.get('token'):
      return response.get('token')
    else:
      raise PopupException(_('No SAS token in RAZ response'), error_code=403)

  def _make_url(self, path, params, do_urlencode=True):
    """
    Construct a complete URL with the given path and optional query parameters.

    The method overrides parent class's `_make_url` method to change parameter normalization and ensures proper escaping
    for RAZ by changing the default behaviour of `urlencode` helper method for special characters.

    Returns:
      str: A fully qualified URL including the scheme, domain, path, and optionally, query parameters.
    """
    res = self._base_url

    if path:
      res += posixpath.normpath('/' + path.lstrip('/'))

    if params:
      param_str = urlencode(params, safe='/', quote_via=quote) if do_urlencode else '&'.join(['%s=%s' % (k, v) for k, v in params.items()])
      res += '?' + param_str

    return iri_to_uri(res)
