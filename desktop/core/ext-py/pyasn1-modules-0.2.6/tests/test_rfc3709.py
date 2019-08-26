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
from pyasn1_modules import rfc3709

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class CertificateExtnTestCase(unittest.TestCase):
    pem_text = """\
MIIC9zCCAn2gAwIBAgIJAKWzVCgbsG46MAoGCCqGSM49BAMDMD8xCzAJBgNVBAYT
AlVTMQswCQYDVQQIDAJWQTEQMA4GA1UEBwwHSGVybmRvbjERMA8GA1UECgwIQm9n
dXMgQ0EwHhcNMTkwNTE0MTAwMjAwWhcNMjAwNTEzMTAwMjAwWjBlMQswCQYDVQQG
EwJVUzELMAkGA1UECBMCVkExEDAOBgNVBAcTB0hlcm5kb24xGzAZBgNVBAoTElZp
Z2lsIFNlY3VyaXR5IExMQzEaMBgGA1UEAxMRbWFpbC52aWdpbHNlYy5jb20wdjAQ
BgcqhkjOPQIBBgUrgQQAIgNiAATwUXZUseiOaqWdrClDCMbp9YFAM87LTmFirygp
zKDU9cfqSCg7zBDIphXCwMcS9zVWDoStCbcvN0jw5CljHcffzpHYX91P88SZRJ1w
4hawHjOsWxvM3AkYgZ5nfdlL7EajggEdMIIBGTALBgNVHQ8EBAMCB4AwQgYJYIZI
AYb4QgENBDUWM1RoaXMgY2VydGlmaWNhdGUgY2Fubm90IGJlIHRydXN0ZWQgZm9y
IGFueSBwdXJwb3NlLjAdBgNVHQ4EFgQU8jXbNATapVXyvWkDmbBi7OIVCMEwHwYD
VR0jBBgwFoAU8jXbNATapVXyvWkDmbBi7OIVCMEwgYUGCCsGAQUFBwEMBHkwd6J1
oHMwcTBvMG0WCWltYWdlL3BuZzAzMDEwDQYJYIZIAWUDBAIBBQAEIJtBNrMSSNo+
6Rwqwctmcy0qf68ilRuKEmlf3GLwGiIkMCsWKWh0dHA6Ly93d3cudmlnaWxzZWMu
Y29tL3ZpZ2lsc2VjX2xvZ28ucG5nMAoGCCqGSM49BAMDA2gAMGUCMGhfLH4kZaCD
H43A8m8mHCUpYt9unT0qYu4TCMaRuOTYEuqj3qtuwyLcfAGuXKp/oAIxAIrPY+3y
Pj22pmfmQi5w21UljqoTj/+lQLkU3wfy5BdVKBwI0GfEA+YL3ctSzPNqAA==
"""

    def setUp(self):
        self.asn1Spec = rfc5280.Certificate()

    def testDerCodec(self):

        substrate = pem.readBase64fromText(self.pem_text)

        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate

        for extn in asn1Object['tbsCertificate']['extensions']:

            if extn['extnID'] == rfc3709.id_pe_logotype:
                s = extn['extnValue']
                logotype, rest = der_decoder.decode(s, rfc3709.LogotypeExtn())
                assert not rest
                assert logotype.prettyPrint()
                assert der_encoder.encode(logotype) == s
                ids = logotype['subjectLogo']['direct']['image'][0]['imageDetails']
                assert ids['mediaType'] == "image/png"
                assert ids['logotypeURI'][0] == "http://www.vigilsec.com/vigilsec_logo.png"

    def testExtensionsMap(self):
        substrate = pem.readBase64fromText(self.pem_text)
        rfc5280.certificateExtensionsMap.update(rfc3709.certificateExtensionsMapUpdate)
        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)
        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate

        for extn in asn1Object['tbsCertificate']['extensions']:
            if extn['extnID'] in rfc5280.certificateExtensionsMap.keys():
                extnValue, rest = der_decoder.decode(extn['extnValue'],
                    asn1Spec=rfc5280.certificateExtensionsMap[extn['extnID']])
                assert der_encoder.encode(extnValue) == extn['extnValue']


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
