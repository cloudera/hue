#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2006-2009 Søren Roug, European Environment Agency
#
# This is free software.  You may redistribute it under the terms
# of the Apache license and the GNU General Public License Version
# 2 or at your option any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

import platform
from setuptools import setup

version = '1.4.0'

if platform.system() in ('Linux','Unix'):
    man1pages = [('share/man/man1', [
           'csv2ods/csv2ods.1',
           'mailodf/mailodf.1',
           'odf2xhtml/odf2xhtml.1',
           'odf2mht/odf2mht.1',
           'odf2xml/odf2xml.1',
           'odfimgimport/odfimgimport.1',
           'odflint/odflint.1',
           'odfmeta/odfmeta.1',
           'odfoutline/odfoutline.1',
           'odfuserfield/odfuserfield.1',
           'xml2odf/xml2odf.1'])]
else:
    man1pages = []
# Currently no other data files to add
datafiles = [] + man1pages

setup(name='odfpy',
      version=version,
      classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      description='Python API and tools to manipulate OpenDocument files',
      long_description = (
"""
Odfpy is a library to read and write OpenDocument v. 1.2 files.
The main focus has been to prevent the programmer from creating invalid
documents. It has checks that raise an exception if the programmer adds
an invalid element, adds an attribute unknown to the grammar, forgets to
add a required attribute or adds text to an element that doesn't allow it.

These checks and the API itself were generated from the RelaxNG
schema, and then hand-edited. Therefore the API is complete and can
handle all ODF constructions.

In addition to the API, there are a few scripts:

- csv2odf - Create OpenDocument spreadsheet from comma separated values
- mailodf - Email ODF file as HTML archive
- odf2xhtml - Convert ODF to (X)HTML
- odf2mht - Convert ODF to HTML archive
- odf2xml - Create OpenDocument XML file from OD? package
- odfimgimport - Import external images
- odflint - Check ODF file for problems
- odfmeta - List or change the metadata of an ODF file
- odfoutline - Show outline of OpenDocument
- odfuserfield - List or change the user-field declarations in an ODF file
- xml2odf - Create OD? package from OpenDocument in XML form

The source code is at https://github.com/eea/odfpy

Visit https://github.com/eea/odfpy/wiki for documentation and examples.

The code at https://joinup.ec.europa.eu/software/odfpy/home is obsolete."""
),
      author='Soren Roug',
      author_email='soren.roug@eea.europa.eu',
      url='https://github.com/eea/odfpy',
      packages=['odf'],
      scripts=[
          'csv2ods/csv2ods',
          'mailodf/mailodf',
          'odf2xhtml/odf2xhtml',
          'odf2mht/odf2mht',
          'odf2xml/odf2xml',
          'odfimgimport/odfimgimport',
          'odflint/odflint',
          'odfmeta/odfmeta',
          'odfoutline/odfoutline',
          'odfuserfield/odfuserfield',
          'xml2odf/xml2odf'],
      data_files=datafiles,
      install_requires=['defusedxml', ]
      )
