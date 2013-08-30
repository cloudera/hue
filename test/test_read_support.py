import csv
import os
import StringIO
import tempfile
import unittest

import parquet


class TestFileFormat(unittest.TestCase):
    def test_header_magic_bytes(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write("PAR1_some_bogus_data")
            t.flush()
            self.assertTrue(parquet._check_header_magic_bytes(t))

    def test_footer_magic_bytes(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write("PAR1_some_bogus_data_PAR1")
            t.flush()
            self.assertTrue(parquet._check_footer_magic_bytes(t))

    def test_not_parquet_file(self):
        with tempfile.NamedTemporaryFile() as t:
            t.write("blah")
            t.flush()
            self.assertFalse(parquet._check_header_magic_bytes(t))
            self.assertFalse(parquet._check_footer_magic_bytes(t))


class TestMetadata(unittest.TestCase):

    f = "test-data/nation.impala.parquet"

    def test_footer_bytes(self):
        with open(self.f) as fo:
            self.assertEquals(327, parquet._get_footer_size(fo))

    def test_read_footer(self):
        footer = parquet.read_footer(self.f)
        self.assertEquals(
            set([s.name for s in footer.schema]),
            set(["schema", "n_regionkey", "n_name", "n_nationkey",
                 "n_comment"]))

    def test_dump_metadata(self):
        data = StringIO.StringIO()
        parquet.dump_metadata(self.f, data)


class Options():
    col = None
    format = 'csv'
    no_headers = True
    limit = -1


class TestCompatibility(object):

    td = "test-data"
    files = [(os.path.join(td, p), os.path.join(td, "nation.csv")) for p in
             ["gzip-nation.impala.parquet", "nation.dict.parquet",
              "nation.impala.parquet", "nation.plain.parquet",
              "snappy-nation.impala.parquet"]]

    def _test_file_csv(self, parquet_file, csv_file):
        """ Given the parquet_file and csv_file representation, converts the
            parquet_file to a csv using the dump utility and then compares the
            result to the csv_file using column agnostic ordering.
        """
        expected_data = []
        with open(csv_file, 'rb') as f:
            expected_data = list(csv.reader(f, delimiter='|'))

        actual_raw_data = StringIO.StringIO()
        parquet.dump(parquet_file, Options(), out=actual_raw_data)
        actual_raw_data.seek(0, 0)
        actual_data = list(csv.reader(actual_raw_data, delimiter='\t'))

        assert expected_data == actual_data, "{0} != {1}".format(
            str(expected_data), str(actual_data))

    def test_all_files(self):
        for parquet_file, csv_file in self.files:
            yield self._test_file_csv, parquet_file, csv_file
