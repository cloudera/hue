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


#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
Tests for "shell"
"""

from nose.tools import assert_true, assert_equal

from desktop.lib.django_test_util import make_logged_in_client
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode
import eventlet
import eventlet.wsgi
from eventlet.green import time
from eventlet.green import os
from eventlet.green import threading
import pwd
import re
import shell
import shell.conf as conf
import shell.constants as constants
import shell.utils as utils
import simplejson

class TestServer(threading.Thread):
  def run(self):
    def dummy_server(env, start_response):
      start_response('200 OK', [('Content-Type', 'text/plain')])
      return ['Dummy response\r\n']
    eventlet.wsgi.server(eventlet.listen(('',55555)), dummy_server)

class TestRequest(object):
  def __init__(self):
    self.POST = {}
    self.DICT = {}
    self.META = {}

def reset_all_users():
  """Reset to a clean state by deleting all users"""
  for user in User.objects.all():
    user.delete()

def test_spawning_check():
  reset_all_users()
  client = make_logged_in_client(username="test", is_superuser=True)

  get_urls = ["/shell/", "/shell/create"]
  post_urls = ["/shell/create", "/shell/process_command", "/shell/restore_shell",
               "/shell/kill_shell", "/shell/retrieve_output", "/shell/add_to_output"]
  for url in get_urls:
    response = client.get(url, follow=True)
    assert "The webserver currently running Hue does not support the Shell app." in response.content

  for url in post_urls:
    response = client.post(url, follow=True)
    assert "notRunningSpawning" in response.content

def test_unix_user_account_check():
  reset_all_users()
  nonexistent_username = "user_%s" % (time.strftime("%s"),)
  client = make_logged_in_client(username=nonexistent_username, is_superuser=True)

  d = { 'eventlet.input' : None }
  response = client.get('/shell/', follow=True, **d)
  assert "The Shell app requires a Unix user account for every user of Hue" in response.content

def test_rest():
  reset_all_users()
  username = pwd.getpwuid(os.getuid()).pw_name
  client = make_logged_in_client(username=username, is_superuser=True)

  d = { 'eventlet.input' : None }
  response = client.get('/shell/', follow=True, **d)

  shell_types_available = []
  for item in shell.conf.SHELL_TYPES.keys():
    nice_name = shell.conf.SHELL_TYPES[item].nice_name.get().strip()
    assert nice_name in response.content
    command = shell.conf.SHELL_TYPES[item].command.get().strip().split()
    if utils.executable_exists(command):
      shell_types_available.append(item)

  if not shell_types_available:
    return

  response = client.get('/shell/create?keyName=%s' % (time.strftime("%s"),), follow=True, **d)
  assert "There is no shell with that name." in response.content

  nonexistent_username = "user_%s" % (time.strftime("%s"),)
  client2 = make_logged_in_client(username=nonexistent_username, is_superuser=True)

  response = client2.get("/shell/create?keyName=%s" % (shell_types_available[0],), follow=True, **d)
  assert "There is no Unix user account for you." in response.content

  response = client.get("/shell/create?keyName=%s" % (shell_types_available[0],), follow=True, **d)
  assert '<span class="shell_id hidden">' in response.content

  shell_id_start = response.content.index('<span class="shell_id hidden">')+len('<span class="shell_id hidden">')
  shell_id_end = response.content.index('</span>')
  shell_id = response.content[shell_id_start:shell_id_end]
  assert re.match(r"^\s*\d+\s*$", shell_id)

  response = client.post("/shell/kill_shell", follow=True, data={constants.SHELL_ID: shell_id}, **d)
  assert response.content.strip() == "Shell successfully killed"

def test_parse_shell_pairs():
  request = TestRequest()
  request.POST[constants.NUM_PAIRS] = 2
  request.POST["%s2" % (constants.SHELL_ID,)] = '0'
  request.POST["%s2" % (constants.OFFSET,)] = '0'
  request.POST["%s1" % (constants.SHELL_ID,)] = '1'
  request.POST["%s1" % (constants.OFFSET,)] = '1'
  parsed_pairs = utils.parse_shell_pairs(request)
  assert parsed_pairs[0][0] == '1'
  assert parsed_pairs[0][1] == 1
  assert parsed_pairs[1][0] == '0'
  assert parsed_pairs[1][1] == 0

  request.POST[constants.NUM_PAIRS] = 1
  assert len(utils.parse_shell_pairs(request)) == 1

  request.POST[constants.NUM_PAIRS] =  'most definitely not a number'
  try:
    utils.parse_shell_pairs(request)
  except ValueError:
    pass
  else:
    assert False, "parse_shell_pairs did not throw an exception when trying to convert a malformed string to integer"

