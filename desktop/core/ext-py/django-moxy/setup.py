#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

from moxy import __version__

requirements = [
        'eventlet >= 0.9.3',
    ]
    
setup(
    name='moxy',
    version=__version__,
    description='''Django db backend for MySQL using MySQLdb and eventlet.db_pool''',
    author='R. Tyler Ballance',
    author_email='tyler@linux.com',
    url='http://github.com/rtyler/django-moxy',
    packages=['moxy'],
    install_requires=requirements,
    test_suite='moxy.tests',
)
