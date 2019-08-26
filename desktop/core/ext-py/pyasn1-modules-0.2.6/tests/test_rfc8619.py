#
# This file is part of pyasn1-modules software.
#
# Copyright (c) 2019, Vigil Security, LLC
# License: http://snmplabs.com/pyasn1/license.html
#
import sys

from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder

from pyasn1_modules import pem
from pyasn1_modules import rfc5280
from pyasn1_modules import rfc8619

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class HKDFSHA256TestCase(unittest.TestCase):
    alg_id_1_pem_text = "MA0GCyqGSIb3DQEJEAMc"

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):

        substrate = pem.readBase64fromText(self.alg_id_1_pem_text)

        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        
        assert asn1Object['algorithm'] == rfc8619.id_alg_hkdf_with_sha256


class HKDFSHA384TestCase(unittest.TestCase):
    alg_id_1_pem_text = "MA0GCyqGSIb3DQEJEAMd"

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):

        substrate = pem.readBase64fromText(self.alg_id_1_pem_text)

        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        
        assert asn1Object['algorithm'] == rfc8619.id_alg_hkdf_with_sha384


class HKDFSHA512TestCase(unittest.TestCase):
    alg_id_1_pem_text = "MA0GCyqGSIb3DQEJEAMe"

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):

        substrate = pem.readBase64fromText(self.alg_id_1_pem_text)

        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        
        assert asn1Object['algorithm'] == rfc8619.id_alg_hkdf_with_sha512


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
