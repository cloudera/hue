#! /usr/bin/env python

# $Id: test_io.py 8098 2017-05-31 21:34:55Z milde $
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Test module for io.py.
"""

import unittest, sys
import DocutilsTestSupport              # must be imported before docutils
from docutils import io
from docutils._compat import b, bytes
from docutils.utils.error_reporting import locale_encoding
from test_error_reporting import BBuf, UBuf

class mock_stdout(UBuf):
    encoding = 'utf8'

    def __init__(self):
        self.buffer = BBuf()
        UBuf.__init__(self)

class HelperTests(unittest.TestCase):

    def test_check_encoding_true(self):
        """Return `True` if lookup returns the same codec"""
        self.assertEqual(io.check_encoding(mock_stdout, 'utf8'), True)
        self.assertEqual(io.check_encoding(mock_stdout, 'utf-8'), True)
        self.assertEqual(io.check_encoding(mock_stdout, 'UTF-8'), True)

    def test_check_encoding_false(self):
        """Return `False` if lookup returns different codecs"""
        self.assertEqual(io.check_encoding(mock_stdout, 'ascii'), False)
        self.assertEqual(io.check_encoding(mock_stdout, 'latin-1'), False)

    def test_check_encoding_none(self):
        """Cases where the comparison fails."""
        # stream.encoding is None:
        self.assertEqual(io.check_encoding(io.FileInput(), 'ascii'), None)
        # stream.encoding does not exist:
        self.assertEqual(io.check_encoding(BBuf, 'ascii'), None)
        # encoding is None:
        self.assertEqual(io.check_encoding(mock_stdout, None), None)
        # encoding is invalid
        self.assertEqual(io.check_encoding(mock_stdout, 'UTF-9'), None)


class InputTests(unittest.TestCase):

    def test_bom(self):
        input = io.StringInput(source=b('\xef\xbb\xbf foo \xef\xbb\xbf bar'),
                               encoding='utf8')
        # Assert BOMs are gone.
        self.assertEqual(input.read(), u' foo  bar')
        # With unicode input:
        input = io.StringInput(source=u'\ufeff foo \ufeff bar')
        # Assert BOMs are still there.
        self.assertEqual(input.read(), u'\ufeff foo \ufeff bar')

    def test_coding_slug(self):
        input = io.StringInput(source=b("""\
.. -*- coding: ascii -*-
data
blah
"""))
        data = input.read()
        self.assertEqual(input.successful_encoding, 'ascii')
        input = io.StringInput(source=b("""\
#! python
# -*- coding: ascii -*-
print "hello world"
"""))
        data = input.read()
        self.assertEqual(input.successful_encoding, 'ascii')
        input = io.StringInput(source=b("""\
#! python
# extraneous comment; prevents coding slug from being read
# -*- coding: ascii -*-
print "hello world"
"""))
        data = input.read()
        self.assertNotEqual(input.successful_encoding, 'ascii')

    def test_bom_detection(self):
        source = u'\ufeffdata\nblah\n'
        input = io.StringInput(source=source.encode('utf-16-be'))
        data = input.read()
        self.assertEqual(input.successful_encoding, 'utf-16-be')
        input = io.StringInput(source=source.encode('utf-16-le'))
        data = input.read()
        self.assertEqual(input.successful_encoding, 'utf-16-le')
        input = io.StringInput(source=source.encode('utf-8'))
        data = input.read()
        self.assertEqual(input.successful_encoding, 'utf-8')

    def test_readlines(self):
        input = io.FileInput(source_path='data/include.txt')
        data = input.readlines()
        self.assertEqual(data, [u'Some include text.\n'])

    def test_heuristics_utf8(self):
        # if no encoding is given, try decoding with utf8:
        input = io.FileInput(source_path='functional/input/cyrillic.txt')
        data = input.read()
        if sys.version_info < (3,0):
            # in Py3k, the locale encoding is used without --input-encoding
            # skipping the heuristic
            self.assertEqual(input.successful_encoding, 'utf-8')

    def test_heuristics_no_utf8(self):
        # if no encoding is given and decoding with utf8 fails,
        # use either the locale encoding (if specified) or latin-1:
        if sys.version_info >= (3,0) and locale_encoding != "utf8":
            # in Py3k, the locale encoding is used without --input-encoding
            # skipping the heuristic unless decoding fails.
            return
        probed_encodings = (locale_encoding, 'latin-1')
        input = io.FileInput(source_path='data/latin1.txt')
        data = input.read()
        if input.successful_encoding not in probed_encodings:
            raise AssertionError(
                "guessed encoding '%s' differs from probed encodings %r"
                % (input.successful_encoding, probed_encodings))
        if input.successful_encoding == 'latin-1':
            self.assertEqual(data, u'Gr\xfc\xdfe\n')

    def test_decode_unicode(self):
        # With the special value "unicode" or "Unicode":
        uniinput = io.Input(encoding='unicode')
        # keep unicode instances as-is
        self.assertEqual(uniinput.decode(u'ja'), u'ja')
        # raise AssertionError if data is not an unicode string
        self.assertRaises(AssertionError, uniinput.decode, b('ja'))


class OutputTests(unittest.TestCase):

    bdata = b('\xfc')
    udata = u'\xfc'

    def setUp(self):
        self.bdrain = BBuf()
        """Buffer accepting binary strings (bytes)"""
        self.udrain = UBuf()
        """Buffer accepting unicode strings"""
        self.mock_stdout = mock_stdout()
        """Stub of sys.stdout under Python 3"""

    def test_write_unicode(self):
        fo = io.FileOutput(destination=self.udrain, encoding='unicode',
                           autoclose=False)
        fo.write(self.udata)
        self.assertEqual(self.udrain.getvalue(), self.udata)

    def test_write_utf8(self):
        if sys.version_info >= (3,0):
            fo = io.FileOutput(destination=self.udrain, encoding='utf8',
                               autoclose=False)
            fo.write(self.udata)
            self.assertEqual(self.udrain.getvalue(), self.udata)
        else:
            fo = io.FileOutput(destination=self.bdrain, encoding='utf8',
                               autoclose=False)
            fo.write(self.udata)
            self.assertEqual(self.bdrain.getvalue(), self.udata.encode('utf8'))

    # With destination in binary mode, data must be binary string
    # and is written as-is:
    def test_write_bytes(self):
        fo = io.FileOutput(destination=self.bdrain, encoding='utf8',
                           mode='wb', autoclose=False)
        fo.write(self.bdata)
        self.assertEqual(self.bdrain.getvalue(), self.bdata)

    # Test for Python 3 features:
    if sys.version_info >= (3,0):
        def test_write_bytes_to_stdout(self):
            # try writing data to `destination.buffer`, if data is
            # instance of `bytes` and writing to `destination` fails:
            fo = io.FileOutput(destination=self.mock_stdout)
            fo.write(self.bdata)
            self.assertEqual(self.mock_stdout.buffer.getvalue(),
                             self.bdata)

        def test_encoding_clash_resolved(self):
            fo = io.FileOutput(destination=self.mock_stdout,
                               encoding='latin1', autoclose=False)
            fo.write(self.udata)
            self.assertEqual(self.mock_stdout.buffer.getvalue(),
                             self.udata.encode('latin1'))

        def test_encoding_clash_nonresolvable(self):
            del(self.mock_stdout.buffer)
            fo = io.FileOutput(destination=self.mock_stdout,
                               encoding='latin1', autoclose=False)
            self.assertRaises(ValueError, fo.write, self.udata)


if __name__ == '__main__':
    unittest.main()
