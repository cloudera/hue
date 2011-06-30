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
from setuptools import setup, find_packages
from hueversion import VERSION
import os

def expand_package_data(src_dirs, strip=""):
  ret = []
  for src_dir in src_dirs:
    for path, dnames, fnames in os.walk(src_dir):
      for fname in fnames:
        ret.append(os.path.join(path, fname).replace(strip, ""))
  return ret

os.chdir(os.path.dirname(os.path.abspath(__file__)))
setup(
  name = "shell",
  version = VERSION,
  url = 'http://github.com/cloudera/hue',
  description = 'Shell interface in Hue',
  author = 'Hue',
  packages = find_packages('src'),
  package_dir = {'': 'src'},
  install_requires = ['setuptools', 'desktop'],
  entry_points = { 'desktop.sdk.application': 'shell=shell' },
  zip_safe = False,
  package_data = {
    # Include static resources.  Package_data doesn't
    # deal well with directory globs, so we enumerate
    # the files manually.
    'shell': expand_package_data(
      ["src/shell/templates", "src/shell/static"],
      "src/shell/")
  }
)
