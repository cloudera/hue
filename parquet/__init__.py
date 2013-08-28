import gzip
import json
import logging
import struct
import thrift
import StringIO
from collections import defaultdict
from ttypes import FileMetaData, CompressionCodec, Encoding, FieldRepetitionType, PageHeader, PageType, Type
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport
import encoding
import schema


logger = logging.getLogger("parquet")

try:
    import snappy
except ImportError:
    logger.warn("Couldn't import snappy. Support for snappy compression disabled.")

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


def _read_page_header(fo):
    """Reads the page_header from the given fo"""
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
            name=se.name, type=Type._VALUES_TO_NAMES[se.type] if se.type else None, type_length=se.type_length,
            repetition_type=FieldRepetitionType._VALUES_TO_NAMES[se.repetition_type] if se.repetition_type else None,
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
                fo.seek(offset, 0)
                values_read = 0
                print("      pages: ")
                while values_read < num_rows:
                    ph = _read_page_header(fo)
                    fo.seek(ph.compressed_page_size, 1) # seek past current page.
                    daph = ph.data_page_header
                    diph = ph.dictionary_page_header
                    type_ = PageType._VALUES_TO_NAMES[ph.type] if ph.type else None
                    raw_bytes = ph.uncompressed_page_size
                    num_values = None
                    if ph.type == PageType.DATA_PAGE:
                        num_values = daph.num_values
                        values_read += num_values
                    if ph.type == PageType.DICTIONARY_PAGE:
                        pass
                        #num_values = diph.num_values

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

def _read_page(fo, page_header, column_metadata):
    """Reads the data page from the given file-object using the column metadata"""
    bytes_from_file = fo.read(page_header.compressed_page_size)
    if column_metadata.codec is not None and column_metadata.codec != CompressionCodec.UNCOMPRESSED:
        if column_metadata.codec == CompressionCodec.SNAPPY:
            raw_bytes = snappy.decompress(bytes_from_file)
        elif column_metadata.codec == CompressionCodec.GZIP:
            io_obj = StringIO.StringIO(bytes_from_file)
            with gzip.GzipFile(fileobj=io_obj, mode='rb') as f:
                raw_bytes = f.read()
    else:
        raw_bytes = bytes_from_file
    return raw_bytes


def _read_data(fo, fo_encoding, value_count, bit_width):
    """Internal method to read data from the file-object using the given encoding. The data
    could be definition levels, repetition levels, or actual values."""
    vals = []
    if fo_encoding == Encoding.RLE:
        seen = 0
        while seen < value_count:
            values = encoding.read_rle_bit_packed_hybrid(fo, bit_width)
            if values is None:
                break  ## EOF was reached.
            vals += values
            seen += len(values)
    elif fo_encoding == Encoding.BIT_PACKED:
        raise NotImplementedError("Bit packing not yet supported")

    return vals


def read_data_page(fo, schema_helper, page_header, column_metadata, dictionary):
    daph = page_header.data_page_header
    raw_bytes = _read_page(fo, page_header, column_metadata)
    io_obj = StringIO.StringIO(raw_bytes)
    vals = []

    print("  definition_level_encoding: {0}".format(Encoding._VALUES_TO_NAMES[daph.definition_level_encoding]))
    print("  repetition_level_encoding: {0}".format(Encoding._VALUES_TO_NAMES[daph.repetition_level_encoding]))
    print("  encoding: {0}".format(Encoding._VALUES_TO_NAMES[daph.encoding]) )

    # definition levels are skipped if data is required.
    if not schema_helper.is_required(column_metadata.path_in_schema[-1]):
        max_definition_level = schema_helper.max_definition_level(column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_definition_level) # TODO Where does the -1 come from?
        print "  max def level: {1}   bit_width: {0}".format(bit_width, max_definition_level)
        if bit_width == 0:
            definition_levels = [0] * daph.num_values
        else:
            definition_levels = _read_data(io_obj, daph.definition_level_encoding, daph.num_values, bit_width)

        print ("  Definition levels: {0}".format(",".join([str(dl) for dl in definition_levels])))
    
    # repetition levels are skipped if data is at the first level.
    if len(column_metadata.path_in_schema) > 1:
        max_repetition_level = schema_helper.max_repetition_level(column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_repetition_level)
        repetition_levels = _read_data(io_obj, daph.repetition_level_encoding, daph.num_values)

    # TODO Actually use the definition and repetition levels.

    if daph.encoding == Encoding.PLAIN:
        for i in range(daph.num_values):
            vals.append(encoding.read_plain(io_obj, column_metadata.type, None))
        print "  Values: " + ",".join([str(x) for x in vals])
    elif daph.encoding == Encoding.PLAIN_DICTIONARY:
        bit_width = struct.unpack("<B", io_obj.read(1))[0]  # bitwidth is stored as single byte.
        print "bit_width: {0}".format(bit_width)
        total_seen = 0
        dict_values_bytes = io_obj.read()
        dict_values_io_obj = StringIO.StringIO(dict_values_bytes)
        while total_seen < daph.num_values:  # TODO jcrobak -- not sure that this loop i sneeded?
            values = encoding.read_rle_bit_packed_hybrid(dict_values_io_obj, bit_width, len(dict_values_bytes))
            vals += [dictionary[v] for v in values]
            total_seen += len(values)
    else:
        raise ParquetFormatException("Unsupported encoding: " + Encoding._VALUES_TO_NAMES[daph.encoding])
    return vals


def read_dictionary_page(fo, page_header, column_metadata):
    raw_bytes = _read_page(fo, page_header, column_metadata)
    io_obj = StringIO.StringIO(raw_bytes)
    dict_items = []
    while io_obj.tell() < len(raw_bytes):
        dict_items.append(encoding.read_plain(io_obj, column_metadata.type, None))  # TODO - length for fixed byte array
    return dict_items


def dump(filename, max_records=10):
    footer = read_footer(filename)
    schema_helper = schema.SchemaHelper(footer.schema)
    for rg in footer.row_groups:
        res = defaultdict(list)
        row_group_rows = rg.num_rows
        dict_items = []
        for idx, cg in enumerate(rg.columns):
            cmd = cg.meta_data
            with open(filename, 'rb') as fo:
                offset = cmd.data_page_offset if (cmd.dictionary_page_offset is None or cmd.data_page_offset < cmd.dictionary_page_offset) else cmd.dictionary_page_offset
                fo.seek(offset, 0)
                values_seen = 0
                print("reading column chunk of type: {0}".format(Type._VALUES_TO_NAMES[cmd.type]))
                while values_seen < row_group_rows:
                    ph = _read_page_header(fo)
                    print("Reading page (type={2}, uncompressed={0} bytes, compressed={1} bytes)".format(
                        ph.uncompressed_page_size, ph.compressed_page_size, PageType._VALUES_TO_NAMES[ph.type]))
                    daph = ph.data_page_header
                    diph = ph.dictionary_page_header
                    if ph.type == PageType.DATA_PAGE:
                        values = read_data_page(fo, schema_helper, ph, cmd, dict_items)
                        res[".".join(cmd.path_in_schema)] += values
                        values_seen += cmd.num_values
                    elif ph.type == PageType.DICTIONARY_PAGE:
                        print ph
                        assert dict_items == []
                        dict_items = read_dictionary_page(fo, ph, cmd)
                        print("Dictionary: " + str(dict_items))
                    else:
                        logger.info("Skipping unknown page type={0}".format(ph.type))
        print "Data for row group: "
        keys = res.keys()
        print "\t".join(keys)
        for i in range(rg.num_rows):
            print "\t".join(str(res[k][i]) for k in keys)
