#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

settings = {
    'name': 'ipaddress',
    'version': '1.0.19',
    'description': 'IPv4/IPv6 manipulation library',
    'long_description': 'Port of the 3.3+ ipaddress module to 2.6, 2.7, 3.2',
    'author': 'Philipp Hagemeister',
    'author_email': 'phihag@phihag.de',
    'url': 'https://github.com/phihag/ipaddress',
    'license': 'Python Software Foundation License',
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Python Software Foundation License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    'py_modules': ['ipaddress'],
}

setup(**settings)
