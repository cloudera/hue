"""parquet - read parquet files."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import gzip
import io
import json
import logging
import os
import struct
import sys
from collections import OrderedDict, defaultdict

import thriftpy2 as thriftpy
from thriftpy2.protocol.compact import TCompactProtocolFactory

from . import encoding, schema
from .converted_types import convert_column
from .thrift_filetransport import TFileTransport

PY3 = sys.version_info > (3,)

if PY3:
    import csv
else:
    from backports import csv  # pylint: disable=import-error

THRIFT_FILE = os.path.join(os.path.dirname(__file__), "parquet.thrift")
parquet_thrift = thriftpy.load(THRIFT_FILE, module_name="parquet_thrift")  # pylint: disable=invalid-name


logger = logging.getLogger("parquet")  # pylint: disable=invalid-name

try:
    import snappy
except ImportError:
    logger.info(
        "Couldn't import snappy. Support for snappy compression disabled.")


class ParquetFormatException(Exception):
    """Generic Exception related to unexpected data format when reading parquet file."""


def _check_header_magic_bytes(file_obj):
    """Check if the file-like obj has the PAR1 magic bytes at the header."""
    file_obj.seek(0, 0)
    magic = file_obj.read(4)
    return magic == b'PAR1'


def _check_footer_magic_bytes(file_obj):
    """Check if the file-like obj has the PAR1 magic bytes at the footer."""
    file_obj.seek(-4, 2)  # seek to four bytes from the end of the file
    magic = file_obj.read(4)
    return magic == b'PAR1'


def _get_footer_size(file_obj):
    """Read the footer size in bytes, which is serialized as little endian."""
    file_obj.seek(-8, 2)
    tup = struct.unpack(b"<i", file_obj.read(4))
    return tup[0]


def _read_footer(file_obj):
    """Read the footer from the given file object and returns a FileMetaData object.

    This method assumes that the fo references a valid parquet file.
    """
    footer_size = _get_footer_size(file_obj)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Footer size in bytes: %s", footer_size)
    file_obj.seek(-(8 + footer_size), 2)  # seek to beginning of footer
    tin = TFileTransport(file_obj)
    pin = TCompactProtocolFactory().get_protocol(tin)
    fmd = parquet_thrift.FileMetaData()
    fmd.read(pin)
    return fmd


def _read_page_header(file_obj):
    """Read the page_header from the given fo."""
    tin = TFileTransport(file_obj)
    pin = TCompactProtocolFactory().get_protocol(tin)
    page_header = parquet_thrift.PageHeader()
    page_header.read(pin)
    return page_header


def read_footer(filename):
    """Read the footer and return the FileMetaData for the specified filename."""
    with open(filename, 'rb') as file_obj:
        if not _check_header_magic_bytes(file_obj) or \
           not _check_footer_magic_bytes(file_obj):
            raise ParquetFormatException("{0} is not a valid parquet file "
                                         "(missing magic bytes)"
                                         .format(filename))
        return _read_footer(file_obj)


def _get_name(type_, value):
    """Return the name for the given value of the given type_.

    The value `None` returns empty string.
    """
    return type_._VALUES_TO_NAMES[value] if value is not None else "None"  # pylint: disable=protected-access


def _get_offset(cmd):
    """Return the offset into the cmd based upon if it's a dictionary page or a data page."""
    dict_offset = cmd.dictionary_page_offset
    data_offset = cmd.data_page_offset
    if dict_offset is None or data_offset < dict_offset:
        return data_offset
    return dict_offset


def dump_metadata(filename, show_row_group_metadata, out=sys.stdout):
    """Dump metadata about the parquet object with the given filename.

    Dump human-readable metadata to specified `out`. Optionally dump the row group metadata as well.
    """
    def println(value):
        """Write a new line containing `value` to `out`."""
        out.write(value + "\n")
    footer = read_footer(filename)
    println("File Metadata: {0}".format(filename))
    println("  Version: {0}".format(footer.version))
    println("  Num Rows: {0}".format(footer.num_rows))
    println("  k/v metadata: ")
    if footer.key_value_metadata:
        for item in footer.key_value_metadata:
            println("    {0}={1}".format(item.key, item.value))
    else:
        println("    (none)")
    println("  schema: ")
    for element in footer.schema:
        println("    {name} ({type}): length={type_length}, "
                "repetition={repetition_type}, "
                "children={num_children}, "
                "converted_type={converted_type}".format(
                    name=element.name,
                    type=parquet_thrift.Type._VALUES_TO_NAMES[element.type]  # pylint: disable=protected-access
                    if element.type else None,
                    type_length=element.type_length,
                    repetition_type=_get_name(parquet_thrift.FieldRepetitionType,
                                              element.repetition_type),
                    num_children=element.num_children,
                    converted_type=element.converted_type))
    if show_row_group_metadata:
        println("  row groups: ")
        for row_group in footer.row_groups:
            num_rows = row_group.num_rows
            size_bytes = row_group.total_byte_size
            println(
                "  rows={num_rows}, bytes={bytes}".format(num_rows=num_rows,
                                                          bytes=size_bytes))
            println("    chunks:")
            for col_group in row_group.columns:
                cmd = col_group.meta_data
                println("      type={type} file_offset={offset} "
                        "compression={codec} "
                        "encodings={encodings} path_in_schema={path_in_schema} "
                        "num_values={num_values} uncompressed_bytes={raw_bytes} "
                        "compressed_bytes={compressed_bytes} "
                        "data_page_offset={data_page_offset} "
                        "dictionary_page_offset={dictionary_page_offset}".format(
                            type=_get_name(parquet_thrift.Type, cmd.type),
                            offset=col_group.file_offset,
                            codec=_get_name(parquet_thrift.CompressionCodec, cmd.codec),
                            encodings=",".join(
                                [_get_name(
                                    parquet_thrift.Encoding, s) for s in cmd.encodings]),
                            path_in_schema=cmd.path_in_schema,
                            num_values=cmd.num_values,
                            raw_bytes=cmd.total_uncompressed_size,
                            compressed_bytes=cmd.total_compressed_size,
                            data_page_offset=cmd.data_page_offset,
                            dictionary_page_offset=cmd.dictionary_page_offset))
                with open(filename, 'rb') as file_obj:
                    offset = _get_offset(cmd)
                    file_obj.seek(offset, 0)
                    values_read = 0
                    println("      pages: ")
                    while values_read < num_rows:
                        page_header = _read_page_header(file_obj)
                        # seek past current page.
                        file_obj.seek(page_header.compressed_page_size, 1)
                        daph = page_header.data_page_header
                        type_ = _get_name(parquet_thrift.PageType, page_header.type)
                        raw_bytes = page_header.uncompressed_page_size
                        num_values = None
                        if page_header.type == parquet_thrift.PageType.DATA_PAGE:
                            num_values = daph.num_values
                            values_read += num_values
                        if page_header.type == parquet_thrift.PageType.DICTIONARY_PAGE:
                            pass

                        encoding_type = None
                        def_level_encoding = None
                        rep_level_encoding = None
                        if daph:
                            encoding_type = _get_name(parquet_thrift.Encoding, daph.encoding)
                            def_level_encoding = _get_name(
                                parquet_thrift.Encoding, daph.definition_level_encoding)
                            rep_level_encoding = _get_name(
                                parquet_thrift.Encoding, daph.repetition_level_encoding)

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


def _read_page(file_obj, page_header, column_metadata):
    """Read the data page from the given file-object and convert it to raw, uncompressed bytes (if necessary)."""
    bytes_from_file = file_obj.read(page_header.compressed_page_size)
    codec = column_metadata.codec
    if codec is not None and codec != parquet_thrift.CompressionCodec.UNCOMPRESSED:
        if column_metadata.codec == parquet_thrift.CompressionCodec.SNAPPY:
            raw_bytes = snappy.decompress(bytes_from_file)
        elif column_metadata.codec == parquet_thrift.CompressionCodec.GZIP:
            io_obj = io.BytesIO(bytes_from_file)
            with gzip.GzipFile(fileobj=io_obj, mode='rb') as file_data:
                raw_bytes = file_data.read()
        else:
            raise ParquetFormatException(
                "Unsupported Codec: {0}".format(codec))
    else:
        raw_bytes = bytes_from_file

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Read page with compression type %s. Bytes %d -> %d",
            _get_name(parquet_thrift.CompressionCodec, codec),
            page_header.compressed_page_size,
            page_header.uncompressed_page_size)
    assert len(raw_bytes) == page_header.uncompressed_page_size, \
        "found {0} raw bytes (expected {1})".format(
            len(raw_bytes),
            page_header.uncompressed_page_size)
    return raw_bytes


def _read_data(file_obj, fo_encoding, value_count, bit_width):
    """Read data from the file-object using the given encoding.

    The data could be definition levels, repetition levels, or actual values.
    """
    vals = []
    if fo_encoding == parquet_thrift.Encoding.RLE:
        seen = 0
        while seen < value_count:
            values = encoding.read_rle_bit_packed_hybrid(file_obj, bit_width)
            if values is None:
                break  # EOF was reached.
            vals += values
            seen += len(values)
    elif fo_encoding == parquet_thrift.Encoding.BIT_PACKED:
        raise NotImplementedError("Bit packing not yet supported")

    return vals


def read_data_page(file_obj, schema_helper, page_header, column_metadata,
                   dictionary):
    """Read the data page from the given file-like object based upon the parameters.

    Metadata in the the schema_helper, page_header, column_metadata, and (optional) dictionary
    are used for parsing data.

    Returns a list of values.
    """
    daph = page_header.data_page_header
    raw_bytes = _read_page(file_obj, page_header, column_metadata)
    io_obj = io.BytesIO(raw_bytes)
    vals = []
    debug_logging = logger.isEnabledFor(logging.DEBUG)

    if debug_logging:
        logger.debug("  definition_level_encoding: %s",
                     _get_name(parquet_thrift.Encoding, daph.definition_level_encoding))
        logger.debug("  repetition_level_encoding: %s",
                     _get_name(parquet_thrift.Encoding, daph.repetition_level_encoding))
        logger.debug("  encoding: %s", _get_name(parquet_thrift.Encoding, daph.encoding))

    # definition levels are skipped if data is required.
    definition_levels = None
    num_nulls = 0
    max_definition_level = -1
    if not schema_helper.is_required(column_metadata.path_in_schema[-1]):
        max_definition_level = schema_helper.max_definition_level(
            column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_definition_level)
        if debug_logging:
            logger.debug("  max def level: %s   bit_width: %s",
                         max_definition_level, bit_width)
        if bit_width == 0:
            definition_levels = [0] * daph.num_values
        else:
            definition_levels = _read_data(io_obj,
                                           daph.definition_level_encoding,
                                           daph.num_values,
                                           bit_width)[:daph.num_values]

        # any thing that isn't at max definition level is a null.
        num_nulls = len(definition_levels) - definition_levels.count(max_definition_level)
        if debug_logging:
            logger.debug("  Definition levels: %s", len(definition_levels))

    # repetition levels are skipped if data is at the first level.
    repetition_levels = None  # pylint: disable=unused-variable
    if len(column_metadata.path_in_schema) > 1:
        max_repetition_level = schema_helper.max_repetition_level(
            column_metadata.path_in_schema)
        bit_width = encoding.width_from_max_int(max_repetition_level)
        repetition_levels = _read_data(io_obj,
                                       daph.repetition_level_encoding,
                                       daph.num_values,
                                       bit_width)

    # NOTE: The repetition levels aren't yet used.
    if daph.encoding == parquet_thrift.Encoding.PLAIN:
        read_values = encoding.read_plain(io_obj, column_metadata.type, daph.num_values - num_nulls)
        schema_element = schema_helper.schema_element(column_metadata.path_in_schema[-1])
        read_values = convert_column(read_values, schema_element) \
            if schema_element.converted_type is not None else read_values
        if definition_levels:
            itr = iter(read_values)
            vals.extend([next(itr) if level == max_definition_level else None for level in definition_levels])
        else:
            vals.extend(read_values)
        if debug_logging:
            logger.debug("  Values: %s, nulls: %s", len(vals), num_nulls)

    elif daph.encoding == parquet_thrift.Encoding.PLAIN_DICTIONARY:
        # bit_width is stored as single byte.
        bit_width = struct.unpack(b"<B", io_obj.read(1))[0]
        if debug_logging:
            logger.debug("bit_width: %d", bit_width)

        dict_values_bytes = io_obj.read()
        dict_values_io_obj = io.BytesIO(dict_values_bytes)
        # read_values stores the bit-packed values. If there are definition levels and the data contains nulls,
        # the size of read_values will be less than daph.num_values
        read_values = []
        while dict_values_io_obj.tell() < len(dict_values_bytes):
            read_values.extend(encoding.read_rle_bit_packed_hybrid(
                dict_values_io_obj, bit_width, len(dict_values_bytes)))

        if definition_levels:
            itr = iter(read_values)
            # add the nulls into a new array, values, but using the definition_levels data.
            values = [dictionary[next(itr)] if level == max_definition_level else None for level in definition_levels]
        else:
            values = [dictionary[v] for v in read_values]

        # there can be extra values on the end of the array because the last bit-packed chunk may be zero-filled.
        if len(values) > daph.num_values:
            values = values[0: daph.num_values]
        vals.extend(values)

        if debug_logging:
            logger.debug("  Read %s values using PLAIN_DICTIONARY encoding and definition levels show %s nulls",
                         len(vals), num_nulls)

    else:
        raise ParquetFormatException("Unsupported encoding: {}".format(
            _get_name(parquet_thrift.Encoding, daph.encoding)))
    return vals


def _read_dictionary_page(file_obj, schema_helper, page_header, column_metadata):
    """Read a page containing dictionary data.

    Consumes data using the plain encoding and returns an array of values.
    """
    raw_bytes = _read_page(file_obj, page_header, column_metadata)
    io_obj = io.BytesIO(raw_bytes)
    values = encoding.read_plain(
        io_obj,
        column_metadata.type,
        page_header.dictionary_page_header.num_values
    )
    # convert the values once, if the dictionary is associated with a converted_type.
    schema_element = schema_helper.schema_element(column_metadata.path_in_schema[-1])
    return convert_column(values, schema_element) if schema_element.converted_type is not None else values


def DictReader(file_obj, columns=None):  # pylint: disable=invalid-name
    """
    Reader for a parquet file object.

    This function is a generator returning an OrderedDict for each row
    of data in the parquet file. Nested values will be flattend into the
    top-level dict and can be referenced with '.' notation (e.g. 'foo' -> 'bar'
    is referenced as 'foo.bar')

    :param file_obj: the file containing parquet data
    :param columns: the columns to include. If None (default), all columns
                    are included. Nested values are referenced with "." notation
    """
    footer = _read_footer(file_obj)
    keys = columns if columns else [s.name for s in
                                    footer.schema if s.type]

    for row in reader(file_obj, columns):
        yield OrderedDict(zip(keys, row))


def reader(file_obj, columns=None):
    """
    Reader for a parquet file object.

    This function is a generator returning a list of values for each row
    of data in the parquet file.

    :param file_obj: the file containing parquet data
    :param columns: the columns to include. If None (default), all columns
                    are included. Nested values are referenced with "." notation
    """
    if hasattr(file_obj, 'mode') and 'b' not in file_obj.mode:
        logger.error("parquet.reader requires the fileobj to be opened in binary mode!")
    footer = _read_footer(file_obj)
    schema_helper = schema.SchemaHelper(footer.schema)
    keys = columns if columns else [s.name for s in
                                    footer.schema if s.type]
    debug_logging = logger.isEnabledFor(logging.DEBUG)
    for row_group in footer.row_groups:
        res = defaultdict(list)
        row_group_rows = row_group.num_rows
        for col_group in row_group.columns:
            dict_items = []
            cmd = col_group.meta_data
            # skip if the list of columns is specified and this isn't in it
            if columns and not ".".join(cmd.path_in_schema) in columns:
                continue

            offset = _get_offset(cmd)
            file_obj.seek(offset, 0)
            values_seen = 0
            if debug_logging:
                logger.debug("reading column chunk of type: %s",
                             _get_name(parquet_thrift.Type, cmd.type))
            while values_seen < row_group_rows:
                page_header = _read_page_header(file_obj)
                if debug_logging:
                    logger.debug("Reading page (type=%s, "
                                 "uncompressed=%s bytes, "
                                 "compressed=%s bytes)",
                                 _get_name(parquet_thrift.PageType, page_header.type),
                                 page_header.uncompressed_page_size,
                                 page_header.compressed_page_size)

                if page_header.type == parquet_thrift.PageType.DATA_PAGE:
                    values = read_data_page(file_obj, schema_helper, page_header, cmd,
                                            dict_items)
                    res[".".join(cmd.path_in_schema)] += values
                    values_seen += page_header.data_page_header.num_values
                elif page_header.type == parquet_thrift.PageType.DICTIONARY_PAGE:
                    if debug_logging:
                        logger.debug(page_header)
                    assert dict_items == []
                    dict_items = _read_dictionary_page(file_obj, schema_helper, page_header, cmd)
                    if debug_logging:
                        logger.debug("Dictionary: %s", str(dict_items))
                else:
                    logger.info("Skipping unknown page type=%s",
                                _get_name(parquet_thrift.PageType, page_header.type))

        for i in range(row_group.num_rows):
            yield [res[k][i] for k in keys if res[k]]


class JsonWriter:  # pylint: disable=too-few-public-methods
    """Utility for dumping rows as JSON objects."""

    def __init__(self, out):
        """Initialize with output destination."""
        self._out = out

    def writerow(self, row):
        """Write a single row."""
        json_text = json.dumps(row)
        if isinstance(json_text, bytes):
            json_text = json_text.decode('utf-8')
        self._out.write(json_text)
        self._out.write(u'\n')


def _dump(file_obj, options, out=sys.stdout):
    """Dump to fo with given options."""
    # writer and keys are lazily loaded. We don't know the keys until we have
    # the first item. And we need the keys for the csv writer.
    total_count = 0
    writer = None
    keys = None
    for row in DictReader(file_obj, options.col):
        if not keys:
            keys = row.keys()
        if not writer:
            writer = csv.DictWriter(out, keys, delimiter=u'\t', quotechar=u'\'', quoting=csv.QUOTE_MINIMAL) \
                if options.format == 'csv' \
                else JsonWriter(out) if options.format == 'json' \
                else None
        if total_count == 0 and options.format == "csv" and not options.no_headers:
            writer.writeheader()
        if options.limit != -1 and total_count >= options.limit:
            return
        row_unicode = {k: v.decode("utf-8") if isinstance(v, bytes) else v for k, v in row.items()}
        writer.writerow(row_unicode)
        total_count += 1


def dump(filename, options, out=sys.stdout):
    """Dump parquet file with given filename using options to `out`."""
    with open(filename, 'rb') as file_obj:
        return _dump(file_obj, options=options, out=out)
