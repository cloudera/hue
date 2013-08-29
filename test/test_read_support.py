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

    f = "/Users/joecrow/Code/parquet-compatibility/parquet-testdata/impala/1.1.1-SNAPPY/nation.impala.parquet"

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


class TestCompatibility(unittest.TestCase):

    files = []

    def _test_file(self, parquet_file, csv_file):
        """ Given the parquet_file and csv_file representation, converts the
            parquet_file to a csv using the dump utility and then compares the
            result to the csv_file using column agnostic ordering.
        """
        pass

    def test_all_files(self):
        for parquet_file, csv_file in self.files:
            yield self._test_file, parquet_file, csv_file
