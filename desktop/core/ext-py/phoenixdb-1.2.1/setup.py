#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from setuptools import setup, find_packages
import setuptools
import sys

cmdclass = {}

try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
except ImportError:
    pass


def readme():
    with open('README.rst') as f:
        return f.read()


if setuptools.__version__ < '20.8.1':
    # Workaround for source install on old setuptools
    # This won't be able to create a proper multi-version pacakage
    install_requires=[
        'protobuf>=3.0.0',
        'requests',
        'requests-gssapi',
        'SQLAlchemy'
    ]
    if sys.version_info < (3,6):
        install_requires.append('gssapi<1.6.0')
    #Don't build the docs on an old stack
    setup_requires=[]
else:
    install_requires=[
        'protobuf>=3.0.0',
        'requests',
        'requests-gssapi',
        'gssapi<1.6.0;python_version<"3.6"',
        'SQLAlchemy'
    ]
    setup_requires=[
        'Sphinx;python_version>="3.6"',
    ],

version = "1.2.1"

setup(
    name="phoenixdb",
    version=version,
    description="Phoenix database adapter for Python",
    long_description=readme(),
    author="Apache Software Foundation",
    author_email="dev@phoenix.apache.org",
    url="http://phoenix.apache.org/python.html",
    license="Apache 2",
    packages=find_packages(),
    include_package_data=True,
    cmdclass=cmdclass,
    command_options={
        'build_sphinx': {
            'version': ('setup.py', version),
            'release': ('setup.py', version),
        },
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    install_requires=install_requires,
    extras_require={
        'SQLAlchemy': ['SQLAlchemy'],
    },
    tests_require=[
        'SQLAlchemy',
        'nose',
        'flake8'
    ],
    setup_requires=setup_requires,
    entry_points={
        "sqlalchemy.dialects": [
            "phoenix = phoenixdb.sqlalchemy_phoenix:PhoenixDialect"
        ]
    },
)
