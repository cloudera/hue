#!/usr/bin/env python

"""Setup script for packaging openpyxl.

To build a package for distribution:
    python setup.py sdist
and upload it to the PyPI with:
    python setup.py upload

Install a link for development work:
    pip install -e .

Thee manifest.in file is used for data files.

"""

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.rst')) as f:
        README = f.read()
except IOError:
    README = ''

try:
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("constants", "./openpyxl/_constants.py")
    constants = module_from_spec(spec)
    spec.loader.exec_module(constants)
except ImportError:
    # python2.7
    import imp
    constants = imp.load_source("constants", "./openpyxl/_constants.py")

__author__ = constants.__author__
__author_email__ = constants.__author_email__
__license__ = constants.__license__
__maintainer_email__ = constants.__maintainer_email__
__url__ = constants.__url__
__version__ = constants.__version__


setup(
    name='openpyxl',
    packages=find_packages(
        exclude=["*.tests", "*.test_.*", "test_.*", "tests", "develop"]
        ),
    package_dir={},
    # metadata
    version=__version__,
    description="A Python library to read/write Excel 2010 xlsx/xlsm files",
    long_description=README,
    author=__author__,
    author_email=__author_email__,
    url=__url__,
    license=__license__,
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        'jdcal', 'et_xmlfile',
        ],
    project_urls={
        'Documentation': 'https://openpyxl.readthedocs.io/en/stable/',
        'Source': 'https://bitbucket.org/openpyxl/openpyxl',
        'Tracker': 'https://bitbucket.org/openpyxl/openpyxl/issues',
    },
    classifiers=[
                 'Development Status :: 5 - Production/Stable',
                 'Operating System :: MacOS :: MacOS X',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 ],
    )
