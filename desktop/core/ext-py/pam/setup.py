from setuptools import setup, find_packages
import sys, os

version = '0.1.3'

setup(name='pam',
      version=version,
      description="PAM interface using ctypes",
      long_description="""\
An interface to the Pluggable Authentication Modules (PAM) library on linux, written in pure python (using ctypes)""",
      classifiers=["Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Operating System :: MacOS :: MacOS X",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: System :: Systems Administration :: Authentication/Directory"
          ],
      keywords='',
      author='Chris AtLee',
      author_email='chris@atlee.ca',
      url='http://atlee.ca/software/pam',
      download_url = "http://atlee.ca/software/pam/dist/%s" % version,
      license='MIT',
      py_modules=["pam"],
      zip_safe=True,
      install_requires=[],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
