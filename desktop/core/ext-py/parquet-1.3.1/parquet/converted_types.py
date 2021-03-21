# -#- coding: utf-8 -#-
"""
Deal with parquet logical types (aka converted types), higher-order things built from primitive types.

The implementations in this class are pure python for the widest compatibility,
but they're not necessarily the most performant.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import codecs
import datetime
import json
import logging
import os
import struct
import sys
from decimal import Decimal

import thriftpy2 as thriftpy

THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name=str("parquet_thrift"))  # pylint: disable=invalid-name

logger = logging.getLogger('parquet')  # pylint: disable=invalid-name

bson = None  # pylint: disable=invalid-name
try:
    import bson
except ImportError:
    pass

PY3 = sys.version_info.major > 2

# define bytes->int for non 2, 4, 8 byte ints
if PY3:
    def intbig(data):
        """Convert big ints using python 3's built-in support."""
        return int.from_bytes(data, 'big', signed=True)
else:
    def intbig(data):
        """Convert big ints using a hack of encoding bytes as hex and decoding to int."""
        return int(codecs.encode(data, 'hex'), 16)

DAYS_TO_MILLIS = 86400000000000
"""Number of millis in a day. Used to convert a Date to a date"""


def _convert_unsigned(data, fmt):
    """Convert data from signed to unsigned in bulk."""
    num = len(data)
    return struct.unpack(
        "{}{}".format(num, fmt.upper()).encode("utf-8"),
        struct.pack("{}{}".format(num, fmt).encode("utf-8"), *data)
    )


def convert_column(data, schemae):
    """Convert known types from primitive to rich."""
    ctype = schemae.converted_type
    if ctype == parquet_thrift.ConvertedType.DECIMAL:
        scale_factor = Decimal("10e-{}".format(schemae.scale))
        if schemae.type == parquet_thrift.Type.INT32 or schemae.type == parquet_thrift.Type.INT64:
            return [Decimal(unscaled) * scale_factor for unscaled in data]
        return [Decimal(intbig(unscaled)) * scale_factor for unscaled in data]
    if ctype == parquet_thrift.ConvertedType.DATE:
        return [datetime.date.fromordinal(d) for d in data]
    if ctype == parquet_thrift.ConvertedType.TIME_MILLIS:
        return [datetime.timedelta(milliseconds=d) for d in data]
    if ctype == parquet_thrift.ConvertedType.TIMESTAMP_MILLIS:
        return [datetime.datetime.utcfromtimestamp(d / 1000.0) for d in data]
    if ctype == parquet_thrift.ConvertedType.UTF8:
        return [codecs.decode(item, "utf-8") for item in data]
    if ctype == parquet_thrift.ConvertedType.UINT_8:
        return _convert_unsigned(data, 'b')
    if ctype == parquet_thrift.ConvertedType.UINT_16:
        return _convert_unsigned(data, 'h')
    if ctype == parquet_thrift.ConvertedType.UINT_32:
        return _convert_unsigned(data, 'i')
    if ctype == parquet_thrift.ConvertedType.UINT_64:
        return _convert_unsigned(data, 'q')
    if ctype == parquet_thrift.ConvertedType.JSON:
        return [json.loads(s) for s in codecs.iterdecode(data, "utf-8")]
    if ctype == parquet_thrift.ConvertedType.BSON and bson:
        return [bson.BSON(s).decode() for s in data]

    logger.info("Converted type '%s'' not handled",
                parquet_thrift.ConvertedType._VALUES_TO_NAMES[ctype])  # pylint:disable=protected-access
    return data
