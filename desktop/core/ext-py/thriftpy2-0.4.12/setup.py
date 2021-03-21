#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import platform

from os.path import join, dirname

from setuptools import setup, find_packages
from setuptools.extension import Extension

with open(join(dirname(__file__), 'thriftpy2', '__init__.py'), 'r') as f:
    version = re.match(r".*__version__ = '(.*?)'", f.read(), re.S).group(1)

install_requires = [
    "ply>=3.4,<4.0",
]

tornado_requires = [
    "tornado>=4.0,<6.0",
]

try:
    from tornado import version as tornado_version
    if tornado_version < '5.0':
        tornado_requires.append("toro>=0.6")
except ImportError:
    # tornado will now only get installed and we'll get the newer one
    pass

dev_requires = [
    "cython>=0.28.4",
    "flake8>=2.5",
    "pytest>=2.8",
    "sphinx-rtd-theme>=0.1.9",
    "sphinx>=1.3",
] + tornado_requires


# cython detection
try:
    from Cython.Build import cythonize
    CYTHON = True
except ImportError:
    CYTHON = False

cmdclass = {}
ext_modules = []

# pypy detection
PYPY = "__pypy__" in sys.modules
UNIX = platform.system() in ("Linux", "Darwin")

# only build ext in CPython with UNIX platform
if UNIX and not PYPY:
    # rebuild .c files if cython available
    if CYTHON:
        cythonize("thriftpy2/transport/cybase.pyx")
        cythonize("thriftpy2/transport/**/*.pyx")
        cythonize("thriftpy2/protocol/cybin/cybin.pyx")

    ext_modules.append(Extension("thriftpy2.transport.cybase",
                                 ["thriftpy2/transport/cybase.c"]))
    ext_modules.append(Extension("thriftpy2.transport.buffered.cybuffered",
                                 ["thriftpy2/transport/buffered/cybuffered.c"]))
    ext_modules.append(Extension("thriftpy2.transport.memory.cymemory",
                                 ["thriftpy2/transport/memory/cymemory.c"]))
    ext_modules.append(Extension("thriftpy2.transport.framed.cyframed",
                                 ["thriftpy2/transport/framed/cyframed.c"]))
    ext_modules.append(Extension("thriftpy2.protocol.cybin",
                                 ["thriftpy2/protocol/cybin/cybin.c"]))

setup(name="thriftpy2",
      version=version,
      description="Pure python implementation of Apache Thrift.",
      keywords="thrift python thriftpy thriftpy2",
      author="ThriftPy Organization",
      author_email="gotzehsing@gmail.com",
      packages=find_packages(exclude=['benchmark', 'docs', 'tests']),
      entry_points={},
      url="https://thriftpy2.readthedocs.io/",
      license="MIT",
      zip_safe=False,
      long_description=open("README.rst").read(),
      install_requires=install_requires,
      tests_require=tornado_requires,
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
      extras_require={
          "dev": dev_requires,
          "tornado": tornado_requires
      },
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      include_package_data=True,
      classifiers=[
          "Topic :: Software Development",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
      ])
