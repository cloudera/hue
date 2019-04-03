"""
Tests for the html module functions.

Adapted for the python-future module from the Python 3.3 standard library tests.
"""

from __future__ import unicode_literals
from future import standard_library

with standard_library.hooks():
    import html

from future.tests.base import unittest


class HtmlTests(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(
            html.escape('\'<script>"&foo;"</script>\''),
            '&#x27;&lt;script&gt;&quot;&amp;foo;&quot;&lt;/script&gt;&#x27;')
        self.assertEqual(
            html.escape('\'<script>"&foo;"</script>\'', False),
            '\'&lt;script&gt;"&amp;foo;"&lt;/script&gt;\'')


if __name__ == '__main__':
    unittest.main()
