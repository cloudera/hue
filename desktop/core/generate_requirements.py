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
Dynamic requirements generator for the Hue build system (Python 3.11).

Generate architecture-specific requirement files at build time, replacing
a static requirements.txt. This tool supports:

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
      # Vendored to relax the hard Mako==1.2.3 pin of djangomako 1.3.2 (see its setup.py).
      "djangomako-1.3.2",
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
      # Must stay >= 2026.10.19, the first release that drops the compromised eMudhra (emSign) CA. 2026.10.23
      # also drops the remaining emSign roots. It is a transitive dependency of requests; pin it so the CA
      # bundle never depends on whatever is newest at build time.
      "certifi==2026.10.23",
      # cryptography 46.x requires cffi >= 2.0.0. Held at 2.0.0 because 2.1.0 needs Python >= 3.10.
      "cffi==2.0.0",
      "configobj==5.0.9",
      "cryptography==46.0.7",
      "cx-Oracle==8.3.0",
      "Django==4.2.30",
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
      "djangorestframework==3.15.2",
      "djangorestframework-simplejwt==5.5.1",
      "djangosaml2==1.9.3",
      "drf-spectacular[sidecar]==0.27.2",
      "future==0.18.3",
      "gcs-oauth2-boto-plugin==3.0",
      "greenlet==3.1.1",
      "gunicorn==23.0.0",
      "ipython==8.12.2",  # Python >= 3.8
      "jaeger-client==4.3.0",
      "kazoo==2.8.0",
      "kerberos==1.3.0",
      "krb5==0.5.1",  # pinned for Sles12, dep of requests-kerberos 0.14.0
      "kubernetes==26.1.0",
      "Mako==1.4.2",
      "openpyxl==3.0.9",
      "phoenixdb==1.2.1",
      "polars[calamine]==1.8.2",  # Python >= 3.8
      "prompt-toolkit==3.0.39",
      # Needs >= 6.33.5 at runtime: desktop/lib/raz/signer_protos_pb2.py is generated with protoc 6.33.5.
      "protobuf==6.33.5",
      "psutil==5.8.0",
      "pyarrow==23.0.1",
      "pydantic==2.10.6",
      "pyformance==0.3.2",
      "PyJWT==2.15.1",
      # Held at 26.0.0: 26.4.0 drops X509Req, which pysaml2 still needs. Caps cryptography at <47.
      "pyOpenSSL==26.0.0",
      "python-daemon==2.2.4",
      "python-dateutil==2.8.2",
      "python-ldap==3.4.5",
      "python-magic==0.4.27",
      "python-oauth2==1.1.0",
      "python-pam==2.0.2",
      "pytidylib==0.3.2",
      "pytz==2021.3",
      "PyYAML==6.0.1",
      "requests==2.33.0",
      "requests-gssapi==1.2.3",
      "requests-kerberos==0.14.0",
      "rsa==4.7.2",
      "ruff==0.11.10",
      "six==1.16.0",
      "slack-sdk==3.31.0",
      "SQLAlchemy==1.3.8",
      # sqlparse is pinned in the architecture-specific requirements below: 0.6.0 fixes three DoS CVEs.
      "tablib==3.10.0",
      "tabulate==0.8.9",
      "thrift-sasl==0.4.3",
      "trino==0.329.0",
      # Needed by pandas.read_excel(engine="xlrd") in the indexer. tablib no longer installs it since 3.0.
      "xlrd==2.0.2",
      "git+https://github.com/gethue/thrift.git",
    ]

    python_311_arch_extras = [
      "async-timeout==5.0.1",
      "lxml==4.9.1",
      "Markdown==3.8.1",
      "numpy==1.24.4",
      "pandas==2.0.3",
      "pure-sasl==0.6.2",
      "setuptools==80.9.0",
      "sqlparse==0.6.0",
    ]

    self.x86_64_requirements = {
      "3.11": python_311_arch_extras,
    }

    self.aarch64_requirements = {
      "3.11": python_311_arch_extras,
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
    if self.python_version_string not in arch_reqs:
      raise ValueError(
        f"Unsupported Python version {self.python_version_string} for architecture {self.arch}. "
        f"Supported: {', '.join(sorted(arch_reqs.keys()))}"
      )
    self.requirements.extend(arch_reqs[self.python_version_string])
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
