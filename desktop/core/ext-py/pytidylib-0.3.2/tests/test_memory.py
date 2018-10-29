# Copyright 2009-2014 Jason Stitt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import unittest
from tidylib import tidy_document, tidy_fragment, sink

try:
    xrange
except NameError:
    xrange = range


class TestSinkMemory(unittest.TestCase):
    """ Make sure error sinks are cleared properly """

    def test_tidy_document(self):
        h = "<p>hello"
        for i in xrange(100):
            doc, err = tidy_document(h)
        self.assertEqual(sink.sinks, {})

    def test_tidy_fragment(self):
        h = "<p>hello"
        for i in xrange(100):
            doc, err = tidy_fragment(h)
        self.assertEqual(sink.sinks, {})


if __name__ == '__main__':
    unittest.main()
