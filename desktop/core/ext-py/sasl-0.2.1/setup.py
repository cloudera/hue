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

from setuptools import setup, Extension

sasl_module = Extension('sasl.saslwrapper',
                        sources=['sasl/saslwrapper.cpp'],
                        include_dirs=["sasl"],
                        libraries=["sasl2"],
                        language="c++")
setup(name='sasl',
      version='0.2.1',
      url="http://github.com/toddlipcon/python-sasl",
      maintainer="Todd Lipcon",
      maintainer_email="todd@cloudera.com",
      description="""Cyrus-SASL bindings for Python""",
      packages=['sasl'],
      install_requires=['six'],
      ext_modules=[sasl_module],
      include_package_data=True)
