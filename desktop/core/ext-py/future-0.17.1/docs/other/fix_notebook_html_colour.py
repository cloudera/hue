#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to re-enable colour in .html files produced from IPython notebooks.

Based on a script in a GitHub gist with this copyright notice:

#----------------------------------------------------------------------------
# Copyright (c) 2013 - Damián Avila
#
# Distributed under the terms of the Modified BSD License.
#
# A little snippet to fix @media print issue printing slides from IPython
#-----------------------------------------------------------------------------
"""

import io
import sys

notebook = sys.argv[1]
assert notebook.endswith('.html')
# notebook = 'jevans.ipynb'
path = notebook[:-5] + '.html'
flag = u'@media print{*{text-shadow:none !important;color:#000 !important'

with io.open(path, 'r') as in_file:
    data = in_file.readlines()
    for i, line in enumerate(data):
        if line[:64] == flag:
            data[i] = data[i].replace('color:#000 !important;', '')

with io.open(path, 'w') as out_file:
    out_file.writelines(data)

print("You can now print your slides")
