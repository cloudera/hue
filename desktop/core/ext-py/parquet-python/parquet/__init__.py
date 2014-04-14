import gzip
import json
import logging
import struct
import StringIO
import sys
from collections import defaultdict
from ttypes import (FileMetaData, CompressionCodec, Encoding,
                    FieldRepetitionType, PageHeader, PageType, Type)
from thrift.protocol import TCompactProtocol
from thrift.transport import TTransport
import encoding
import schema


logger = logging.getLogger("parquet")

try:
    import snappy
except ImportError:
    logger.warn(
        "Couldn't import snappy. Support for snappy compression disabled.")


class ParquetFormatException(Exception):
    pass


def _check_header_magic_bytes(fo):
    "Returns true if the file-like obj has the PAR1 magic bytes at the header"
    fo.seek(0, 0)
    magic = fo.read(4)
    return magic == 'PAR1'


def _check_footer_magic_bytes(fo):
    "Returns true if the file-like obj has the PAR1 magic bytes at the footer"
    fo.seek(-4, 2)  # seek to four bytes from the end of the file
    magic = fo.read(4)
    return magic == 'PAR1'


def _get_footer_size(fo):
    "Readers the footer size in bytes, which is serialized as little endian"
    fo.seek(-8, 2)
    tup = struct.unpack("<i", fo.read(4))
    return tup[0]


def _read_footer(fo):
    """Reads the footer from the given file object, returning a FileMetaData
    object. This method assumes that the fo references a valid parquet file"""
    footer_size = _get_footer_size(fo)
    logger.debug("Footer size in bytes: %s", footer_size)
    fo.seek(-(8 + footer_size), 2)  # seek to beginning of footer
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
        if not _check_header_magic_bytes(fo) or \
           not _check_footer_magic_bytes(fo):
            raise ParquetFormatException("{0} is not a valid parquet file "
                                         "(missing magic bytes)"
                                         .format(filename))
        return _read_footer(fo)


def _get_name(type_, value):
    """Returns the name for the given value of the given type_ unless value is
    None, in which case it returns empty string"""
    return type_._VALUES_TO_NAMES[value] if value is not None else "None"


def _get_offset(cmd):
    """Returns the offset into the cmd based upon if it's a dictionary page or
    a data page"""
    dict_offset = cmd.dictionary_page_offset
    data_offset = cmd.data_page_offset
    if dict_offset is None or data_offset < dict_offset:
        return data_offset
    return dict_offset


def dump_metadata(filename, show_row_group_metadata, out=sys.stdout):
    def println(value):
        out.write(value + "\n")
    footer = read_footer(filename)
    println("File Metadata: {0}".format(filename))
    println("  Version: {0}".format(footer.version))
    println("  Num Rows: {0}".format(footer.num_rows))
    println("  k/v metadata: ")
    if footer.key_value_metadata and len(footer.key_value_metadata) > 0:
        for kv in footer.key_value_metadata:
            println("    {0}={1}".format(kv.key, kv.value))
    else:
        println("    (none)")
    println("  schema: ")
    for se in footer.schema:
        println("    {name} ({type}): length={type_length}, "
                "repetition={repetition_type}, "
                "children={num_children}, "
                "converted_type={converted_type}".format(
                    name=se.name,
                    type=Type._VALUES_TO_NAMES[se.type] if se.type else None,
                    type_length=se.type_length,
                    repetition_type=_get_name(FieldRepetitionType,
                                              se.repetition_type),
                    num_children=se.num_children,
                    converted_type=se.converted_type))
    if show_row_group_metadata:
        println("  row groups: ")
        for rg in footer.row_groups:
            num_rows = rg.num_rows
            bytes = rg.total_byte_size
            println(
                "  rows={num_rows}, bytes={bytes}".format(num_rows=num_rows,
                                                          bytes=bytes))
            println("    chunks:")
            for cg in rg.columns:
                cmd = cg.meta_data
                println("      type={type} file_offset={offset} "
                        "compression={codec} "
                        "encodings={encodings} path_in_schema={path_in_schema} "
                        "num_values={num_values} uncompressed_bytes={raw_bytes} "
                        "compressed_bytes={compressed_bytes} "
                        "data_page_offset={data_page_offset} "
                        "dictionary_page_offset={dictionary_page_offset}".format(
                            type=_get_name(Type, cmd.type),
                            offset=cg.file_offset,
                            codec=_get_name(CompressionCodec, cmd.codec),
                            encodings=",".join(
                                [_get_name(
                                    Encoding, s) for s in cmd.encodings]),
                            path_in_schema=cmd.path_in_schema,
                            num_values=cmd.num_values,
                            raw_bytes=cmd.total_uncompressed_size,
                            compressed_bytes=cmd.total_compressed_size,
                            data_page_offset=cmd.data_page_offset,
                            dictionary_page_offset=cmd.dictionary_page_offset))
                with open(filename, 'rb') as fo:
                    offset = _get_offset(cmd)
                    fo.seek(offset, 0)
                    values_read = 0
                    println("      pages: ")
                    while values_read < num_rows:
                        ph = _read_page_header(fo)
                        # seek past current page.
                        fo.seek(ph.compressed_page_size, 1)
                        daph = ph.data_page_header
                        type_ = _get_name(PageType, ph.type)
                        raw_bytes = ph.uncompressed_page_size
                        num_values = None
                        if ph.type == PageType.DATA_PAGE:
                            num_values = daph.num_values
                            values_read += num_values
                        if ph.type == PageType.DICTIONARY_PAGE:
                            pass
                            #num_values = diph.num_values

                        encoding_type = None
                        def_level_encoding = None
                        rep_level_encoding = None
                        if daph:
                            encoding_type = _get_name(Encoding, daph.encoding)
                            def_level_encoding = _get_name(
                                Encoding, daph.definition_level_encoding)
                            rep_level_encoding = _get_name(
                                Encoding, daph.repetition_level_encoding)

                        println("        page header: type={type} "
                                "uncompressed_size={raw_bytes} "
                                "num_values={num_values} encoding={encoding} "
                                "def_level_encoding={def_level_encoding} "
                                "rep_level_encoding={rep_level_encoding}".format(
                                    type=type_,
                                    raw_bytes=raw_bytes,
                                    num_values=num_values,
                                    encoding=encoding_type,
                                    def_level_encoding=def_level_encoding,
                                    rep_level_encoding=rep_level_encoding))


def _read_page(fo, page_header, column_metadata):
    """Internal function to read the data page from the given file-object
    and convert it to raw, uncompressed bytes (if necessary)."""
    bytes_from_file = fo.read(page_header.compressed_page_size)
    codec = column_metadata.codec
    if codec is not None and codec != CompressionCodec.UNCOMPRESSED:
        if column_metadata.codec == CompressionCodec.SNAPPY:
            raw_bytes = snappy.decompress(bytes_from_file)
        elif column_metadata.codec == CompressionCodec.GZIP:
            io_obj = StringIO.StringIO(bytes_from_file)
            with gzip.GzipFile(fileobj=io_obj, mode='rb') as f:
                raw_bytes = f.read()
        else:
            raise ParquetFormatException(
                "Unsupported Codec: {0}".format(codec))
    else:
        raw_bytes = bytes_from_file
    logger.debug(
        "Read page with compression type {0}. Bytes {1} -> {2}".format(
        _get_name(CompressionCodec, codec),
        page_header.compressed_page_size,
        page_header.uncompressed_page_size))
    assert len(raw_bytes) == page_header.uncompressed_page_size, \
        "found {0} raw bytes (expected {1})".format(
            len(raw_bytes),
            page_header.uncompressed_page_size)
    return raw_bytes


def _read_data(fo, fo_encoding, value_count, bit_width):
    """Internal method to read data from the file-object using the given
    encoding. The data could be definition levels, repetition levels, or
    actual values.
    """
    vals = []
    if fo_encoding == Encoding.RLE:
        seen = 0
        while seen < value_count:
            values = encoding.read_rle_bit_packed_hybrid(fo, bit_width)
            if values is None:
                break  # EOF was reached.
            vals += values
            seen += len(values)
    elif fo_encoding == Encoding.BIT_PACKED:
        raise NotImplementedError("Bit packing not yet supported")

    return vals


def read_data_page(fo, schema_helper, page_header, column_metadata,
                   dictionary):
    """Reads the datapage from the given file-like object based upon the
    metadata in the schema_helper, page_header, column_metadata, and
    (optional) dictionary. Returns a list of values.
    """
    daph = page_header.data_page_header
    raw_bytes = _read_page(fo, page_header, column_metadata)
    io_obj = StringIO.StringIO(raw_bytes)
    vals = []

    logger.debug("  definition_level_encoding: %s",
                 _get_name(Encoding, daph.definition_level_encoding))
    logger.debug("  repetition_level_encoding: %s",
                 _get_name(Encoding, daph.repetition_level_encoding))
    logger.debug("  encoding: %s", _get_name(Encoding, daph.encoding))

    # definition levels are skipped if data is required.
    if not schema_helper.is_required(column_metadata.path_in_schema[-1]):
        max_definition_level = schema_helper.max_definition_level(
            column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_definition_level)
        logger.debug("  max def level: %s   bit_width: %s",
                     max_definition_level, bit_width)
        if bit_width == 0:
            definition_levels = [0] * daph.num_values
        else:
            definition_levels = _read_data(io_obj,
                                           daph.definition_level_encoding,
                                           daph.num_values,
                                           bit_width)

        logger.debug("  Definition levels: %s",
                     ",".join([str(dl) for dl in definition_levels]))

    # repetition levels are skipped if data is at the first level.
    if len(column_metadata.path_in_schema) > 1:
        max_repetition_level = schema_helper.max_repetition_level(
            column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_repetition_level)
        repetition_levels = _read_data(io_obj,
                                       daph.repetition_level_encoding,
                                       daph.num_values)

    # TODO Actually use the definition and repetition levels.

    if daph.encoding == Encoding.PLAIN:
        for i in range(daph.num_values):
            vals.append(
                encoding.read_plain(io_obj, column_metadata.type, None))
        logger.debug("  Values: %s", ",".join([str(x) for x in vals]))
    elif daph.encoding == Encoding.PLAIN_DICTIONARY:
        # bit_width is stored as single byte.
        bit_width = struct.unpack("<B", io_obj.read(1))[0]
        logger.debug("bit_width: %d", bit_width)
        total_seen = 0
        dict_values_bytes = io_obj.read()
        dict_values_io_obj = StringIO.StringIO(dict_values_bytes)
        # TODO jcrobak -- not sure that this loop is needed?
        while total_seen < daph.num_values:
            values = encoding.read_rle_bit_packed_hybrid(
                dict_values_io_obj, bit_width, len(dict_values_bytes))
            vals += [dictionary[v] for v in values]
            total_seen += len(values)
    else:
        raise ParquetFormatException("Unsupported encoding: %s",
                                     _get_name(Encoding, daph.encoding))
    return vals


def read_dictionary_page(fo, page_header, column_metadata):
    raw_bytes = _read_page(fo, page_header, column_metadata)
    io_obj = StringIO.StringIO(raw_bytes)
    dict_items = []
    while io_obj.tell() < len(raw_bytes):
        # TODO - length for fixed byte array
        dict_items.append(
            encoding.read_plain(io_obj, column_metadata.type, None))
    return dict_items


def _dump(fo, options, out=sys.stdout):
    def println(value):
        out.write(value + "\n")

    footer = _read_footer(fo)
    schema_helper = schema.SchemaHelper(footer.schema)
    total_count = 0
    for rg in footer.row_groups:
        res = defaultdict(list)
        row_group_rows = rg.num_rows
        for idx, cg in enumerate(rg.columns):
            dict_items = []
            cmd = cg.meta_data
            # skip if the list of columns is specified and this isn't in it
            if options.col and not ".".join(cmd.path_in_schema) in options.col:
                continue

            offset = _get_offset(cmd)
            fo.seek(offset, 0)
            values_seen = 0
            logger.debug("reading column chunk of type: %s",
                         _get_name(Type, cmd.type))
            while values_seen < row_group_rows:
                ph = _read_page_header(fo)
                logger.debug("Reading page (type=%s, "
                             "uncompressed=%s bytes, "
                             "compressed=%s bytes)",
                             _get_name(PageType, ph.type),
                             ph.uncompressed_page_size,
                             ph.compressed_page_size)

                if ph.type == PageType.DATA_PAGE:
                    values = read_data_page(fo, schema_helper, ph, cmd,
                                            dict_items)
                    res[".".join(cmd.path_in_schema)] += values
                    values_seen += cmd.num_values
                elif ph.type == PageType.DICTIONARY_PAGE:
                    logger.debug(ph)
                    assert dict_items == []
                    dict_items = read_dictionary_page(fo, ph, cmd)
                    logger.debug("Dictionary: %s", str(dict_items))
                else:
                    logger.warn("Skipping unknown page type={0}".format(
                        _get_name(PageType, ph.type)))
        keys = options.col if options.col else [s.name for s in
                                                footer.schema if s.name in res]
        if options.format == "csv" and not options.no_headers:
            println("\t".join(keys))
        for i in range(rg.num_rows):
            if options.limit != -1 and i + total_count >= options.limit:
                return
            if options.format == "csv":
                println("\t".join(str(res[k][i]) for k in keys))
            elif options.format == "json":
                println(json.dumps(dict([(k, res[k][i]) for k in keys])))
        total_count += rg.num_rows


def dump(filename, options, out=sys.stdout):
    with open(filename, 'rb') as fo:
        return _dump(fo, options=options, out=out)
