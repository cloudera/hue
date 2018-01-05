import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from configobj import ConfigObj, get_extra_values
from validate import Validator

thisdir = os.path.dirname(os.path.join(os.getcwd(), __file__))
inipath = os.path.join(thisdir, 'conf.ini')
specpath = os.path.join(thisdir, 'conf.spec')


class TestValidateErrors(unittest.TestCase):
    
    def test_validate_no_valid_entries(self):
        conf = ConfigObj(inipath, configspec=specpath)
        
        validator = Validator()
        result = conf.validate(validator)
        self.assertFalse(result)
    
    
    def test_validate_preserve_errors(self):
        conf = ConfigObj(inipath, configspec=specpath)
        
        validator = Validator()
        result = conf.validate(validator, preserve_errors=True)
        
        self.assertFalse(result['value'])
        self.assertFalse(result['missing-section'])
        
        section = result['section']
        self.assertFalse(section['value'])
        self.assertFalse(section['sub-section']['value'])
        self.assertFalse(section['missing-subsection'])
        
    
    def test_validate_extra_values(self):
        conf = ConfigObj(inipath, configspec=specpath)
        conf.validate(Validator(), preserve_errors=True)
        
        self.assertEqual(conf.extra_values, ['extra', 'extra-section'])
        
        self.assertEqual(conf['section'].extra_values, ['extra-sub-section'])
        self.assertEqual(conf['section']['sub-section'].extra_values,
                         ['extra'])
        
    
    def test_get_extra_values(self):
        conf = ConfigObj(inipath, configspec=specpath)
        
        conf.validate(Validator(), preserve_errors=True)
        extra_values = get_extra_values(conf)
        
        expected = sorted([
            ((), 'extra'),
            ((), 'extra-section'),
            (('section', 'sub-section'), 'extra'),
            (('section',), 'extra-sub-section'),
        ])
        self.assertEqual(sorted(extra_values), expected)

if __name__ == '__main__':
    unittest.main()
