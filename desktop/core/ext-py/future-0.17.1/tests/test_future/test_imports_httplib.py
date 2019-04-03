from __future__ import absolute_import, print_function
import sys

from future.utils import PY2
from future.tests.base import unittest


class ImportHttplibTest(unittest.TestCase):
    def test_issue_159(self):
        """
        The latest version of urllib3 (as of 2015-07-25)
        uses http.client.HTTPMessage, which isn't normally
        exported on Py2 through __all__ in httplib.py.
        """
        from http.client import HTTPMessage
        if PY2:
            import mimetools
            assert issubclass(HTTPMessage, mimetools.Message)
        else:
            import email.message
            assert issubclass(HTTPMessage, email.message.Message)


if __name__ == '__main__':
    unittest.main()
