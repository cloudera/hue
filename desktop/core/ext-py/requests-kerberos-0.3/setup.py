#!/usr/bin/env python
# coding: utf-8
import os
from setuptools import setup

import compiler

with open('requirements.txt') as requirements:
    requires = [line.strip() for line in requirements if line.strip()]

path = os.path.dirname(__file__)
desc_fd = os.path.join(path, 'README.rst')
hist_fd = os.path.join(path, 'HISTORY.rst')

long_desc = ''
short_desc = 'A Kerberos authentication handler for python-requests'

if os.path.isfile(desc_fd):
    long_desc = open(desc_fd).read()

if os.path.isfile(hist_fd):
    long_desc = '\n\n'.join([long_desc, open(hist_fd).read()])

# It seems like per the requests module, we'd like to get the version
# from __init__.py however, __init__.py will import the kerberos
# module.  The kerberos module may not be installed - and when it's
# not, it's pulled in by the requirements.txt.  When it's being
# installed, however, this setup.py is evaluated before the
# kerberos.so module is built and installed, and this bombs.
#
# To fix this, we can use the compiler module to parse __init__.py,
# and as long as __version__ is defined as a constant so that we
# don't have to evaluate it to get the value, we can do some dubious
# groping arond the AST and get the version from that
parsed = compiler.parseFile('requests_kerberos/__init__.py')    
for n in parsed.getChildNodes()[0]:
    if 'nodes' in dir(n): 
        if n.nodes[0].name == '__version__':
            my_version = n.expr.value        
    
setup(
    name='requests-kerberos',
    description=short_desc,
    long_description=long_desc,
    url='https://github.com/requests/requests-kerberos',
    packages=['requests_kerberos'],
    package_data={'': ['LICENSE', 'AUTHORS']},
    include_package_data=True,
    version = my_version,
    install_requires=requires,
)
