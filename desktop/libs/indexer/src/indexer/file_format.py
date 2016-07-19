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
import operator
import itertools
import logging

from django.utils.translation import ugettext as _

from indexer.fields import Field, guess_field_type_from_samples
from indexer.argument import TextArgument, CheckboxArgument

LOG = logging.getLogger(__name__)

def get_format_types():
  return [
    CSVFormat,
    HueFormat
  ]

def get_format_mapping():
  return dict([(format_.get_name(), format_) for format_ in get_format_types()])

def get_file_format_instance(file, format_=None):
  file_stream = file['stream']
  file_extension = file['name'].split('.')[-1] if '.' in file['name'] else ''

  format_mapping = get_format_mapping()

  if format_ and "type" in format_:
    type_ = format_["type"]
    if type_ in format_mapping:
      if format_mapping[type_].valid_format(format_):
        return format_mapping[type_](file_stream, format_)
      else:
        return None

  matches = [type_ for type_ in get_format_types() if file_extension in type_.get_extensions()]

  return (matches[0] if matches else get_format_types()[0])(file_stream, format_)

class FileFormat(object):
  _name = None
  _description = None
  _customizable = True
  _args = []
  _extensions = []

  @classmethod
  def get_extensions(cls):
    return cls._extensions

  @classmethod
  def get_name(cls):
    return cls._name

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
      "isCustomizable": cls.is_customizable()
    }

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

class HueFormat(FileFormat):
  _name = "hue"
  _description = _("Hue Log File")
  _customizable = False
  _extensions = ["log"]

  def __init__(self, file_stream, format_):
    self._fields = [
      Field("date", "date"),
      Field("component", "string"),
      Field("log_level", "string"),
      Field("details", "string"),
      Field("message", "text")
    ]

  @property
  def fields(self):
    return self._fields

class CSVFormat(FileFormat):
  _name = "csv"
  _description = _("CSV File")
  _args = [
    TextArgument("fieldSeparator", "Field Separator"),
    TextArgument("recordSeparator", "Record Separator"),
    TextArgument("quoteChar", "Quote Character"),
    CheckboxArgument("hasHeader", "Has Header")
  ]
  _extensions = ["csv", "tsv"]

  @classmethod
  def _valid_character(self, char):
    return isinstance(char, basestring) and len(char) == 1

  @classmethod
  def valid_format(cls, format_):
    valid = super(CSVFormat, cls).valid_format(format_)
    valid = valid and cls._valid_character(format_["fieldSeparator"])
    valid = valid and cls._valid_character(format_["recordSeparator"])
    valid = valid and cls._valid_character(format_["quoteChar"])
    valid = valid and isinstance(format_["hasHeader"], bool)

    return valid

  def __init__(self, file_stream, format_=None):
    file_stream.seek(0)
    sample = '\n'.join(file_stream.read(1024*1024*5).splitlines())
    file_stream.seek(0)

    if self.valid_format(format_):
      self._delimiter = format_["fieldSeparator"].encode('utf-8')
      self._line_terminator = format_["recordSeparator"].encode('utf-8')
      self._quote_char = format_["quoteChar"].encode('utf-8')
      self._has_header = format_["hasHeader"]
    else:
      try:
        dialect, self._has_header = self._guess_dialect(sample)
        self._delimiter = dialect.delimiter
        self._line_terminator = dialect.lineterminator
        self._quote_char = dialect.quotechar
      except Exception:
        # guess dialect failed, fall back to defaults:
        self._delimiter = ','
        self._line_terminator = '\n'
        self._quote_char = '"'
        self._has_header = False

    # sniffer insists on \r\n even when \n. This is safer and good enough for a preview
    self._line_terminator = self._line_terminator.replace("\r\n", "\n")

    self._sample_rows = self._get_sample_rows(sample)

    self._num_columns = self._guess_num_columns(self._sample_rows)

    self._fields = self._guess_fields(sample)

    super(CSVFormat, self).__init__()

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
      "fieldSeparator":self.delimiter,
      "recordSeparator":self.line_terminator,
      "quoteChar":self.quote_char,
      "hasHeader":self._has_header
    }
    format_.update(specific_format)

    return format_

  def _guess_dialect(self, sample):
    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(sample)
    has_header = sniffer.has_header(sample)
    return dialect, has_header

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

  def _guess_field_names(self, sample):
    reader = self._get_sample_reader(sample)

    first_row = reader.next()

    if self._has_header:
      header = first_row
    else:
      header = ["field_%d" % (i+1) for i in range(self._num_columns)]

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
