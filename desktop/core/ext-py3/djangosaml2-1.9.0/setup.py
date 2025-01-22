# Copyright (C) 2011-2012 Yaco Sistemas <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import codecs
import os

from setuptools import find_packages, setup


def read(*rnames):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), *rnames), encoding="utf-8"
    ).read()


setup(
    name="djangosaml2",
    version="1.9.3",
    description="pysaml2 integration for Django",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords="django,pysaml2,sso,saml2,federated authentication,authentication",
    author="Yaco Sistemas and independent contributors",
    author_email="lorenzo.gil.sanchez@gmail.com",
    maintainer="Giuseppe De Marco",
    url="https://github.com/IdentityPython/djangosaml2",
    download_url="https://pypi.org/project/djangosaml2/",
    license="Apache 2.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=["defusedxml>=0.4.1", "Django>=3.2", "pysaml2>=6.5.1"],
)
