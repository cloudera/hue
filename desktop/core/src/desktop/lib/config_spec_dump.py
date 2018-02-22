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
import desktop.appmanager

from desktop.lib.conf import BoundContainer, UnspecifiedConfigSection, is_anonymous

class ConfigSpec():
  def __init__(self, configspec):
    self.indent = 0
    self.level = 0
    self.file = configspec

  def generate(self, **options):
    self.recurse(desktop.lib.conf.GLOBAL_CONFIG)
    self.file.close()

  def p(self, s):
    self.file.write("\n" + " " * self.indent + s + "\n")

  def recurse(self, config_obj):
    if isinstance(config_obj, BoundContainer):
      if is_anonymous(config_obj.config.key):
        key = "__many__"
      else:
        key = config_obj.config.key
      if self.level != 0:
        self.p("%s" % "[" * self.level + key + "]" * self.level)
      self.indent += 2
      self.level += 1
      sections = []
      for v in config_obj.get().values():
        if isinstance(v, BoundContainer):
          sections.append(v)
        else:
          self.p("%s=" % (v.config.key))

      if isinstance(config_obj.config, UnspecifiedConfigSection) and sections:
        self.recurse(sections[0])
      else:
        for sec in sections:
          self.recurse(sec)

      self.indent -= 2
      self.level -= 1
