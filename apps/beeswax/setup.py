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

setup(
      name = "beeswax",
      version = VERSION,
      author = "Hue",
      url = 'http://github.com/cloudera/hue',
      description = "Hive Interface on Hue",
      packages = find_packages('src') + find_packages('gen-py'),
      package_dir = {'hive_metastore': 'gen-py', 'beeswaxd': 'gen-py', 'fb303': 'gen-py', 'TCLIService': 'gen-py', '': 'src'},
      install_requires = ['setuptools', 'desktop'],
      entry_points = {
        'desktop.sdk.application': 'beeswax=beeswax'
      }
)
