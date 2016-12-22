# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from codecs import open
from os import path
import sys

from setuptools import find_packages
from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

requirements = ["python-dateutil>=2.1,<3.0.0",
                "docutils>=0.10",
                "pyyaml>=3.11",
                "colorama>=0.2.5,<=0.3.3",
                "pycrypto>=2.6.1",
                "requests>=2.9.1"]
if sys.version_info[:2] == (2, 6):
    requirements.append("argparse>=1.1")
    requirements.append("ordereddict==1.1")
    requirements.append("simplejson==3.3.0")

setup(
    name='navoptapi',
    version='0.1.0',
    description='Cloudera Navigator Optimizer Api',
    long_description=long_description,
    url='http://www.cloudera.com/',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: System Administrators',
        'License :: OSI Approved :: Apache License 2.0',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7,'
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
)
