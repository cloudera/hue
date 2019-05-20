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

from copy import deepcopy

import StringIO
import logging

from nose.tools import assert_equal, assert_true
from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest

from django.contrib.auth.models import User

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access, add_to_group
from hadoop.pseudo_hdfs4 import is_live_cluster, shared_cluster

from indexer.conf import ENABLE_SCALABLE_INDEXER
from indexer.controller import CollectionManagerController
from indexer.file_format import ApacheCombinedFormat, RubyLogFormat, HueLogFormat
from indexer.fields import Field
from indexer.indexers.morphline_operations import get_operator
from indexer.indexers.morphline import MorphlineIndexer
from indexer.solr_client import SolrClient
from indexer.solr_client_tests import MockSolrCdhCloudHdfsApi


LOG = logging.getLogger(__name__)


class TestIndexer():

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

  def setUp(self):
    self.c = make_logged_in_client(is_superuser=False)
    grant_access("test", "test", "indexer")
    add_to_group("test")
    self.user = User.objects.get(username='test')
    self.solr_client = SolrClient(self.user, api=MockSolrCdhCloudHdfsApi())

    self.finish = ENABLE_SCALABLE_INDEXER.set_for_testing(True)

  def tearDown(self):
    self.finish()

  def test_guess_csv_format(self):
    stream = StringIO.StringIO(TestIndexer.simpleCSVString)
    indexer = MorphlineIndexer("test", solr_client=self.solr_client)

    guessed_format = indexer.guess_format({'file': {"stream": stream, "name": "test.csv"}})

    fields = indexer.guess_field_types({"file": {"stream": stream, "name": "test.csv"}, "format": guessed_format})['columns']
    # test format
    expected_format = self.simpleCSVFormat

    assert_equal(expected_format, guessed_format)

    # test fields
    expected_fields = self.simpleCSVFields

    for expected, actual in zip(expected_fields, fields):
      for key in ("name", "type"):
        assert_equal(expected[key], actual[key])

  def test_guess_format_invalid_csv_format(self):
    indexer = MorphlineIndexer("test", solr_client=self.solr_client)
    stream = StringIO.StringIO(TestIndexer.simpleCSVString)

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
    indexer = MorphlineIndexer("test", solr_client=self.solr_client)
    morphline = indexer.generate_morphline_config("test_collection", {
        "columns": deepcopy(self.simpleCSVFields),
        "format": self.simpleCSVFormat
      })

    assert_true(isinstance(morphline, basestring))

  def test_generate_apache_combined_morphline(self):
    self._test_fixed_type_format_generate_morphline(ApacheCombinedFormat)

  def test_generate_ruby_logs_morphline(self):
    raise SkipTest
    self._test_fixed_type_format_generate_morphline(RubyLogFormat)

  def test_generate_hue_log_morphline(self):
    self._test_fixed_type_format_generate_morphline(HueLogFormat)

  def test_generate_split_operation_morphline(self):
    split_dict = get_operator('split').get_default_operation()

    split_dict['fields'] = [
        Field("test_field_1", "string").to_dict(),
        Field("test_field_2", "string").to_dict()
      ]

    self._test_generate_field_operation_morphline(split_dict)

  def test_generate_extract_uri_components_operation_morphline(self):
    extract_uri_dict = get_operator('extract_uri_components').get_default_operation()

    extract_uri_dict['fields'] = [
        Field("test_field_1", "string").to_dict(),
        Field("test_field_2", "string").to_dict()
      ]

    self._test_generate_field_operation_morphline(extract_uri_dict)

  def test_generate_grok_operation_morphline(self):
    grok_dict = get_operator('grok').get_default_operation()

    grok_dict['fields'] = [
        Field("test_field_1", "string").to_dict(),
        Field("test_field_2", "string").to_dict()
      ]

    self._test_generate_field_operation_morphline(grok_dict)

  def test_generate_convert_date_morphline(self):
    convert_date_dict = get_operator('convert_date').get_default_operation()

    self._test_generate_field_operation_morphline(convert_date_dict)

  def test_generate_geo_ip_morphline(self):
    geo_ip_dict = get_operator('geo_ip').get_default_operation()

    geo_ip_dict['fields'] = [
        Field("test_field_1", "string").to_dict(),
        Field("test_field_2", "string").to_dict()
      ]

    self._test_generate_field_operation_morphline(geo_ip_dict)

  def test_generate_translate_morphline(self):
    translate_dict = get_operator('translate').get_default_operation()

    translate_dict['fields'] = [
      Field("test_field_1", "string").to_dict(),
      Field("test_field_2", "string").to_dict()
    ]

    translate_dict['settings']['mapping'].append({"key":"key","value":"value"})

    self._test_generate_field_operation_morphline(translate_dict)

  def test_generate_find_replace_morphline(self):
    find_replace_dict = get_operator('find_replace').get_default_operation()

    self._test_generate_field_operation_morphline(find_replace_dict)

  @attr('integration')
  def test_end_to_end(self):
    if not is_live_cluster(): # Skipping as requires morplines libs to be setup
      raise SkipTest()

    cluster = shared_cluster()
    fs = cluster.fs
    make_logged_in_client(username="test", groupname="default", recreate=True, is_superuser=False)
    user = User.objects.get(username="test")
    collection_name = "test_collection"
    indexer = MorphlineIndexer("test", fs=fs, jt=cluster.jt, solr_client=self.solr_client)
    input_loc = "/tmp/test.csv"

    # upload the test file to hdfs
    fs.create(input_loc, data=TestIndexer.simpleCSVString, overwrite=True)

    # open a filestream for the file on hdfs
    stream = fs.open(input_loc)

    # guess the format of the file
    file_type_format = indexer.guess_format({'file': {"stream": stream, "name": "test.csv"}})

    field_types = indexer.guess_field_types({"file":{"stream": stream, "name": "test.csv"}, "format": file_type_format})

    format_ = field_types.copy()
    format_['format'] = file_type_format

    # find a field name available to use for the record's uuid
    unique_field = indexer.get_unique_field(format_)
    is_unique_generated = indexer.is_unique_generated(format_)

    # generate morphline
    morphline = indexer.generate_morphline_config(collection_name, format_, unique_field)

    schema_fields = indexer.get_kept_field_list(format_['columns'])
    if is_unique_generated:
      schema_fields += [{"name": unique_field, "type": "string"}]


    # create the collection from the specified fields
    collection_manager = CollectionManagerController("test")
    if collection_manager.collection_exists(collection_name):
      collection_manager.delete_collection(collection_name, None)
    collection_manager.create_collection(collection_name, schema_fields, unique_key_field=unique_field)

    # index the file
    indexer.run_morphline(MockedRequest(user=user, fs=cluster.fs, jt=cluster.jt), collection_name, morphline, input_loc)

  def _test_fixed_type_format_generate_morphline(self, format_):
    indexer = MorphlineIndexer("test", solr_client=self.solr_client)
    format_instance = format_()

    morphline = indexer.generate_morphline_config("test_collection", {
        "columns": [field.to_dict() for field in format_instance.fields],
        "format": format_instance.get_format()
      })

    assert_true(isinstance(morphline, basestring))

  def _test_generate_field_operation_morphline(self, operation_format):
    fields = deepcopy(TestIndexer.simpleCSVFields)
    fields[0]['operations'].append(operation_format)

    indexer = MorphlineIndexer("test", solr_client=self.solr_client)
    morphline =indexer.generate_morphline_config("test_collection", {
        "columns": fields,
        "format": TestIndexer.simpleCSVFormat
      })

    assert_true(isinstance(morphline, basestring))


class MockedRequest():
  def __init__(self, user, fs, jt):
    self.user = user
    self.fs = fs
    self.jt = jt
