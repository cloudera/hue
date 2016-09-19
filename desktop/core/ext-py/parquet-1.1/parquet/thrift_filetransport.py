from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from thriftpy.transport import TTransportBase

class TFileTransport(TTransportBase):

    def __init__(self, fo):
        """fo -- the file object to read from"""
        self._fo = fo
        self._pos = fo.tell()

    def _read(self, sz):
        return self._fo.read(sz)