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
import simplejson

import common

LOG = logging.getLogger(__name__)

class AppRegistry(object):
  """
  Represents a registry.
  """
  def __init__(self):
    """Open the existing registry"""
    self._reg_path = os.path.join(common.INSTALL_ROOT, 'app.reg')
    self._initialized = False
    self._apps = { }    # Map of name -> DesktopApp
    self._open()


  def _open(self):
    """Open the registry file. May raise OSError"""
    if os.path.exists(self._reg_path):
      reg_file = file(self._reg_path)
      app_list = simplejson.load(reg_file)
      reg_file.close()

      for app_json in app_list:
        app = DesktopApp.create(app_json)
        self._apps[app.name] = app

    self._initialized = True


  def _write(self, path):
    """Write out the registry to the given path"""
    outfile = file(path, 'w')
    simplejson.dump(self._apps.values(), outfile, cls=AppJsonEncoder, indent=2)
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
        LOG.error('A newer version of %s is already installed' % (app,))
        return False
    except KeyError:
      pass

    LOG.info('Updating registry with %s' % (app,))
    self._apps[app.name] = app
    return True


  def unregister(self, app_name):
    """unregister(app_Name) -> DesktopApp. May raise KeyError"""
    assert self._initialized, "Registry not yet initialized"

    app = self._apps[app_name]
    del self._apps[app_name]
    return app


  def get_all_apps(self):
    """get_all_apps() -> List of DesktopApp"""
    return self._apps.values()


  def save(self):
    """Save and write out the registry"""
    assert self._initialized, "Registry not yet initialized"

    tmp_path = self._reg_path + '.new'
    self._write(tmp_path)
    os.rename(tmp_path, self._reg_path)
    LOG.info('=== Saved registry at %s' % (self._reg_path,))


class DesktopApp(object):
  """
  Represents an app.
  """
  @staticmethod
  def create(json):
    return DesktopApp(json['name'], json['version'], json['path'], json['desc'])

  def __init__(self, name, version, path, desc):
    self.name = name
    self.version = version
    self.path = path
    self.desc = desc

  def __str__(self):
    return "%s (version %s)" % (self.name, self.version)

  def __cmp__(self, other):
    if not isinstance(other, DesktopApp):
      raise TypeError
    return cmp((self.name, self.version), (other.name, other.version))

  def jsonable(self):
    return dict(name=self.name, version=self.version, path=self.path, desc=self.desc)

  def find_ext_pys(self):
    """find_ext_pys() -> A list of paths for all ext-py packages"""
    return glob.glob(os.path.join(self.path, 'ext-py', '*'))


class AppJsonEncoder(simplejson.JSONEncoder):
  def __init__(self, **kwargs):
    simplejson.JSONEncoder.__init__(self, **kwargs)

  def default(self, obj):
    if isinstance(obj, DesktopApp):
      return obj.jsonable()
    return simplejson.JSONEncoder.default(self, obj)
