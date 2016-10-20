"""thrift_filetransport.py - read thrift encoded data from a file object."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from thriftpy.transport import TTransportBase


class TFileTransport(TTransportBase):  # pylint: disable=too-few-public-methods
    """TTransportBase implementation for decoding data from a file object."""

    def __init__(self, fo):
        """Initialize with `fo`, the file object to read from."""
        self._fo = fo
        self._pos = fo.tell()

    def _read(self, sz):
        """Read data `sz` bytes."""
        return self._fo.read(sz)
