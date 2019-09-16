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
from pyasn1_modules import rfc5649

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class AESKeyWrapTestCase(unittest.TestCase):
    kw_alg_id_pem_text = "MAsGCWCGSAFlAwQBLQ=="

    def setUp(self):
        self.asn1Spec = rfc5649.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.kw_alg_id_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc5649.id_aes256_wrap
        assert der_encoder.encode(asn1Object) == substrate


class AESKeyWrapWithPadTestCase(unittest.TestCase):
    kw_pad_alg_id_pem_text = "MAsGCWCGSAFlAwQBMA=="

    def setUp(self):
        self.asn1Spec = rfc5649.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.kw_pad_alg_id_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc5649.id_aes256_wrap_pad
        assert der_encoder.encode(asn1Object) == substrate


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
