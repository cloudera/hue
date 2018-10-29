#!/usr/bin/env python
"""
pasteurize.py
=============

This script is only used by the unit tests. Another script called "pasteurize"
is created automatically (without the .py extension) by setuptools.

pasteurize.py attempts to turn Py3 code into relatively clean Py3 code that is
also compatible with Py2 when using the ``future`` package.


Licensing
---------
Copyright 2013-2016 Python Charmers Pty Ltd, Australia.
The software is distributed under an MIT licence. See LICENSE.txt.
"""

import sys

from libpasteurize.main import main

sys.exit(main())
