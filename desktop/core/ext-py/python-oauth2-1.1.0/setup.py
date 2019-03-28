import os

from setuptools import setup
from oauth2 import VERSION

setup(name="python-oauth2",
      version=VERSION,
      description="OAuth 2.0 provider for python",
      long_description=open("README.rst").read(),
      author="Markus Meyer",
      author_email="hydrantanderwand@gmail.com",
      url="https://github.com/wndhydrnt/python-oauth2",
      packages=[d[0].replace("/", ".") for d in os.walk("oauth2") if not d[0].endswith("__pycache__")],
      extras_require={
          "memcache": ["python-memcached"],
          "mongodb": ["pymongo"],
          "redis": ["redis"]
      },
      classifiers=[
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6",
      ]
      )
