# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.import logging
import csv
import gzip
import operator
import itertools
import logging
import StringIO

from django.utils.translation import ugettext as _

from desktop.lib import i18n

from indexer.argument import CheckboxArgument, TextDelimiterArgument
from indexer.conf import ENABLE_SCALABLE_INDEXER
from indexer.fields import Field, guess_field_type_from_samples
from indexer.indexers.morphline_operations import get_operator


LOG = logging.getLogger(__name__)


IMPORT_PEEK_SIZE = 1024 * 1024
IMPORT_PEEK_NLINES = 20


def get_format_types():
  formats = [CSVFormat]

  if ENABLE_SCALABLE_INDEXER.get():
    formats.extend([
      ApacheCombinedFormat,
      SyslogFormat,
      HueLogFormat,
      #RubyLogFormat,
      #ParquetFormat
    ])

  return formats


def get_file_indexable_format_types():
  return [format_ for format_ in get_format_types() if format_.is_file_indexable]

def _get_format_mapping():
  return dict([(format_.get_name(), format_) for format_ in get_format_types()])

def get_file_format_class(type_):
  mapping = _get_format_mapping()
  return mapping[type_] if type_ in mapping else None

def get_file_format_instance(file, format_=None):
  file_stream = file['stream']
  file_extension = file['name'].split('.')[-1] if '.' in file['name'] else ''

  format_mapping = _get_format_mapping()

  if format_ and "type" in format_:
    type_ = format_["type"]
    if type_ in format_mapping:
      if format_mapping[type_].valid_format(format_):
        return format_mapping[type_].get_instance(file_stream, format_)
      else:
        return None

  matches = [type_ for type_ in get_format_types() if file_extension in type_.get_extensions()]

  return (matches[0] if matches else get_format_types()[0]).get_instance(file_stream, format_)


class FileFormat(object):
  _name = None
  _description = None
  _customizable = True
  _args = []
  _extensions = []
  _parse_type = None
  _file_indexable = True

  @classmethod
  def is_file_indexable(cls):
    return cls._file_indexable

  @classmethod
  def get_extensions(cls):
    return cls._extensions

  @classmethod
  def get_name(cls):
    return cls._name

  @classmethod
  def get_parse_type(cls):
    return cls._parse_type if cls._parse_type else cls.get_name()

  @classmethod
  def get_description(cls):
    return cls._description

  @classmethod
  def get_arguments(cls):
    return cls._args

  @classmethod
  def is_customizable(cls):
    return cls._customizable

  @classmethod
  def valid_format(cls, format_):
    return format_ and all([arg.name in format_ for arg in cls.get_arguments()])

  @classmethod
  def format_info(cls):
    return {
      "name": cls.get_name(),
      "args": [arg.to_dict() for arg in cls.get_arguments()],
      "description": cls.get_description(),
      "isCustomizable": cls.is_customizable(),
    }

  @classmethod
  def get_instance(cls, file_stream, format_):
    return cls()

  def __init__(self):
    pass

  @property
  def sample(self):
    pass

  @property
  def fields(self):
    return []

  def get_format(self):
    return {"type": self.get_name()}

  def get_fields(self):
    obj = {}

    obj['columns'] = [field.to_dict() for field in self.fields]
    obj['sample'] = self.sample

    return obj

  def to_dict(self):
    obj = {}

    obj['format'] = self.get_format()
    obj['columns'] = [field.to_dict() for field in self.fields]
    obj['sample'] = self.sample

    return obj


class GrokkedFormat(FileFormat):
  _grok = None
  _customizable = False

  @classmethod
  def get_grok(cls):
    return cls._grok

  def get_format(self):
    format_ = super(GrokkedFormat, self).get_format()
    specific_format = {
      "grok": self.get_grok()
    }
    format_.update(specific_format)

    return format_

  @property
  def fields(self):
    return self._fields


class HueLogFormat(GrokkedFormat):
  _name = "hue"
  _description = _("Hue Log File")
  _extensions = ["log"]

  def __init__(self):
    geo_ip_operation = get_operator("geo_ip").get_default_operation()

    geo_ip_operation['settings']["/country/names/en"] = True
    geo_ip_operation['settings']["/city/names/en"] = True
    geo_ip_operation['settings']["/location/latitude"] = True
    geo_ip_operation['settings']["/location/longitude"] = True

    geo_ip_operation['fields'] += [
      Field("country", "string").to_dict(),
      Field("city", "string").to_dict(),
      Field("latitude", "double").to_dict(),
      Field("longitude", "double").to_dict()
    ]

    self._fields = [
      Field("date", "date"),
      Field("component", "string"),
      Field("log_level", "string"),
      Field("details", "string"),
      Field("message", "text_general"),
      Field("ip", "string", [geo_ip_operation]),
      Field("user", "string"),
      Field("http_method", "string"),
      Field("path", "string"),
      Field("protocol", "string")
    ]


class GrokLineFormat(GrokkedFormat):
  _parse_type = "grok_line"


class ApacheCombinedFormat(GrokLineFormat):
  _name = "combined_apache"
  _description = _("Combined Apache Log File")
  _extensions = ["log"]
  _grok = "%{COMBINEDAPACHELOG}"

  def __init__(self):
    self._fields = [
      Field("clientip", "string"),
      Field("ident", "string"),
      Field("auth", "string"),
      Field("timestamp", "date"),
      Field("verb", "string"),
      Field("request", "string"),
      Field("httpversion", "double"),
      Field("rawrequest", "long"),
      Field("response", "long"),
      Field("bytes", "long"),
      Field("referrer", "string"),
      Field("field_line", "text_general")
    ]


class RubyLogFormat(GrokLineFormat):
  _name = "ruby_log"
  _description = _("Ruby Log")
  _extensions = ["log"]
  _grok = "%{RUBY_LOGGER}"

  def __init__(self):
    self._fields = [
      Field("timestamp", "string"),
      Field("pid", "long"),
      Field("loglevel", "string"),
      Field("progname", "string"),
      Field("message", "text_general"),
      Field("field_line", "text_general")
    ]


class SyslogFormat(GrokLineFormat):
  _name = "syslog"
  _description = _("Syslog")
  _grok = "%{SYSLOGLINE}"

  def __init__(self):
    self._fields = [
      Field("timestamp", "string"),
      Field("timestamp8601", "string"),
      Field("facility", "string"),
      Field("priority", "string"),
      Field("logsource", "string"),
      Field("program", "string"),
      Field("pid", "string"),
      Field("message", "text_general"),
    ]


class ParquetFormat(FileFormat):
  _name = "parquet"
  _description = _("Parquet Table")


class CSVFormat(FileFormat):
  _name = "csv"
  _description = _("CSV File")
  _args = [
    TextDelimiterArgument("fieldSeparator", "Field Separator"),
    TextDelimiterArgument("recordSeparator", "Record Separator"),
    TextDelimiterArgument("quoteChar", "Quote Character"),
    CheckboxArgument("hasHeader", "Has Header")
  ]
  _extensions = ["csv", "tsv"]

  def __init__(self, delimiter=',', line_terminator='\n', quote_char='"', has_header=False, sample="", fields=None):
    self._delimiter = delimiter
    self._line_terminator = line_terminator
    self._quote_char = quote_char
    self._has_header = has_header

    # sniffer insists on \r\n even when \n. This is safer and good enough for a preview
    self._line_terminator = self._line_terminator.replace("\r\n", "\n")
    self._sample_rows = self._get_sample_rows(sample)
    self._num_columns = self._guess_num_columns(self._sample_rows)
    self._fields = fields if fields else self._guess_fields(sample)

    super(CSVFormat, self).__init__()

  @staticmethod
  def format_character(string):
    # Morphline supports only one char representation
    string = string.replace('"', '\\"')
    string = string.replace('\t', '\\t')
    string = string.replace('\n', '\\n')
    string = string.replace('\u0001', '\\u0001')
    string = string.replace('\x00', '\\u0000')
    string = string.replace('\x01', '\\u0001')
    string = string.replace('\x02', '\\u0002')
    string = string.replace('\x03', '\\u0003')

    return string

  @classmethod
  def _valid_character(self, char):
    return isinstance(char, basestring) and len(char) == 1 or char.startswith('\\')

  @classmethod
  def _guess_dialect(cls, sample):
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)
    has_header = cls._hasHeader(sniffer, sample, dialect)
    return dialect, has_header

  # Copied from python2.7/csv.py with small modification to 1st line
  # Results in large performance gain from not having to reprocess the file if dialect is known.
  @classmethod
  def _hasHeader(self, sniffer, sample, dialect):
    # ******Changed from********
    # rdr = reader(StringIO(sample), self.sniff(sample))
    from _csv import reader
    rdr = reader(StringIO.StringIO(sample), dialect)

    header = rdr.next()  # assume first row is header

    columns = len(header)
    columnTypes = {}
    for i in range(columns): columnTypes[i] = None

    checked = 0
    for row in rdr:
      # arbitrary number of rows to check, to keep it sane
      if checked > 20:
        break
      checked += 1

      if len(row) != columns:
        continue  # skip rows that have irregular number of columns

      for col in columnTypes.keys():

        for thisType in [int, long, float, complex]:
          try:
            thisType(row[col])
            break
          except (ValueError, OverflowError):
            pass
        else:
          # fallback to length of string
          thisType = len(row[col])

        # treat longs as ints
        if thisType == long:
          thisType = int

        if thisType != columnTypes[col]:
          if columnTypes[col] is None:  # add new column type
            columnTypes[col] = thisType
          else:
            # type is inconsistent, remove column from
            # consideration
            del columnTypes[col]

    # finally, compare results against first row and "vote"
    # on whether it's a header
    hasHeader = 0
    for col, colType in columnTypes.items():
      if type(colType) == type(0):  # it's a length
        if len(header[col]) != colType:
          hasHeader += 1
        else:
          hasHeader -= 1
      else:  # attempt typecast
        try:
          colType(header[col])
        except (ValueError, TypeError):
          hasHeader += 1
        else:
          hasHeader -= 1

    return hasHeader > 0

  @classmethod
  def valid_format(cls, format_):
    valid = super(CSVFormat, cls).valid_format(format_)
    valid = valid and cls._valid_character(cls.format_character(format_["fieldSeparator"]))
    valid = valid and cls._valid_character(cls.format_character(format_["recordSeparator"]))
    valid = valid and cls._valid_character(cls.format_character(format_["quoteChar"]))
    valid = valid and isinstance(format_["hasHeader"], bool)

    return valid

  @classmethod
  def _get_sample(cls, file_stream):
    encoding = i18n.get_site_encoding()

    for reader in [TextFileReader, GzipFileReader]:
      file_stream.seek(0)
      sample_data, sample_lines = reader.readlines(file_stream, encoding)
      file_stream.seek(0)

      if sample_data is not None:
        yield sample_data, sample_lines

  @classmethod
  def _guess_from_file_stream(cls, file_stream):
    for sample_data, sample_lines in cls._get_sample(file_stream):
      try:
        lines = itertools.islice(StringIO.StringIO(sample_data), IMPORT_PEEK_NLINES)
        sample_data_lines = ''
        for line in lines:
          sample_data_lines += line
        dialect, has_header = cls._guess_dialect(sample_data_lines) # Only use first few lines for guessing. Greatly improves performance of CSV library.
        delimiter = dialect.delimiter
        line_terminator = dialect.lineterminator
        quote_char = dialect.quotechar

        return cls(**{
          "delimiter": delimiter,
          "line_terminator": line_terminator,
          "quote_char": quote_char,
          "has_header": has_header,
          "sample": sample_data
        })
      except Exception:
        LOG.exception('Warning, cannot read the file format.')

    # Guess dialect failed, fall back to defaults:
    return cls()

  @classmethod
  def _from_format(cls, file_stream, format_):
    for sample_data, sample_lines in cls._get_sample(file_stream):
      try:
        delimiter = format_["fieldSeparator"].encode('utf-8')
        line_terminator = format_["recordSeparator"].encode('utf-8')
        quote_char = format_["quoteChar"].encode('utf-8')
        has_header = format_["hasHeader"]

        return cls(**{
          "delimiter": delimiter,
          "line_terminator": line_terminator,
          "quote_char": quote_char,
          "has_header": has_header,
          "sample": sample_data
        })
      except Exception:
        LOG.exception('Warning, cannot read the file format.')

  @classmethod
  def get_instance(cls, file_stream, format_):
    if cls.valid_format(format_):
      return cls._from_format(file_stream, format_)
    else:
      return cls._guess_from_file_stream(file_stream)

  @property
  def sample(self):
    return self._sample_rows

  @property
  def fields(self):
    return self._fields

  @property
  def delimiter(self):
    return self._delimiter

  @property
  def line_terminator(self):
    return self._line_terminator

  @property
  def quote_char(self):
    return self._quote_char

  def get_format(self):
    format_ = super(CSVFormat, self).get_format()
    specific_format = {
      "fieldSeparator": self.delimiter,
      "recordSeparator": self.line_terminator,
      "quoteChar": self.quote_char,
      "hasHeader": self._has_header
    }
    format_.update(specific_format)

    return format_

  def _guess_num_columns(self, sample_rows):
    counts = {}

    for row in sample_rows:
      num_columns = len(row)

      if num_columns not in counts:
        counts[num_columns] = 0
      counts[num_columns] += 1

    if counts:
      num_columns_guess = max(counts.iteritems(), key=operator.itemgetter(1))[0]
    else:
      num_columns_guess = 0
    return num_columns_guess

  def _guess_field_types(self, sample_rows):
    field_type_guesses = []

    num_columns = self._num_columns

    for col in range(num_columns):
      column_samples = [sample_row[col] for sample_row in sample_rows if len(sample_row) > col]

      field_type_guess = guess_field_type_from_samples(column_samples)
      field_type_guesses.append(field_type_guess)

    return field_type_guesses

  def _get_sample_reader(self, sample):
    if self.line_terminator != '\n':
      sample = sample.replace('\n', '\\n')
      return csv.reader(sample.split(self.line_terminator), delimiter=self.delimiter, quotechar=self.quote_char)
    else:
      return csv.reader(StringIO.StringIO(sample), delimiter=self.delimiter, quotechar=self.quote_char)

  def _guess_field_names(self, sample):
    reader = self._get_sample_reader(sample)

    first_row = reader.next()

    if self._has_header:
      header = []
      for i, field in enumerate(first_row):
        header.append(field if field not in header else '%s_%s' % (field, i))
    else:
      header = ["field_%d" % (i + 1) for i in range(self._num_columns)]

    return header

  def _get_sample_rows(self, sample):
    NUM_SAMPLES = 5

    header_offset = 1 if self._has_header else 0
    reader = itertools.islice(self._get_sample_reader(sample), header_offset, NUM_SAMPLES + 1)

    sample_rows = list(reader)
    return sample_rows

  def _guess_fields(self, sample):
    header = self._guess_field_names(sample)
    types = self._guess_field_types(self._sample_rows)

    if len(header) == len(types):
      # create the fields
      fields = [Field(header[i], types[i]) for i in range(len(header))]
    else:
      # likely failed to guess correctly
      LOG.warn("Guess field types failed - number of headers didn't match number of predicted types.")
      fields = []

    return fields


class GzipFileReader(object):
  TYPE = 'gzip'

  @staticmethod
  def readlines(fileobj, encoding):
    gz = gzip.GzipFile(fileobj=fileobj, mode='rb')
    try:
      data = gz.read(IMPORT_PEEK_SIZE)
    except IOError:
      return None, None
    try:
      return data, itertools.islice(csv.reader(StringIO.StringIO(data)), IMPORT_PEEK_NLINES)
    except UnicodeError:
      return None, None


class TextFileReader(object):
  TYPE = 'text'

  @staticmethod
  def readlines(fileobj, encoding):
    try:
      data = fileobj.read(IMPORT_PEEK_SIZE)
      return data, itertools.islice(csv.reader(StringIO.StringIO(data)), IMPORT_PEEK_NLINES)
    except UnicodeError:
      return None, None


class HiveFormat(CSVFormat):

  FIELD_TYPE_TRANSLATE = {
    "BOOLEAN_TYPE": "boolean",
    "TINYINT_TYPE": "long",
    "SMALLINT_TYPE": "long",
    "INT_TYPE": "long",
    "BIGINT_TYPE": "long",
    "FLOAT_TYPE": "double",
    "DOUBLE_TYPE": "double",
    "STRING_TYPE": "string",
    "TIMESTAMP_TYPE": "date",
    "DATETIME_TYPE": "date",
    "BINARY_TYPE": "string",
    "DECIMAL_TYPE": "double",
    "DATE_TYPE": "date",
    "boolean": "string",
    "tinyint": "long",
    "smallint": "long",
    "int": "long",
    "bigint": "long",
    "float": "double",
    "double": "double",
    "string": "string",
    "timestamp": "date",
    "binary": "string",
    "decimal": "double", # Won't match decimal(16,6)
    "date": "date",
  }

  @classmethod
  def get_instance(cls, file_stream, format_):
    sample_data, sample_lines = cls._get_sample(file_stream)

    fields = []

    for field in format_["fields"]:
      fields.append(Field(
        name=field["name"],
        field_type_name=cls.FIELD_TYPE_TRANSLATE.get(field['type'], 'string')
      ))

    return cls(**{
      "delimiter":',',
      "line_terminator": '\n',
      "quote_char": '"',
      "has_header": False,
      "sample": sample_data,
      "fields": format_["fields"]
    })
