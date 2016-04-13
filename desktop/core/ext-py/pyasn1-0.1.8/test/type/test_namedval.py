from pyasn1.type import namedval
from pyasn1.error import PyAsn1Error
from sys import version_info
if version_info[0:2] < (2, 7) or \
   version_info[0:2] in ( (3, 0), (3, 1) ):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest

class NamedValuesCaseBase(unittest.TestCase):
    def setUp(self):
        self.e = namedval.NamedValues(('off', 0), ('on', 1))
    def testIter(self):
        off, on = self.e
        assert off == ('off', 0) or of == ('on', 1), 'unpack fails'
    def testRepr(self):
        assert eval(repr(self.e), { 'NamedValues': namedval.NamedValues }) == self.e, 'repr() fails'

if __name__ == '__main__': unittest.main()
