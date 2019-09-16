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
from pyasn1_modules import rfc5208
from pyasn1_modules import rfc8410

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class PrivateKeyTestCase(unittest.TestCase):
    no_pub_key_pem_text = "MC4CAQAwBQYDK2VwBCIEINTuctv5E1hK1bbY8fdp+K06/nwoy/HU++CXqI9EdVhC"

    def setUp(self):
        self.asn1Spec = rfc5208.PrivateKeyInfo()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.no_pub_key_pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert asn1Object['privateKeyAlgorithm']['algorithm'] == rfc8410.id_Ed25519
        assert asn1Object['privateKey'].isValue
        assert asn1Object['privateKey'].prettyPrint()[0:10] == "0x0420d4ee"
        assert der_encoder.encode(asn1Object) == substrate


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
