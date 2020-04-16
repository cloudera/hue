##
# Copyright (c) 2006-2018 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from os.path import dirname, join as joinpath
from setuptools import setup, Extension

try:
    from subprocess import getoutput
except ImportError:
    from commands import getoutput


#
# Options
#

project_name = "kerberos"

version_string = "1.3.0"

description = "Kerberos high-level interface"

long_description = open(joinpath(dirname(__file__), "README.rst")).read()

url = "https://github.com/apple/ccs-pykerberos"

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Systems Administration :: Authentication/Directory",
]

author = "Apple Inc."

author_email = "calendarserver-dev@lists.macosforge.org"

license = "Apache License, Version 2.0"

platforms = ["all"]


#
# Entry points
#

entry_points = {
    "console_scripts": [],
}


#
# Dependencies
#

setup_requirements = []

install_requirements = []

extras_requirements = {}

extra_link_args = getoutput("krb5-config --libs gssapi").split()

extra_compile_args = getoutput("krb5-config --cflags gssapi").split()


#
# Set up Extension modules that need to be built
#

extensions = [
    Extension(
        "kerberos",
        extra_link_args=extra_link_args,
        extra_compile_args=extra_compile_args,
        sources=[
            "src/base64.c",
            "src/kerberos.c",
            "src/kerberosbasic.c",
            "src/kerberosgss.c",
            "src/kerberospw.c",
        ],
    ),
]


#
# Run setup
#

def doSetup():
    setup(
        name=project_name,
        version=version_string,
        description=description,
        long_description=long_description,
        url=url,
        classifiers=classifiers,
        author=author,
        author_email=author_email,
        license=license,
        platforms=platforms,
        ext_modules=extensions,
        setup_requires=setup_requirements,
        install_requires=install_requirements,
        extras_require=extras_requirements,
    )


#
# Main
#

if __name__ == "__main__":
    doSetup()
