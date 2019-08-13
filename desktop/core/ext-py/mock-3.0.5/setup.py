import re
from os.path import join

import setuptools

setuptools.setup(
    version=re.search("__version__ = '([^']+)'",
                      open(join('mock', 'mock.py')).read()).group(1),
    long_description=open('README.rst').read(),
)
