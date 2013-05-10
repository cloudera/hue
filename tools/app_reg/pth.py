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
PTH_SYMLINK = 'hue.link.pth'
PTH_FILE = 'hue.pth'


def _get_pth_symlink():
  """
  _get_pth_symlink -> Path to the .pth symlink.
  May raise SystemError if the virtual env is absent.
  """
  return os.path.join(common._get_python_site_packages_dir(), PTH_SYMLINK)


def _get_pth_filename():
  """
  _get_pth_filename -> Path to the .pth file.
  Location can be defined via HUE_PTH_DIR environment variable.
  May raise SystemError if the virtual env is absent.
  """
  pth_dir = os.environ.get('HUE_PTH_DIR', None)
  if pth_dir:
    return os.path.join(pth_dir, PTH_FILE)
  else:
    return os.path.join(common._get_python_site_packages_dir(), PTH_FILE)


class PthFile(object):
  def __init__(self):
    """May raise SystemError if the virtual env is absent"""
    self._symlink_path = _get_pth_symlink()
    self._path = _get_pth_filename()
    self._entries = [ ]
    self._read()

  def _read(self):
    if os.path.exists(self._path):
      self._entries = set(file(self._path).read().split('\n'))

  def add(self, app):
    """
    Add the app and its ext eggs into the pth file
    """
    module_path = os.path.join(app.path, 'src')
    LOG.debug('Add to %s: %s' % (self._path, module_path))
    self._entries.add(module_path)

    # Eggs could be in ext-py/<pkg>/dist/*.egg
    ext_pys = app.find_ext_pys()
    for py in ext_pys:
      ext_egg = glob.glob(os.path.join(py, 'dist', '*.egg'))
      LOG.debug('Add to %s: %s' % (self._path, ext_egg))
      self._entries.update(ext_egg)

    # And eggs could also be in ext-eggs/*.egg
    for egg_file in glob.glob(os.path.join(app.path, 'ext-eggs', '*.egg')):
      LOG.debug('Add to %s: %s' % (self._path, egg_file))
      self._entries.add(egg_file)

  def remove(self, app):
    """
    Remove the app and its ext eggs from the pth file
    """
    for path in self._entries.copy():
      if path.startswith(app.path):
        self._entries.remove(path)

  def save(self):
    """
    Save the pth file
    Create a symlink to the path if it does not already exist.
    """
    tmp_path = self._path + '.new'
    file(tmp_path, 'w').write('\n'.join(sorted(self._entries)))
    os.rename(tmp_path, self._path)
    LOG.info('=== Saved %s' % self._path)

    # relpath defined in common.py for python 2.4 and 2.5
    rel_symlink_path = os.path.relpath(self._path, os.path.dirname(self._symlink_path))

    # overwrite symlink if the path it points to is different from desired PTH.
    if os.path.exists(self._symlink_path) and os.path.realpath(self._symlink_path) != rel_symlink_path:
      os.remove(self._symlink_path)

    if not os.path.exists(self._symlink_path):
      os.symlink(rel_symlink_path, self._symlink_path)
      LOG.debug('=== Create symbolic link at %s to %s' % (self._symlink_path, rel_symlink_path))

  def sync(self, apps):
    """Sync the .pth file with the installed apps"""
    self._entries = set()
    for app in apps:
      self.add(app)
