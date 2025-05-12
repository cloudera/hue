"""
Dynamic requirements generator for Hue multi-python build system.

Generates architecture- and Python-version-specific requirement files
at build time. This tool replaces static requirements.txt and supports:
  - Local editable paths for Hue extensions.
  - Binary wheels for specific platforms (e.g., ppc64le).
  - Architecture-aware dependency lists.
"""

import os
import sys
import shutil
import platform

this_dir = os.path.dirname(os.path.abspath(__file__))


class RequirementsGenerator:
    def __init__(self):
        self.local_requirements = [
            "boto-2.49.0",
            "django-axes-5.13.0",
            "django-babel",
            "djangosaml2-0.18.0",
            "pysaml2-7.3.1",
            "python-sasl-0.3.1",
        ]

        self.requirements = [
            "setuptools==70.0.0",
            "apache-ranger==0.0.3",
            "requests-gssapi==1.2.3",
            "asn1crypto==0.24.0",
            "avro-python3==1.8.2",
            "Babel==2.9.1",
            "celery[redis]==5.4.0",
            "cffi==1.15.0",
            "channels==4.0.0",
            "channels-redis==4.0.0",
            "configobj==5.0.9",
            "cx-Oracle==8.3.0",
            "django-auth-ldap==4.3.0",
            "Django==4.1.13",
            "daphne==3.0.2",
            "django-redis==5.4.0",
            "django-celery-beat==2.6.0",
            "django-celery-results==2.5.1",
            "django-cors-headers==3.13.0",
            "django-crequest==2018.5.11",
            "django-debug-panel==0.8.3",
            "django-debug-toolbar==3.6.0",
            "django-extensions==3.2.1",
            "django-ipware==3.0.2",
            "django_opentracing==1.1.0",
            "django_prometheus==1.0.15",
            "django-webpack-loader==1.0.0",
            "djangomako==1.3.2",
            "djangorestframework-simplejwt==5.2.1",
            "djangorestframework==3.14.0",
            "future==0.18.3",
            "gcs-oauth2-boto-plugin==3.0",
            "greenlet==3.1.1",
            "gunicorn==23.0.0",
            "ipython==8.12.2",  # Python >= 3.8
            "jaeger-client==4.3.0",
            "jdcal==1.0.1",
            "kazoo==2.8.0",
            "kerberos==1.3.0",
            "kubernetes==26.1.0",
            "Mako==1.2.3",
            "Markdown==3.7",
            "openpyxl==3.0.9",
            "phoenixdb==1.2.1",
            "prompt-toolkit==3.0.39",
            "protobuf==3.20.3",
            "pyarrow==17.0.0",
            "pyformance==0.3.2",
            "polars[calamine]==1.8.2",  # Python >= 3.8
            "python-dateutil==2.8.2",
            "python-daemon==2.2.4",
            "python-ldap==3.4.3",
            "python-magic==0.4.27",
            "python-oauth2==1.1.0",
            "python-pam==2.0.2",
            "pytidylib==0.3.2",
            "pytz==2021.3",
            "PyJWT==2.4.0",
            "PyYAML==6.0.1",
            "requests==2.32.3",
            "requests-kerberos==0.14.0",
            "krb5==0.5.1",  # pinned for Sles12, dep of requests-kerberos 0.14.0
            "rsa==4.7.2",
            "ruff==0.4.2",
            "slack-sdk==3.31.0",
            "SQLAlchemy==1.3.8",
            "sqlparse==0.5.0",
            "tablib==0.13.0",
            "tabulate==0.8.9",
            "trino==0.329.0",
            "git+https://github.com/gethue/thrift.git",
            "thrift-sasl==0.4.3",
            "django-utils-six==2.0",
            "six==1.16.0",
            "psutil==5.8.0",
            "drf-spectacular[sidecar]==0.27.2",
        ]
        self.ppc64le_requirements = {
            "default": [],
            "3.8": [
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/cryptography-41.0.1-cp38-cp38-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/numpy-1.23.1-cp38-cp38-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/pandas-1.4.3-cp38-cp38-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/lxml-4.6.4-cp38-cp38-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "PyYAML==5.4.1",
                "sasl==0.3.1",
            ],
            "3.9": [
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/cryptography-41.0.1-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/numpy-1.23.1-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/pandas-1.4.3-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "http://ibm-ppc-builds.s3.amazonaws.com/silx-py-libs/lxml-4.6.4-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl",
                "PyYAML==6.0.1",
                "sasl==0.3.1",
            ]
        }
        self.x86_64_requirements = {
            "default": [
                "cryptography==42.0.8",
                "numpy==1.24.4",
                "pandas==2.0.3",
                "lxml==4.9.1",
                "sasl==0.3.1",
            ],
            "3.11": [
                "cryptography==42.0.8",
                "numpy==1.24.4",
                "pandas==2.0.3",
                "lxml==4.9.1",
                "async-timeout==5.0.1",
                "pure-sasl==0.6.2",
            ],
        }
        self.aarch64_requirements = {
            "default": [
                "cryptography==42.0.8",
                "numpy==1.24.4",
                "pandas==2.0.3",
                "lxml==4.9.1",
                "sasl==0.3.1",
            ],
            "3.11": [
                "cryptography==42.0.8",
                "numpy==1.24.4",
                "pandas==2.0.3",
                "lxml==4.9.1",
                "async-timeout==5.0.1",
                "pure-sasl==0.6.2",
            ],
        }
        self.pytorch_requirements = {
            "default": [
                "--extra-index-url \"https://cloudera-build-us-west-1.vpc.cloudera.com/whl/cpu\" torch==2.2.2+cpu torchvision==0.17.2+cpu",
            ]
        }
        self.arch_requirements_map = {
            "ppc64le": self.ppc64le_requirements,
            "x86_64": self.x86_64_requirements,
            "aarch64": self.aarch64_requirements,
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
        self.requirements.extend(self.pytorch_requirements.get(self.python_version_string, self.pytorch_requirements["default"]))

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
