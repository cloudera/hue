#!/usr/bin/env python


from setuptools import find_packages, setup
from eventlet import __version__
from os import path
import sys

requirements = []
for flag, req in [('--without-greenlet','greenlet >= 0.3')]:
    if flag in sys.argv:
        sys.argv.remove(flag)
    else:
        requirements.append(req)

setup(
    name='eventlet',
    version=__version__,
    description='Highly concurrent networking library',
    author='Linden Lab',
    author_email='eventletdev@lists.secondlife.com',
    url='http://eventlet.net',
    packages=find_packages(exclude=['tests', 'benchmarks']),
    install_requires=requirements,
    zip_safe=False,
    long_description=open(
        path.join(
            path.dirname(__file__),
            'README'
        )
    ).read(),
    test_suite = 'nose.collector',
    tests_require = 'httplib2',
    classifiers=[
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX",
    "Operating System :: Microsoft :: Windows",
    "Topic :: Internet",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Intended Audience :: Developers",
    "Development Status :: 4 - Beta"]
    )

