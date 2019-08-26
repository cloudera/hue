#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages

version = None
with open('jaeger_client/__init__.py', 'r') as f:
    for line in f:
        m = re.match(r'^__version__\s*=\s*(["\'])([^"\']+)\1', line)
        if m:
            version = m.group(2)
            break

assert version is not None, \
    'Could not determine version number from jaeger_client/__init__.py'

setup(
    name='jaeger-client',
    version=version,
    url='https://github.com/jaegertracing/jaeger-client-python',
    description='Jaeger Python OpenTracing Tracer implementation',
    author='Yuri Shkuro',
    author_email='ys@uber.com',
    packages=find_packages(exclude=['crossdock', 'tests', 'example', 'tests.*']),
    include_package_data=True,
    license='Apache License 2.0',
    zip_safe=False,
    keywords='jaeger, tracing, opentracing',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'threadloop>=1,<2',
        'thrift',
        'tornado>=4.3,<5',
        'opentracing>=2.1,<3.0',
    ],
    # Uncomment below if need to test with unreleased version of opentracing
    # dependency_links=[
    #     'git+ssh://git@github.com/opentracing/opentracing-python.git@BRANCHNAME#egg=opentracing',
    # ],
    test_suite='tests',
    extras_require={
        ':python_version<"3"': [
            'futures',
        ],
        'tests': [
            'mock==1.0.1',
            'pycurl>=7.43,<8',
            # pinned to avoid RemovedInPytest4Warning
            'pytest>=3.7.0,<3.8.0',
            'pytest-cov==2.5.1',
            'coverage<4.4',  # can remove after https://bitbucket.org/ned/coveragepy/issues/581/44b1-44-breaking-in-ci
            'pytest-timeout==1.3.1',
            'pytest-tornado',
            # pin <3.2 as otherwise it requires pytest>=3.8
            'pytest-benchmark[histogram]>=3.0.0rc1,<3.2',
            'pytest-localserver',
            'flake8',
            'flake8-quotes',
            'codecov',
            'tchannel>=0.27', # This is only used in python 2
            'opentracing_instrumentation>=2,<3',
            'prometheus_client==0.3.1',
        ]
    },
)
