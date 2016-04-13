#!/usr/bin/env python

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


install_requires = [
    # core dependencies
    'decorator',
    'requests >= 1.0.0',
    'paste',
    'zope.interface',
    'repoze.who',
    'pycrypto >= 2.2',  # 'Crypto'
    'pytz',
    'pyOpenSSL',
    'python-dateutil',
    'argparse'
]

tests_require = [
    'mongodict',
    'pyasn1',
    'pymongo',
    'python-memcached == 1.51',
    'pytest',
    'mako',
    #'pytest-coverage',
]


# only for Python 2.6
if sys.version_info < (2, 7):
    install_requires.append('importlib')

setup(
    name='pysaml2',
    version='2.4.0',
    description='Python implementation of SAML Version 2',
    # long_description = read("README"),
    author='Roland Hedberg',
    author_email='roland.hedberg@adm.umu.se',
    license='Apache 2.0',
    url='https://github.com/rohe/pysaml2',

    packages=['saml2', 'xmldsig', 'xmlenc', 's2repoze', 's2repoze.plugins',
              "saml2/profile", "saml2/schema", "saml2/extension",
              "saml2/attributemaps", "saml2/authn_context",
              "saml2/entity_category", "saml2/userinfo"],

    package_dir={'': 'src'},
    package_data={'': ['xml/*.xml']},
    classifiers=["Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"],

    scripts=["tools/parse_xsd2.py", "tools/make_metadata.py",
             "tools/mdexport.py", "tools/merge_metadata.py"],

    tests_require=tests_require,
    extras_require={
        'testing': tests_require,
    },
    install_requires=install_requires,
    zip_safe=False,
    test_suite='tests',
    cmdclass={'test': PyTest},
)
