# -*- coding: utf-8 -*-

import unittest

class TestUnicodeInAssertion(unittest.TestCase):

    def test_unicodeInAssertion(self):
        print "Wurst!"
        raise ValueError("Käse!")
