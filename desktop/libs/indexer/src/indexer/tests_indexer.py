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
# limitations under the License.from nose.tools import assert_equal
import StringIO
import logging

from nose.tools import assert_equal, assert_true
from nose.plugins.skip import SkipTest

from hadoop import cluster
from hadoop.pseudo_hdfs4 import is_live_cluster

from indexer.smart_indexer import Indexer
from indexer.controller import CollectionManagerController

from indexer.file_format import ApacheCombinedFormat, RubyLogFormat, HueLogFormat

LOG = logging.getLogger(__name__)

def _test_fixed_type_format_generate_morphline(format_):
  indexer = Indexer("test", None)
  format_instance = format_()

  morphline = indexer.generate_morphline_config("test_collection", {
      "columns": [field.to_dict() for field in format_instance.fields],
      "format": format_instance.get_format()
    })

  assert_true(isinstance(morphline, basestring))


class IndexerTest():
  simpleCSVString = """id,Rating,Location,Name,Time
1,5,San Francisco,Good Restaurant,8:30pm
2,4,San Mateo,Cafe,11:30am
3,3,Berkeley,Sauls,2:30pm
"""
  simpleCSVFields = [
    {
      "name": "id",
      "type": "long",
      "operations": [],
      "keep": True,
      "required": False
    },
    {
      "name": "Rating",
      "type": "long",
      "operations": [],
      "keep": True,
      "required": False
    },
    {
      "name": "Location",
      "type": "string",
      "operations": [],
      "keep": True,
      "required": False
    },
    {
      "name": "Name",
      "type": "string",
      "operations": [],
      "keep": True,
      "required": False
    },
    {
      "name": "Time",
      "type": "string",
      "operations": [],
      "keep": True,
      "required": False
    }
  ]
  simpleCSVFormat = {
    'type': 'csv',
    'fieldSeparator': ',',
    'recordSeparator': '\n',
    'hasHeader': True,
    'quoteChar': '"'
  }

  def test_guess_csv_format(self):
    stream = StringIO.StringIO(IndexerTest.simpleCSVString)
    indexer = Indexer("test", None)

    guessed_format = indexer.guess_format({'file': {"stream": stream, "name": "test.csv"}})

    fields = indexer.guess_field_types({"file":{"stream": stream, "name": "test.csv"}, "format": guessed_format})['columns']
    # test format
    expected_format = self.simpleCSVFormat

    assert_equal(expected_format, guessed_format)

    # test fields
    expected_fields = self.simpleCSVFields

    for expected, actual in zip(expected_fields, fields):
      for key in ("name", "type"):
        assert_equal(expected[key], actual[key])

  def test_guess_format_invalid_csv_format(self):
    indexer = Indexer("test", None)
    stream = StringIO.StringIO(IndexerTest.simpleCSVString)

    guessed_format = indexer.guess_format({'file': {"stream": stream, "name": "test.csv"}})

    guessed_format["fieldSeparator"] = "invalid separator"

    fields = indexer.guess_field_types({"file": {"stream": stream, "name": "test.csv"}, "format": guessed_format})['columns']
    assert_equal(fields, [])

    stream.seek(0)
    guessed_format = indexer.guess_format({'file':  {"stream": stream, "name": "test.csv"}})

    guessed_format["recordSeparator"] = "invalid separator"

    fields = indexer.guess_field_types({"file": {"stream": stream, "name": "test.csv"}, "format": guessed_format})['columns']
    assert_equal(fields, [])

    stream.seek(0)
    guessed_format = indexer.guess_format({'file':  {"stream": stream, "name": "test.csv"}})

    guessed_format["quoteChar"] = "invalid quoteChar"

    fields = indexer.guess_field_types({"file": {"stream": stream, "name": "test.csv"}, "format": guessed_format})['columns']
    assert_equal(fields, [])

  def test_generate_csv_morphline(self):
    indexer = Indexer("test", None)
    morphline =indexer.generate_morphline_config("test_collection", {
        "columns": self.simpleCSVFields,
        "format": self.simpleCSVFormat
      })

    assert_true(isinstance(morphline, basestring))

  def test_generate_apache_combined_morphline(self):
    _test_fixed_type_format_generate_morphline(ApacheCombinedFormat)

  def test_generate_ruby_logs_morphline(self):
    _test_fixed_type_format_generate_morphline(RubyLogFormat)

  def test_generate_hue_log_morphline(self):
    _test_fixed_type_format_generate_morphline(HueLogFormat)

  def test_end_to_end(self):
    if not is_live_cluster():
      raise SkipTest()

    fs = cluster.get_hdfs()
    collection_name = "test_collection"
    indexer = Indexer("test", fs)
    input_loc = "/tmp/test.csv"

    # upload the test file to hdfs
    fs.create(input_loc, data=IndexerTest.simpleCSVString, overwrite=True)

    # open a filestream for the file on hdfs
    stream = fs.open(input_loc)

    # guess the format of the file
    file_type_format = indexer.guess_format({'file': {"stream": stream, "name": "test.csv"}})

    field_types = indexer.guess_field_types({"file":{"stream": stream, "name": "test.csv"}, "format": file_type_format})

    format_ = field_types.copy()
    format_['format'] = file_type_format

    # find a field name available to use for the record's uuid
    unique_field = indexer.get_uuid_name(format_)

    # generate morphline
    morphline = indexer.generate_morphline_config(collection_name, format_, unique_field)

    schema_fields = [{"name": unique_field, "type": "string"}] + indexer.get_kept_field_list(format_['columns'])

    # create the collection from the specified fields
    collection_manager = CollectionManagerController("test")
    if collection_manager.collection_exists(collection_name):
      collection_manager.delete_collection(collection_name, None)
    collection_manager.create_collection(collection_name, schema_fields, unique_key_field=unique_field)

    # index the file
    indexer.run_morphline(collection_name, morphline, input_loc)
