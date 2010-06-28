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

import os
import logging
import re
import sys
import traceback
import pkg_resources

import desktop
import desktop.lib.apputil
from desktop.lib.paths import get_desktop_root

# Directories where apps and libraries are to be found
APP_DIRS = [get_desktop_root('core-apps'),
            get_desktop_root('apps'),
            get_desktop_root('libs')]

LOG = logging.getLogger(__name__)

######################################################################
# Global variables set after calling load_apps()
######################################################################

# List of DesktopModuleInfo that have been loaded and skipped
SKIPPED_APPS = None
DESKTOP_LIBS = None
DESKTOP_APPS = None
DESKTOP_MODULES = [ ]           # Sum of APPS and LIBS

def _import_module_or_none(module):
  """Like import_module, but returns None if the module does not exist.
  This will properly handle nested ImportErrors in such a way that, if the
  module should exist but throws ImportError, we *will* raise through
  that error.
  """
  try:
    __import__(module)
    return sys.modules[module]
  except ImportError, ie:
    # If the exception came from us importing, we want to just
    # return None. We need to inspect the stack, though, so we properly
    # reraise in the case that the module we're importing triggered
    # an import error itself.
    tb = sys.exc_info()[2]
    top_frame = traceback.extract_tb(tb)[-1]
    err_file = re.sub(r'\.pyc','.py', top_frame[0])
    my_file = re.sub(r'\.pyc','.py', __file__)
    if err_file == my_file:
      return None
    else:
      LOG.error("Failed to import '%s'" % (module,))
      raise

class DesktopModuleInfo(object):
  """
  Desktop app, specified via module.

  A Desktop app is encapsulated by a module.
  These modules are found using the "desktop.sdk.application"
  entrypoint (from pkg_resources/setup.py).

  Each desktop app may have a settings file,
  which lists DJANGO_APPS to be installed as
  apps in the django framework.  If so,
  urls is queried as well.  conf is queried
  for configuration.

  A static directory is found in a subdirectory
  of the module, or, (and this is the case with
  older apps), two levels up.
  """
  def __init__(self, module):
    """
    Initializes a DesktopModuleInfo based on a python
    module.  Static directories, settings, urls, etc.
    will be found based on that module.
    """
    self.module = module
    self.name = module.__name__

    # Set up paths
    module_root = os.path.dirname(module.__file__)
    self.root_dir = os.path.join(module_root, "..", "..")

    # Load application settings
    self._load_settings_module(module.__name__ + ".settings")

    if hasattr(self.settings, "NICE_NAME"):
      self.nice_name = self.settings.NICE_NAME
    else:
      self.nice_name = self.name

    # Look for static directory in two places:
    new_style, old_style = [ os.path.abspath(p) for p in [
      os.path.join(module_root, "static"),
      os.path.join(self.root_dir, "static")
    ]]

    self.static_dir = None
    if os.path.isdir(new_style):
      self.static_dir = new_style
    else:
      if os.path.isdir(old_style):
        LOG.debug("Old-style static directory: " + str(old_style))
        self.static_dir = old_style

    self.help_dir = None
    if self.static_dir:
      potential_help_dir = os.path.join(self.static_dir, "help")
      if os.path.exists(potential_help_dir):
        self.help_dir = potential_help_dir

  def _load_settings_module(self, module_name):
    """Load the myapp.settings module"""
    s = _import_module_or_none(module_name)
    if s is not None:
      self.django_apps = getattr(s, 'DJANGO_APPS', [])
      self.depender_yamls = \
          [self._resolve_appdir_path(p) for p in getattr(s, 'DEPENDER_PACKAGE_YMLS', [])]
      self.depender_jsons = \
          [(depname, self._resolve_appdir_path(p))
           for depname, p in getattr(s, 'DEPENDER_SCRIPTS_JSON', [])]
    else:
      self.django_apps = []
      self.depender_yamls = []
      self.depender_jsons = []

  def _resolve_appdir_path(self, path):
    """ Takes a path relative to the application dir and returns an absolute path. """
    return os.path.abspath(os.path.join(self.root_dir, path))

  @property
  def urls(self):
    return self._submodule("urls")

  @property
  def conf(self):
    return self._submodule("conf")

  def get_bootstrap_file(self):
    if self.static_dir:
      f = os.path.join(self.static_dir, "bootstrap.js")
      if os.path.exists(f):
        return file(f)
    else:
      return None

  @property
  def settings(self):
    return self._submodule("settings")

  def _submodule(self, name):
    return _import_module_or_none(self.module.__name__ + "." + name)

  def __str__(self):
    return "DesktopModule(%s: %s)" % (self.nice_name, self.module.__name__)


def load_libs():
  global DESKTOP_MODULES
  global DESKTOP_LIBS

  if DESKTOP_LIBS is not None:
    raise Exception("load_apps already has been called!")
  DESKTOP_LIBS = [ ]

  for lib in pkg_resources.iter_entry_points("desktop.sdk.lib"):
    m = lib.load()
    DESKTOP_LIBS.append(DesktopModuleInfo(m))


  LOG.debug("Loaded Desktop Libraries: " + ", ".join(a.name for a in DESKTOP_LIBS))
  DESKTOP_MODULES += DESKTOP_LIBS
  # Desktop itself is "special"; neither an app or a lib, but
  # just a module.  (If you add it as a lib, Desktop will
  # try to load its conf module, which it does not need to do.)
  DESKTOP_MODULES.append(DesktopModuleInfo(desktop))


def load_apps():
  """Loads the applications from the directories in APP_DIRS.
  Sets DESKTOP_MODULES and DJANGO_APPS globals in this module.

  TODO(todd) make this a singleton perhaps if people are anti-global?
  """
  global DESKTOP_MODULES
  global DESKTOP_APPS
  global SKIPPED_APPS

  if DESKTOP_APPS is not None:
    raise Exception("load_apps already has been called!")
  DESKTOP_APPS = []
  SKIPPED_APPS = []

  hadoop_ok = desktop.lib.apputil.has_hadoop()

  for sdk_app in pkg_resources.iter_entry_points("desktop.sdk.application"):
    m = sdk_app.load()
    dmi = DesktopModuleInfo(m)
    # If there is no hadoop installation, skips apps that requires hadoop
    if not hadoop_ok:
      app_settings = dmi.settings
      # <app_module>.settings.REQUIRES_HADOOP is True by default
      if app_settings is None or getattr(app_settings, 'REQUIRES_HADOOP', True):
        LOG.warn('Skipping app %s because Hadoop is not found' % (sdk_app,))
        SKIPPED_APPS.append(dmi)
        continue
    DESKTOP_APPS.append(dmi)

  LOG.debug("Loaded Desktop Applications: " + ", ".join(a.name for a in DESKTOP_APPS))
  DESKTOP_MODULES += DESKTOP_APPS

def get_desktop_module(name):
  """
  Harmless linear search.
  """
  global DESKTOP_MODULES
  for app in DESKTOP_MODULES:
    if app.name == name:
      return app
  return None
