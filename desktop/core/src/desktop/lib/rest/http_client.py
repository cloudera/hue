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

import cookielib
import logging
import posixpath
import types
import urllib
import urllib2

from urllib2_kerberos import HTTPKerberosAuthHandler

__docformat__ = "epytext"

LOG = logging.getLogger(__name__)


class HueCookieJar(cookielib.CookieJar):
  def _process_rfc2109_cookies(self, cookies):
    rfc2109_as_ns = getattr(self._policy, 'rfc2109_as_netscape', None)
    if rfc2109_as_ns is None:
      rfc2109_as_ns = not self._policy.rfc2965
    for cookie in cookies:
      if cookie.version == 1:
        cookie.rfc2109 = True
        if rfc2109_as_ns:
          # treat 2109 cookies as Netscape cookies rather than
          # as RFC2965 cookies
          cookie.version = 0


  def make_cookies(self, response, request):
    """Return sequence of Cookie objects extracted from response object."""
    # get cookie-attributes for RFC 2965 and Netscape protocols
    headers = response.info()
    rfc2965_hdrs = headers.getheaders("Set-Cookie2")
    ns_hdrs = headers.getheaders("Set-Cookie")

    rfc2965 = self._policy.rfc2965
    netscape = self._policy.netscape

    if ((not rfc2965_hdrs and not ns_hdrs) or
        (not ns_hdrs and not rfc2965) or
        (not rfc2965_hdrs and not netscape) or
        (not netscape and not rfc2965)):
        return []  # no relevant cookie headers: quick exit

    try:
      cookies = self._cookies_from_attrs_set(cookielib.split_header_words(rfc2965_hdrs), request)
    except:
      cookielib.reraise_unmasked_exceptions()
      cookies = []

    if ns_hdrs and netscape:
      try:
        ns_cookies = self._cookies_from_attrs_set(cookielib.parse_ns_headers(ns_hdrs), request)
      except:
        cookielib.reraise_unmasked_exceptions()
        ns_cookies = []
      self._process_rfc2109_cookies(ns_cookies)

      # Written by Abe
      if rfc2965:
        lookup = {}
        for cookie in cookies:
          lookup[(cookie.domain, cookie.path, cookie.name)] = None

        def no_matching_rfc2965(ns_cookie, lookup=lookup):
          key = ns_cookie.domain, ns_cookie.path, ns_cookie.name
          return key not in lookup
        ns_cookies = filter(no_matching_rfc2965, ns_cookies)

      if ns_cookies:
        cookies.extend(ns_cookies)

    return cookies


class HueCookiePolicy(cookielib.DefaultCookiePolicy):
  def __init__(self,
               blocked_domains=None, allowed_domains=None,
               netscape=True, rfc2965=False,
               rfc2109_as_netscape=None,
               hide_cookie2=False,
               strict_domain=False,
               strict_rfc2965_unverifiable=True,
               strict_ns_unverifiable=False,
               strict_ns_domain=0,
               strict_ns_set_initial_dollar=False,
               strict_ns_set_path=False):
    self.rfc2109_as_netscape = rfc2109_as_netscape
    return cookielib.DefaultCookiePolicy.__init__(self, blocked_domains=blocked_domains, allowed_domains=allowed_domains,
                                                  netscape=netscape, rfc2965=rfc2965,
                                                  hide_cookie2=hide_cookie2,
                                                  strict_domain=strict_domain,
                                                  strict_rfc2965_unverifiable=strict_rfc2965_unverifiable,
                                                  strict_ns_unverifiable=strict_ns_unverifiable,
                                                  strict_ns_domain=strict_ns_domain,
                                                  strict_ns_set_initial_dollar=strict_ns_set_initial_dollar,
                                                  strict_ns_set_path=strict_ns_set_path)


class RestException(Exception):
  """
  Any error result from the Rest API is converted into this exception type.
  """
  def __init__(self, error):
    Exception.__init__(self, error)
    self._error = error
    self._code = None
    self._message = str(error)
    self._headers = {}

    # Get more information if urllib2.HTTPError.
    try:
      self._code = error.code
      self._message = error.read()
      self._headers = error.info()
    except AttributeError:
      pass

  def __str__(self):
    res = self._message or ""
    if self._code is not None:
      res += " (error %s)" % (self._code,)
    return res

  def get_parent_ex(self):
    if isinstance(self._error, Exception):
      return self._error
    return None

  @property
  def code(self):
    return self._code

  @property
  def message(self):
    return self._message


class HttpClient(object):
  """
  Basic HTTP client tailored for rest APIs.
  """
  def __init__(self, base_url, exc_class=None, logger=None):
    """
    @param base_url: The base url to the API.
    @param exc_class: An exception class to handle non-200 results.

    Creates an HTTP(S) client to connect to the Cloudera Manager API.
    """
    self._base_url = base_url.rstrip('/')
    self._exc_class = exc_class or RestException
    self._logger = logger or LOG
    self._headers = { }

    # Make a cookie processor
    self._cookiejar = HueCookieJar(HueCookiePolicy())

    self._opener = urllib2.build_opener(
        HTTPErrorProcessor(),
        urllib2.HTTPCookieProcessor(self._cookiejar))


  def set_basic_auth(self, username, password, realm):
    """
    Set up basic auth for the client
    @param username: Login name.
    @param password: Login password.
    @param realm: The authentication realm.
    @return: The current object
    """
    # Make a basic auth handler that does nothing. Set credentials later.
    passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(realm, self._base_url, username, password)
    authhandler = urllib2.HTTPBasicAuthHandler(passmgr)

    self._opener.add_handler(authhandler)
    return self


  def set_kerberos_auth(self):
    """Set up kerberos auth for the client, based on the current ticket."""
    authhandler = HTTPKerberosAuthHandler()
    self._opener.add_handler(authhandler)
    return self


  def set_headers(self, headers):
    """
    Add headers to the request
    @param headers: A dictionary with the key value pairs for the headers
    @return: The current object
    """
    self._headers = headers
    return self


  @property
  def base_url(self):
    return self._base_url

  @property
  def logger(self):
    return self._logger

  def _get_headers(self, headers):
    res = self._headers.copy()
    if headers:
      res.update(headers)
    return res

  def execute(self, http_method, path, params=None, data=None, headers=None):
    """
    Submit an HTTP request.
    @param http_method: GET, POST, PUT, DELETE
    @param path: The path of the resource. Unsafe characters will be quoted.
    @param params: Key-value parameter data.
    @param data: The data to attach to the body of the request.
    @param headers: The headers to set for this request.

    @return: The result of urllib2.urlopen()
    """
    # Prepare URL and params
    path = urllib.quote(smart_str(path))
    url = self._make_url(path, params)
    if http_method in ("GET", "DELETE"):
      if data is not None:
        self.logger.warn(
            "GET method does not pass any data. Path '%s'" % (path,))
        data = None

    # Setup the request
    request = urllib2.Request(url, data)
    # Hack/workaround because urllib2 only does GET and POST
    request.get_method = lambda: http_method

    headers = self._get_headers(headers)

    for k, v in headers.items():
      request.add_header(k, v)

    # Call it
    self.logger.debug("%s %s" % (http_method, url))
    self.logger.debug("Cookies %s" % self._cookiejar)
    try:
      return self._opener.open(request)
    except (urllib2.HTTPError, urllib2.URLError), ex:
      raise self._exc_class(ex)

  def _make_url(self, path, params):
    res = self._base_url
    if path:
      res += posixpath.normpath('/' + path.lstrip('/'))
    if params:
      param_str = urllib.urlencode(params)
      res += '?' + param_str
    return iri_to_uri(res)


class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
  """
  Python 2.4 only recognize 200 and 206 as success. It's broken. So we install
  the following processor to catch the bug.
  """
  def http_response(self, request, response):
    if 200 <= response.code < 300:
      return response
    return urllib2.HTTPErrorProcessor.http_response(self, request, response)

  https_response = http_response

#
# Method copied from Django
#
def iri_to_uri(iri):
    """
    Convert an Internationalized Resource Identifier (IRI) portion to a URI
    portion that is suitable for inclusion in a URL.

    This is the algorithm from section 3.1 of RFC 3987.  However, since we are
    assuming input is either UTF-8 or unicode already, we can simplify things a
    little from the full method.

    Returns an ASCII string containing the encoded result.
    """
    # The list of safe characters here is constructed from the "reserved" and
    # "unreserved" characters specified in sections 2.2 and 2.3 of RFC 3986:
    #     reserved    = gen-delims / sub-delims
    #     gen-delims  = ":" / "/" / "?" / "#" / "[" / "]" / "@"
    #     sub-delims  = "!" / "$" / "&" / "'" / "(" / ")"
    #                   / "*" / "+" / "," / ";" / "="
    #     unreserved  = ALPHA / DIGIT / "-" / "." / "_" / "~"
    # Of the unreserved characters, urllib.quote already considers all but
    # the ~ safe.
    # The % character is also added to the list of safe characters here, as the
    # end of section 3.1 of RFC 3987 specifically mentions that % must not be
    # converted.
    if iri is None:
        return iri
    return urllib.quote(smart_str(iri), safe="/#%[]=:;$&()+,!?*@'~")

#
# Method copied from Django
#
def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    elif not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s

