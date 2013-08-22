import struct
import thrift
import logging
from ttypes import FileMetaData
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport

logger = logging.getLogger("parquet")

def _check_header_magic_bytes(fo):
    """Returns true if the file-like obj has the PAR1 magic bytes at the header"""
    fo.seek(0, 0)
    magic = fo.read(4)
    return magic == 'PAR1'

def _check_footer_magic_bytes(fo):
    """Returns true if the file-like obj has the PAR1 magic bytes at the footer"""
    fo.seek(-4, 2)  # seek to four bytes from the end of the file
    magic = fo.read(4)
    return magic == 'PAR1'


def _get_footer_size(fo):
    """Readers the footer size in bytes, which is serialized as little endian"""
    fo.seek(-8, 2)
    tup = struct.unpack("<i", fo.read(4))
    return tup[0]

def _read_footer(fo):
    """Reads the footer from the given file object, returning a FileMetaData object. This method
    assumes that the fo references a valid parquet file"""
    footer_size = _get_footer_size(fo)
    logger.debug("Footer size in bytes: %s", footer_size)
    fo.seek(-(8+footer_size), 2)  # seek to beginning of footer
    tin = TTransport.TFileObjectTransport(fo)
    pin = TCompactProtocol.TCompactProtocol(tin)
    fmd = FileMetaData()
    fmd.read(pin)
    return fmd

def read_footer(filename):
    with open(filename, 'rb') as fo:
        if not _check_header_magic_bytes(fo) or not _check_footer_magic_bytes(fo):
            raise ParquetFormatException("%s is not a valid parquet file (missing magic bytes".format(filename))
        return _read_footer(fo)