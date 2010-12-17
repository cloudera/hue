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

from desktop.lib.windmill_util import logged_in_client, logout

def test_user_creation():
  client = logged_in_client()

  # launch useradmin
  client.click(id='hue-useradmin-menu')
  client.waits.forElement(jquery='(".useradmin")[0]', timeout='2000')

  # click add user and add "windmill_joe" user
  client.click(jquery="('.useradmin_add_user')[0]")
  client.type(text='windmill_joe', id='id_username')
  client.type(text='windmill', id='id_password1')
  client.type(text='windmill', id='id_password2')
  client.click(value='Save')
  # verify user is in list
  client.waits.forElement(classname='useradmin_userlist', timeout='2000')
  client.asserts.assertTextIn(classname='useradmin_userlist', validator='windmill_joe')

  # log in as windmill_joe
  logout(client)

  client = logged_in_client(user='windmill_joe', passwd='windmill')
  logout(client)

  client = logged_in_client()

  # launch useradmin
  client.click(id='hue-useradmin-menu')
  client.waits.forElement(jquery='(".useradmin")[0]', timeout='2000')

  # delete the user
  client.click(jquery="('tr:contains(windmill_joe) .delete:last')[0]")
  client.click(jquery="('.useradmin .closeWin')[1]")

  # verify user is NOT in list
  client.waits.forElement(classname='useradmin_userlist', timeout='2000')
  client.asserts.assertNotTextIn(classname='useradmin_userlist', validator='windmill_joe')
