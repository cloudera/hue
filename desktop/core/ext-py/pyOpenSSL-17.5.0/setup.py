#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Jean-Paul Calderone 2008-2015, All rights reserved
#

"""
Installation script for the OpenSSL package.
"""

import codecs
import os
import re

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
META_PATH = os.path.join("src", "OpenSSL", "version.py")


def read_file(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "ascii") as f:
        return f.read()


META_FILE = read_file(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__ = ['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


URI = find_meta("uri")
LONG = (
    read_file("README.rst") + "\n\n" +
    "Release Information\n" +
    "===================\n\n" +
    re.search("(\d{2}.\d.\d \(.*?\)\n.*?)\n\n\n----\n",
              read_file("CHANGELOG.rst"), re.S).group(1) +
    "\n\n`Full changelog " +
    "<{uri}en/stable/changelog.html>`_.\n\n"
).format(uri=URI)


if __name__ == "__main__":
    setup(
        name=find_meta("title"),
        version=find_meta("version"),
        description=find_meta("summary"),
        long_description=LONG,
        author=find_meta("author"),
        author_email=find_meta("email"),
        maintainer="Hynek Schlawack",
        maintainer_email="hs@ox.cx",
        url=URI,
        license=find_meta("license"),
        classifiers=[
            'Development Status :: 6 - Mature',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',

            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',

            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Security :: Cryptography',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Networking',
        ],

        packages=find_packages(where="src"),
        package_dir={"": "src"},
        install_requires=[
            # Fix cryptographyMinimum in tox.ini when changing this!
            "cryptography>=2.1.4",
            "six>=1.5.2"
        ],
        extras_require={
            "test": [
                "flaky",
                "pretend",
                # pytest 3.3 doesn't support Python 2.6 anymore.
                # Remove this pin once we drop Python 2.6 too.
                "pytest>=3.0.1,<3.3.0",
            ],
            "docs": [
                "sphinx",
                "sphinx_rtd_theme",
            ]
        },
    )
