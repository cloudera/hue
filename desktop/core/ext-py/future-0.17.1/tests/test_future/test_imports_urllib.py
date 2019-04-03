from __future__ import absolute_import, print_function

import sys
from future.tests.base import unittest
from future.standard_library import install_aliases


class ImportUrllibTest(unittest.TestCase):
    def test_urllib(self):
        """
        Tests that urllib isn't changed from under our feet. (This might not
        even be a problem?)
        """
        from future import standard_library
        import urllib
        orig_file = urllib.__file__
        with standard_library.hooks():
            import urllib.response
        self.assertEqual(orig_file, urllib.__file__)

    def test_issue_158(self):
        """
        CherryPy conditional import in _cpcompat.py: issue 158
        """
        install_aliases()
        try:
            from urllib.parse import unquote as parse_unquote

            def unquote_qs(atom, encoding, errors='strict'):
                return parse_unquote(
                    atom.replace('+', ' '),
                    encoding=encoding,
                    errors=errors)
        except ImportError:
            from urllib import unquote as parse_unquote

            def unquote_qs(atom, encoding, errors='strict'):
                return parse_unquote(atom.replace('+', ' ')).decode(encoding, errors)
        self.assertEqual(unquote_qs('/%7Econnolly/', 'utf-8'),
                         '/~connolly/')


if __name__ == '__main__':
    unittest.main()
