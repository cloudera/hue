#!/usr/bin/env python
from __future__ import absolute_import, division, print_function

import sys

from setuptools import setup

has_enum = sys.version_info >= (3, 4)

readme = """
enum-compat
===========

This is a virtual package, its whole purpose is to install enum34 on
Python older than 3.4. On Python 3.4+ it's a no-op.

"""

if __name__ == '__main__':
    setup(
        name='enum-compat',
        version='0.0.2',
        description='enum/enum34 compatibility package',
        long_description=readme,
        author='Jakub Stasiak',
        author_email='jakub@stasiak.at',
        url='https://github.com/jstasiak/enum-compat',
        license='MIT',
        zip_safe=False,
        classifiers=[
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
        keywords=[
            'enum', 'compatibility', 'enum34',
        ],
        install_requires=[] if has_enum else ['enum34'],
    )
