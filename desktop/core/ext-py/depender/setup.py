from setuptools import setup, find_packages
import os

base = os.path.join(os.path.dirname(__file__), "src")

setup(
      name = "depender",
      version = "0.3",
      url = 'http://www.mootools.net',
      description = "Depender: JS Dep loader",
      install_requires = ['setuptools', 'django', 'PyYAML', 'simplejson'],
      packages = find_packages(base),
      package_dir={'': base}
)
