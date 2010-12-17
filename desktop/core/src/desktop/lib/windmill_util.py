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

from windmill.authoring import WindmillTestClient
import windmill
import time

def logged_in_client(user='test', passwd='test', client=None):
  """
  Opens up the root URL.  If user is not logged in, logs him in.
  """
  if client is None:
    client = WindmillTestClient(__name__)
  client.open(url=windmill.settings['TEST_URL'] + '?clearSession=true')
  client.waits.forPageLoad()
  client.waits.forElement(classname='hue-loaded')
  if client.execJS(js="!!$('hue-login')")["output"]:
    client.waits.forElement(classname='hue-username')
    client.click(jquery='(".hue-username")[0]')
    client.type(classname='hue-username', text=user)
    client.click(classname='hue-password')
    client.type(classname='hue-password', text=passwd)
    client.click(classname='hue-continue')
  # Health dashboard launches at login; ideally we'd have a 
  # better "ready" notification.
  time.sleep(2.0) # TODO: Hacky sleep!
  client.waits.forElement(classname='loggedIn', timeout='20000')
  return client

def logout(client):
  """
    logs the user out of desktop
  """
  client.click(jquery='("#hue-logout a")[0]')
  # TODO(philip,nutron): Occasional bug.
  # We've seen the login box never show up.  This doesn't
  # trigger test failures, because we open the first page
  # at every test, but ideally we should assert that the login
  # box appears again.
  # client.waits.forElement(timeout='2000', classname='hue-username')
