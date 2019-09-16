#
# This file is part of pyasn1-modules software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
import sys

from pyasn1.codec.der import decoder as der_decoder
from pyasn1.codec.der import encoder as der_encoder

from pyasn1.type import char
from pyasn1.type import univ

from pyasn1_modules import pem
from pyasn1_modules import rfc2986
from pyasn1_modules import rfc5280


try:
    import unittest2 as unittest

except ImportError:
    import unittest


class CertificationRequestTestCase(unittest.TestCase):
    pem_text = """\
MIICxjCCAa4CAQAwgYAxCzAJBgNVBAYTAlVTMR0wGwYDVQQDDBRmY3UuZmFrZS5h
ZGRyZXNzLm9yZzEXMBUGA1UEBwwOUGxlYXNhbnQgR3JvdmUxHDAaBgNVBAoME0Zh
a2UgQ29tcGFueSBVbml0ZWQxDTALBgNVBAgMBFV0YWgxDDAKBgNVBAsMA0VuZzCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALvnYesymhLKSm9Llix53BUA
h99xMDBUYk0OB1VIdNQyjmFabHinM+lYUzVzrfcm1xtYB5QYKbsYuwZ4r5WI7qho
CRJy6JwXqKpOe72ScCogxlGDr2QtKjtvyWrRwXBHX1/OqVSZ3hdz3njhKpmq6HgK
87vH26RCSmK8FqCgn+qePfpspA7GzBvYwXhXluQtG7r4yBMKNRTQlPst8Vcy+iK+
pI8hmQVrzGi8Hgbpr2L9EjPUOlAQEb8hxeKc7s5VhjN/RHMLVMX8YczZYt7mcDKr
3PMwOVmXL1DMCtnS50MA2AxcPWcbQBeGyMroP+DLhAt6y1/IT0H5sQruNQw4euMC
AwEAAaAAMA0GCSqGSIb3DQEBCwUAA4IBAQBQXYQPfH5Wy4o0ZFbKQOO1e3dHV8rl
e8m9Z6qLgJO8rtW+OI+4FavJ6zjUvNVzd9JJxgwQ/1xprwrXh36nPcSyNLpGs7JT
6u7TGQ38QQAOmziLXzauMWGBeLuzWGmOKA1cs5HFGLSmbxF3+0IWpz4GlD86pU1+
WYyWgWHHAMA+kFYwBUR6CvPkmhshnZ8vrQavoOlcidCJ8o6IGA7N/Z0/NrgIDcoz
YaruhoMrmRKHKNpfamhT0gvqEPBec+UB3uLElESIqaeqYc6eMtUQP3lqyghF6I0M
fi6h7i9VVAZpslaKFfkNg12gLbbsCB1q36l5VXjHY/qe0FIUa9ogRrOi
"""

    def setUp(self):
        self.asn1Spec = rfc2986.CertificationRequest()

    def testDerCodec(self):

        substrate = pem.readBase64fromText(self.pem_text)

        asn1Object, rest = der_decoder.decode(substrate, asn1Spec=self.asn1Spec)

        assert not rest
        assert asn1Object.prettyPrint()
        assert der_encoder.encode(asn1Object) == substrate

    def testOpenTypes(self):
        algorithmIdentifierMapUpdate = {
            univ.ObjectIdentifier('1.2.840.113549.1.1.1'): univ.Null(""),
            univ.ObjectIdentifier('1.2.840.113549.1.1.5'): univ.Null(""),
            univ.ObjectIdentifier('1.2.840.113549.1.1.11'): univ.Null(""),
        }

        rfc5280.algorithmIdentifierMap.update(algorithmIdentifierMapUpdate)
        substrate = pem.readBase64fromText(self.pem_text)
        asn1Object, rest = der_decoder.decode(substrate,
            asn1Spec=rfc2986.CertificationRequest(),
            decodeOpenTypes=True)
        assert not rest
        assert asn1Object.prettyPrint()

        assert der_encoder.encode(asn1Object) == substrate

        for rdn in asn1Object['certificationRequestInfo']['subject']['rdnSequence']:
            for atv in rdn:
                if atv['type'] == rfc5280.id_at_countryName:
                    assert atv['value'] == char.PrintableString('US')
                else:
                    assert len(atv['value']['utf8String']) > 2

        spki_alg = asn1Object['certificationRequestInfo']['subjectPKInfo']['algorithm']
        assert spki_alg['parameters'] == univ.Null("")

        sig_alg = asn1Object['signatureAlgorithm']
        assert sig_alg['parameters'] == univ.Null("")


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    import sys

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
