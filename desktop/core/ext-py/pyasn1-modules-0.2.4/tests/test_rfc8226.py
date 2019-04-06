#
# This file is part of pyasn1-modules software.
#
# Created by Russ Housley
# Copyright (c) 2019, Vigil Security, LLC
# License: http://snmplabs.com/pyasn1/license.html
#

import sys

from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder

from pyasn1_modules import pem
from pyasn1_modules import rfc8226

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class JWTClaimConstraintsTestCase(unittest.TestCase):
    jwtcc_pem_text = "MD2gBzAFFgNmb2+hMjAwMBkWA2ZvbzASDARmb28xDARmb28yDARmb28zMBMWA2JhcjAMDARiYXIxDARiYXIy"

    def setUp(self):
        self.asn1Spec = rfc8226.JWTClaimConstraints()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.jwtcc_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate


class TNAuthorizationListTestCase(unittest.TestCase):
    tnal_pem_text = "MCugBxYFYm9ndXOhEjAQFgo1NzE1NTUxMjEyAgIDFKIMFgo3MDM1NTUxMjEy"

    def setUp(self):
        self.asn1Spec = rfc8226.TNAuthorizationList()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.tnal_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
