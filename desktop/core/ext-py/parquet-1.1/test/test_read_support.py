from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import os
import sys
import tempfile
import unittest

import parquet

PY3 = sys.version_info > (3,)

if PY3:
    import csv
else:
    from backports import csv

TEST_DATA = "test-data"
TEST_FILE = os.path.join(TEST_DATA, "nation.impala.parquet")
CSV_FILE = os.path.join(TEST_DATA, "nation.csv")

TAB_DELIM = u'\t'
PIPE_DELIM = u'|'

class TestFileFormat(unittest.TestCase):
    def test_header_magic_bytes(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"PAR1_some_bogus_data")
            t.flush()
            self.assertTrue(parquet._check_header_magic_bytes(t))

    def test_footer_magic_bytes(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"PAR1_some_bogus_data_PAR1")
            t.flush()
            self.assertTrue(parquet._check_footer_magic_bytes(t))

    def test_not_parquet_file(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"blah")
            t.flush()
            self.assertFalse(parquet._check_header_magic_bytes(t))
            self.assertFalse(parquet._check_footer_magic_bytes(t))


class TestMetadata(unittest.TestCase):

    def test_footer_bytes(self):
        with io.open(TEST_FILE, 'rb') as fo:
            self.assertEquals(327, parquet._get_footer_size(fo))

    def test_read_footer(self):
        footer = parquet.read_footer(TEST_FILE)
        self.assertEquals(
            set([s.name for s in footer.schema]),
            set(["schema", "n_regionkey", "n_name", "n_nationkey",
                 "n_comment"]))

    def test_dump_metadata(self):
        data = io.StringIO()
        parquet.dump_metadata(TEST_FILE, data)

class Options(object):

    def __init__(self, col=None, format='csv', no_headers=True, limit=-1):
        self.col = col
        self.format = format
        self.no_headers = no_headers
        self.limit = limit


class TestReadApi(unittest.TestCase):

    def test_projection(self):
        pass

    def test_limit(self):
        """Test the limit option"""
        limit = 2
        expected_data = []
        with io.open(CSV_FILE, 'r', encoding="utf-8") as fo:
            expected_data = list(csv.reader(fo, delimiter='|'))[:limit]

        actual_raw_data = io.StringIO()
        parquet.dump(TEST_FILE, Options(limit=limit), out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter='\t'))

        self.assertListEqual(expected_data, actual_data)


class TestCompatibility(object):

    tc = unittest.TestCase('__init__')
    files = [(os.path.join(TEST_DATA, p), os.path.join(TEST_DATA, "nation.csv")) for p in
             ["gzip-nation.impala.parquet", "nation.dict.parquet",
              "nation.impala.parquet", "nation.plain.parquet",
              "snappy-nation.impala.parquet"]]

    def _test_file_csv(self, parquet_file, csv_file):
        """ Given the parquet_file and csv_file representation, converts the
            parquet_file to a csv using the dump utility and then compares the
            result to the csv_file.
        """
        expected_data = []
        with io.open(csv_file, 'r', encoding="utf-8") as f:
            expected_data = list(csv.reader(f, delimiter=PIPE_DELIM))

        actual_raw_data = io.StringIO()
        parquet.dump(parquet_file, Options(), out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter=TAB_DELIM))

        #assert expected_data == actual_data, "{0} != {1}".format(
        #    str(expected_data), str(actual_data))
        self.tc.assertListEqual(expected_data, actual_data)

        actual_raw_data = io.StringIO()
        parquet.dump(parquet_file, Options(no_headers=False),
                     out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter=TAB_DELIM))[1:]

        self.tc.assertListEqual(expected_data, actual_data)
        #assert expected_data == actual_data, "{0} != {1}".format(
        #    str(expected_data), str(actual_data))

    def _test_file_json(self, parquet_file, csv_file):
        """ Given the parquet_file and csv_file representation, converts the
            parquet_file to json using the dump utility and then compares the
            result to the csv_file using column agnostic ordering.
        """
        expected_data = []
        with io.open(csv_file, 'r', encoding='utf-8') as f:
            expected_data = list(csv.reader(f, delimiter=PIPE_DELIM))

        actual_raw_data = io.StringIO()
        parquet.dump(parquet_file, Options(format='json'),
                     out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = [json.loads(x.rstrip()) for x in
                       actual_raw_data.read().split("\n") if len(x) > 0]

        assert len(expected_data) == len(actual_data)
        footer = parquet.read_footer(parquet_file)
        cols = [s.name for s in footer.schema]
        for expected, actual in zip(expected_data, actual_raw_data):
            assert len(expected) == len(actual)
            for i, c in enumerate(cols):
                if c in actual:
                    assert expected[i] == actual[c]

    def _test_file_custom(self, parquet_file, csv_file):
        """ Given the parquet_file and csv_file representation, converts the
            parquet_file to json using the dump utility and then compares the
            result to the csv_file using column agnostic ordering.
        """
        expected_data = []
        with io.open(csv_file, 'r', encoding="utf-8") as f:
            expected_data = list(csv.reader(f, delimiter=PIPE_DELIM))

        actual_data = []
        with open(parquet_file, "rb") as parquet_fo:
            actual_data = list(parquet.DictReader(parquet_fo))

        self.tc.assertEquals(len(expected_data), len(actual_data))
        footer = parquet.read_footer(parquet_file)
        cols = [s.name for s in footer.schema]

        for expected, actual in zip(expected_data, actual_data):
            self.tc.assertEquals(len(expected), len(actual))
            for i, c in enumerate([c for c in cols if c in actual]):
                self.tc.assertEquals(expected[i],
                    actual[c].decode('utf-8') if type(actual[c]) is bytes \
                    # this makes '0' = 0, since csv reads all strings.
                    else str(actual[c]))

    def test_all_files(self):
        for parquet_file, csv_file in self.files:
            yield self._test_file_csv, parquet_file, csv_file
            yield self._test_file_json, parquet_file, csv_file
            yield self._test_file_custom, parquet_file, csv_file


class TestDefinitionlevel(unittest.TestCase):

    def test_null_int(self):
        with open(os.path.join(TEST_DATA, "test-null.parquet"), "rb") as parquet_fo:
            actual_data = list(parquet.DictReader(parquet_fo))

        self.assertListEqual(
            # this is the contents of test-null.parquet. Two records, one that is null.
            [{"foo": 1, "bar": 2}, {"foo": 1, "bar": None}],
            actual_data
        )
