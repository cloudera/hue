# -#- coding: utf-8 -#-
"""
Deal with parquet logical types (aka converted types), higher-order
things built from primitive types.

The implementations in this class are pure python for the widest compatibility,
but they're not necessarily the most performant.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import datetime
import logging
import json
import os
import struct
import sys
from decimal import Decimal

import thriftpy

THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name=str("parquet_thrift"))

logger = logging.getLogger('parquet')

bson = None
try:
    import bson
except ImportError:
    pass

PY3 = sys.version_info.major > 2

# define bytes->int for non 2, 4, 8 byte ints
if PY3:
    intbig = lambda x: int.from_bytes(x, 'big', signed=True)
else:
    intbig = lambda x: int(codecs.encode(x, 'hex'), 16)

DAYS_TO_MILLIS = 86400000000000
"""Number of millis in a day. Used to convert a Date to a date"""


def convert_unsigned(data, fmt):
    num = len(data)
    return struct.unpack(
        "{}{}".format(num, fmt.upper()),
        struct.pack("{}{}".format(num, fmt), *data)
        )

def convert_column(data, schemae):
    """Convert known types from primitive to rich."""
    ctype = schemae.converted_type
    if ctype == parquet_thrift.ConvertedType.DECIMAL:
        scale_factor = Decimal("10e-{}".format(schemae.scale))
        if schemae.type == parquet_thrift.Type.INT32 or schemae.type == parquet_thrift.Type.INT64:
            return [Decimal(unscaled) * scale_factor for unscaled in data]
        return [Decimal(intbig(unscaled)) * scale_factor for unscaled in data]
    elif ctype == parquet_thrift.ConvertedType.DATE:
        return [datetime.date.fromordinal(d) for d in data]
    elif ctype == parquet_thrift.ConvertedType.TIME_MILLIS:
        return [datetime.timedelta(milliseconds=d) for d in data]
    elif ctype == parquet_thrift.ConvertedType.TIMESTAMP_MILLIS:
        return [datetime.datetime.utcfromtimestamp(d/1000.0) for d in data]
    elif ctype == parquet_thrift.ConvertedType.UTF8:
        return list(codecs.iterdecode(data, "utf-8"))
    elif ctype == parquet_thrift.ConvertedType.UINT_8:
        return convert_unsigned(data, 'b')
    elif ctype == parquet_thrift.ConvertedType.UINT_16:
        return convert_unsigned(data, 'h')
    elif ctype == parquet_thrift.ConvertedType.UINT_32:
        return convert_unsigned(data, 'i')
    elif ctype == parquet_thrift.ConvertedType.UINT_64:
        return convert_unsigned(data, 'q')
    elif ctype == parquet_thrift.ConvertedType.JSON:
        return [json.loads(s) for s in codecs.iterdecode(data, "utf-8")]
    elif ctype == parquet_thrift.ConvertedType.BSON and bson:
        return [bson.BSON(s).decode() for s in data]
    else:
        logger.warn("Converted type '{}'' not handled".format(
            parquet_thrift.ConvertedType._VALUES_TO_NAMES[ctype]))
    return data