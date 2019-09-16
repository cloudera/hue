#
# This file is part of pyasn1-modules software.
#
# Created by Russ Housley
# Copyright (c) 2018, 2019  Vigil Security, LLC
# License: http://snmplabs.com/pyasn1/license.html
#

import sys

from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder

from pyasn1_modules import pem
from pyasn1_modules import rfc5652
from pyasn1_modules import rfc5083
from pyasn1_modules import rfc5035

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


class AuthEnvelopedDataOpenTypesTestCase(unittest.TestCase):
    pem_text = """\
MIICvQYLKoZIhvcNAQkQARegggKsMIICqAIBADGCAiekggIjBgsqhkiG9w0BCRAN
ATCCAhICAQAEE3B0Zi1rbWM6MTM2MTQxMjIxMTIwDQYLKoZIhvcNAQkQAzAwCwYJ
YIZIAWUDBAEtMIIBsDCCAawCAQKAFJ7rZ8m5WnTUTS8WOWaA6AG1y6ScMA0GCSqG
SIb3DQEBAQUABIIBgHfnHNqDbyyql2NqX6UQggelWMTjwzJJ1L2erbsj1bIAGmpI
sUijw+fX8VOS7v1C9ui2Md9NFgCfkmKLo8T/jELqrk7MpMu09G5zDgeXzJfQDFc1
15wbrWAUU3XP7XIb6TNOc3xtq4UxA5V6jNUK2XyWKpjzOtM7gm0VWIJGVVlYu+u3
2LQcCjRFb87kvOY/WEnjxQpCW8g+4V747Ud97dYpMub7TLJiRNZkdHnq8xEGKlXj
VHSgc10lhphe1kFGeCpfJEsqjtN7YsVzf65ri9Z+3FJ1IO4cnMDbzGhyRXkS7a0k
58/miJbSj88PvzKNSURwpu4YHMQQX/mjT2ey1SY4ihPMuxxgTdCa04L0UxaRr7xA
ucz3n2UWShelm3IIjnWRlYdXypnXvKvwCLoeh5mJwUl1JNFPCQkQ487cKRyobUyN
gXQKT4ZDHCgXciwsX5nTsom87Ixp5vqSDJ+DhXA0r/Caiu1vnY5X9GLHSkqgXkgq
gUuu0LfcsQERD8psfQQogbiuZDqJmYt1Iau/pkuGfmeeqeiM3aeQ4NZf9AFZUVWB
GArPNHrvVDA3BgkqhkiG9w0BBwEwGwYJYIZIAWUDBAEuMA4EDMr+ur76ztut3sr4
iIANmvLRbyFUf87+2bPvLQQMoOWSXMGE4BckY8RMojEwLwYLKoZIhvcNAQkQAgQx
IDAeDBFXYXRzb24sIGNvbWUgaGVyZQYJKoZIhvcNAQcB
"""

    def setUp(self):
        self.asn1Spec = rfc5652.ContentInfo()

    def testDerCodec(self):
        substrate = pem.readBase64fromText(self.pem_text)
        rfc5652.cmsAttributesMap.update(rfc5035.ESSAttributeMap)
        rfc5652.cmsContentTypesMap.update(rfc5083.cmsContentTypesMapUpdate)
        asn1Object, rest = der_decoder.decode(substrate,
                                              asn1Spec=self.asn1Spec,
                                              decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate

        assert asn1Object['contentType'] in rfc5652.cmsContentTypesMap
        assert asn1Object['contentType'] == rfc5083.id_ct_authEnvelopedData
        authenv = asn1Object['content']
        assert authenv['version'] == rfc5652.CMSVersion().subtype(value='v0')

        for attr in authenv['unauthAttrs']:
            assert attr['attrType'] in rfc5652.cmsAttributesMap
            if attr['attrType'] == rfc5035.id_aa_contentHint:
                assert 'Watson' in attr['attrValues'][0]['contentDescription']


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
