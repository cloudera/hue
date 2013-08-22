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

	f = "/Users/joecrow/Code/parquet-compatibility/parquet-testdata/impala/1.0.4-SNAPPY/nation.impala.parquet"
	
	def testFooterBytes(self):
		with open(self.f) as fo:
			self.assertEquals(229, parquet._get_footer_size(fo))

	def testReadFOoter(self):
		parquet.read_footer(self.f)
