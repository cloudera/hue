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
#
# Tests for proxy app.

import threading
import logging
import BaseHTTPServer
import StringIO

from nose.tools import assert_true, assert_false
from django.test.client import Client
from desktop.lib.django_test_util import make_logged_in_client

from proxy.views import _rewrite_links
import proxy.conf


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  """
  To avoid mocking out urllib, we setup a web server
  that does very little, and test proxying against it.
  """
  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html; charset=utf8")
    self.end_headers()
    self.wfile.write("Hello there.")
    self.wfile.write("You requested: " + self.path + ".")
    self.wfile.write("Image: <img src='/foo.jpg'>")
    self.wfile.write("Link: <a href='/baz?with=parameter'>link</a>")

  def do_POST(self):
    self.send_response(200)
    self.send_header("Content-type", "text/html; charset=utf8")
    self.end_headers()
    self.wfile.write("Hello there.")
    self.wfile.write("You requested: " + self.path + ".")
    # Somehow in this architecture read() blocks, so we read the exact
    # number of bytes the test sends.
    self.wfile.write("Data: " + self.rfile.read(16))

  def log_message(self, fmt, *args):
    logging.debug("%s - - [%s] %s" %
                  (self.address_string(),
                   self.log_date_time_string(),
                   fmt % args))


def run_test_server():
  """
  Returns the server, and a method to close it out.
  """
  # We need to proxy a server, so we go ahead and create one.
  httpd = BaseHTTPServer.HTTPServer(("127.0.0.1", 0), Handler)
  # Spawn a thread that serves exactly one request.
  thread = threading.Thread(target=httpd.handle_request)
  thread.daemon = True
  thread.start()

  def finish():
    # Make sure the server thread is done.
    print "Closing thread " + str(thread)
    thread.join(10.0) # Wait at most 10 seconds
    assert_false(thread.isAlive())

  return httpd, finish
run_test_server.__test__ = False

def test_proxy_get():
  """
  Proxying test.
  """
  client = Client()
  # All apps require login.
  client.login(username="test", password="test")
  httpd, finish = run_test_server()
  try:
    # Test the proxying
    finish_conf = proxy.conf.WHITELIST.set_for_testing(r"127\.0\.0\.1:\d*")
    try:
      response_get = client.get('/proxy/127.0.0.1/%s/' % httpd.server_port, dict(foo="bar"))
    finally:
      finish_conf()
    assert_true("Hello there" in response_get.content)
    assert_true("You requested: /?foo=bar." in response_get.content)
    assert_true("/proxy/127.0.0.1/%s/foo.jpg" % httpd.server_port in response_get.content)
    assert_true("/proxy/127.0.0.1/%s/baz?with=parameter" % httpd.server_port in response_get.content)
  finally:
    finish()

def test_proxy_post():
  """
  Proxying test, using POST.
  """
  client = Client()
  # All apps require login.
  client.login(username="test", password="test")
  httpd, finish = run_test_server()
  try:
    # Test the proxying
    finish_conf = proxy.conf.WHITELIST.set_for_testing(r"127\.0\.0\.1:\d*")
    try:
      response_post = client.post('/proxy/127.0.0.1/%s/' % httpd.server_port, dict(foo="bar", foo2="bar"))
    finally:
      finish_conf()
    assert_true("Hello there" in response_post.content)
    assert_true("You requested: /." in response_post.content)
    assert_true("foo=bar" in response_post.content)
    assert_true("foo2=bar" in response_post.content)
  finally:
    finish()

def test_blacklist():
  client = make_logged_in_client('test')
  finish_confs = [
    proxy.conf.WHITELIST.set_for_testing(r"localhost:\d*"),
    proxy.conf.BLACKLIST.set_for_testing(r"localhost:\d*/(foo|bar)/fred/"),
  ]
  try:
    # Request 1: Hit the blacklist
    resp = client.get('/proxy/localhost/1234//foo//fred/')
    assert_true("is blocked" in resp.content)

    # Request 2: This is not a match
    httpd, finish = run_test_server()
    try:
      resp = client.get('/proxy/localhost/%s//foo//fred_ok' % (httpd.server_port,))
      assert_true("Hello there" in resp.content)
    finally:
      finish()
  finally:
    for fin in finish_confs:
      fin()


class UrlLibFileWrapper(StringIO.StringIO):
  """
  urllib2.urlopen returns a file-like object; we fake it here.
  """
  def __init__(self, buf, url):
    StringIO.StringIO.__init__(self, buf)
    self.url = url

  def geturl(self):
    """URL we were initialized with."""
    return self.url

def test_rewriting():
  """
  Tests that simple re-writing is working.
  """
  html = "<a href='foo'>bar</a><a href='http://alpha.com'>baz</a>"
  assert_true('<a href="/proxy/abc.com/80/sub/foo">bar</a>' in _rewrite_links(UrlLibFileWrapper(html, "http://abc.com/sub/")),
    msg="Relative links")
  assert_true('<a href="/proxy/alpha.com/80/">baz</a>' in _rewrite_links(UrlLibFileWrapper(html, "http://abc.com/sub/")),
    msg="Absolute links")

  # Test url with port and invalid port
  html = "<a href='http://alpha.com:1234/bar'>bar</a><a href='http://alpha.com:-1/baz'>baz</a>"
  assert_true('<a href="/proxy/alpha.com/1234/bar">bar</a><a>baz</a>' in
              _rewrite_links(UrlLibFileWrapper(html, "http://abc.com/sub/")),
              msg="URL with invalid port")

  html = """
  <img src="/static/hadoop-logo.jpg"/><br>
  """
  rewritten = _rewrite_links(UrlLibFileWrapper(html, "http://abc.com/sub/"))
  assert_true('<img src="/proxy/abc.com/80/static/hadoop-logo.jpg">' in
              rewritten,
              msg="Rewrite images")
