#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Jean-Paul Calderone 2008-2015, All rights reserved
#

"""
Installation script for the OpenSSL module
"""

from setuptools import setup


# XXX Deduplicate this
__version__ = '0.15.1'

setup(name='pyOpenSSL', version=__version__,
      packages = ['OpenSSL'],
      package_dir = {'OpenSSL': 'OpenSSL'},
      py_modules  = ['OpenSSL.__init__',
                     'OpenSSL.tsafe',
                     'OpenSSL.rand',
                     'OpenSSL.crypto',
                     'OpenSSL.SSL',
                     'OpenSSL.version',
                     'OpenSSL.test.__init__',
                     'OpenSSL.test.util',
                     'OpenSSL.test.test_crypto',
                     'OpenSSL.test.test_rand',
                     'OpenSSL.test.test_ssl',
                     'OpenSSL.test.test_tsafe',
                     'OpenSSL.test.test_util',],
      description = 'Python wrapper module around the OpenSSL library',
      author = 'Jean-Paul Calderone',
      author_email = 'exarkun@twistedmatrix.com',
      maintainer = 'Jean-Paul Calderone',
      maintainer_email = 'exarkun@twistedmatrix.com',
      url = 'https://github.com/pyca/pyopenssl',
      license = 'APL2',
      install_requires=["cryptography>=0.7", "six>=1.5.2"],
      long_description = """\
High-level wrapper around a subset of the OpenSSL library, includes
 * SSL.Connection objects, wrapping the methods of Python's portable
   sockets
 * Callbacks written in Python
 * Extensive error-handling mechanism, mirroring OpenSSL's error codes
...  and much more ;)""",
      classifiers = [
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',

        # General classifiers to indicate "this project supports Python 2" and
        # "this project supports Python 3".
        'Programming Language :: Python :: 2',
        # In particular, this makes pyOpenSSL show up on
        # https://pypi.python.org/pypi?:action=browse&c=533&show=all and is in
        # accordance with
        # http://docs.python.org/2/howto/pyporting.html#universal-bits-of-advice
        'Programming Language :: Python :: 3',

        # More specific classifiers to indicate more precisely which versions
        # of those languages the project supports.
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',

        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        ],
      test_suite="OpenSSL")
