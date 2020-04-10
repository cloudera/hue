#!/usr/bin/env python
# coding: utf-8
import os
import re
from setuptools import setup

path = os.path.dirname(__file__)
desc_fd = os.path.join(path, 'README.rst')
hist_fd = os.path.join(path, 'HISTORY.rst')

long_desc = ''
short_desc = 'A Kerberos authentication handler for python-requests'

if os.path.isfile(desc_fd):
    with open(desc_fd) as fd:
        long_desc = fd.read()

if os.path.isfile(hist_fd):
    with open(hist_fd) as fd:
        long_desc = '\n\n'.join([long_desc, fd.read()])


def get_version():
    """
    Simple function to extract the current version using regular expressions.
    """
    reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
    with open('requests_kerberos/__init__.py') as fd:
        matches = list(filter(lambda x: x, map(reg.match, fd)))

    if not matches:
        raise RuntimeError(
            'Could not find the version information for requests_kerberos'
            )

    return matches[0].group(1)


setup(
    name='requests-kerberos',
    description=short_desc,
    long_description=long_desc,
    author='Ian Cordasco, Cory Benfield, Michael Komitee',
    author_email='graffatcolmingov@gmail.com',
    url='https://github.com/requests/requests-kerberos',
    packages=['requests_kerberos'],
    package_data={'': ['LICENSE', 'AUTHORS']},
    include_package_data=True,
    version=get_version(),
    install_requires=[
        'requests>=1.1.0',
        'cryptography>=1.3;python_version!="3.3"',
        'cryptography>=1.3,<2;python_version=="3.3"'
    ],
    extras_require={
        ':sys_platform=="win32"': ['winkerberos>=0.5.0'],
        ':sys_platform!="win32"': ['pykerberos>=1.1.8,<2.0.0'],
    },
    test_suite='test_requests_kerberos',
    tests_require=['mock'],
)
