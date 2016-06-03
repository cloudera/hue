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

from nose.tools import assert_equal
from nose.plugins.skip import SkipTest

from hadoop import cluster
from hadoop.pseudo_hdfs4 import is_live_cluster

from indexer.smart_indexer import Indexer
from indexer.controller import CollectionManagerController

LOG = logging.getLogger(__name__)

class IndexerTest():
  simpleCSVString = """id,Rating,Location,Name,Time
1,5,San Francisco,Good Restaurant,8:30pm
2,4,San Mateo,Cafe,11:30am
3,3,Berkeley,Sauls,2:30pm
"""

  def setup(self):
    if not is_live_cluster():
      raise SkipTest()

  def test_guess_format(self):
    stream = StringIO.StringIO(IndexerTest.simpleCSVString)
    indexer = Indexer("hue", None)

    guessed_format = indexer.guess_format({'file': stream})

    fields = indexer.guess_field_types({"file":stream, "format": guessed_format})['columns']
    # test format
    assert_equal('csv', guessed_format['type'])
    assert_equal(',', guessed_format['fieldSeparator'])
    assert_equal('\n', guessed_format['recordSeparator'])

    # test fields
    expected_fields = [
      {
        "name": "id",
        "type": "long"
      },
      {
        "name": "Rating",
        "type": "long"
      },
      {
        "name": "Location",
        "type": "string"
      },
      {
        "name": "Name",
        "type": "string"
      },
      {
        "name": "Time",
        "type": "string"
      }
    ]

    for i in range(len(expected_fields)):
      expected = expected_fields[i]
      actual = fields[i]

      for key in ("name", "type"):
        assert_equal(expected[key], actual[key])

  def test_end_to_end(self):
    fs = cluster.get_hdfs()
    collection_name = "test_collection"
    indexer = Indexer("test", fs)
    input_loc = "/tmp/test.csv"

    # upload the test file to hdfs
    fs.create(input_loc, data=IndexerTest.simpleCSVString, overwrite=True)

    # open a filestream for the file on hdfs
    stream = fs.open(input_loc)

    # guess the format of the file
    file_type_format = indexer.guess_format({'file': stream})

    field_types = indexer.guess_field_types({"file":stream, "format": file_type_format})

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
