"""test_read_support.py - unit and integration tests for reading parquet data."""

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
    """Test various file-level decoding functions."""

    def test_header_magic_bytes(self):
        """Test reading the header magic bytes."""
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"PAR1_some_bogus_data")
            t.flush()
            self.assertTrue(parquet._check_header_magic_bytes(t))

    def test_footer_magic_bytes(self):
        """Test reading the footer magic bytes."""
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"PAR1_some_bogus_data_PAR1")
            t.flush()
            self.assertTrue(parquet._check_footer_magic_bytes(t))

    def test_not_parquet_file(self):
        """Test reading a non-parquet file."""
        with tempfile.NamedTemporaryFile() as t:
            t.write(b"blah")
            t.flush()
            self.assertFalse(parquet._check_header_magic_bytes(t))
            self.assertFalse(parquet._check_footer_magic_bytes(t))


class TestMetadata(unittest.TestCase):
    """Test various metadata reading functions."""

    def test_footer_bytes(self):
        """Test reading the footer size value."""
        with io.open(TEST_FILE, 'rb') as fo:
            self.assertEquals(327, parquet._get_footer_size(fo))

    def test_read_footer(self):
        """Test reading the footer."""
        footer = parquet.read_footer(TEST_FILE)
        self.assertEquals(
            set([s.name for s in footer.schema]),
            set(["schema", "n_regionkey", "n_name", "n_nationkey",
                 "n_comment"]))

    def test_dump_metadata(self):
        """Test dumping metadata."""
        data = io.StringIO()
        parquet.dump_metadata(TEST_FILE, data)


class Options(object):
    """Fake Options (a la `__main__.py`)."""

    def __init__(self, col=None, format='csv', no_headers=True, limit=-1):
        """Create a fake options."""
        self.col = col
        self.format = format
        self.no_headers = no_headers
        self.limit = limit


class TestReadApi(unittest.TestCase):
    """Test the read apis."""

    def test_limit(self):
        """Test the limit option."""
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
    """Integration tests for compatibility with reference parquet files."""

    tc = unittest.TestCase('__init__')
    files = [(os.path.join(TEST_DATA, p), os.path.join(TEST_DATA, "nation.csv")) for p in
             ["gzip-nation.impala.parquet", "nation.dict.parquet",
              "nation.impala.parquet", "nation.plain.parquet",
              "snappy-nation.impala.parquet"]]

    def _test_file_csv(self, parquet_file, csv_file):
        """Test the dump function by outputting to a csv file.

        Given the parquet_file and csv_file representation, converts the parquet_file to a csv
        using the dump utility and then compares the result to the csv_file.
        """
        expected_data = []
        with io.open(csv_file, 'r', encoding="utf-8") as f:
            expected_data = list(csv.reader(f, delimiter=PIPE_DELIM))

        actual_raw_data = io.StringIO()
        parquet.dump(parquet_file, Options(), out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter=TAB_DELIM))

        self.tc.assertListEqual(expected_data, actual_data)

        actual_raw_data = io.StringIO()
        parquet.dump(parquet_file, Options(no_headers=False),
                     out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter=TAB_DELIM))[1:]

        self.tc.assertListEqual(expected_data, actual_data)

    def _test_file_json(self, parquet_file, csv_file):
        """Test the dump function by outputting to a json file.

        Given the parquet_file and csv_file representation, converts the parquet_file to json using
        the dump utility and then compares the result to the csv_file using column agnostic ordering.
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
        """Test the DictReader function against csv data.

        Given the parquet_file and csv_file representation, reads the parquet file using DictReader
        and then compares the result to the csv_file using column agnostic ordering.
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
                self.tc.assertEquals(
                    expected[i],
                    actual[c].decode('utf-8') if type(actual[c]) is bytes \
                    # this makes '0' = 0, since csv reads all strings.
                    else str(actual[c]))

    def test_all_files(self):
        """Test all files using the three above test functions.

        This function generates additional tests.
        """
        for parquet_file, csv_file in self.files:
            yield self._test_file_csv, parquet_file, csv_file
            yield self._test_file_json, parquet_file, csv_file
            yield self._test_file_custom, parquet_file, csv_file


class TestDefinitionLevel(unittest.TestCase):
    """Test the DefinitionLevel handling."""

    def test_null_int(self):
        """Test reading a file that contains null records."""
        with open(os.path.join(TEST_DATA, "test-null.parquet"), "rb") as parquet_fo:
            actual_data = list(parquet.DictReader(parquet_fo))

        self.assertListEqual(
            # this is the contents of test-null.parquet. Two records, one that is null.
            [{"foo": 1, "bar": 2}, {"foo": 1, "bar": None}],
            actual_data
        )

    def test_converted_type_null(self):
        """Test reading a file that contains null records for a plain column that is converted to utf-8."""
        with open(os.path.join(TEST_DATA, "test-converted-type-null.parquet"), "rb") as parquet_fo:
            actual_data = list(parquet.DictReader(parquet_fo))

        self.assertListEqual(
            # this is the contents of test-converted-type-null.parquet. 2 records.
            [{"foo": "bar"}, {"foo": None}],
            actual_data
        )

    def test_null_plain_dictionary(self):
        """Test reading a file that contains null records for a plain dictionary column."""
        with open(os.path.join(TEST_DATA, "test-null-dictionary.parquet"), "rb") as parquet_fo:
            actual_data = list(parquet.DictReader(parquet_fo))

        self.assertListEqual(
            # this is the contents of test-null-dictionary.parquet. 7 records.
            # The first record is null, and the rest alternate between values of 'bar' and 'baz.'
            [{"foo": None}] + [{"foo": "bar"}, {"foo": "baz"}] * 3,
            actual_data
        )
