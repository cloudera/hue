"""
Py2 only. int tests involving division for the case that:

    >>> from __future__ import division

is not in effect.
"""

from __future__ import (absolute_import,
                        print_function, unicode_literals)
from future import standard_library
from future.builtins import *
from future.tests.base import unittest
from future.utils import PY2

import sys
import random


@unittest.skipIf(not PY2, 'old division tests only for Py2')
class IntTestCasesOldDivision(unittest.TestCase):

    def setUp(self):
        self.longMessage = True


    def test_div(self):
        """
        Issue #38
        """
        a = int(3)
        self.assertEqual(a / 5., 0.6)
        self.assertEqual(a / 5, 0)


    def test_idiv(self):
        a = int(3)
        a /= 2
        self.assertEqual(a, 1)
        self.assertTrue(isinstance(a, int))
        b = int(10)
        b /= 2
        self.assertEqual(b, 5)
        self.assertTrue(isinstance(b, int))
        c = int(-3)
        c /= 2.0
        self.assertEqual(c, -1.5)
        self.assertTrue(isinstance(c, float))


    def test_truediv(self):
        """
        Test int.__truediv__ and friends (rtruediv, itruediv)
        """
        a = int(3)
        self.assertEqual(a / 2, 1)  # since "from __future__ import division"
                                      # is in effect
        self.assertEqual(type(a / 2), int)

        b = int(2)
        self.assertEqual(a / b, 1)  # since "from __future__ import division"
                                      # is in effect
        self.assertEqual(type(a / b), int)

        c = int(3) / b
        self.assertEqual(c, 1)
        self.assertTrue(isinstance(c, int))

        d = int(5)
        d /= 5
        self.assertEqual(d, 1)
        self.assertTrue(isinstance(d, int))

        e = int(10)
        f = int(20)
        e /= f
        self.assertEqual(e, 0)
        self.assertTrue(isinstance(e, int))


    def test_divmod(self):
        """
        Test int.__divmod__
        """
        vals = [10**i for i in range(0, 20)]
        for i in range(200):
            x = random.choice(vals)
            y = random.choice(vals)
            self.assertEqual(int(y).__rdivmod__(int(x)), divmod(x, y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(-y).__rdivmod__(int(x)), divmod(x, -y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(y).__rdivmod__(int(-x)), divmod(-x, y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(-y).__rdivmod__(int(-x)), divmod(-x, -y), msg='x={0}; y={1}'.format(x, y))

            self.assertEqual(int(x).__rdivmod__(int(y)), long(x).__rdivmod__(y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(-x).__rdivmod__(int(y)), long(-x).__rdivmod__(y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(x).__rdivmod__(int(-y)), long(x).__rdivmod__(-y), msg='x={0}; y={1}'.format(x, y))
            self.assertEqual(int(-x).__rdivmod__(int(-y)), long(-x).__rdivmod__(-y), msg='x={0}; y={1}'.format(x, y))


if __name__ == "__main__":
    unittest.main()
