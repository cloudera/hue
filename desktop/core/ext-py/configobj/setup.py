# setup.py
# Install script for ConfigObj
# Copyright (C) 2005-2009 Michael Foord, Mark Andrews, Nicola Larosa
# E-mail: fuzzyman AT voidspace DOT org DOT uk
#         mark AT la-la DOT com
#         nico AT tekNico DOT net

# This software is licensed under the terms of the BSD license.
# http://www.voidspace.org.uk/python/license.shtml

import sys
from distutils.core import setup
from configobj import __version__ as VERSION

NAME = 'configobj'
MODULES = 'configobj', 'validate'
DESCRIPTION = 'Config file reading, writing, and validation.'
URL = 'http://www.voidspace.org.uk/python/configobj.html'
LICENSE = 'BSD'
PLATFORMS = ["Platform Independent"]

setup(name= NAME,
      version= VERSION,
      description= DESCRIPTION,
      license = LICENSE,
      platforms = PLATFORMS,
      author= 'Michael Foord & Nicola Larosa',
      author_email= 'fuzzyman@voidspace.org.uk',
      url= URL,
      py_modules = MODULES,
     )
