#!/usr/bin/env python
# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2009-2015 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""OpenID integration for django.contrib.auth

A library that can be used to add OpenID support to Django applications.
The library integrates with Django's built in authentication system, so
most applications require minimal changes to support OpenID llogin. The
library also includes the following features:
  * Basic user details are transferred from the OpenID server via the
    Simple Registration extension or Attribute Exchange extension.
  * can be configured to use a fixed OpenID server URL, for use in SSO.
  * supports the launchpad.net teams extension to get team membership
    info.
"""

import sys

from setuptools import find_packages, setup

PY3 = sys.version_info.major >= 3


description, long_description = __doc__.split('\n\n', 1)
VERSION = '0.14'

install_requires = ['django>=1.6', 'six']
if PY3:
    install_requires.append('python3-openid')
else:
    install_requires.append('python-openid>=2.2.0')

setup(
    name='django-openid-auth',
    version=VERSION,

    packages=find_packages(),
    install_requires=install_requires,
    package_data={
        'django_openid_auth': ['templates/openid/*.html'],
    },

    # metadata for upload to PyPI
    author='Canonical Ltd',
    author_email='noreply@canonical.com',
    description=description,
    long_description=long_description,
    license='BSD',
    platforms=['any'],
    url='https://launchpad.net/django-openid-auth',
    download_url=('http://launchpad.net/django-openid-auth/trunk/%s/+download'
                  '/django-openid-auth-%s.tar.gz' % (VERSION, VERSION)),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
)
