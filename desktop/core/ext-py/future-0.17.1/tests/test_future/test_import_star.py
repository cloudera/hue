"""
This tests whether

    from future.builtins import *

works as expected:
- This should NOT introduce namespace pollution on Py3.
- On Python 2, this should not introduce any symbols that aren't in
  __builtin__.

"""

from __future__ import absolute_import, print_function, unicode_literals

import copy

from future import utils
from future.tests.base import unittest, skip26


original_locals = set(copy.copy(locals()))
original_globals = set(copy.copy(globals()))
new_names = set(['original_locals', 'original_globals', 'new_names'])
from future.builtins import *
new_locals = set(copy.copy(locals())) - new_names - original_locals
new_globals = set(copy.copy(globals())) - new_names - original_globals - \
              set(['new_locals'])


class TestImportStar(unittest.TestCase):
    def test_namespace_pollution_locals(self):
        if utils.PY3:
            self.assertEqual(len(new_locals), 0,
                             'namespace pollution: {0}'.format(new_locals))
        else:
            pass   # maybe check that no new symbols are introduced

    def test_namespace_pollution_globals(self):
        if utils.PY3:
            self.assertEqual(len(new_globals), 0,
                             'namespace pollution: {0}'.format(new_globals))
        else:
            pass   # maybe check that no new symbols are introduced

    def test_iterators(self):
        self.assertNotEqual(type(range(10)), list)

    def test_super(self):
        pass

    def test_str(self):
        self.assertIsNot(str, bytes)            # Py2: assertIsNot only in 2.7
        self.assertEqual(str('blah'), u'blah')  # Py3.3 and Py2 only

    def test_python_2_unicode_compatible_decorator(self):
        # This should not be in the namespace
        assert 'python_2_unicode_compatible' not in locals()


if __name__ == '__main__':
    unittest.main()
