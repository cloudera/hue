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

# Proxies HTTP requests through the Desktop server.
# This is intended to be used to view the "built-in"
# UIs.
#
# TODO(philip): Instead of whitelists, also offer a way
# to create links (within the application) to trusted
# URLs, by appending an HMAC to the parameters.

import logging
import re
from urllib2 import urlopen
from urlparse import urlparse, urlunparse

from django.core import urlresolvers
from django.http import HttpResponse
from desktop.lib.exceptions import MessageException

from proxy import conf

LOGGER = logging.getLogger(__name__)

def check_host_port(host, port):
  """
  Return true if this host:port pair is allowed to be proxied.
  """

  # Check explicit whitelist
  hostport = "%s:%d" % (host, port)
  for regexp in conf.WHITELIST.get():
    if regexp.match(hostport):
      return True

  return False

def check_blacklist(host, port, path):
  """
  Return true if this host:port path combo is allowed to be proxied.
  """
  blacklist = conf.BLACKLIST.get()
  if not blacklist:
    return True

  # Make a canonical path, since "/forbidden//path" (string) does not match
  # "/forbidden/path" (regex).
  has_trailing_slash = path.endswith('/')
  path_elems = path.split('/')
  path_elems = [ p for p in path_elems if p ]
  canon_url = "%s:%s/%s" % (host, port, '/'.join(path_elems))
  if has_trailing_slash:
    canon_url += '/'

  for regexp in blacklist:
    if regexp.match(canon_url):
      return False
  return True


def proxy(request, host, port, path):
  """
  Proxies an HTTP request by fetching the data
  and re-writing links.
  """
  port = int(port)

  if not check_host_port(host, port):
    raise MessageException(
      ("%s:%d is not whitelisted for reverse proxying, nor a daemon that Cluster Health " +
       "is aware of.  Contact your administrator.") % (host, port))
  if not check_blacklist(host, port, path):
    raise MessageException(
      "Access to %s:%s%s is blocked. Contact your administrator." % (host, port, path))

  # The tuple here is: (scheme, netloc, path, params, query, fragment).
  # We don't support params or fragment.
  url = urlunparse(("http", "%s:%d" % (host,port), 
                    path, 
                    None, 
                    request.META.get("QUERY_STRING"), 
                    None))
  LOGGER.info("Retrieving %s." % url)
  if request.method == 'POST':
    post_data = request.POST.urlencode()
  else:
    post_data = None
  data = urlopen(url, data=post_data)
  content_type = data.headers.get("content-type", "text/plain")
  if not re.match(r'^text/html\s*(?:;.*)?$', content_type):
    resp_text = data.read(1024*1024) # read 1MB
  else:
    resp_text = _rewrite_links(data)
  request.path = _reverse(host, port, path)
  return HttpResponse(resp_text, content_type=data.headers.get("content-type"))

def _reverse(host, port, path):
  return urlresolvers.reverse("proxy.views.proxy",
                              kwargs=dict(host=host, port=port, path=path))
def _rewrite_url(url):
  """Used by _rewrite_links"""
  scheme, netloc, path, params, query, fragment = urlparse(url)
  if scheme != "http": # scheme
    # Only re-write http URLs, since that's all
    # we proxy.
    return url
  if ":" in netloc: # netloc
    host, port = netloc.rsplit(":", 1)
  else:
    host, port = netloc, str(80)
  path = path or "/"

  try:
    # We may hit invalid urls. Return None to strip out the link entirely.
    out = _reverse(host, port, path)
  except urlresolvers.NoReverseMatch, ex:
    LOGGER.error("Encountered malformed URL '%s' when rewriting proxied page." % (url,))
    return None

  if query:
    out = out + "?" + query
  return out

def _rewrite_links(data):
  import lxml.html
  html = lxml.html.parse(data)
  html.getroot().rewrite_links(_rewrite_url, resolve_base_href=True, base_href=data.geturl())
  return lxml.html.tostring(html)
