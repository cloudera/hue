#!/usr/bin/env python

# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import os
import platform
import sys

from setuptools import find_packages, setup


base_dir = os.path.dirname(__file__)
src_dir = os.path.join(base_dir, "src")

# When executing the setup.py, we need to be able to import ourselves, this
# means that we need to add the src/ directory to the sys.path.
sys.path.insert(0, src_dir)

about = {}
with open(os.path.join(src_dir, "cryptography", "__about__.py")) as f:
    exec (f.read(), about)


# `setup_requirements` must be kept in sync with `pyproject.toml`
setup_requirements = ["cffi>=1.12"]

if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (5, 4):
        raise RuntimeError(
            "cryptography is not compatible with PyPy < 5.4. Please upgrade "
            "PyPy to use this library."
        )


with open(os.path.join(base_dir, "README.rst")) as f:
    long_description = f.read()


try:
    setup(
        name=about["__title__"],
        version=about["__version__"],
        description=about["__summary__"],
        long_description=long_description,
        long_description_content_type="text/x-rst",
        license=about["__license__"],
        url=about["__uri__"],
        author=about["__author__"],
        author_email=about["__email__"],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: Apache Software License",
            "License :: OSI Approved :: BSD License",
            "Natural Language :: English",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX",
            "Operating System :: POSIX :: BSD",
            "Operating System :: POSIX :: Linux",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Security :: Cryptography",
        ],
        package_dir={"": "src"},
        packages=find_packages(
            where="src", exclude=["_cffi_src", "_cffi_src.*"]
        ),
        include_package_data=True,
        python_requires=(
            ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*"
        ),
        install_requires=["six >= 1.4.1"] + setup_requirements,
        setup_requires=setup_requirements,
        extras_require={
            ":python_version < '3'": ["enum34", "ipaddress"],
            "test": [
                "pytest>=3.6.0,!=3.9.0,!=3.9.1,!=3.9.2",
                "pretend",
                "iso8601",
                "pytz",
                "hypothesis>=1.11.4,!=3.79.2",
            ],
            "docs": [
                "sphinx >= 1.6.5,!=1.8.0,!=3.1.0,!=3.1.1",
                "sphinx_rtd_theme",
            ],
            "docstest": [
                "doc8",
                "pyenchant >= 1.6.11",
                "twine >= 1.12.0",
                "sphinxcontrib-spelling >= 4.0.1",
            ],
            "pep8test": [
                "black",
                "flake8",
                "flake8-import-order",
                "pep8-naming",
            ],
            # This extra is for OpenSSH private keys that use bcrypt KDF
            # Versions: v3.1.3 - ignore_few_rounds, v3.1.5 - abi3
            "ssh": ["bcrypt >= 3.1.5"],
        },
        # for cffi
        zip_safe=False,
        ext_package="cryptography.hazmat.bindings",
        cffi_modules=[
            "src/_cffi_src/build_openssl.py:ffi",
            "src/_cffi_src/build_padding.py:ffi",
        ],
    )
except:  # noqa: E722
    # Note: This is a bare exception that re-raises so that we don't interfere
    # with anything the installation machinery might want to do. Because we
    # print this for any exception this msg can appear (e.g. in verbose logs)
    # even if there's no failure. For example, SetupRequirementsError is raised
    # during PEP517 building and prints this text. setuptools raises SystemExit
    # when compilation fails right now, but it's possible this isn't stable
    # or a public API commitment so we'll remain ultra conservative.
    print(
        """
    =============================DEBUG ASSISTANCE=============================
    If you are seeing a compilation error please try the following steps to
    successfully install cryptography:
    1) Upgrade to the latest pip and try again. This will fix errors for most
       users. See: https://pip.pypa.io/en/stable/installing/#upgrading-pip
    2) Read https://cryptography.io/en/latest/installation.html for specific
       instructions for your platform.
    3) Check our frequently asked questions for more information:
       https://cryptography.io/en/latest/faq.html
    =============================DEBUG ASSISTANCE=============================
    """
    )
    raise
