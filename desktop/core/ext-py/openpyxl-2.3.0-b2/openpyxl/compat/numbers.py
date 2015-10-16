from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

try:
    # Python 2
    long = long
except NameError:
    # Python 3
    long = int

from decimal import Decimal

NUMERIC_TYPES = (int, float, long, Decimal)

