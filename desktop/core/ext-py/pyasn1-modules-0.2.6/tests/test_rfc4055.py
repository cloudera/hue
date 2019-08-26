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

from pyasn1.type import univ

from pyasn1_modules import pem
from pyasn1_modules import rfc5280
from pyasn1_modules import rfc4055

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class PSSDefautTestCase(unittest.TestCase):
    pss_default_pem_text = "MAsGCSqGSIb3DQEBCg=="

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.pss_default_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc4055.id_RSASSA_PSS
        assert der_encoder.encode(asn1Object) == substrate
        assert substrate == der_encoder.encode(asn1Object)

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.pss_default_pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        assert not asn1Object['parameters'].hasValue()


class PSSSHA512TestCase(unittest.TestCase):
    pss_sha512_pem_text = "MDwGCSqGSIb3DQEBCjAvoA8wDQYJYIZIAWUDBAIDBQChHDAaBgkqhkiG9w0BAQgwDQYJYIZIAWUDBAIDBQA="

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.pss_sha512_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc4055.id_RSASSA_PSS
        assert der_encoder.encode(asn1Object) == substrate
        assert substrate == der_encoder.encode(asn1Object)

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.pss_sha512_pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        assert asn1Object['parameters'].hasValue()
        assert asn1Object['parameters']['saltLength'] == 20


class OAEPDefautTestCase(unittest.TestCase):
    oaep_default_pem_text = "MAsGCSqGSIb3DQEBBw=="

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.oaep_default_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc4055.id_RSAES_OAEP
        assert der_encoder.encode(asn1Object) == substrate
        assert substrate == der_encoder.encode(asn1Object)

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.oaep_default_pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        assert not asn1Object['parameters'].hasValue()


class OAEPSHA256TestCase(unittest.TestCase):
    oaep_sha256_pem_text = "MDwGCSqGSIb3DQEBBzAvoA8wDQYJYIZIAWUDBAIBBQChHDAaBgkqhkiG9w0BAQgwDQYJYIZIAWUDBAIBBQA="

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.oaep_sha256_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc4055.id_RSAES_OAEP
        assert der_encoder.encode(asn1Object) == substrate
        assert substrate == der_encoder.encode(asn1Object)

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.oaep_sha256_pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        assert asn1Object['parameters'].hasValue()
        oaep_p = asn1Object['parameters']
        assert oaep_p['hashFunc']['parameters'] == univ.Null("")
        assert oaep_p['maskGenFunc']['parameters']['parameters'] == univ.Null("")


class OAEPFullTestCase(unittest.TestCase):
    oaep_full_pem_text = "MFMGCSqGSIb3DQEBBzBGoA8wDQYJYIZIAWUDBAICBQChHDAaBgkqhkiG9w0BAQgwDQYJYIZIAWUDBAICBQCiFTATBgkqhkiG9w0BAQkEBmZvb2Jhcg=="

    def setUp(self):
        self.asn1Spec = rfc5280.AlgorithmIdentifier()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.oaep_full_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object[0] == rfc4055.id_RSAES_OAEP
        assert der_encoder.encode(asn1Object) == substrate
        assert substrate == der_encoder.encode(asn1Object)

    def testOpenTypes(self):
        substrate = pem.readBase64fromText(self.oaep_full_pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate
        assert asn1Object['parameters'].hasValue()
        oaep_p = asn1Object['parameters']
        assert oaep_p['hashFunc']['parameters'] == univ.Null("")
        assert oaep_p['maskGenFunc']['parameters']['parameters'] == univ.Null("")
        assert oaep_p['pSourceFunc']['parameters'] == univ.OctetString(value='foobar')


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys
	
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
