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
from pyasn1_modules import rfc5083

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class AuthEnvelopedDataTestCase(unittest.TestCase):
    pem_text = """\
MIICdQIBADGCAiekggIjBgsqhkiG9w0BCRANATCCAhICAQAEE3B0Zi1rbWM6MTM2MTQxMjIx
MTIwDQYLKoZIhvcNAQkQAzAwCwYJYIZIAWUDBAEtMIIBsDCCAawCAQKAFJ7rZ8m5WnTUTS8W
OWaA6AG1y6ScMA0GCSqGSIb3DQEBAQUABIIBgHfnHNqDbyyql2NqX6UQggelWMTjwzJJ1L2e
rbsj1bIAGmpIsUijw+fX8VOS7v1C9ui2Md9NFgCfkmKLo8T/jELqrk7MpMu09G5zDgeXzJfQ
DFc115wbrWAUU3XP7XIb6TNOc3xtq4UxA5V6jNUK2XyWKpjzOtM7gm0VWIJGVVlYu+u32LQc
CjRFb87kvOY/WEnjxQpCW8g+4V747Ud97dYpMub7TLJiRNZkdHnq8xEGKlXjVHSgc10lhphe
1kFGeCpfJEsqjtN7YsVzf65ri9Z+3FJ1IO4cnMDbzGhyRXkS7a0k58/miJbSj88PvzKNSURw
pu4YHMQQX/mjT2ey1SY4ihPMuxxgTdCa04L0UxaRr7xAucz3n2UWShelm3IIjnWRlYdXypnX
vKvwCLoeh5mJwUl1JNFPCQkQ487cKRyobUyNgXQKT4ZDHCgXciwsX5nTsom87Ixp5vqSDJ+D
hXA0r/Caiu1vnY5X9GLHSkqgXkgqgUuu0LfcsQERD8psfQQogbiuZDqJmYt1Iau/pkuGfmee
qeiM3aeQ4NZf9AFZUVWBGArPNHrvVDA3BgkqhkiG9w0BBwEwGwYJYIZIAWUDBAEuMA4EDMr+
ur76ztut3sr4iIANmvLRbyFUf87+2bPvLQQMoOWSXMGE4BckY8RM
"""

    def setUp(self):
        self.asn1Spec = rfc5083.AuthEnvelopedData()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.pem_text)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
