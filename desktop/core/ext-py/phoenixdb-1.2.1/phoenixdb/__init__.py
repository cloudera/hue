# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys

import gssapi

from phoenixdb import errors, types
from phoenixdb.avatica import AvaticaClient
from phoenixdb.connection import Connection
from phoenixdb.errors import *  # noqa: F401,F403
from phoenixdb.types import *  # noqa: F401,F403

from requests.auth import HTTPBasicAuth, HTTPDigestAuth

from requests_gssapi import HTTPSPNEGOAuth

if sys.version_info.major == 3:
    from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
else:
    from urllib import urlencode
    from urlparse import urlparse, urlunparse, parse_qs

__all__ = ['connect', 'apilevel', 'threadsafety', 'paramstyle'] + types.__all__ + errors.__all__


apilevel = "2.0"
"""
This module supports the `DB API 2.0 interface <https://www.python.org/dev/peps/pep-0249/>`_.
"""

threadsafety = 1
"""
Multiple threads can share the module, but neither connections nor cursors.
"""

paramstyle = 'qmark'
"""
Parmetrized queries should use the question mark as a parameter placeholder.

For example::

 cursor.execute("SELECT * FROM table WHERE id = ?", [my_id])
"""


def connect(url, max_retries=None, auth=None, authentication=None, avatica_user=None, avatica_password=None,
            truststore=None, verify=None, do_as=None, user=None, password=None, **kwargs):
    """Connects to a Phoenix query server.

    :param url:
        URL to the Phoenix query server, e.g. ``http://localhost:8765/``

    :param autocommit:
        Switch the connection to autocommit mode.

    :param readonly:
        Switch the connection to readonly mode.

    :param max_retries:
        The maximum number of retries in case there is a connection error.

    :param cursor_factory:
        If specified, the connection's :attr:`~phoenixdb.connection.Connection.cursor_factory`
        is set to it.

    :param auth:
        Authentication configuration object as expected by the underlying python_requests and
        python_requests_gssapi library

    :param verify:
        The path to the PEM file for verifying the server's certificate. It is passed directly to
        the `~verify` parameter of the underlying python_requests library.
        Setting it to False disables the server certificate verification.

    :param do_as:
        Username to impersonate (sets the Hadoop doAs URL parameter)

    :param authentication:
        Alternative way to specify the authentication mechanism that mimics
        the semantics of the JDBC drirver

    :param avatica_user:
        Username for BASIC or DIGEST authentication. Use in conjunction with the
        `~authentication' option.

    :param avatica_password:
        Password for BASIC or DIGEST authentication. Use in conjunction with the
        `~authentication' option.

    :param user
        If `~authentication' is BASIC or DIGEST then alias for `~avatica_user`
        If `~authentication' is NONE or SPNEGO then alias for `~do_as`

    :param password
        If `~authentication' is BASIC or DIGEST then is alias for `~avatica_password`

    :param truststore:
        Alias for verify

    :returns:
        :class:`~phoenixdb.connection.Connection` object.
    """

    (url, auth, verify) = _process_args(
        url, auth=auth, authentication=authentication,
        avatica_user=avatica_user, avatica_password=avatica_password,
        truststore=truststore, verify=verify, do_as=do_as, user=user, password=password)

    client = AvaticaClient(url, max_retries=max_retries, auth=auth, verify=verify)
    client.connect()
    return Connection(client, **kwargs)


def _get_SPNEGOAuth():
    try:
        spnego = gssapi.mechs.Mechanism.from_sasl_name("SPNEGO")
    except AttributeError:
        spnego = gssapi.OID.from_int_seq("1.3.6.1.5.5.2")
    return HTTPSPNEGOAuth(opportunistic_auth=True, mech=spnego)


def _process_args(
        url, auth=None, authentication=None, avatica_user=None, avatica_password=None,
        truststore=None, verify=None, do_as=None, user=None, password=None):
    url_parsed = urlparse(url)
    url_params = parse_qs(url_parsed.query, keep_blank_values=True)

    # Parse supported JDBC compatible parameters from URL. args have precendece
    # Unlike the JDBC driver, we are expecting these as query params, as the avatica java client
    # has a different idea of what an URL param is than urlparse. (urlparse seems just broken
    # in this regard)
    params_changed = False
    if auth is None and authentication is None and 'authentication' in url_params:
        authentication = url_params['authentication'][0]
        del url_params['authentication']
        params_changed = True

    if avatica_user is None and 'avatica_user' in url_params:
        avatica_user = url_params['avatica_user'][0]
        del url_params['avatica_user']
        params_changed = True

    if avatica_password is None and 'avatica_password' in url_params:
        avatica_password = url_params['avatica_password'][0]
        del url_params['avatica_password']
        params_changed = True

    if verify is None and truststore is None and 'truststore' in url_params:
        truststore = url_params['truststore'][0]
        del url_params['truststore']
        params_changed = True

    if authentication == 'BASIC' or authentication == 'DIGEST':
        # Handle standard user and password parameters
        if user is not None and avatica_user is None:
            avatica_user = user
        if password is not None and avatica_password is None:
            avatica_password = password
    else:
        # interpret standard user parameter as do_as for SPNEGO and NONE
        if user is not None and do_as is None:
            do_as = user

    # Add doAs
    if do_as:
        url_params['doAs'] = do_as
        params_changed = True

    if params_changed:
        url_parsed = url_parsed._replace(query=urlencode(url_params))
        url = urlunparse(url_parsed)

    if auth == "SPNEGO":
        # Special case for backwards compatibility
        auth = _get_SPNEGOAuth()
    elif auth is None and authentication is not None:
        if authentication == "SPNEGO":
            auth = _get_SPNEGOAuth()
        elif authentication == "BASIC" and avatica_user is not None and avatica_password is not None:
            auth = HTTPBasicAuth(avatica_user, avatica_password)
        elif authentication == "DIGEST" and avatica_user is not None and avatica_password is not None:
            auth = HTTPDigestAuth(avatica_user, avatica_password)

    if verify is None and truststore is not None:
        verify = truststore

    return (url, auth, verify)
