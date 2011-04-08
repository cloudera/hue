#!/usr/bin/env python
# Copyright (c) 2008, Donovan Preston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys

# Insert src/ into our path so we can pull the version and include it
sys.path.insert(0, 'src')
from spawning import __version__

from os import path

from setuptools import find_packages, setup

install_requires = ['eventlet >= 0.9.12',]

try:
    import json
except ImportError:
    install_requires.append('simplejson')

setup(
    name='Spawning',
    description='Spawning is a wsgi server which supports multiple processes, multiple threads, green threads, non-blocking HTTP io, and automatic graceful upgrading of code.',
    long_description=file(
        path.join(
            path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author='Donovan Preston',
    author_email='dsposx@mac.com',
    maintainer='R. Tyler Croy',
    maintainer_email='tyler@monkeypox.org',
    include_package_data = True,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    version=__version__,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [],
        'paste.server_factory': [
            'main=spawning.paste_factory:server_factory'
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Development Status :: 4 - Beta"
    ]
)

