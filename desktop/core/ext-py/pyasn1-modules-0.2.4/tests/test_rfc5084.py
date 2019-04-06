#
# This file is part of pyasn1-modules software.
#
# Created by Russ Housley
# Copyright (c) 2018, Vigil Security, LLC
# License: http://snmplabs.com/pyasn1/license.html
#

import sys

from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder

from pyasn1_modules import pem
from pyasn1_modules import rfc5084

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class CCMParametersTestCase(unittest.TestCase):
    ccm_pem_text = "MBEEDE2HVyIurFKUEX8MEgIBBA=="

    def setUp(self):
        self.asn1Spec = rfc5084.CCMParameters()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.ccm_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate


class GCMParametersTestCase(unittest.TestCase):
    gcm_pem_text = "MBEEDE2HVyIurFKUEX8MEgIBEA=="

    def setUp(self):
        self.asn1Spec = rfc5084.GCMParameters()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.gcm_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
