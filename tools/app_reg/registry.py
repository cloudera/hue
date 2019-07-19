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
Registry for the applications
"""

import glob
import logging
import os
import json

import common

LOG = logging.getLogger(__name__)

class AppRegistry(object):
  """
  Represents a registry.
  """
  def __init__(self):
    """Open the existing registry"""
    self._reg_path = os.path.join(common.HUE_APP_REG_DIR, 'app.reg')
    self._initialized = False
    self._apps = { }    # Map of name -> HueApp
    self._open()

  def _open(self):
    """Open the registry file. May raise OSError"""
    if os.path.exists(self._reg_path):
      reg_file = file(self._reg_path)
      app_list = json.load(reg_file)
      reg_file.close()

      for app_json in app_list:
        app_json.setdefault('author', 'Unknown')        # Added after 0.9
        app = HueApp.create(app_json)
        self._apps[app.name] = app

    self._initialized = True

  def _write(self, path):
    """Write out the registry to the given path"""
    outfile = file(path, 'w')
    json.dump(self._apps.values(), outfile, cls=AppJsonEncoder, indent=2)
    outfile.close()

  def contains(self, app):
    """Returns whether the app (of the same version) is in the registry"""
    try:
      existing = self._apps[app.name]
      return existing.version == app.version
    except KeyError:
      return False

  def register(self, app):
    """register(app) -> True/False"""
    assert self._initialized, "Registry not yet initialized"
    try:
      existing = self._apps[app.name]
      version_diff = common.cmp_version(existing.version, app.version)
      if version_diff == 0:
        LOG.warn('%s is already registered' % (app,))
        return False
      elif version_diff < 0:
        LOG.info('Upgrading %s from version %s' % (app, existing.version))
      elif version_diff > 0:
        LOG.error('A newer version (%s) of %s is already installed' % (existing.version, app))
        return False
    except KeyError:
      pass

    LOG.info('Updating registry with %s' % (app,))
    self._apps[app.name] = app
    return True

  def unregister(self, app_name):
    """unregister(app_Name) -> HueApp. May raise KeyError"""
    assert self._initialized, "Registry not yet initialized"

    app = self._apps[app_name]
    del self._apps[app_name]
    return app

  def get_all_apps(self):
    """get_all_apps() -> List of HueApp"""
    return self._apps.values()

  def save(self):
    """Save and write out the registry"""
    assert self._initialized, "Registry not yet initialized"

    self._write(self._reg_path)
    LOG.info('=== Saved registry at %s' % (self._reg_path,))


class HueApp(object):
  """
  Represents an app.

  Path provided should be absolute or relative to common.APPS_ROOT
  """
  @staticmethod
  def create(json):
    return HueApp(json['name'], json['version'], json['path'], json['desc'], json['author'])

  def __init__(self, name, version, path, desc, author):
    self.name = name
    self.version = version
    self.path = path
    self.desc = desc
    self.author = author

  def __str__(self):
    return "%s v.%s" % (self.name, self.version)

  def __cmp__(self, other):
    if not isinstance(other, HueApp):
      raise TypeError
    return cmp((self.name, self.version), (other.name, other.version))

  @property
  def rel_path(self):
    if os.path.isabs(self.path):
      return os.path.relpath(self.path, common.APPS_ROOT)
    else:
      return self.path

  @property
  def abs_path(self):
    if not os.path.isabs(self.path):
      return os.path.abspath(os.path.join(common.APPS_ROOT, self.path))
    else:
      return self.path

  def use_rel_path(self):
    self.path = self.rel_path

  def use_abs_path(self):
    self.path = self.abs_path

  def jsonable(self):
    return dict(name=self.name, version=self.version, path=self.path,
                desc=self.desc, author=self.author)

  def find_ext_pys(self):
    """find_ext_pys() -> A list of paths for all ext-py packages"""
    return glob.glob(os.path.join(self.abs_path, 'ext-py', '*'))

  def get_conffiles(self):
    """get_conffiles() -> A list of config (.ini) files"""
    return glob.glob(os.path.join(self.abs_path, 'conf', '*.ini'))


  def install_conf(self):
    """
    install_conf() -> True/False

    Symlink the app's conf/*.ini files into the conf directory.
    """
    installed = [ ]

    for target in self.get_conffiles():
      link_name = os.path.join(common.HUE_CONF_DIR, os.path.basename(target))

      # Does the link already exists?
      if os.path.islink(link_name):
        try:
          cur = os.readlink(link_name)
          if cur == target:
            LOG.warn("Symlink for configuration already exists: %s" % (link_name,))
            installed.append(link_name)
            continue
          # Remove broken link
          if not os.path.exists(cur):
            os.unlink(link_name)
            LOG.warn("Removing broken link: %s" % (link_name,))
        except OSError, ex:
          LOG.warn("Error checking for existing link %s: %s" % (link_name, ex))

      # Actually install the link
      try:
        os.symlink(target, link_name)
        LOG.info('Symlink config %s -> %s' % (link_name, target))
        installed.append(link_name)
      except OSError, ex:
        LOG.error("Failed to symlink %s to %s: %s" % (target, link_name, ex))
        for lnk in installed:
          try:
            os.unlink(lnk)
          except OSError, ex2:
            LOG.error("Failed to cleanup link %s: %s" % (link_name, ex2))
        return False
    return True


  def uninstall_conf(self):
    """uninstall_conf() -> True/False"""
    app_conf_dir = os.path.abspath(os.path.join(self.abs_path, 'conf'))
    if not os.path.isdir(app_conf_dir):
      return True

    # Check all symlink in the conf dir and remove any that point to this app
    for name in os.listdir(common.HUE_CONF_DIR):
      path = os.path.join(common.HUE_CONF_DIR, name)
      if not os.path.islink(path):
        continue
      target = os.readlink(path)
      target_dir = os.path.abspath(os.path.dirname(target))
      if target_dir == app_conf_dir:
        try:
          os.unlink(path)
          LOG.info('Remove config symlink %s -> %s' % (path, target))
        except OSError, ex:
          LOG.error("Failed to remove configuration link %s: %s" % (path, ex))
          return False
    return True


class AppJsonEncoder(json.JSONEncoder):
  def __init__(self, **kwargs):
    json.JSONEncoder.__init__(self, **kwargs)

  def default(self, obj):
    if isinstance(obj, HueApp):
      return obj.jsonable()
    return json.JSONEncoder.default(self, obj)
