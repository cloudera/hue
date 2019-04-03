"""
Tests for the future.standard_library module
"""

from __future__ import absolute_import, print_function
from future import standard_library
from future import utils
from future.tests.base import unittest, CodeHandler, expectedFailurePY2

import sys
import tempfile
import os
import copy
import textwrap
from subprocess import CalledProcessError


class TestChainMap(CodeHandler):

    def setUp(self):
        self.interpreter = sys.executable
        standard_library.install_aliases()
        super(TestChainMap, self).setUp()

    def tearDown(self):
        # standard_library.remove_hooks()
        pass

    @staticmethod
    def simple_cm():
        from collections import ChainMap
        c = ChainMap()
        c['one'] = 1
        c['two'] = 2
    
        cc = c.new_child()
        cc['one'] = 'one'
    
        return c, cc
    
    
    def test_repr(self):
        c, cc = TestChainMap.simple_cm()
    
        order1 = "ChainMap({'one': 'one'}, {'one': 1, 'two': 2})"
        order2 = "ChainMap({'one': 'one'}, {'two': 2, 'one': 1})"
        assert repr(cc) in [order1, order2]
    
    
    def test_recursive_repr(self):
        """
        Test for degnerative recursive cases. Very unlikely in
        ChainMaps. But all must bow before the god of testing coverage.
        """
        from collections import ChainMap
        c = ChainMap()
        c['one'] = c
        assert repr(c) == "ChainMap({'one': ...})"
    
    
    def test_get(self):
        c, cc = TestChainMap.simple_cm()
    
        assert cc.get('two') == 2
        assert cc.get('three') == None
        assert cc.get('three', 'notthree') == 'notthree'
    
    
    def test_bool(self):
        from collections import ChainMap
        c = ChainMap()
        assert not(bool(c))
    
        c['one'] = 1
        c['two'] = 2
        assert bool(c)
    
        cc = c.new_child()
        cc['one'] = 'one'
        assert cc
    
    
    def test_fromkeys(self):
        from collections import ChainMap
        keys = 'a b c'.split()
        c = ChainMap.fromkeys(keys)
        assert len(c) == 3
        assert c['a'] == None
        assert c['b'] == None
        assert c['c'] == None
    
    
    def test_copy(self):
        c, cc = TestChainMap.simple_cm()
        new_cc = cc.copy()
        assert new_cc is not cc
        assert sorted(new_cc.items()) == sorted(cc.items())
    
    
    def test_parents(self):
        c, cc = TestChainMap.simple_cm()
    
        new_c = cc.parents
        assert c is not new_c
        assert len(new_c) == 2
        assert new_c['one'] == c['one']
        assert new_c['two'] == c['two']
    
    
    def test_delitem(self):
        c, cc = TestChainMap.simple_cm()
    
        with self.assertRaises(KeyError):
            del cc['two']
    
        del cc['one']
        assert len(cc) == 2
        assert cc['one'] == 1
        assert cc['two'] == 2
    
    
    def test_popitem(self):
        c, cc = TestChainMap.simple_cm()
    
        assert cc.popitem() == ('one', 'one')
    
        with self.assertRaises(KeyError):
            cc.popitem()
    
    
    def test_pop(self):
        c, cc = TestChainMap.simple_cm()
    
        assert cc.pop('one') == 'one'
    
        with self.assertRaises(KeyError):
            cc.pop('two')
    
        assert len(cc) == 2
    
    
    def test_clear(self):
        c, cc = TestChainMap.simple_cm()
    
        cc.clear()
        assert len(cc) == 2
        assert cc['one'] == 1
        assert cc['two'] == 2
    
    
    def test_missing(self):
    
        c, cc = TestChainMap.simple_cm()
    
        with self.assertRaises(KeyError):
            cc['clown']


if __name__ == '__main__':
    unittest.main()
