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

# Copyright (c) 2011-2013 Cloudera, Inc. All rights reserved.

import httplib
import logging
import socket
import sys
import time
import urllib2
from urllib2_kerberos import HTTPKerberosAuthHandler

from M2Crypto import httpslib
from M2Crypto import SSL
from M2Crypto import m2

logging.basicConfig()
LOG = logging.getLogger(__name__)

# urlopen_with_timeout.
#
# The optional secure_http_service_name parameter allows callers to connect to
# secure HTTP servers via the urllib2_kerberos library. We have a modified
# version of the HTTPKerberosAuthHandler code which takes the Kerberos service
# name rather than construct the name using the HTTP request host. We always add
# the HTTPKerberosAuthHandler to urllib2 opener handlers because it has no effect
# if security is not actually enabled.
#
# The optional username and pasword parameters similarly handle setting up HTTP
# digest authentication. Again, this has no effect if HTTP digest authentication
# is not in use on the connection.
#
# The cafile, capath and max_cert_depth control the SSL certificate verification
# behavior. https://www.openssl.org/docs/ssl/SSL_CTX_load_verify_locations.html
# explains the semantics of the parameters. Passing none for both means that
# no verification of the server certification (including the server's hostname)
# will be performed.
def urlopen_with_timeout(url,
                         data=None,
                         timeout=None,
                         secure_http_service_name=None,
                         username=None,
                         password=None,
                         cafile=None,
                         capath=None,
                         max_cert_depth=9):

  openers = []
  openers.append(_make_https_handler(cafile,
                                     capath,
                                     max_cert_depth))

  openers.append(HTTPKerberosAuthHandler(secure_http_service_name))

  full_url = url
  if isinstance(url, urllib2.Request):
    full_url = url.get_full_url()
  openers.append(_make_http_digest_auth_handler(full_url, username, password))

  LOG.info("url_util: urlopen_with_timeout: full_url: %s" % full_url)
  if sys.version_info < (2, 6):
    # The timeout parameter to urlopen was introduced in Python 2.6.
    # To workaround it in older versions of python, we copy, with
    # minor modification, httplib.HTTPConnection, and hook it all
    # up.
    openers.append(_make_timeout_handler(timeout))
    opener = urllib2.build_opener(*openers)
    LOG.info("url_util: urlopen_with_timeout: sys.version_inf < (2, 6): opener: %s" % opener)
    return opener.open(url, data)
  else:
    openers.append(_make_timeout_handler(timeout))
    opener = urllib2.build_opener(*openers)
    LOG.info("url_util: urlopen_with_timeout: sys.version_inf > (2, 6): opener: %s" % opener)
    return opener.open(url, data, timeout)

def head_request_with_timeout(url,
                              data=None,
                              timeout=None,
                              secure_http_service_name=None,
                              username=None,
                              password=None,
                              cafile=None,
                              capath=None,
                              max_cert_depth=9):

  class HeadRequest(urllib2.Request):
    def get_method(self):
      return "HEAD"

  if isinstance(url, urllib2.Request):
    raise Exception("Unsupported url type: urllib2.Request.")

  LOG.info("url_util: head_request_with_timeout: url: %s: timeout: %s" % (url, timeout))
  return urlopen_with_timeout(HeadRequest(url),
                              data,
                              timeout,
                              secure_http_service_name,
                              username,
                              password,
                              cafile,
                              capath,
                              max_cert_depth)

def _make_timeout_handler(timeout):
  # Create these two helper classes fresh each time, since
  # timeout needs to be in the closure.

  class TimeoutHTTPConnection(httplib.HTTPConnection):
    def connect(self):
      """Connect to the host and port specified in __init__."""
      msg = "getaddrinfo returns an empty list"
      for res in socket.getaddrinfo(self.host, self.port, 0,
                      socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
          self.sock = socket.socket(af, socktype, proto)
          if timeout is not None:
            self.sock.settimeout(timeout)
          if self.debuglevel > 0:
            LOG.info("connect: (%s, %s)" % (self.host, self.port))
          self.sock.connect(sa)
        except socket.error, msg:
          if self.debuglevel > 0:
            LOG.info('connect fail:', (self.host, self.port))
          if self.sock:
            self.sock.close()
          self.sock = None
          continue
        break
      if not self.sock:
        raise socket.error, msg

  class TimeoutHTTPHandler(urllib2.HTTPHandler):
    http_request = urllib2.AbstractHTTPHandler.do_request_
    def http_open(self, req):
      return self.do_open(TimeoutHTTPConnection, req)

  return TimeoutHTTPHandler

def _make_http_digest_auth_handler(url, username, password):
  password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
  password_manager.add_password(None, # realm
                                url,
                                username,
                                password)
  return urllib2.HTTPDigestAuthHandler(password_manager)

def _make_https_handler(cafile=None,
                        capath=None,
                        max_cert_depth=9):
  class HTTPSConnection(httpslib.HTTPSConnection):
    """
    A class that extends the default HTTPSConnection to ensure two things:
    1) Enforce tlsv1 protocol for all ssl connection. Some older pythons
       (e.g., sles11, probably all versions <= 2.6) attempt SSLv23 handshake
       that is rejected by newer web servers. See OPSAPS-32192 for an example.
    2) Force validation if cafile/capath is supplied.
    """

    def __init__(self, host, port=None, **ssl):
      # Specifying sslv23 enables the following ssl versions:
      # SSLv3, SSLv23, TLSv1, TLSv1.1, and TLSv1.2. We will explicitly exclude
      # SSLv3 and SSLv2 below. This mimics what is done by create_default_context
      # on newer python versions (python >= 2.7).
      ctx = SSL.Context('sslv23')
      # SSL_OP_ALL turns on all workarounds for known bugs. See
      # https://www.openssl.org/docs/manmaster/ssl/SSL_CTX_set_options.html for
      # a full list of these workarounds. I believe that we don't really need
      # any of these workarounds, but, this is default in later pythons and is
      # future looking.
      ctx.set_options(m2.SSL_OP_ALL | m2.SSL_OP_NO_SSLv2 | m2.SSL_OP_NO_SSLv3)

      if cafile is not None or capath is not None:
        ctx.set_verify(SSL.verify_peer | SSL.verify_fail_if_no_peer_cert,
                       max_cert_depth)
        ctx.load_verify_info(cafile=cafile, capath=capath)
        self._postConnectionCheck = True
      else:
        ctx.set_verify(SSL.verify_none, max_cert_depth)
        self._postConnectionCheck = False
      httpslib.HTTPSConnection.__init__(self, host, port, ssl_context=ctx)

    def connect(self):
      # This is a bit ugly but we need to override the connect method in order
      # to disable hostname verification. This is buried deep inside M2Crypto
      # and the only way to disable it is to disable post connection checks on
      # the socket itself.
      self.sock = SSL.Connection(self.ssl_ctx)
      if self.session:
        self.sock.set_session(self.session)

      if not self._postConnectionCheck:
        self.sock.postConnectionCheck = None

      self.sock.connect((self.host, self.port))

  class HTTPSHandler(urllib2.HTTPSHandler):

    def https_open(self, req):
      return self.do_open(HTTPSConnection, req)

  return HTTPSHandler()

def urlopen_with_retry_on_authentication_errors(function,
                                                retries,
                                                sleeptime):
  # See OPSAPS-28469: we retry on 401 errors on the presumption that we
  # are hitting a race with the kinit from the kt_renewer.
  attempt = 1
  while True:
    try:
      return function()
    except urllib2.HTTPError, err:
      if err.code == 401 and attempt <= retries:
        LOG.exception("Autentication error on attempt %d. Retrying after "
                      "sleeping %f seconds." % (attempt, sleeptime))
        time.sleep(sleeptime)
        attempt += 1
      else:
        raise
