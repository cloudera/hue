#!/usr/bin/env python
#
# Copyright (C) 2008-2018 Martin Owens
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
#
# pylint: disable=bad-whitespace
"""Setup the crontab module"""

import os
from setuptools import setup
from crontab import __version__, __pkgname__

# remove MANIFEST. distutils doesn't properly update it when the
# contents of directories change.
if os.path.exists('MANIFEST'):
    os.remove('MANIFEST')

# Grab description for Pypi
with open('README.rst') as fhl:
    description = fhl.read()

# Used for rpm building
RELEASE = "1"

setup(
    name             = __pkgname__,
    version          = __version__,
    release          = RELEASE,
    description      = 'Python Crontab API',
    long_description = description,
    author           = 'Martin Owens',
    url              = 'https://gitlab.com/doctormo/python-crontab/',
    author_email     = 'doctormo@gmail.com',
    test_suite       = 'tests',
    platforms        = 'linux',
    license          = 'LGPLv3',
    py_modules       = ['crontab', 'crontabs', 'cronlog'],
    provides         = ['crontab', 'crontabs', 'cronlog'],
    install_requires = ['python-dateutil'],
    extras_require   = {
        'cron-schedule': ['croniter'],
        'cron-description': ['cron-descriptor'],
    },
    classifiers      = [
        'Development Status :: 5 - Production/Stable',
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: SunOS/Solaris',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    options = {
        'bdist_rpm': {
            'build_requires': [
                'python',
                'python-setuptools',
            ],
            'release': RELEASE,
        },
    },
)
