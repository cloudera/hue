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
Interface to providing custom toolbars in the FileBrowser
"""

import logging

LOG = logging.getLogger(__name__)

class Toolbar(object):
  """
  All custom toolbars must derive from this class.
  """
  def display(self, context):
    """
    display(context) -> toolbar HTML

    Return the HTML to display the toolbar. The HTML must contain one single
    top-level <div> of class "toolbar".

    ``context`` is a DisplayContext.

    May return an empty string to hide the toolbar.
    """
    raise NotImplementedError

  def get_app_name(self):
    """
    get_app_name() -> The name of the toolbar provider app.
    """
    raise NotImplementedError

  def get_name(self):
    """
    get_name() -> The name of the toolbar, which is unique for the app.
    """
    raise NotImplementedError

  def __str__(self):
    return 'FileBrowser toolbar "%s" from %s' % (self.get_name(), self.get_app_name())


class DisplayContext(object):
  """Context object for displaying the Toolbar"""
  def __init__(self, template, request, data):
    self.template = template
    self.request = request
    self.data = data


# Map of (app_name, name) -> toolbar obj
_toolbars = { }

def register(toolbar):
  """Register a toolbar. Returns True/False."""
  global _toolbars

  key = (toolbar.get_app_name(), toolbar.get_name())
  if _toolbars.has_key(key):
    LOG.error('Failed to register %s: Already registered' % (toolbar,))
    return False

  _toolbars[key] = toolbar
  return True


def lookup(app_name, toolbar_name):
  """lookup(app_name, toolbar_name) -> Toolbar or None"""
  return _toolbars.get((app_name, toolbar_name))


def all():
  """all() -> [ all toolbars ]"""
  return _toolbars.values()
