#!/usr/bin/env python
import os
from setuptools import setup, find_packages

version = __import__('unicodecsv').__version__

setup(
    name='unicodecsv',
    version=version,
    description="Python2's stdlib csv module is nice, but it doesn't support unicode. This module is a drop-in replacement which *does*.",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'rb').read().decode('utf-8'),
    author='Jeremy Dunck',
    author_email='jdunck@gmail.com',
    url='https://github.com/jdunck/python-unicodecsv',
    packages=find_packages(),
    tests_require=['unittest2>=0.5.1'],
    test_suite='runtests.get_suite',
    license='BSD License',
    classifiers=['Development Status :: 5 - Production/Stable',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: BSD License',
                'Natural Language :: English',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3.3',
                'Programming Language :: Python :: 3.4',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: Implementation :: PyPy',
                'Programming Language :: Python :: Implementation :: CPython',],
)

