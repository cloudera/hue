# Copyright 2015 Cloudera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Parts of this file were taken from the pandas project
# (https://github.com/pandas-dev/pandas), which is permitted for use under
# the BSD 3-Clause License

from distutils.sysconfig import get_config_var
from distutils.version import LooseVersion
import os
import platform
from setuptools import setup, Extension
import sys


# From https://github.com/pandas-dev/pandas/pull/24274:
# For mac, ensure extensions are built for macos 10.9 when compiling on a
# 10.9 system or above, overriding distuitls behaviour which is to target
# the version that python was built for. This may be overridden by setting
# MACOSX_DEPLOYMENT_TARGET before calling setup.py
if sys.platform == 'darwin':
    if 'MACOSX_DEPLOYMENT_TARGET' not in os.environ:
        current_system = LooseVersion(platform.mac_ver()[0])
        python_target = LooseVersion(
            get_config_var('MACOSX_DEPLOYMENT_TARGET'))
        if python_target < '10.9' and current_system >= '10.9':
            os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.9'


sasl_module = Extension('sasl.saslwrapper',
                        sources=['sasl/saslwrapper.cpp'],
                        include_dirs=["sasl"],
                        libraries=["sasl2"],
                        language="c++")
setup(name='sasl',
      version='0.3.1',
      url="http://github.com/cloudera/python-sasl",
      maintainer="Todd Lipcon",
      maintainer_email="todd@cloudera.com",
      description="""Cyrus-SASL bindings for Python""",
      classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
      ],
      packages=['sasl'],
      install_requires=['six'],
      ext_modules=[sasl_module],
      include_package_data=True,
      license='Apache License, Version 2.0')
