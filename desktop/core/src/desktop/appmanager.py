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
from desktop.lib.paths import get_desktop_root

from django.utils.translation import ugettext as _

# Directories where apps and libraries are to be found
APP_DIRS = [get_desktop_root('core-apps'),
            get_desktop_root('apps'),
            get_desktop_root('libs')]

LOG = logging.getLogger(__name__)

######################################################################
# Global variables set after calling load_apps()
######################################################################

# List of DesktopModuleInfo that have been loaded
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

    # For clarification purposes, all of these different names need a
    # bit of explanation. The name is the actual name of the application.
    # The display name is used by dump_config, and will either be the
    # app name or the config key, if the config key has been defined in the
    # app's settings.  Mostly, it's around for consistency's sake.
    # The nice name is just a more formal name, i.e. useradmin might
    # have a nice name of User Administration Tool, or something
    # similarly flowery.
    self.module = module
    self.name = module.__name__
    self.display_name = module.__name__

    # Set up paths
    module_root = os.path.dirname(module.__file__)
    self.root_dir = os.path.join(module_root, "..", "..")

    # Load application settings
    self._load_settings_module(module.__name__ + ".settings")

    if hasattr(self.settings, "NICE_NAME"):
      self.nice_name = self.settings.NICE_NAME
    else:
      self.nice_name = self.name

    if hasattr(self.settings, "ICON"):
        self.icon_path = self.settings.ICON
    else:
        self.icon_path = ""

    if hasattr(self.settings, "MENU_INDEX"):
        self.menu_index = self.settings.MENU_INDEX
    else:
        self.menu_index = 999

    self.is_url_namespaced = hasattr(self.settings, 'IS_URL_NAMESPACED')

    if self.config_key is not None:
      self.display_name = self.config_key

    # Look for static directory in two places:
    new_style, old_style = [ os.path.abspath(p) for p in [
      os.path.join(module_root, "static", self.name),
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
      self.config_key = getattr(s, 'CONFIG_KEY', None)
    else:
      self.django_apps = []
      self.config_key = None

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

  @property
  def locale_path(self):
    return os.path.join(os.path.dirname(self.module.__file__), 'locale')

  @property
  def migrations_path(self):
    path = os.path.join(os.path.dirname(self.module.__file__), 'migrations')
    if path and os.path.exists(path):
      return path
    else:
      return None

  def _submodule(self, name):
    return _import_module_or_none(self.module.__name__ + "." + name)

  def __str__(self):
    return "DesktopModule(%s: %s)" % (self.nice_name, self.module.__name__)

def get_apps(user):
  return filter(lambda app: user.has_hue_permission(action="access", app=app.display_name), DESKTOP_APPS)

def get_apps_dict(user=None):
  if user is not None:
    apps = get_apps(user)
  else:
    apps = DESKTOP_APPS

  return dict([(app.name, app) for app in apps])

def load_libs():
  global DESKTOP_MODULES
  global DESKTOP_LIBS

  if DESKTOP_LIBS is not None:
    raise Exception("load_apps already has been called.")
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


def load_apps(app_blacklist):
  """Loads the applications from the directories in APP_DIRS.
  Sets DESKTOP_MODULES and DJANGO_APPS globals in this module.

  TODO(todd) make this a singleton perhaps if people are anti-global?
  """
  global DESKTOP_MODULES
  global DESKTOP_APPS

  if DESKTOP_APPS is not None:
    raise Exception(_("load_apps has already been called."))
  DESKTOP_APPS = []

  for sdk_app in pkg_resources.iter_entry_points("desktop.sdk.application"):
    if sdk_app.name not in app_blacklist:
      # TODO: Remove once pig and jobsub have been migrated to editor
      if 'oozie' in app_blacklist and sdk_app.name in ('pig', 'jobsub'):
        LOG.warn('%s depends on oozie which is blacklisted, will skip loading %s app.' % (sdk_app.name, sdk_app.name))
      else:
        m = sdk_app.load()
        dmi = DesktopModuleInfo(m)
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
