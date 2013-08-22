import struct
import thrift
import logging
from ttypes import FileMetaData, CompressionCodec, Encoding, PageHeader, PageType, Type
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport

logger = logging.getLogger("parquet")

class ParquetFormatException(Exception):
    pass

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


def _read_page_header(fo, offset):
    """Reads the page_header at the given offset"""
    fo.seek(offset, 0)
    tin = TTransport.TFileObjectTransport(fo)
    pin = TCompactProtocol.TCompactProtocol(tin)
    ph = PageHeader()
    ph.read(pin)
    return ph

def read_footer(filename):
    """Reads and returns the FileMetaData object for the given file."""
    with open(filename, 'rb') as fo:
        if not _check_header_magic_bytes(fo) or not _check_footer_magic_bytes(fo):
            raise ParquetFormatException("{0} is not a valid parquet file (missing magic bytes)".format(filename))
        return _read_footer(fo)


def dump_metadata(filename):
    footer = read_footer(filename)
    print("File: {0}".format(filename))
    print("  version: {0}".format(footer.version))
    print("  num rows: {0}".format(footer.num_rows))
    print("  k/v metadata: ")
    if footer.key_value_metadata and len(footer.key_value_metadata) > 0:
        for kv in footer.key_value_metadata:
            print("    {0}={1}".format(kv.key, kv.value)) 
    else:
        print("    (none)")
    print("  schema: ")
    for se in footer.schema:
        print("    {name} ({type}): length={type_length}, repetition={repetition_type}, children={num_children}, converted_type={converted_type}".format(
            name=se.name, type=Type._VALUES_TO_NAMES[se.type] if se.type else None, type_length=se.type_length, repetition_type=se.repetition_type,
            num_children=se.num_children, converted_type=se.converted_type))
    print("  row groups: ")
    for rg in footer.row_groups:
        num_rows = rg.num_rows
        bytes = rg.total_byte_size
        print("  rows={num_rows}, bytes={bytes}".format(num_rows=num_rows, bytes=bytes))
        print("    chunks:")
        for cg in rg.columns:
            cmd = cg.meta_data
            print("      type={type} file_offset={offset} compression={codec} "
                  "encodings={encodings} path_in_schema={path_in_schema} "
                  "num_values={num_values} uncompressed_bytes={raw_bytes} "
                  "compressed_bytes={compressed_bytes} data_page_offset={data_page_offset} "
                  "dictionary_page_offset={dictionary_page_offset}".format(
                    type=cmd.type, offset=cg.file_offset, codec=CompressionCodec._VALUES_TO_NAMES[cmd.codec],
                    encodings=",".join([Encoding._VALUES_TO_NAMES[s] for s in cmd.encodings]),
                    path_in_schema=cmd.path_in_schema, num_values=cmd.num_values,
                    raw_bytes=cmd.total_uncompressed_size, compressed_bytes=cmd.total_compressed_size,
                    data_page_offset=cmd.data_page_offset, dictionary_page_offset=cmd.dictionary_page_offset
                    ))
            with open(filename, 'rb') as fo:
                offset = cmd.data_page_offset if (cmd.dictionary_page_offset is None or cmd.data_page_offset < cmd.dictionary_page_offset) else cmd.dictionary_page_offset
                values_read = 0
                print("      pages: ")
                while values_read < num_rows:
                    ph = _read_page_header(fo, offset)
                    daph = ph.data_page_header
                    diph = ph.dictionary_page_header
                    type_ = PageType._VALUES_TO_NAMES[ph.type] if ph.type else None
                    raw_bytes = ph.uncompressed_page_size
                    num_values = None
                    if ph.type == PageType.DATA_PAGE:
                        num_values = daph.num_values
                        values_read += num_values
                    if ph.type == PageType.DICTIONARY_PAGE:
                        num_values = diph.num_values

                    encoding = None
                    def_level_encoding = None
                    rep_level_encoding = None
                    if daph:
                        encoding = Encoding._VALUES_TO_NAMES[daph.encoding]
                        def_level_encoding = Encoding._VALUES_TO_NAMES[daph.definition_level_encoding]
                        rep_level_encoding = Encoding._VALUES_TO_NAMES[daph.repetition_level_encoding]

                    print("        page header: type={type} uncompressed_size={raw_bytes} "
                          "num_values={num_values} encoding={encoding} "
                          "def_level_encoding={def_level_encoding} "
                          "rep_level_encoding={rep_level_encoding}".format(
                            type=type_, raw_bytes=raw_bytes, num_values=num_values,
                            encoding=encoding, def_level_encoding=def_level_encoding,
                            rep_level_encoding=rep_level_encoding))

