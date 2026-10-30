#
# pyformance 0.3.2 (https://github.com/omergertel/pyformance), vendored for Hue.
#
# Sources are the pyformance 0.3.2 release unchanged, except pyformance/__init__.py:
# its pkg_resources.declare_namespace() call is removed (see the comment there).
#
from setuptools import setup, find_packages

setup(
  name="pyformance",
  version="0.3.2",
  author="Omer Getrel",
  author_email="omer.gertel@gmail.com",
  description="Performance metrics, based on Coda Hale's Yammer metrics",
  license="Apache 2.0",
  classifiers=[
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 2.7",
  ],
  packages=find_packages(),
)
