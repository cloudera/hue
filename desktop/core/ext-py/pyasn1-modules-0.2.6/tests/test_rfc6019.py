#
# This file is part of pyasn1-modules software.
#
# Copyright (c) 2019, Vigil Security, LLC
# License: http://snmplabs.com/pyasn1/license.html
#
import sys

from pyasn1.codec.der.decoder import decode as der_decode
from pyasn1.codec.der.encoder import encode as der_encode

from pyasn1.type import univ

from pyasn1_modules import pem
from pyasn1_modules import rfc5652
from pyasn1_modules import rfc6019

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class BinarySigningTimeTestCase(unittest.TestCase):
    pem_text = "MBUGCyqGSIb3DQEJEAIuMQYCBFy/hlQ="

    def setUp(self):
        self.asn1Spec = rfc5652.Attribute()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.pem_text)

        asn1Object, rest = der_decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encode(asn1Object) == substrate

        assert asn1Object['attrType'] == rfc6019.id_aa_binarySigningTime
        bintime, rest = der_decode(asn1Object['attrValues'][0],
                                   asn1Spec=rfc6019.BinaryTime())
        assert bintime == 0x5cbf8654

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.pem_text)
        
        rfc5652.cmsAttributesMap.update(rfc6019.cmsAttributesMapUpdate)
        asn1Object, rest = der_decode(substrate,
                                      asn1Spec=self.asn1Spec,
                                      decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encode(asn1Object) == substrate

        assert asn1Object['attrType'] in rfc5652.cmsAttributesMap.keys()
        assert asn1Object['attrValues'][0] == 0x5cbf8654


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
