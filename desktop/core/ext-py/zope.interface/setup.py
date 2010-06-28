##############################################################################
#
# Copyright (c) 2004-2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for zope.interface package

$Id: setup.py 101374 2009-07-01 15:55:00Z fdrake $
"""

import os, sys

from distutils.errors import (CCompilerError, DistutilsExecError, 
                              DistutilsPlatformError)

try:
    from setuptools import setup, Extension, Feature
    from setuptools.command.build_ext import build_ext
except ImportError, e:
    # do we need to support plain distutils for building when even
    # the package itself requires setuptools for installing?
    from distutils.core import setup, Extension
    from distutils.command.build_ext import build_ext

    if sys.version_info[:2] >= (2, 4):
        extra = dict(
            package_data={
                'zope.interface': ['*.txt'],
                'zope.interface.tests': ['*.txt'],
                }
            )
    else:
        extra = {}

else:
    codeoptimization = Feature("Optional code optimizations",
                               standard = True,
                               ext_modules = [Extension(
                                             "zope.interface._zope_interface_coptimizations",
                                             [os.path.normcase(
                                             os.path.join('src', 'zope',
                                             'interface',
                                             '_zope_interface_coptimizations.c')
                                             )]
                                             )])
    extra = dict(
        namespace_packages=["zope"],
        include_package_data = True,
        zip_safe = False,
        tests_require = ['zope.testing'],
        install_requires = ['setuptools'],
        extras_require={'docs': ['z3c.recipe.sphinxdoc']},
        features = {'codeoptimization': codeoptimization}
        )

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n.. contents::\n\n' +
        read('src', 'zope', 'interface', 'README.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'adapter.txt')
        + '\n' +
        read('src', 'zope', 'interface', 'human.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '********\n'
        )


class optional_build_ext(build_ext):
    """This class subclasses build_ext and allows
       the building of C extensions to fail.
    """
    def run(self):
        try:
            build_ext.run(self)
        
        except DistutilsPlatformError, e:
            self._unavailable(e)

    def build_extension(self, ext):
       try:
           build_ext.build_extension(self, ext)
        
       except (CCompilerError, DistutilsExecError), e:
           self._unavailable(e)

    def _unavailable(self, e):
        print >> sys.stderr, '*' * 80
        print >> sys.stderr, """WARNING:

        An optional code optimization (C extension) could not be compiled.

        Optimizations for this package will not be available!"""
        print >> sys.stderr
        print >> sys.stderr, e
        print >> sys.stderr, '*' * 80
    


setup(name='zope.interface',
      version = '3.5.2',
      url='http://pypi.python.org/pypi/zope.interface',
      license='ZPL 2.1',
      description='Interfaces for Python',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=long_description,

      packages = ['zope', 'zope.interface'],
      package_dir = {'': 'src'},
      cmdclass = {'build_ext': optional_build_ext},
      **extra)
