from __future__ import with_statement

import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from configobj import ConfigObj

try:
    # Python 2.6 only
    from warnings import catch_warnings
except ImportError:
    # this will cause an error, but at least the other tests
    # will run on Python 2.5
    catch_warnings = None

class TestConfigObj(unittest.TestCase):
    
    def test_order_preserved(self):
        c = ConfigObj()
        c['a'] = 1
        c['b'] = 2
        c['c'] = 3
        c['section'] = {}
        c['section']['a'] = 1
        c['section']['b'] = 2
        c['section']['c'] = 3
        c['section']['section'] = {}
        c['section']['section2'] = {}
        c['section']['section3'] = {}
        c['section2'] = {}
        c['section3'] = {}
        
        c2 = ConfigObj(c)
        self.assertEqual(c2.scalars, ['a', 'b', 'c'])
        self.assertEqual(c2.sections, ['section', 'section2', 'section3'])
        self.assertEqual(c2['section'].scalars, ['a', 'b', 'c'])
        self.assertEqual(c2['section'].sections, ['section', 'section2', 'section3'])
        
        self.assertFalse(c['section'] is c2['section'])
        self.assertFalse(c['section']['section'] is c2['section']['section'])
    
    if catch_warnings is not None:
        # poor man's skipTest
        def test_options_deprecation(self):
            with catch_warnings(record=True) as log:
                ConfigObj(options={})
            
            # unpack the only member of log
            warning, = log
            self.assertEqual(warning.category, DeprecationWarning)
    
    def test_list_members(self):
        c = ConfigObj()
        c['a'] = []
        c['a'].append('foo')
        self.assertEqual(c['a'], ['foo'])
    
    def test_list_interpolation_with_pop(self):
        c = ConfigObj()
        c['a'] = []
        c['a'].append('%(b)s')
        c['b'] = 'bar'
        self.assertEqual(c.pop('a'), ['bar'])
    
    def test_with_default(self):
        c = ConfigObj()
        c['a'] = 3
        
        self.assertEqual(c.pop('a'), 3)
        self.assertEqual(c.pop('b', 3), 3)
        self.assertRaises(KeyError, c.pop, 'c')
    
    
    def test_interpolation_with_section_names(self):
        cfg = """
item1 = 1234
[section]
    [[item1]]
    foo='bar'
    [[DEFAULT]]
        [[[item1]]]
        why = would you do this?
    [[other-subsection]]
    item2 = '$item1'""".splitlines()
        c = ConfigObj(cfg, interpolation='Template')
        
        # This raises an exception in 4.7.1 and earlier due to the section
        # being found as the interpolation value
        repr(c)
    
    def test_interoplation_repr(self):
        c = ConfigObj(['foo = $bar'], interpolation='Template')
        c['baz'] = {}
        c['baz']['spam'] = '%(bar)s'
        
        # This raises a MissingInterpolationOption exception in 4.7.1 and earlier
        repr(c)

