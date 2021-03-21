"""thrift_filetransport.py - read thrift encoded data from a file object."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from thriftpy2.transport import TTransportBase


class TFileTransport(TTransportBase):  # pylint: disable=too-few-public-methods
    """TTransportBase implementation for decoding data from a file object."""

    def __init__(self, fo):
        """Initialize with `fo`, the file object to read from."""
        self._fo = fo
        self._pos = fo.tell()

    def _read(self, sz):
        """Read data `sz` bytes."""
        return self._fo.read(sz)

    def open(self):
        """Open which is a no-op."""
        if not self.is_open():
            raise ValueError("Already closed.")

    def is_open(self):
        """Return true if open."""
        return not self._fo.closed

    def close(self):
        """Close the file object."""
        self._fo.close()

    def read(self, sz):
        """Read data `sz` bytes."""
        return self._fo.read(sz)

    def write(self, buf):
        """Write buf to the file object."""
        self._fo.write(buf)

    def flush(self):
        """Flush the output."""
        self._fo.flush()
