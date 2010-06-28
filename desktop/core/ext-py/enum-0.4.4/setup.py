#! /usr/bin/env python
# -*- coding: utf-8 -*-

# setup.py
# Part of enum, a package providing enumerated types for Python.
#
# Copyright © 2007–2009 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later
# or, at your option, the terms of the Python license.

""" Python distutils setup for ‘enum’ distribution.
    """

import textwrap

from setuptools import setup, find_packages


distribution_name = "enum"
main_module_name = 'enum'
main_module = __import__(main_module_name)
version = main_module.__version__

main_module_doc = main_module.__doc__.decode('utf-8')
short_description, long_description = (
    textwrap.dedent(desc).strip()
    for desc in main_module_doc.split('\n\n', 1)
    )


setup(
    name=distribution_name,
    version=version,
    packages=find_packages(exclude=["test"]),
    py_modules=[main_module_name],

    # Setuptools metadata.
    zip_safe=False,
    install_requires=[
        "setuptools",
        ],
    test_suite="test.test_enum.suite",

    # PyPI metadata.
    author=main_module.__author_name__,
    author_email=main_module.__author_email__,
    description=short_description,
    license=main_module.__license__,
    keywords="enum enumerated enumeration",
    url=main_module.__url__,
    long_description=long_description,
    classifiers=[
        # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: Python Software Foundation License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        ],
    )


# Local variables:
# mode: python
# End:
# vim: filetype=python fileencoding=utf-8 :
