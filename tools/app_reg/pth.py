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
Tools to manipulate the .pth file in the virtualenv.
"""

import glob
import logging
import os

import common

LOG = logging.getLogger(__name__)
PTH_FILE = 'hue.pth'


def _get_pth_filename():
  """
  _get_pth_filename -> Path to the .pth file.
  Location can be defined via HUE_PTH_DIR environment variable.
  May raise SystemError if the virtual env is absent.
  """
  pth_dir = common.HUE_PTH_DIR
  if pth_dir:
    return os.path.join(pth_dir, PTH_FILE)
  else:
    return os.path.join(common._get_python_site_packages_dir(), PTH_FILE)


class PthFile(object):
  def __init__(self):
    """May raise SystemError if the virtual env is absent"""
    self._path = _get_pth_filename()
    self._entries = [ ]
    self._read()

  def _relpath(self, path):
    return os.path.relpath(path, os.path.dirname(self._path))

  def _read(self):
    if os.path.exists(self._path):
      self._entries = set(file(self._path).read().split('\n'))

  def add(self, app):
    """
    Add the app and its ext eggs into the pth file

    PTH files need paths relative to the pth file, not APPS_ROOT
    """
    if os.path.isabs(app.path):
      # Absolute path
      module_path = os.path.join(app.abs_path, 'src')
      self._entries.add(module_path)
      LOG.debug('Add to %s: %s' % (self._path, module_path))

      # Add gen-py path if found
      gen_py_path = os.path.join(app.abs_path, 'gen-py')
      if os.path.exists(gen_py_path):
        self._entries.add(gen_py_path)
        LOG.debug('Add to %s: %s' % (self._path, gen_py_path))

      # Eggs could be in ext-py/<pkg>/dist/*.egg
      for py in app.find_ext_pys():
        ext_eggs = glob.glob(os.path.join(py, 'dist', '*.egg'))
        self._entries.update(ext_eggs)
        LOG.debug('Add to %s: %s' % (self._path, ext_eggs))

      # And eggs could also be in ext-eggs/*.egg
      egg_files = glob.glob(os.path.join(app.path, 'ext-eggs', '*.egg'))
      self._entries.update(egg_files)
      LOG.debug('Add to %s: %s' % (self._path, egg_files))

    else:
      # Relative paths require some transformation.
      # Paths are relative to directory of pth file
      module_path = self._relpath(os.path.join(app.abs_path, 'src'))
      self._entries.add(module_path)
      LOG.debug('Add to %s: %s' % (self._path, module_path))

      # Add gen-py path if found
      gen_py_path = self._relpath(os.path.join(app.abs_path, 'gen-py'))
      if os.path.exists(os.path.join(app.abs_path, 'gen-py')):
        self._entries.add(gen_py_path)
        LOG.debug('Add to %s: %s' % (self._path, gen_py_path))

      # Eggs could be in ext-py/<pkg>/dist/*.egg
      for py in app.find_ext_pys():
        ext_eggs = [self._relpath(egg) for egg in glob.glob(os.path.join(py, 'dist', '*.egg'))]
        self._entries.update(ext_eggs)
        LOG.debug('Add to %s: %s' % (self._path, ext_eggs))

      # And eggs could also be in ext-eggs/*.egg
      egg_files = [self._relpath(egg_file) for egg_file in glob.glob(os.path.join(app.path, 'ext-eggs', '*.egg'))]
      self._entries.update(egg_files)
      LOG.debug('Add to %s: %s' % (self._path, egg_files))

  def remove(self, app):
    """
    Remove the app and its ext eggs from the pth file
    """
    for path in self._entries.copy():
      module_path = os.path.join(app.abs_path, 'src')
      if path.startswith(module_path):
        self._entries.remove(module_path)

      rel_module_path = self._relpath(module_path)
      if path.startswith(rel_module_path):
        self._entries.remove(rel_module_path)

  def save(self):
    """
    Save the pth file
    Create a symlink to the path if it does not already exist.
    """
    with open(self._path, 'w') as _file:
      # We want the Hue libraries to come before system libraries in
      # case there is a name collision.
      _file.write("import sys; sys.__plen = len(sys.path)\n")
      _file.write('\n'.join(sorted(self._entries)))
      _file.write("\nimport sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; sys.path[0:0]=new\n")
    LOG.info('=== Saved %s' % self._path)

  def sync(self, apps):
    """Sync the .pth file with the installed apps"""
    self._entries = set()
    for app in apps:
      self.add(app)
