__version__ = '2.0'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

PYTHON3 = sys.version_info > (3, )
PYPY = getattr(sys, 'pypy_version_info', False) and True or False

install_requires = []

tests_require = install_requires + [
    'coverage',
    'mock',
    'nose',
]

if not (PYTHON3 or PYPY):
    tests_require += [
        'gevent',
    ]

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    install_requires.extend([
        'gevent',
    ])

setup(
    name='kazoo',
    version=__version__,
    description='Higher Level Zookeeper Client',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Communications",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Networking",
    ],
    keywords='zookeeper lock leader configuration',
    author="Kazoo team",
    author_email="python-zk@googlegroups.com",
    url="https://kazoo.readthedocs.org",
    license="Apache 2.0",
    packages=find_packages(),
    test_suite="kazoo.tests",
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
)
