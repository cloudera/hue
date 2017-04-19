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
from __future__ import unicode_literals

import sys

from django.core import management
from django.core.management import get_commands
from django.test import SimpleTestCase
from django.utils.six import StringIO

class CmdTests(SimpleTestCase):
  def checkcmd(self):
    ldapcmd = "ldaptest"
    try:
      app_name = get_commands()[ldapcmd]
    except:
      app_name = None
    self.assertIsNotNone(app_name)

  def runcommand(self):
    old_stdout = sys.stdout
    sys.stdout = out = StringIO()
    try:
      with self.assertRaises(SystemExit):
        management.ManagementUtility(['hue', 'ldaptest']).execute()
    finally:
      sys.stdout = old_stdout
    self.assertIn("Could not find LDAP_URL server in hue.ini required for authentication", out.getvalue())

  def handlenoargs(self):
    old_stderr = sys.stderr
    sys.stderr = err = StringIO()
    try:
      with self.assertRaises(SystemExit):
        management.ManagementUtility(['hue', 'ldaptest', '-i']).execute()
    finally:
      sys.stderr = old_stderr
    self.assertIn("no such option", err.getvalue())
