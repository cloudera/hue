import os
import functools
import platform
from setuptools import setup, find_packages

_IN_PACKAGE_DIR = functools.partial(os.path.join, "pyformance")

with open(_IN_PACKAGE_DIR("__version__.py")) as version_file:
    exec(version_file.read())

install_requires = []  # optional: ["blinker==1.2"]
if platform.python_version() < '2.7':
    install_requires.append('unittest2')

setup(name="pyformance",
      classifiers=[
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Programming Language :: Python :: 2.7",
      ],
      description="Performance metrics, based on Coda Hale's Yammer metrics",
      license="Apache 2.0",
      author="Omer Getrel",
      author_email="omer.gertel@gmail.com",
      version=__version__,
      packages=find_packages(exclude=["tests"]),
      data_files=[],
      install_requires=install_requires,
      scripts=[],
      )
