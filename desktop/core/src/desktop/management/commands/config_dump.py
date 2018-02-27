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
"""
Dumps configuration data for debugging.

Note that this dump representation is not machine readable;
this command is still a few steps away from dumping a ConfigObj-compatible,
textual representation.
"""
from django.core.management.base import BaseCommand
import desktop.appmanager
import textwrap

from django.utils.translation import ugettext as _

from desktop.lib.conf import BoundContainer, is_anonymous

class Command(BaseCommand):
  def __init__(self, *args, **kwargs):
    super(Command, self).__init__(*args, **kwargs)
    self.indent = 0

  """Prints documentation for configuration."""
  def handle(self, *args, **options):
    print _("Dumping configuration...")
    print
    self.recurse(desktop.lib.conf.GLOBAL_CONFIG)

  def p(self, s):
    print " "*self.indent + s

  def fill(self, s):
    print textwrap.fill(s.strip(),
      initial_indent=" "*self.indent, subsequent_indent=" "*self.indent)
    

  def recurse(self, config_obj):
    if isinstance(config_obj, BoundContainer):
      if is_anonymous(config_obj.config.key):
        key = "/default/"
      else:
        key = config_obj.config.key

      self.p("%s:" % key)
      self.indent += 2
      print textwrap.fill(config_obj.config.help or _("No help available."),
        initial_indent=" "*self.indent, subsequent_indent=" "*self.indent)
      print
      for v in config_obj.get().values():
        self.recurse(v)
      self.indent -= 2

    else:
      self.p("%s=%s" % (config_obj.config.key, config_obj.get()))
      self.indent += 2
      self.fill(config_obj.config.help or _("No help available."))
      self.indent -= 2
