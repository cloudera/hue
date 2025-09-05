#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Dynamic requirements generator for the Hue multi-Python build system.

Generate architecture- and Python-version-specific requirement files at
build time, replacing a static requirements.txt. This tool supports:

- Local editable paths for Hue extensions.
- Binary wheels for specific platforms (e.g., ppc64le).
- Architecture-aware dependency lists.
"""

import os
import platform
import shutil
import sys

this_dir = os.path.dirname(os.path.abspath(__file__))


class RequirementsGenerator:
  def __init__(self):
    self.local_requirements = [
      "boto-2.49.0",
      "django-axes-5.13.0",
      "django-babel",
      "pysaml2-7.3.1",
      "python-sasl-0.3.1",
    ]

    self.requirements = [
      "apache-ranger==0.0.3",
      "asn1crypto==0.24.0",
      "avro-python3==1.8.2",
      "Babel==2.9.1",
      "boto3==1.37.38",
      "celery[redis]==5.4.0",
      "cffi==1.15.0",
      "channels==4.2.2",
      "channels-redis==4.2.1",
      "configobj==5.0.9",
      "cx-Oracle==8.3.0",
      "daphne==3.0.2",
      "Django==4.2.23",
      "django-auth-ldap==4.3.0",
      "django-celery-beat==2.6.0",
      "django-celery-results==2.5.1",
      "django-cors-headers==4.4.0",
      "django-crequest==2018.5.11",
      "django-extensions==3.2.3",
      "django-ipware==3.0.2",
      "django_opentracing==1.1.0",
      "django_prometheus==2.3.1",
      "django-redis==5.4.0",
      "django-utils-six==2.0",
      "django-webpack-loader==1.0.0",
      "djangomako==1.3.2",
      "djangorestframework==3.15.2",
      "djangorestframework-simplejwt==5.3.1",
      "djangosaml2==1.9.3",
      "drf-spectacular[sidecar]==0.27.2",
      "future==0.18.3",
      "gcs-oauth2-boto-plugin==3.0",
      "greenlet==3.1.1",
      "gunicorn==23.0.0",
      "ipython==8.12.2",  # Python >= 3.8
      "jaeger-client==4.3.0",
      "jdcal==1.0.1",
      "kazoo==2.8.0",
      "kerberos==1.3.0",
      "krb5==0.5.1",  # pinned for Sles12, dep of requests-kerberos 0.14.0
      "kubernetes==26.1.0",
      "Mako==1.2.3",
      "openpyxl==3.0.9",
      "phoenixdb==1.2.1",
      "polars[calamine]==1.8.2",  # Python >= 3.8
      "prompt-toolkit==3.0.39",
      "protobuf==3.20.3",
      "psutil==5.8.0",
      "pyarrow==17.0.0",
      "pydantic==2.10.6",
      "pyformance==0.3.2",
      "PyJWT==2.4.0",
      "python-daemon==2.2.4",
      "python-dateutil==2.8.2",
      "python-ldap==3.4.3",
      "python-magic==0.4.27",
      "python-oauth2==1.1.0",
      "python-pam==2.0.2",
      "pytidylib==0.3.2",
      "pytz==2021.3",
      "PyYAML==6.0.1",
      "requests==2.32.3",
      "requests-gssapi==1.2.3",
      "requests-kerberos==0.14.0",
      "rsa==4.7.2",
      "ruff==0.11.10",
      "setuptools==70.0.0",
      "six==1.16.0",
      "slack-sdk==3.31.0",
      "SQLAlchemy==1.3.8",
      "sqlparse==0.5.0",
      "tablib==0.13.0",
      "tabulate==0.8.9",
      "thrift-sasl==0.4.3",
      "trino==0.329.0",
      "git+https://github.com/gethue/thrift.git",
    ]

    self.x86_64_requirements = {
      "default": [
        "cryptography==42.0.8",
        "lxml==4.9.1",
        "Markdown==3.1",
        "numpy==1.24.4",
        "pandas==2.0.3",
        "sasl==0.3.1",
      ],
      "3.9": [
        "decorator==5.1.1",
        "lxml==4.9.1",
        "Markdown==3.8",
        "numpy==1.24.4",
        "pandas==2.0.3",
        "pyopenssl==22.1.0",
        "sasl==0.3.1",
      ],
      "3.11": [
        "async-timeout==5.0.1",
        "cryptography==42.0.8",
        "lxml==4.9.1",
        "Markdown==3.8",
        "numpy==1.24.4",
        "pandas==2.0.3",
        "pure-sasl==0.6.2",
      ],
    }

    self.aarch64_requirements = {
      "default": [
        "cryptography==42.0.8",
        "lxml==4.9.1",
        "Markdown==3.1",
        "numpy==1.24.4",
        "pandas==2.0.3",
      ],
      "3.9": [
        "decorator==5.1.1",
        "lxml==4.9.1",
        "Markdown==3.8",
        "numpy==1.24.4",
        "pandas==2.0.3",
        "pyopenssl==22.1.0",
        "sasl==0.3.1",
      ],
      "3.11": [
        "async-timeout==5.0.1",
        "cryptography==42.0.8",
        "lxml==4.9.1",
        "Markdown==3.8",
        "numpy==1.24.4",
        "pandas==2.0.3",
        "pure-sasl==0.6.2",
      ],
    }
    self.arch_requirements_map = {
      "x86_64": self.x86_64_requirements,
      "aarch64": self.aarch64_requirements,
      "arm64": self.aarch64_requirements,  # arm64 is treated as aarch64
    }
    self.arch = platform.machine()
    self.python_version_string = f"{sys.version_info.major}.{sys.version_info.minor}"

  def copy_local_requirements(self, python_version_string):
    local_dir = f"{this_dir}/{python_version_string}"
    if os.path.exists(local_dir):
      shutil.rmtree(local_dir, ignore_errors=True)
    shutil.copytree(f"{this_dir}/ext-py3", local_dir)
    return list(map(lambda x: f"file://{local_dir}/{x}", self.local_requirements))

  def generate_requirements(self):
    if self.arch not in self.arch_requirements_map:
      raise ValueError(f"Unsupported architecture: {self.arch}")
    arch_reqs = self.arch_requirements_map[self.arch]
    self.requirements.extend(arch_reqs.get(self.python_version_string, arch_reqs["default"]))
    self.requirements.extend(self.copy_local_requirements(self.python_version_string))
    with open(f"{this_dir}/requirements-{self.arch}-{self.python_version_string}.txt", "w") as f:
      f.write("\n".join(self.requirements))

  def get_file_name(self):
    return f"{this_dir}/requirements-{self.arch}-{self.python_version_string}.txt"


if __name__ == "__main__":
  generator = RequirementsGenerator()
  try:
    generator.generate_requirements()
    print(generator.get_file_name())
  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
