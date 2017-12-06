# Copyright (c) Jean-Paul Calderone
# See LICENSE file for details.

"""
Unit tests for :py:mod:`OpenSSL.crypto`.
"""

from warnings import simplefilter

import base64
from subprocess import PIPE, Popen
from datetime import datetime, timedelta

import pytest

from six import binary_type

from cryptography import x509
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import flaky

from OpenSSL.crypto import TYPE_RSA, TYPE_DSA, Error, PKey, PKeyType
from OpenSSL.crypto import X509, X509Type, X509Name, X509NameType
from OpenSSL.crypto import (
    X509Store,
    X509StoreFlags,
    X509StoreType,
    X509StoreContext,
    X509StoreContextError
)
from OpenSSL.crypto import X509Req, X509ReqType
from OpenSSL.crypto import X509Extension, X509ExtensionType
from OpenSSL.crypto import load_certificate, load_privatekey
from OpenSSL.crypto import load_publickey, dump_publickey
from OpenSSL.crypto import FILETYPE_PEM, FILETYPE_ASN1, FILETYPE_TEXT
from OpenSSL.crypto import dump_certificate, load_certificate_request
from OpenSSL.crypto import dump_certificate_request, dump_privatekey
from OpenSSL.crypto import PKCS7, PKCS7Type, load_pkcs7_data
from OpenSSL.crypto import PKCS12, PKCS12Type, load_pkcs12
from OpenSSL.crypto import CRL, Revoked, dump_crl, load_crl
from OpenSSL.crypto import NetscapeSPKI, NetscapeSPKIType
from OpenSSL.crypto import (
    sign, verify, get_elliptic_curve, get_elliptic_curves)

from .util import EqualityTestsMixin, is_consistent_type, WARNING_TYPE_EXPECTED


def normalize_privatekey_pem(pem):
    return dump_privatekey(FILETYPE_PEM, load_privatekey(FILETYPE_PEM, pem))


GOOD_CIPHER = "blowfish"
BAD_CIPHER = "zippers"

GOOD_DIGEST = "SHA1"
BAD_DIGEST = "monkeys"

old_root_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIIC7TCCAlagAwIBAgIIPQzE4MbeufQwDQYJKoZIhvcNAQEFBQAwWDELMAkGA1UE
BhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdDaGljYWdvMRAwDgYDVQQKEwdU
ZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3QgQ0EwIhgPMjAwOTAzMjUxMjM2
NThaGA8yMDE3MDYxMTEyMzY1OFowWDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAklM
MRAwDgYDVQQHEwdDaGljYWdvMRAwDgYDVQQKEwdUZXN0aW5nMRgwFgYDVQQDEw9U
ZXN0aW5nIFJvb3QgQ0EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAPmaQumL
urpE527uSEHdL1pqcDRmWzu+98Y6YHzT/J7KWEamyMCNZ6fRW1JCR782UQ8a07fy
2xXsKy4WdKaxyG8CcatwmXvpvRQ44dSANMihHELpANTdyVp6DCysED6wkQFurHlF
1dshEaJw8b/ypDhmbVIo6Ci1xvCJqivbLFnbAgMBAAGjgbswgbgwHQYDVR0OBBYE
FINVdy1eIfFJDAkk51QJEo3IfgSuMIGIBgNVHSMEgYAwfoAUg1V3LV4h8UkMCSTn
VAkSjch+BK6hXKRaMFgxCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJJTDEQMA4GA1UE
BxMHQ2hpY2FnbzEQMA4GA1UEChMHVGVzdGluZzEYMBYGA1UEAxMPVGVzdGluZyBS
b290IENBggg9DMTgxt659DAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUAA4GB
AGGCDazMJGoWNBpc03u6+smc95dEead2KlZXBATOdFT1VesY3+nUOqZhEhTGlDMi
hkgaZnzoIq/Uamidegk4hirsCT/R+6vsKAAxNTcBjUeZjlykCJWy5ojShGftXIKY
w/njVbKMXrvc83qmTdGl3TAM0fxQIpqgcglFLveEBgzn
-----END CERTIFICATE-----
"""

root_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIIC6TCCAlKgAwIBAgIIPQzE4MbeufQwDQYJKoZIhvcNAQEFBQAwWDELMAkGA1UE
BhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdDaGljYWdvMRAwDgYDVQQKEwdU
ZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3QgQ0EwHhcNMTcwNjExMjIzMjU5
WhcNMzcwNjA2MjIzMjU5WjBYMQswCQYDVQQGEwJVUzELMAkGA1UECBMCSUwxEDAO
BgNVBAcTB0NoaWNhZ28xEDAOBgNVBAoTB1Rlc3RpbmcxGDAWBgNVBAMTD1Rlc3Rp
bmcgUm9vdCBDQTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEA+ZpC6Yu6ukTn
bu5IQd0vWmpwNGZbO773xjpgfNP8nspYRqbIwI1np9FbUkJHvzZRDxrTt/LbFewr
LhZ0prHIbwJxq3CZe+m9FDjh1IA0yKEcQukA1N3JWnoMLKwQPrCRAW6seUXV2yER
onDxv/KkOGZtUijoKLXG8ImqK9ssWdsCAwEAAaOBuzCBuDAdBgNVHQ4EFgQUg1V3
LV4h8UkMCSTnVAkSjch+BK4wgYgGA1UdIwSBgDB+gBSDVXctXiHxSQwJJOdUCRKN
yH4ErqFcpFowWDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdD
aGljYWdvMRAwDgYDVQQKEwdUZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3Qg
Q0GCCD0MxODG3rn0MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEANFYQ
R+T70VcZ+SnvURnwviFgCXeedBzCr21meo+DNHbkp2gudB9W8Xrned/wtUBVymy9
gjB5jINfU7Lci0H57Evsw96UJJVfhXdUMHpqt1RGCoEd9FWnrDyrSy0NysnBT2bH
lEqxh3aFEUx9IOQ4sgnx1/NOFXBpkRtivl6O0Ec=
-----END CERTIFICATE-----
"""

root_key_pem = b"""-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQD5mkLpi7q6ROdu7khB3S9aanA0Zls7vvfGOmB80/yeylhGpsjA
jWen0VtSQke/NlEPGtO38tsV7CsuFnSmschvAnGrcJl76b0UOOHUgDTIoRxC6QDU
3claegwsrBA+sJEBbqx5RdXbIRGicPG/8qQ4Zm1SKOgotcbwiaor2yxZ2wIDAQAB
AoGBAPCgMpmLxzwDaUmcFbTJUvlLW1hoxNNYSu2jIZm1k/hRAcE60JYwvBkgz3UB
yMEh0AtLxYe0bFk6EHah11tMUPgscbCq73snJ++8koUw+csk22G65hOs51bVb7Aa
6JBe67oLzdtvgCUFAA2qfrKzWRZzAdhUirQUZgySZk+Xq1pBAkEA/kZG0A6roTSM
BVnx7LnPfsycKUsTumorpXiylZJjTi9XtmzxhrYN6wgZlDOOwOLgSQhszGpxVoMD
u3gByT1b2QJBAPtL3mSKdvwRu/+40zaZLwvSJRxaj0mcE4BJOS6Oqs/hS1xRlrNk
PpQ7WJ4yM6ZOLnXzm2mKyxm50Mv64109FtMCQQDOqS2KkjHaLowTGVxwC0DijMfr
I9Lf8sSQk32J5VWCySWf5gGTfEnpmUa41gKTMJIbqZZLucNuDcOtzUaeWZlZAkA8
ttXigLnCqR486JDPTi9ZscoZkZ+w7y6e/hH8t6d5Vjt48JVyfjPIaJY+km58LcN3
6AWSeGAdtRFHVzR7oHjVAkB4hutvxiOeiIVQNBhM6RSI9aBPMI21DoX2JRoxvNW2
cbvAhow217X9V0dVerEOKxnNYspXRrh36h7k4mQA+sDq
-----END RSA PRIVATE KEY-----
"""

intermediate_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIICVzCCAcCgAwIBAgIRAMPzhm6//0Y/g2pmnHR2C4cwDQYJKoZIhvcNAQENBQAw
WDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdDaGljYWdvMRAw
DgYDVQQKEwdUZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3QgQ0EwHhcNMTQw
ODI4MDIwNDA4WhcNMjQwODI1MDIwNDA4WjBmMRUwEwYDVQQDEwxpbnRlcm1lZGlh
dGUxDDAKBgNVBAoTA29yZzERMA8GA1UECxMIb3JnLXVuaXQxCzAJBgNVBAYTAlVT
MQswCQYDVQQIEwJDQTESMBAGA1UEBxMJU2FuIERpZWdvMIGfMA0GCSqGSIb3DQEB
AQUAA4GNADCBiQKBgQDYcEQw5lfbEQRjr5Yy4yxAHGV0b9Al+Lmu7wLHMkZ/ZMmK
FGIbljbviiD1Nz97Oh2cpB91YwOXOTN2vXHq26S+A5xe8z/QJbBsyghMur88CjdT
21H2qwMa+r5dCQwEhuGIiZ3KbzB/n4DTMYI5zy4IYPv0pjxShZn4aZTCCK2IUwID
AQABoxMwETAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBDQUAA4GBAPIWSkLX
QRMApOjjyC+tMxumT5e2pMqChHmxobQK4NMdrf2VCx+cRT6EmY8sK3/Xl/X8UBQ+
9n5zXb1ZwhW/sTWgUvmOceJ4/XVs9FkdWOOn1J0XBch9ZIiFe/s5ASIgG7fUdcUF
9mAWS6FK2ca3xIh5kIupCXOFa0dPvlw/YUFT
-----END CERTIFICATE-----
"""

intermediate_key_pem = b"""-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDYcEQw5lfbEQRjr5Yy4yxAHGV0b9Al+Lmu7wLHMkZ/ZMmKFGIb
ljbviiD1Nz97Oh2cpB91YwOXOTN2vXHq26S+A5xe8z/QJbBsyghMur88CjdT21H2
qwMa+r5dCQwEhuGIiZ3KbzB/n4DTMYI5zy4IYPv0pjxShZn4aZTCCK2IUwIDAQAB
AoGAfSZVV80pSeOKHTYfbGdNY/jHdU9eFUa/33YWriXU+77EhpIItJjkRRgivIfo
rhFJpBSGmDLblaqepm8emsXMeH4+2QzOYIf0QGGP6E6scjTt1PLqdqKfVJ1a2REN
147cujNcmFJb/5VQHHMpaPTgttEjlzuww4+BCDPsVRABWrkCQQD3loH36nLoQTtf
+kQq0T6Bs9/UWkTAGo0ND81ALj0F8Ie1oeZg6RNT96RxZ3aVuFTESTv6/TbjWywO
wdzlmV1vAkEA38rTJ6PTwaJlw5OttdDzAXGPB9tDmzh9oSi7cHwQQXizYd8MBYx4
sjHUKD3dCQnb1dxJFhd3BT5HsnkRMbVZXQJAbXduH17ZTzcIOXc9jHDXYiFVZV5D
52vV0WCbLzVCZc3jMrtSUKa8lPN5EWrdU3UchWybyG0MR5mX8S5lrF4SoQJAIyUD
DBKaSqpqONCUUx1BTFS9FYrFjzbL4+c1qHCTTPTblt8kUCrDOZjBrKAqeiTmNSum
/qUot9YUBF8m6BuGsQJATHHmdFy/fG1VLkyBp49CAa8tN3Z5r/CgTznI4DfMTf4C
NbRHn2UmYlwQBa+L5lg9phewNe8aEwpPyPLoV85U8Q==
-----END RSA PRIVATE KEY-----
"""

server_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIICJDCCAY2gAwIBAgIJAJn/HpR21r/8MA0GCSqGSIb3DQEBBQUAMFgxCzAJBgNV
BAYTAlVTMQswCQYDVQQIDAJJTDEQMA4GA1UEBwwHQ2hpY2FnbzEQMA4GA1UECgwH
VGVzdGluZzEYMBYGA1UEAwwPVGVzdGluZyBSb290IENBMB4XDTE3MDYxMjAwMTA1
N1oXDTM3MDYwNzAwMTA1N1owGDEWMBQGA1UEAwwNbG92ZWx5IHNlcnZlcjCBnzAN
BgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAvqb4brndXS2kEL84qXbZXE6LYK+UrhNi
70sdIM/24NVN7tXkPlOXqrMWhFHHml+aeSpPkH5b1vKnY1TcULmEubnNICtvjmZ5
SGMQn+J+RmBs1SMd0EgY/0wBBQdlrlYp2QYgm8YC+zxTNSqWvhMFZAgHbj6Un5SS
T8JGBqytjB0CAwEAAaM2MDQwHQYDVR0OBBYEFINVdy1eIfFJDAkk51QJEo3IfgSu
MBMGA1UdJQQMMAoGCCsGAQUFBwMBMA0GCSqGSIb3DQEBBQUAA4GBAGki1K6WgHHJ
qC6aY2EowjaWOXLO6jUZIhGk7BA7vMRfNug429AOZ4m5F6OQhzmJmlw67Jyu2FeI
h0VtBuQoHPtjqZXF59oX6hMMmGLMs9pV0UA3fJs5MYA4/V5ZcQy0Ie0QoJNejLzE
6V1Qz1rRTYLUyEcpI7ZCmBg2KQQI8YZI
-----END CERTIFICATE-----
"""

server_key_pem = normalize_privatekey_pem(b"""-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQC+pvhuud1dLaQQvzipdtlcTotgr5SuE2LvSx0gz/bg1U3u1eQ+
U5eqsxaEUceaX5p5Kk+QflvW8qdjVNxQuYS5uc0gK2+OZnlIYxCf4n5GYGzVIx3Q
SBj/TAEFB2WuVinZBiCbxgL7PFM1Kpa+EwVkCAduPpSflJJPwkYGrK2MHQIDAQAB
AoGAbwuZ0AR6JveahBaczjfnSpiFHf+mve2UxoQdpyr6ROJ4zg/PLW5K/KXrC48G
j6f3tXMrfKHcpEoZrQWUfYBRCUsGD5DCazEhD8zlxEHahIsqpwA0WWssJA2VOLEN
j6DuV2pCFbw67rfTBkTSo32ahfXxEKev5KswZk0JIzH3ooECQQDgzS9AI89h0gs8
Dt+1m11Rzqo3vZML7ZIyGApUzVan+a7hbc33nbGRkAXjHaUBJO31it/H6dTO+uwX
msWwNG5ZAkEA2RyFKs5xR5USTFaKLWCgpH/ydV96KPOpBND7TKQx62snDenFNNbn
FwwOhpahld+vqhYk+pfuWWUpQciE+Bu7ZQJASjfT4sQv4qbbKK/scePicnDdx9th
4e1EeB9xwb+tXXXUo/6Bor/AcUNwfiQ6Zt9PZOK9sR3lMZSsP7rMi7kzuQJABie6
1sXXjFH7nNJvRG4S39cIxq8YRYTy68II/dlB2QzGpKxV/POCxbJ/zu0CU79tuYK7
NaeNCFfH3aeTrX0LyQJAMBWjWmeKM2G2sCExheeQK0ROnaBC8itCECD4Jsve4nqf
r50+LF74iLXFwqysVCebPKMOpDWp/qQ1BbJQIPs7/A==
-----END RSA PRIVATE KEY-----
""")

intermediate_server_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIICWDCCAcGgAwIBAgIRAPQFY9jfskSihdiNSNdt6GswDQYJKoZIhvcNAQENBQAw
ZjEVMBMGA1UEAxMMaW50ZXJtZWRpYXRlMQwwCgYDVQQKEwNvcmcxETAPBgNVBAsT
CG9yZy11bml0MQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0ExEjAQBgNVBAcTCVNh
biBEaWVnbzAeFw0xNDA4MjgwMjEwNDhaFw0yNDA4MjUwMjEwNDhaMG4xHTAbBgNV
BAMTFGludGVybWVkaWF0ZS1zZXJ2aWNlMQwwCgYDVQQKEwNvcmcxETAPBgNVBAsT
CG9yZy11bml0MQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0ExEjAQBgNVBAcTCVNh
biBEaWVnbzCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEAqpJZygd+w1faLOr1
iOAmbBhx5SZWcTCZ/ZjHQTJM7GuPT624QkqsixFghRKdDROwpwnAP7gMRukLqiy4
+kRuGT5OfyGggL95i2xqA+zehjj08lSTlvGHpePJgCyTavIy5+Ljsj4DKnKyuhxm
biXTRrH83NDgixVkObTEmh/OVK0CAwEAATANBgkqhkiG9w0BAQ0FAAOBgQBa0Npw
UkzjaYEo1OUE1sTI6Mm4riTIHMak4/nswKh9hYup//WVOlr/RBSBtZ7Q/BwbjobN
3bfAtV7eSAqBsfxYXyof7G1ALANQERkq3+oyLP1iVt08W1WOUlIMPhdCF/QuCwy6
x9MJLhUCGLJPM+O2rAPWVD9wCmvq10ALsiH3yA==
-----END CERTIFICATE-----
"""

intermediate_server_key_pem = b"""-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCqklnKB37DV9os6vWI4CZsGHHlJlZxMJn9mMdBMkzsa49PrbhC
SqyLEWCFEp0NE7CnCcA/uAxG6QuqLLj6RG4ZPk5/IaCAv3mLbGoD7N6GOPTyVJOW
8Yel48mALJNq8jLn4uOyPgMqcrK6HGZuJdNGsfzc0OCLFWQ5tMSaH85UrQIDAQAB
AoGAIQ594j5zna3/9WaPsTgnmhlesVctt4AAx/n827DA4ayyuHFlXUuVhtoWR5Pk
5ezj9mtYW8DyeCegABnsu2vZni/CdvU6uiS1Hv6qM1GyYDm9KWgovIP9rQCDSGaz
d57IWVGxx7ODFkm3gN5nxnSBOFVHytuW1J7FBRnEsehRroECQQDXHFOv82JuXDcz
z3+4c74IEURdOHcbycxlppmK9kFqm5lsUdydnnGW+mvwDk0APOB7Wg7vyFyr393e
dpmBDCzNAkEAyv6tVbTKUYhSjW+QhabJo896/EqQEYUmtMXxk4cQnKeR/Ao84Rkf
EqD5IykMUfUI0jJU4DGX+gWZ10a7kNbHYQJAVFCuHNFxS4Cpwo0aqtnzKoZaHY/8
X9ABZfafSHCtw3Op92M+7ikkrOELXdS9KdKyyqbKJAKNEHF3LbOfB44WIQJAA2N4
9UNNVUsXRbElEnYUS529CdUczo4QdVgQjkvk5RiPAUwSdBd9Q0xYnFOlFwEmIowg
ipWJWe0aAlP18ZcEQQJBAL+5lekZ/GUdQoZ4HAsN5a9syrzavJ9VvU1KOOPorPZK
nMRZbbQgP+aSB7yl6K0gaLaZ8XaK0pjxNBh6ASqg9f4=
-----END RSA PRIVATE KEY-----
"""

client_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIICIjCCAYugAwIBAgIJAKxpFI5lODkjMA0GCSqGSIb3DQEBBQUAMFgxCzAJBgNV
BAYTAlVTMQswCQYDVQQIDAJJTDEQMA4GA1UEBwwHQ2hpY2FnbzEQMA4GA1UECgwH
VGVzdGluZzEYMBYGA1UEAwwPVGVzdGluZyBSb290IENBMB4XDTE3MDYxMjAwMDQx
M1oXDTM3MDYwNzAwMDQxM1owFjEUMBIGA1UEAwwLdWdseSBjbGllbnQwgZ8wDQYJ
KoZIhvcNAQEBBQADgY0AMIGJAoGBAMBmH9JG02bme0xPipvpjMSlOugyWrauf4at
EdGJn7GQLD8IY2Fu0+Kvv9DFpSPboFKZCsfDVsYoRs+xaJbtt1dJ6ymX7EqKS7gb
8q+eeZZ14keqyJd5Rm2q6swQtw9ADD3E8cS6GqpQm+8SgxOycISoYz7sO1ugJFqN
jId+W4BFAgMBAAGjNjA0MB0GA1UdDgQWBBSDVXctXiHxSQwJJOdUCRKNyH4ErjAT
BgNVHSUEDDAKBggrBgEFBQcDAjANBgkqhkiG9w0BAQUFAAOBgQAMqcHyweaCOZNN
dWQQOsBKQlL5wqVVZwucHPWqobjxpULKy9gS2ha2zbgkXcB/BnBOSwe0Fm+MJV0T
NbnTghcGJNpEH7VKn4xSLvIGZmnZZWgxeIB16z4GhpkK2fShBJ+6GKZjsgjT0lSH
JRgjHbWutZfZvbSHXr9n7PIphG1Ojg==
-----END CERTIFICATE-----
"""

client_key_pem = normalize_privatekey_pem(b"""-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDAZh/SRtNm5ntMT4qb6YzEpTroMlq2rn+GrRHRiZ+xkCw/CGNh
btPir7/QxaUj26BSmQrHw1bGKEbPsWiW7bdXSespl+xKiku4G/KvnnmWdeJHqsiX
eUZtqurMELcPQAw9xPHEuhqqUJvvEoMTsnCEqGM+7DtboCRajYyHfluARQIDAQAB
AoGATkZ+NceY5Glqyl4mD06SdcKfV65814vg2EL7V9t8+/mi9rYL8KztSXGlQWPX
zuHgtRoMl78yQ4ZJYOBVo+nsx8KZNRCEBlE19bamSbQLCeQMenWnpeYyQUZ908gF
h6L9qsFVJepgA9RDgAjyDoS5CaWCdCCPCH2lDkdcqC54SVUCQQDseuduc4wi8h4t
V8AahUn9fn9gYfhoNuM0gdguTA0nPLVWz4hy1yJiWYQe0H7NLNNTmCKiLQaJpAbb
TC6vE8C7AkEA0Ee8CMJUc20BnGEmxwgWcVuqFWaKCo8jTH1X38FlATUsyR3krjW2
dL3yDD9NwHxsYP7nTKp/U8MV7U9IBn4y/wJBAJl7H0/BcLeRmuJk7IqJ7b635iYB
D/9beFUw3MUXmQXZUfyYz39xf6CDZsu1GEdEC5haykeln3Of4M9d/4Kj+FcCQQCY
si6xwT7GzMDkk/ko684AV3KPc/h6G0yGtFIrMg7J3uExpR/VdH2KgwMkZXisSMvw
JJEQjOMCVsEJlRk54WWjAkEAzoZNH6UhDdBK5F38rVt/y4SEHgbSfJHIAmPS32Kq
f6GGcfNpip0Uk7q7udTKuX7Q/buZi/C4YW7u3VKAquv9NA==
-----END RSA PRIVATE KEY-----
""")

cleartextCertificatePEM = b"""-----BEGIN CERTIFICATE-----
MIIC6TCCAlKgAwIBAgIIPQzE4MbeufQwDQYJKoZIhvcNAQEFBQAwWDELMAkGA1UE
BhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdDaGljYWdvMRAwDgYDVQQKEwdU
ZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3QgQ0EwHhcNMTcwNjExMjIzMjU5
WhcNMzcwNjA2MjIzMjU5WjBYMQswCQYDVQQGEwJVUzELMAkGA1UECBMCSUwxEDAO
BgNVBAcTB0NoaWNhZ28xEDAOBgNVBAoTB1Rlc3RpbmcxGDAWBgNVBAMTD1Rlc3Rp
bmcgUm9vdCBDQTCBnzANBgkqhkiG9w0BAQEFAAOBjQAwgYkCgYEA+ZpC6Yu6ukTn
bu5IQd0vWmpwNGZbO773xjpgfNP8nspYRqbIwI1np9FbUkJHvzZRDxrTt/LbFewr
LhZ0prHIbwJxq3CZe+m9FDjh1IA0yKEcQukA1N3JWnoMLKwQPrCRAW6seUXV2yER
onDxv/KkOGZtUijoKLXG8ImqK9ssWdsCAwEAAaOBuzCBuDAdBgNVHQ4EFgQUg1V3
LV4h8UkMCSTnVAkSjch+BK4wgYgGA1UdIwSBgDB+gBSDVXctXiHxSQwJJOdUCRKN
yH4ErqFcpFowWDELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQHEwdD
aGljYWdvMRAwDgYDVQQKEwdUZXN0aW5nMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3Qg
Q0GCCD0MxODG3rn0MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEANFYQ
R+T70VcZ+SnvURnwviFgCXeedBzCr21meo+DNHbkp2gudB9W8Xrned/wtUBVymy9
gjB5jINfU7Lci0H57Evsw96UJJVfhXdUMHpqt1RGCoEd9FWnrDyrSy0NysnBT2bH
lEqxh3aFEUx9IOQ4sgnx1/NOFXBpkRtivl6O0Ec=
-----END CERTIFICATE-----
"""

cleartextPrivateKeyPEM = normalize_privatekey_pem(b"""\
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQD5mkLpi7q6ROdu7khB3S9aanA0Zls7vvfGOmB80/yeylhGpsjA
jWen0VtSQke/NlEPGtO38tsV7CsuFnSmschvAnGrcJl76b0UOOHUgDTIoRxC6QDU
3claegwsrBA+sJEBbqx5RdXbIRGicPG/8qQ4Zm1SKOgotcbwiaor2yxZ2wIDAQAB
AoGBAPCgMpmLxzwDaUmcFbTJUvlLW1hoxNNYSu2jIZm1k/hRAcE60JYwvBkgz3UB
yMEh0AtLxYe0bFk6EHah11tMUPgscbCq73snJ++8koUw+csk22G65hOs51bVb7Aa
6JBe67oLzdtvgCUFAA2qfrKzWRZzAdhUirQUZgySZk+Xq1pBAkEA/kZG0A6roTSM
BVnx7LnPfsycKUsTumorpXiylZJjTi9XtmzxhrYN6wgZlDOOwOLgSQhszGpxVoMD
u3gByT1b2QJBAPtL3mSKdvwRu/+40zaZLwvSJRxaj0mcE4BJOS6Oqs/hS1xRlrNk
PpQ7WJ4yM6ZOLnXzm2mKyxm50Mv64109FtMCQQDOqS2KkjHaLowTGVxwC0DijMfr
I9Lf8sSQk32J5VWCySWf5gGTfEnpmUa41gKTMJIbqZZLucNuDcOtzUaeWZlZAkA8
ttXigLnCqR486JDPTi9ZscoZkZ+w7y6e/hH8t6d5Vjt48JVyfjPIaJY+km58LcN3
6AWSeGAdtRFHVzR7oHjVAkB4hutvxiOeiIVQNBhM6RSI9aBPMI21DoX2JRoxvNW2
cbvAhow217X9V0dVerEOKxnNYspXRrh36h7k4mQA+sDq
-----END RSA PRIVATE KEY-----
""")

cleartextCertificateRequestPEM = b"""-----BEGIN CERTIFICATE REQUEST-----
MIIBnjCCAQcCAQAwXjELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAklMMRAwDgYDVQQH
EwdDaGljYWdvMRcwFQYDVQQKEw5NeSBDb21wYW55IEx0ZDEXMBUGA1UEAxMORnJl
ZGVyaWNrIERlYW4wgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBANp6Y17WzKSw
BsUWkXdqg6tnXy8H8hA1msCMWpc+/2KJ4mbv5NyD6UD+/SqagQqulPbF/DFea9nA
E0zhmHJELcM8gUTIlXv/cgDWnmK4xj8YkjVUiCdqKRAKeuzLG1pGmwwF5lGeJpXN
xQn5ecR0UYSOWj6TTGXB9VyUMQzCClcBAgMBAAGgADANBgkqhkiG9w0BAQUFAAOB
gQAAJGuF/R/GGbeC7FbFW+aJgr9ee0Xbl6nlhu7pTe67k+iiKT2dsl2ti68MVTnu
Vrb3HUNqOkiwsJf6kCtq5oPn3QVYzTa76Dt2y3Rtzv6boRSlmlfrgS92GNma8JfR
oICQk3nAudi6zl1Dix3BCv1pUp5KMtGn3MeDEi6QFGy2rA==
-----END CERTIFICATE REQUEST-----
"""

encryptedPrivateKeyPEM = b"""-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,9573604A18579E9E

SHOho56WxDkT0ht10UTeKc0F5u8cqIa01kzFAmETw0MAs8ezYtK15NPdCXUm3X/2
a17G7LSF5bkxOgZ7vpXyMzun/owrj7CzvLxyncyEFZWvtvzaAhPhvTJtTIB3kf8B
8+qRcpTGK7NgXEgYBW5bj1y4qZkD4zCL9o9NQzsKI3Ie8i0239jsDOWR38AxjXBH
mGwAQ4Z6ZN5dnmM4fhMIWsmFf19sNyAML4gHenQCHhmXbjXeVq47aC2ProInJbrm
+00TcisbAQ40V9aehVbcDKtS4ZbMVDwncAjpXpcncC54G76N6j7F7wL7L/FuXa3A
fvSVy9n2VfF/pJ3kYSflLHH2G/DFxjF7dl0GxhKPxJjp3IJi9VtuvmN9R2jZWLQF
tfC8dXgy/P9CfFQhlinqBTEwgH0oZ/d4k4NVFDSdEMaSdmBAjlHpc+Vfdty3HVnV
rKXj//wslsFNm9kIwJGIgKUa/n2jsOiydrsk1mgH7SmNCb3YHgZhbbnq0qLat/HC
gHDt3FHpNQ31QzzL3yrenFB2L9osIsnRsDTPFNi4RX4SpDgNroxOQmyzCCV6H+d4
o1mcnNiZSdxLZxVKccq0AfRpHqpPAFnJcQHP6xyT9MZp6fBa0XkxDnt9kNU8H3Qw
7SJWZ69VXjBUzMlQViLuaWMgTnL+ZVyFZf9hTF7U/ef4HMLMAVNdiaGG+G+AjCV/
MbzjS007Oe4qqBnCWaFPSnJX6uLApeTbqAxAeyCql56ULW5x6vDMNC3dwjvS/CEh
11n8RkgFIQA0AhuKSIg3CbuartRsJnWOLwgLTzsrKYL4yRog1RJrtw==
-----END RSA PRIVATE KEY-----
"""

encryptedPrivateKeyPEMPassphrase = b"foobar"


cleartextPublicKeyPEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxszlc+b71LvlLS0ypt/l
gT/JzSVJtnEqw9WUNGeiChywX2mmQLHEt7KP0JikqUFZOtPclNY823Q4pErMTSWC
90qlUxI47vNJbXGRfmO2q6Zfw6SE+E9iUb74xezbOJLjBuUIkQzEKEFV+8taiRV+
ceg1v01yCT2+OjhQW3cxG42zxyRFmqesbQAUWgS3uhPrUQqYQUEiTmVhh4FBUKZ5
XIneGUpX1S7mXRxTLH6YzRoGFqRoc9A0BBNcoXHTWnxV215k4TeHMFYE5RG0KYAS
8Xk5iKICEXwnZreIt3jyygqoOKsKZMK/Zl2VhMGhJR6HXRpQCyASzEG7bgtROLhL
ywIDAQAB
-----END PUBLIC KEY-----
"""

# Some PKCS#7 stuff.  Generated with the openssl command line:
#
#    openssl crl2pkcs7 -inform pem -outform pem -certfile s.pem -nocrl
#
# with a certificate and key (but the key should be irrelevant) in s.pem
pkcs7Data = b"""\
-----BEGIN PKCS7-----
MIIDNwYJKoZIhvcNAQcCoIIDKDCCAyQCAQExADALBgkqhkiG9w0BBwGgggMKMIID
BjCCAm+gAwIBAgIBATANBgkqhkiG9w0BAQQFADB7MQswCQYDVQQGEwJTRzERMA8G
A1UEChMITTJDcnlwdG8xFDASBgNVBAsTC00yQ3J5cHRvIENBMSQwIgYDVQQDExtN
MkNyeXB0byBDZXJ0aWZpY2F0ZSBNYXN0ZXIxHTAbBgkqhkiG9w0BCQEWDm5ncHNA
cG9zdDEuY29tMB4XDTAwMDkxMDA5NTEzMFoXDTAyMDkxMDA5NTEzMFowUzELMAkG
A1UEBhMCU0cxETAPBgNVBAoTCE0yQ3J5cHRvMRIwEAYDVQQDEwlsb2NhbGhvc3Qx
HTAbBgkqhkiG9w0BCQEWDm5ncHNAcG9zdDEuY29tMFwwDQYJKoZIhvcNAQEBBQAD
SwAwSAJBAKy+e3dulvXzV7zoTZWc5TzgApr8DmeQHTYC8ydfzH7EECe4R1Xh5kwI
zOuuFfn178FBiS84gngaNcrFi0Z5fAkCAwEAAaOCAQQwggEAMAkGA1UdEwQCMAAw
LAYJYIZIAYb4QgENBB8WHU9wZW5TU0wgR2VuZXJhdGVkIENlcnRpZmljYXRlMB0G
A1UdDgQWBBTPhIKSvnsmYsBVNWjj0m3M2z0qVTCBpQYDVR0jBIGdMIGagBT7hyNp
65w6kxXlxb8pUU/+7Sg4AaF/pH0wezELMAkGA1UEBhMCU0cxETAPBgNVBAoTCE0y
Q3J5cHRvMRQwEgYDVQQLEwtNMkNyeXB0byBDQTEkMCIGA1UEAxMbTTJDcnlwdG8g
Q2VydGlmaWNhdGUgTWFzdGVyMR0wGwYJKoZIhvcNAQkBFg5uZ3BzQHBvc3QxLmNv
bYIBADANBgkqhkiG9w0BAQQFAAOBgQA7/CqT6PoHycTdhEStWNZde7M/2Yc6BoJu
VwnW8YxGO8Sn6UJ4FeffZNcYZddSDKosw8LtPOeWoK3JINjAk5jiPQ2cww++7QGG
/g5NDjxFZNDJP1dGiLAxPW6JXwov4v0FmdzfLOZ01jDcgQQZqEpYlgpuI5JEWUQ9
Ho4EzbYCOaEAMQA=
-----END PKCS7-----
"""

pkcs7DataASN1 = base64.b64decode(b"""
MIIDNwYJKoZIhvcNAQcCoIIDKDCCAyQCAQExADALBgkqhkiG9w0BBwGgggMKMIID
BjCCAm+gAwIBAgIBATANBgkqhkiG9w0BAQQFADB7MQswCQYDVQQGEwJTRzERMA8G
A1UEChMITTJDcnlwdG8xFDASBgNVBAsTC00yQ3J5cHRvIENBMSQwIgYDVQQDExtN
MkNyeXB0byBDZXJ0aWZpY2F0ZSBNYXN0ZXIxHTAbBgkqhkiG9w0BCQEWDm5ncHNA
cG9zdDEuY29tMB4XDTAwMDkxMDA5NTEzMFoXDTAyMDkxMDA5NTEzMFowUzELMAkG
A1UEBhMCU0cxETAPBgNVBAoTCE0yQ3J5cHRvMRIwEAYDVQQDEwlsb2NhbGhvc3Qx
HTAbBgkqhkiG9w0BCQEWDm5ncHNAcG9zdDEuY29tMFwwDQYJKoZIhvcNAQEBBQAD
SwAwSAJBAKy+e3dulvXzV7zoTZWc5TzgApr8DmeQHTYC8ydfzH7EECe4R1Xh5kwI
zOuuFfn178FBiS84gngaNcrFi0Z5fAkCAwEAAaOCAQQwggEAMAkGA1UdEwQCMAAw
LAYJYIZIAYb4QgENBB8WHU9wZW5TU0wgR2VuZXJhdGVkIENlcnRpZmljYXRlMB0G
A1UdDgQWBBTPhIKSvnsmYsBVNWjj0m3M2z0qVTCBpQYDVR0jBIGdMIGagBT7hyNp
65w6kxXlxb8pUU/+7Sg4AaF/pH0wezELMAkGA1UEBhMCU0cxETAPBgNVBAoTCE0y
Q3J5cHRvMRQwEgYDVQQLEwtNMkNyeXB0byBDQTEkMCIGA1UEAxMbTTJDcnlwdG8g
Q2VydGlmaWNhdGUgTWFzdGVyMR0wGwYJKoZIhvcNAQkBFg5uZ3BzQHBvc3QxLmNv
bYIBADANBgkqhkiG9w0BAQQFAAOBgQA7/CqT6PoHycTdhEStWNZde7M/2Yc6BoJu
VwnW8YxGO8Sn6UJ4FeffZNcYZddSDKosw8LtPOeWoK3JINjAk5jiPQ2cww++7QGG
/g5NDjxFZNDJP1dGiLAxPW6JXwov4v0FmdzfLOZ01jDcgQQZqEpYlgpuI5JEWUQ9
Ho4EzbYCOaEAMQA=
""")

crlData = b"""\
-----BEGIN X509 CRL-----
MIIBWzCBxTANBgkqhkiG9w0BAQQFADBYMQswCQYDVQQGEwJVUzELMAkGA1UECBMC
SUwxEDAOBgNVBAcTB0NoaWNhZ28xEDAOBgNVBAoTB1Rlc3RpbmcxGDAWBgNVBAMT
D1Rlc3RpbmcgUm9vdCBDQRcNMDkwNzI2MDQzNDU2WhcNMTIwOTI3MDI0MTUyWjA8
MBUCAgOrGA8yMDA5MDcyNTIzMzQ1NlowIwICAQAYDzIwMDkwNzI1MjMzNDU2WjAM
MAoGA1UdFQQDCgEEMA0GCSqGSIb3DQEBBAUAA4GBAEBt7xTs2htdD3d4ErrcGAw1
4dKcVnIWTutoI7xxen26Wwvh8VCsT7i/UeP+rBl9rC/kfjWjzQk3/zleaarGTpBT
0yp4HXRFFoRhhSE/hP+eteaPXRgrsNRLHe9ZDd69wmh7J1wMDb0m81RG7kqcbsid
vrzEeLDRiiPl92dyyWmu
-----END X509 CRL-----
"""

crlDataUnsupportedExtension = b"""\
-----BEGIN X509 CRL-----
MIIGRzCCBS8CAQIwDQYJKoZIhvcNAQELBQAwJzELMAkGA1UEBhMCVVMxGDAWBgNV
BAMMD2NyeXB0b2dyYXBoeS5pbxgPMjAxNTAxMDEwMDAwMDBaGA8yMDE2MDEwMTAw
MDAwMFowggTOMBQCAQAYDzIwMTUwMTAxMDAwMDAwWjByAgEBGA8yMDE1MDEwMTAw
MDAwMFowXDAYBgNVHRgEERgPMjAxNTAxMDEwMDAwMDBaMDQGA1UdHQQtMCukKTAn
MQswCQYDVQQGEwJVUzEYMBYGA1UEAwwPY3J5cHRvZ3JhcGh5LmlvMAoGA1UdFQQD
CgEAMHICAQIYDzIwMTUwMTAxMDAwMDAwWjBcMBgGA1UdGAQRGA8yMDE1MDEwMTAw
MDAwMFowNAYDVR0dBC0wK6QpMCcxCzAJBgNVBAYTAlVTMRgwFgYDVQQDDA9jcnlw
dG9ncmFwaHkuaW8wCgYDVR0VBAMKAQEwcgIBAxgPMjAxNTAxMDEwMDAwMDBaMFww
GAYDVR0YBBEYDzIwMTUwMTAxMDAwMDAwWjA0BgNVHR0ELTArpCkwJzELMAkGA1UE
BhMCVVMxGDAWBgNVBAMMD2NyeXB0b2dyYXBoeS5pbzAKBgNVHRUEAwoBAjByAgEE
GA8yMDE1MDEwMTAwMDAwMFowXDAYBgNVHRgEERgPMjAxNTAxMDEwMDAwMDBaMDQG
A1UdHQQtMCukKTAnMQswCQYDVQQGEwJVUzEYMBYGA1UEAwwPY3J5cHRvZ3JhcGh5
LmlvMAoGA1UdFQQDCgEDMHICAQUYDzIwMTUwMTAxMDAwMDAwWjBcMBgGA1UdGAQR
GA8yMDE1MDEwMTAwMDAwMFowNAYDVR0dBC0wK6QpMCcxCzAJBgNVBAYTAlVTMRgw
FgYDVQQDDA9jcnlwdG9ncmFwaHkuaW8wCgYDVR0VBAMKAQQwcgIBBhgPMjAxNTAx
MDEwMDAwMDBaMFwwGAYDVR0YBBEYDzIwMTUwMTAxMDAwMDAwWjA0BgNVHR0ELTAr
pCkwJzELMAkGA1UEBhMCVVMxGDAWBgNVBAMMD2NyeXB0b2dyYXBoeS5pbzAKBgNV
HRUEAwoBBTByAgEHGA8yMDE1MDEwMTAwMDAwMFowXDAYBgNVHRgEERgPMjAxNTAx
MDEwMDAwMDBaMDQGA1UdHQQtMCukKTAnMQswCQYDVQQGEwJVUzEYMBYGA1UEAwwP
Y3J5cHRvZ3JhcGh5LmlvMAoGA1UdFQQDCgEGMHICAQgYDzIwMTUwMTAxMDAwMDAw
WjBcMBgGA1UdGAQRGA8yMDE1MDEwMTAwMDAwMFowNAYDVR0dBC0wK6QpMCcxCzAJ
BgNVBAYTAlVTMRgwFgYDVQQDDA9jcnlwdG9ncmFwaHkuaW8wCgYDVR0VBAMKAQgw
cgIBCRgPMjAxNTAxMDEwMDAwMDBaMFwwGAYDVR0YBBEYDzIwMTUwMTAxMDAwMDAw
WjA0BgNVHR0ELTArpCkwJzELMAkGA1UEBhMCVVMxGDAWBgNVBAMMD2NyeXB0b2dy
YXBoeS5pbzAKBgNVHRUEAwoBCTByAgEKGA8yMDE1MDEwMTAwMDAwMFowXDAYBgNV
HRgEERgPMjAxNTAxMDEwMDAwMDBaMDQGA1UdHQQtMCukKTAnMQswCQYDVQQGEwJV
UzEYMBYGA1UEAwwPY3J5cHRvZ3JhcGh5LmlvMAoGA1UdFQQDCgEKMC4CAQsYDzIw
MTUwMTAxMDAwMDAwWjAYMAoGA1UdFQQDCgEBMAoGAyoDBAQDCgEAMA0GCSqGSIb3
DQEBCwUAA4IBAQBTaloHlPaCZzYee8LxkWej5meiqxQVNWFoVdjesroa+f1FRrH+
drRU60Nq97KCKf7f9GNN/J3ZIlQmYhmuDqh12f+XLpotoj1ZRfBz2hjFCkJlv+2c
oWWGNHgA70ndFoVtcmX088SYpX8E3ARATivS4q2h9WlwV6rO93mhg3HGIe3JpcK4
7BcW6Poi/ut/zsDOkVbI00SqaujRpdmdCTht82MH3ztjyDkI9KYaD/YEweKSrWOz
SdEILd164bfBeLuplVI+xpmTEMVNpXBlSXl7+xIw9Vk7p7Q1Pa3k/SvhOldYCm6y
C1xAg/AAq6w78yzYt18j5Mj0s6eeHi1YpHKw
-----END X509 CRL-----
"""


# A broken RSA private key which can be used to test the error path through
# PKey.check.
inconsistentPrivateKeyPEM = b"""-----BEGIN RSA PRIVATE KEY-----
MIIBPAIBAAJBAKy+e3dulvXzV7zoTZWc5TzgApr8DmeQHTYC8ydfzH7EECe4R1Xh
5kwIzOuuFfn178FBiS84gngaNcrFi0Z5fAkCAwEaAQJBAIqm/bz4NA1H++Vx5Ewx
OcKp3w19QSaZAwlGRtsUxrP7436QjnREM3Bm8ygU11BjkPVmtrKm6AayQfCHqJoT
zIECIQDW0BoMoL0HOYM/mrTLhaykYAVqgIeJsPjvkEhTFXWBuQIhAM3deFAvWNu4
nklUQ37XsCT2c9tmNt1LAT+slG2JOTTRAiAuXDtC/m3NYVwyHfFm+zKHRzHkClk2
HjubeEgjpj32AQIhAJqMGTaZVOwevTXvvHwNeH+vRWsAYU/gbx+OQB+7VOcBAiEA
oolb6NMg/R3enNPvS1O4UU1H8wpaF77L4yiSWlE0p4w=
-----END RSA PRIVATE KEY-----
"""

# certificate with NULL bytes in subjectAltName and common name

nulbyteSubjectAltNamePEM = b"""-----BEGIN CERTIFICATE-----
MIIE2DCCA8CgAwIBAgIBADANBgkqhkiG9w0BAQUFADCBxTELMAkGA1UEBhMCVVMx
DzANBgNVBAgMBk9yZWdvbjESMBAGA1UEBwwJQmVhdmVydG9uMSMwIQYDVQQKDBpQ
eXRob24gU29mdHdhcmUgRm91bmRhdGlvbjEgMB4GA1UECwwXUHl0aG9uIENvcmUg
RGV2ZWxvcG1lbnQxJDAiBgNVBAMMG251bGwucHl0aG9uLm9yZwBleGFtcGxlLm9y
ZzEkMCIGCSqGSIb3DQEJARYVcHl0aG9uLWRldkBweXRob24ub3JnMB4XDTEzMDgw
NzEzMTE1MloXDTEzMDgwNzEzMTI1MlowgcUxCzAJBgNVBAYTAlVTMQ8wDQYDVQQI
DAZPcmVnb24xEjAQBgNVBAcMCUJlYXZlcnRvbjEjMCEGA1UECgwaUHl0aG9uIFNv
ZnR3YXJlIEZvdW5kYXRpb24xIDAeBgNVBAsMF1B5dGhvbiBDb3JlIERldmVsb3Bt
ZW50MSQwIgYDVQQDDBtudWxsLnB5dGhvbi5vcmcAZXhhbXBsZS5vcmcxJDAiBgkq
hkiG9w0BCQEWFXB5dGhvbi1kZXZAcHl0aG9uLm9yZzCCASIwDQYJKoZIhvcNAQEB
BQADggEPADCCAQoCggEBALXq7cn7Rn1vO3aA3TrzA5QLp6bb7B3f/yN0CJ2XFj+j
pHs+Gw6WWSUDpybiiKnPec33BFawq3kyblnBMjBU61ioy5HwQqVkJ8vUVjGIUq3P
vX/wBmQfzCe4o4uM89gpHyUL9UYGG8oCRa17dgqcv7u5rg0Wq2B1rgY+nHwx3JIv
KRrgSwyRkGzpN8WQ1yrXlxWjgI9de0mPVDDUlywcWze1q2kwaEPTM3hLAmD1PESA
oY/n8A/RXoeeRs9i/Pm/DGUS8ZPINXk/yOzsR/XvvkTVroIeLZqfmFpnZeF0cHzL
08LODkVJJ9zjLdT7SA4vnne4FEbAxDbKAq5qkYzaL4UCAwEAAaOB0DCBzTAMBgNV
HRMBAf8EAjAAMB0GA1UdDgQWBBSIWlXAUv9hzVKjNQ/qWpwkOCL3XDALBgNVHQ8E
BAMCBeAwgZAGA1UdEQSBiDCBhYIeYWx0bnVsbC5weXRob24ub3JnAGV4YW1wbGUu
Y29tgSBudWxsQHB5dGhvbi5vcmcAdXNlckBleGFtcGxlLm9yZ4YpaHR0cDovL251
bGwucHl0aG9uLm9yZwBodHRwOi8vZXhhbXBsZS5vcmeHBMAAAgGHECABDbgAAAAA
AAAAAAAAAAEwDQYJKoZIhvcNAQEFBQADggEBAKxPRe99SaghcI6IWT7UNkJw9aO9
i9eo0Fj2MUqxpKbdb9noRDy2CnHWf7EIYZ1gznXPdwzSN4YCjV5d+Q9xtBaowT0j
HPERs1ZuytCNNJTmhyqZ8q6uzMLoht4IqH/FBfpvgaeC5tBTnTT0rD5A/olXeimk
kX4LxlEx5RAvpGB2zZVRGr6LobD9rVK91xuHYNIxxxfEGE8tCCWjp0+3ksri9SXx
VHWBnbM9YaL32u3hxm8sYB/Yb8WSBavJCWJJqRStVRHM1koZlJmXNx2BX4vPo6iW
RFEIPQsFZRLrtnCAiEhyT8bC2s/Njlu6ly9gtJZWSV46Q3ZjBL4q9sHKqZQ=
-----END CERTIFICATE-----"""

large_key_pem = b"""-----BEGIN RSA PRIVATE KEY-----
MIIJYgIBAAKCAg4AtRua8eIeevRfsj+fkcHr1vmse7Kgb+oX1ssJAvCb1R7JQMnH
hNDjDP6b3vEkZuPUzlDHymP+cNkXvvi4wJ4miVbO3+SeU4Sh+jmsHeHzGIXat9xW
9PFtuPM5FQq8zvkY8aDeRYmYwN9JKu4/neMBCBqostYlTEWg+bSytO/qWnyHTHKh
g0GfaDdqUQPsGQw+J0MgaYIjQOCVASHAPlzbDQLCtuOb587rwTLkZA2GwoHB/LyJ
BwT0HHgBaiObE12Vs6wi2en0Uu11CiwEuK1KIBcZ2XbE6eApaZa6VH9ysEmUxPt7
TqyZ4E2oMIYaLPNRxuvozdwTlj1svI1k1FrkaXGc5MTjbgigPMKjIb0T7b/4GNzt
DhP1LvAeUMnrEi3hJJrcJPXHPqS8/RiytR9xQQW6Sdh4LaA3f9MQm3WSevWage3G
P8YcCLssOVKsArDjuA52NF5LmYuAeUzXprm4ITDi2oO+0iFBpFW6VPEK4A9vO0Yk
M/6Wt6tG8zyWhaSH1zFUTwfQ9Yvjyt5w1lrUaAJuoTpwbMVZaDJaEhjOaXU0dyPQ
jOsePDOQcU6dkeTWsQ3LsHPEEug/X6819TLG5mb3V7bvV9nPFBfTJSCEG794kr90
XgZfIN71FrdByxLerlbuJI21pPs/nZi9SXi9jAWeiS45/azUxMsyYgJArui+gjq7
sV1pWiBm6/orAgMBAAECggINQp5L6Yu+oIXBqcSjgq8tfF9M5hd30pLuf/EheHZf
LA7uAqn2fVGFI2OInIJhXIOT5OxsAXO0xXfltzawZxIFpOFMqajj4F7aYjvSpw9V
J4EdSiJ/zgv8y1qUdbwEZbHVThRZjoSlrtSzilonBoHZAE0mHtqMz7iRFSk1zz6t
GunRrvo/lROPentf3TsvHquVNUYI5yaapyO1S7xJhecMIIYSb8nbsHI54FBDGNas
6mFmpPwI/47/6HTwOEWupnn3NicsjrHzUInOUpaMig4cRR+aP5bjqg/ty8xI8AoN
evEmCytiWTc+Rvbp1ieN+1jpjN18PjUk80/W7qioHUDt4ieLic8uxWH2VD9SCEnX
Mpi9tA/FqoZ+2A/3m1OfrY6jiZVE2g+asi9lCK7QVWL39eK82H4rPvtp0/dyo1/i
ZZz68TXg+m8IgEZcp88hngbkuoTTzpGE73QuPKhGA1uMIimDdqPPB5WP76q+03Oi
IRR5DfZnqPERed49by0enJ7tKa/gFPZizOV8ALKr0Dp+vfAkxGDLPLBLd2A3//tw
xg0Q/wltihHSBujv4nYlDXdc5oYyMYZ+Lhc/VuOghHfBq3tgEQ1ECM/ofqXEIdy7
nVcpZn3Eeq8Jl5CrqxE1ee3NxlzsJHn99yGQpr7mOhW/psJF3XNz80Meg3L4m1T8
sMBK0GbaassuJhdzb5whAoIBBw48sx1b1WR4XxQc5O/HjHva+l16i2pjUnOUTcDF
RWmSbIhBm2QQ2rVhO8+fak0tkl6ZnMWW4i0U/X5LOEBbC7+IS8bO3j3Revi+Vw5x
j96LMlIe9XEub5i/saEWgiz7maCvfzLFU08e1OpT4qPDpP293V400ubA6R7WQTCv
pBkskGwHeu0l/TuKkVqBFFUTu7KEbps8Gjg7MkJaFriAOv1zis/umK8pVS3ZAM6e
8w5jfpRccn8Xzta2fRwTB5kCmfxdDsY0oYGxPLRAbW72bORoLGuyyPp/ojeGwoik
JX9RttErc6FjyZtks370Pa8UL5QskyhMbDhrZW2jFD+RXYM1BrvmZRjbAoIBBwy4
iFJpuDfytJfz1MWtaL5DqEL/kmiZYAXl6hifNhGu5GAipVIIGsDqEYW4i+VC15aa
7kOCwz/I5zsB3vSDW96IRs4wXtqEZSibc2W/bqfVi+xcvPPl1ZhQ2EAwa4D/x035
kyf20ffWOU+1yf2cnijzqs3IzlveUm+meLw5s3Rc+iG7DPWWeCoe1hVwANI1euNc
pqKwKY905yFyjOje2OgiEU2kS4YME4zGeBys8yo7E42hNnN2EPK6xkkUqzdudLLQ
8OUlKRTc8AbIf3XG1rpA4VUpTv3hhxGGwCRy6If8zgZQsNYchgNztRGk72Gcb8Dm
vFSEN3ZtwxU64G3YZzntdcr2WPzxAoIBBw30g6Fgdb/gmVnOpL0//T0ePNDKIMPs
jVJLaRduhoZgB1Bb9qPUPX0SzRzLZtg1tkZSDjBDoHmOHJfhxUaXt+FLCPPbrE4t
+nq9n/nBaMM779w9ClqhqLOyGrwKoxjSmhi+TVEHyIxCbXMvPHVHfX9WzxjbcGrN
ZvRaEVZWo+QlIX8yqdSwqxLk1WtAIRzvlcj7NKum8xBxPed6BNFep/PtgIAmoLT5
L8wb7EWb2iUdc2KbZ4OaY51lDScqpATgXu3WjXfM+Q52G0mX6Wyd0cjlL711Zrjb
yLbiueZT94lgIHHRRKtKc8CEqcjkQV5OzABS3P/gQSfgZXBdLKjOpTnKDUq7IBeH
AoIBBweAOEIAPLQg1QRUrr3xRrYKRwlakgZDii9wJt1l5AgBTICzbTA1vzDJ1JM5
AqSpCV6w9JWyYVcXK+HLdKBRZLaPPNEQDJ5lOxD6uMziWGl2rg8tj+1xNMWfxiPz
aTCjoe4EoBUMoTq2gwzRcM2usEQNikXVhnj9Wzaivsaeb4bJ3GRPW5DkrO6JSEtT
w+gvyMqQM2Hy5k7E7BT46sXVwaj/jZxuqGnebRixXtnp0WixdRIqYWUr1UqLf6hQ
G7WP2BgoxCMaCmNW8+HMD/xuxucEotoIhZ+GgJKBFoNnjl3BX+qxYdSe9RbL/5Tr
4It6Jxtj8uETJXEbv9Cg6v1agWPS9YY8RLTBAoIBBwrU2AsAUts6h1LgGLKK3UWZ
oLH5E+4o+7HqSGRcRodVeN9NBXIYdHHOLeEG6YNGJiJ3bFP5ZQEu9iDsyoFVKJ9O
Mw/y6dKZuxOCZ+X8FopSROg3yWfdOpAm6cnQZp3WqLNX4n/Q6WvKojfyEiPphjwT
0ymrUJELXLWJmjUyPoAk6HgC0Gs28ZnEXbyhx7CSbZNFyCU/PNUDZwto3GisIPD3
le7YjqHugezmjMGlA0sDw5aCXjfbl74vowRFYMO6e3ItApfSRgNV86CDoX74WI/5
AYU/QVM4wGt8XGT2KwDFJaxYGKsGDMWmXY04dS+WPuetCbouWUusyFwRb9SzFave
vYeU7Ab/
-----END RSA PRIVATE KEY-----"""

ec_private_key_pem = b"""-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgYirTZSx+5O8Y6tlG
cka6W6btJiocdrdolfcukSoTEk+hRANCAAQkvPNu7Pa1GcsWU4v7ptNfqCJVq8Cx
zo0MUVPQgwJ3aJtNM1QMOQUayCrRwfklg+D/rFSUwEUqtZh7fJDiFqz3
-----END PRIVATE KEY-----
"""

ec_root_key_pem = b"""-----BEGIN EC PRIVATE KEY-----
MIGlAgEBBDEAz/HOBFPYLB0jLWeTpJn4Yc4m/C4mdWymVHBjOmnwiPHKT326iYN/
ZhmSs+RM94RsoAcGBSuBBAAioWQDYgAEwE5vDdla/nLpWAPAQ0yFGqwLuw4BcN2r
U+sKab5EAEHzLeceRa8ffncYdCXNoVsBcdob1y66CFZMEWLetPTmGapyWkBAs6/L
8kUlkU9OsE+7IVo4QQJkgV5gM+Dim1XE
-----END EC PRIVATE KEY-----
"""

ec_root_cert_pem = b"""-----BEGIN CERTIFICATE-----
MIICLTCCAbKgAwIBAgIMWW/hwTl6ufz6/WkCMAoGCCqGSM49BAMDMFgxGDAWBgNV
BAMTD1Rlc3RpbmcgUm9vdCBDQTEQMA4GA1UEChMHVGVzdGluZzEQMA4GA1UEBxMH
Q2hpY2FnbzELMAkGA1UECBMCSUwxCzAJBgNVBAYTAlVTMCAXDTE3MDcxOTIyNDgz
M1oYDzk5OTkxMjMxMjM1OTU5WjBYMRgwFgYDVQQDEw9UZXN0aW5nIFJvb3QgQ0Ex
EDAOBgNVBAoTB1Rlc3RpbmcxEDAOBgNVBAcTB0NoaWNhZ28xCzAJBgNVBAgTAklM
MQswCQYDVQQGEwJVUzB2MBAGByqGSM49AgEGBSuBBAAiA2IABMBObw3ZWv5y6VgD
wENMhRqsC7sOAXDdq1PrCmm+RABB8y3nHkWvH353GHQlzaFbAXHaG9cuughWTBFi
3rT05hmqclpAQLOvy/JFJZFPTrBPuyFaOEECZIFeYDPg4ptVxKNDMEEwDwYDVR0T
AQH/BAUwAwEB/zAPBgNVHQ8BAf8EBQMDBwQAMB0GA1UdDgQWBBSoTrF0H2m8RDzB
MnY2KReEPfz7ZjAKBggqhkjOPQQDAwNpADBmAjEA3+G1oVCxGjYX4iUN93QYcNHe
e3fJQJwX9+KsHRut6qNZDUbvRbtO1YIAwB4UJZjwAjEAtXCPURS5A4McZHnSwgTi
Td8GMrwKz0557OxxtKN6uVVy4ACFMqEw0zN/KJI1vxc9
-----END CERTIFICATE-----"""


@pytest.fixture
def x509_data():
    """
    Create a new private key and start a certificate request (for a test
    to finish in one way or another).
    """
    # Basic setup stuff to generate a certificate
    pkey = PKey()
    pkey.generate_key(TYPE_RSA, 384)
    req = X509Req()
    req.set_pubkey(pkey)
    # Authority good you have.
    req.get_subject().commonName = "Yoda root CA"
    x509 = X509()
    subject = x509.get_subject()
    subject.commonName = req.get_subject().commonName
    x509.set_issuer(subject)
    x509.set_pubkey(pkey)
    now = datetime.now()
    expire = datetime.now() + timedelta(days=100)
    x509.set_notBefore(now.strftime("%Y%m%d%H%M%SZ").encode())
    x509.set_notAfter(expire.strftime("%Y%m%d%H%M%SZ").encode())
    yield pkey, x509


class TestX509Ext(object):
    """
    Tests for `OpenSSL.crypto.X509Extension`.
    """

    def test_str(self):
        """
        The string representation of `X509Extension` instances as
        returned by `str` includes stuff.
        """
        # This isn't necessarily the best string representation.  Perhaps it
        # will be changed/improved in the future.
        assert (
            str(X509Extension(b'basicConstraints', True, b'CA:false')) ==
            'CA:FALSE'
        )

    def test_type(self):
        """
        `X509Extension` and `X509ExtensionType` refer to the same type object
        and can be used to create instances of that type.
        """
        assert X509Extension is X509ExtensionType
        assert is_consistent_type(
            X509Extension,
            'X509Extension', b'basicConstraints', True, b'CA:true')

    def test_construction(self):
        """
        `X509Extension` accepts an extension type name, a critical flag,
        and an extension value and returns an `X509ExtensionType` instance.
        """
        basic = X509Extension(b'basicConstraints', True, b'CA:true')
        assert isinstance(basic, X509ExtensionType)

        comment = X509Extension(b'nsComment', False, b'pyOpenSSL unit test')
        assert isinstance(comment, X509ExtensionType)

    @pytest.mark.parametrize('type_name, critical, value', [
        (b'thisIsMadeUp', False, b'hi'),
        (b'basicConstraints', False, b'blah blah'),

        # Exercise a weird one (an extension which uses the r2i method).  This
        # exercises the codepath that requires a non-NULL ctx to be passed to
        # X509V3_EXT_nconf.  It can't work now because we provide no
        # configuration database.  It might be made to work in the future.
        (b'proxyCertInfo', True,
         b'language:id-ppl-anyLanguage,pathlen:1,policy:text:AB')
    ])
    def test_invalid_extension(self, type_name, critical, value):
        """
        `X509Extension` raises something if it is passed a bad
        extension name or value.
        """
        with pytest.raises(Error):
            X509Extension(type_name, critical, value)

    @pytest.mark.parametrize('critical_flag', [True, False])
    def test_get_critical(self, critical_flag):
        """
        `X509ExtensionType.get_critical` returns the value of the
        extension's critical flag.
        """
        ext = X509Extension(b'basicConstraints', critical_flag, b'CA:true')
        assert ext.get_critical() == critical_flag

    @pytest.mark.parametrize('short_name, value', [
        (b'basicConstraints', b'CA:true'),
        (b'nsComment', b'foo bar'),
    ])
    def test_get_short_name(self, short_name, value):
        """
        `X509ExtensionType.get_short_name` returns a string giving the
        short type name of the extension.
        """
        ext = X509Extension(short_name, True, value)
        assert ext.get_short_name() == short_name

    def test_get_data(self):
        """
        `X509Extension.get_data` returns a string giving the data of
        the extension.
        """
        ext = X509Extension(b'basicConstraints', True, b'CA:true')
        # Expect to get back the DER encoded form of CA:true.
        assert ext.get_data() == b'0\x03\x01\x01\xff'

    def test_unused_subject(self, x509_data):
        """
        The `subject` parameter to `X509Extension` may be provided for an
        extension which does not use it and is ignored in this case.
        """
        pkey, x509 = x509_data
        ext1 = X509Extension(
            b'basicConstraints', False, b'CA:TRUE', subject=x509)
        x509.add_extensions([ext1])
        x509.sign(pkey, 'sha1')
        # This is a little lame.  Can we think of a better way?
        text = dump_certificate(FILETYPE_TEXT, x509)
        assert b'X509v3 Basic Constraints:' in text
        assert b'CA:TRUE' in text

    def test_subject(self, x509_data):
        """
        If an extension requires a subject, the `subject` parameter to
        `X509Extension` provides its value.
        """
        pkey, x509 = x509_data
        ext3 = X509Extension(
            b'subjectKeyIdentifier', False, b'hash', subject=x509)
        x509.add_extensions([ext3])
        x509.sign(pkey, 'sha1')
        text = dump_certificate(FILETYPE_TEXT, x509)
        assert b'X509v3 Subject Key Identifier:' in text

    def test_missing_subject(self):
        """
        If an extension requires a subject and the `subject` parameter
        is given no value, something happens.
        """
        with pytest.raises(Error):
            X509Extension(b'subjectKeyIdentifier', False, b'hash')

    @pytest.mark.parametrize('bad_obj', [
        True,
        object(),
        "hello",
        [],
    ])
    def test_invalid_subject(self, bad_obj):
        """
        If the `subject` parameter is given a value which is not an
        `X509` instance, `TypeError` is raised.
        """
        with pytest.raises(TypeError):
            X509Extension(
                'basicConstraints', False, 'CA:TRUE', subject=bad_obj)

    def test_unused_issuer(self, x509_data):
        """
        The `issuer` parameter to `X509Extension` may be provided for an
        extension which does not use it and is ignored in this case.
        """
        pkey, x509 = x509_data
        ext1 = X509Extension(
            b'basicConstraints', False, b'CA:TRUE', issuer=x509)
        x509.add_extensions([ext1])
        x509.sign(pkey, 'sha1')
        text = dump_certificate(FILETYPE_TEXT, x509)
        assert b'X509v3 Basic Constraints:' in text
        assert b'CA:TRUE' in text

    def test_issuer(self, x509_data):
        """
        If an extension requires an issuer, the `issuer` parameter to
        `X509Extension` provides its value.
        """
        pkey, x509 = x509_data
        ext2 = X509Extension(
            b'authorityKeyIdentifier', False, b'issuer:always',
            issuer=x509)
        x509.add_extensions([ext2])
        x509.sign(pkey, 'sha1')
        text = dump_certificate(FILETYPE_TEXT, x509)
        assert b'X509v3 Authority Key Identifier:' in text
        assert b'DirName:/CN=Yoda root CA' in text

    def test_missing_issuer(self):
        """
        If an extension requires an issue and the `issuer` parameter is
        given no value, something happens.
        """
        with pytest.raises(Error):
            X509Extension(
                b'authorityKeyIdentifier',
                False, b'keyid:always,issuer:always')

    @pytest.mark.parametrize('bad_obj', [
        True,
        object(),
        "hello",
        [],
    ])
    def test_invalid_issuer(self, bad_obj):
        """
        If the `issuer` parameter is given a value which is not an
        `X509` instance, `TypeError` is raised.
        """
        with pytest.raises(TypeError):
            X509Extension(
                'basicConstraints', False, 'keyid:always,issuer:always',
                issuer=bad_obj)


class TestPKey(object):
    """
    Tests for `OpenSSL.crypto.PKey`.
    """

    def test_convert_from_cryptography_private_key(self):
        """
        PKey.from_cryptography_key creates a proper private PKey.
        """
        key = serialization.load_pem_private_key(
            intermediate_key_pem, None, backend
        )
        pkey = PKey.from_cryptography_key(key)

        assert isinstance(pkey, PKey)
        assert pkey.bits() == key.key_size
        assert pkey._only_public is False
        assert pkey._initialized is True

    def test_convert_from_cryptography_public_key(self):
        """
        PKey.from_cryptography_key creates a proper public PKey.
        """
        key = serialization.load_pem_public_key(cleartextPublicKeyPEM, backend)
        pkey = PKey.from_cryptography_key(key)

        assert isinstance(pkey, PKey)
        assert pkey.bits() == key.key_size
        assert pkey._only_public is True
        assert pkey._initialized is True

    def test_convert_from_cryptography_unsupported_type(self):
        """
        PKey.from_cryptography_key raises TypeError with an unsupported type.
        """
        key = serialization.load_pem_private_key(
            ec_private_key_pem, None, backend
        )
        with pytest.raises(TypeError):
            PKey.from_cryptography_key(key)

    def test_convert_public_pkey_to_cryptography_key(self):
        """
        PKey.to_cryptography_key creates a proper cryptography public key.
        """
        pkey = load_publickey(FILETYPE_PEM, cleartextPublicKeyPEM)
        key = pkey.to_cryptography_key()

        assert isinstance(key, rsa.RSAPublicKey)
        assert pkey.bits() == key.key_size

    def test_convert_private_pkey_to_cryptography_key(self):
        """
        PKey.to_cryptography_key creates a proper cryptography private key.
        """
        pkey = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        key = pkey.to_cryptography_key()

        assert isinstance(key, rsa.RSAPrivateKey)
        assert pkey.bits() == key.key_size

    def test_type(self):
        """
        `PKey` and `PKeyType` refer to the same type object and can be used to
        create instances of that type.
        """
        assert PKey is PKeyType
        assert is_consistent_type(PKey, 'PKey')

    def test_construction(self):
        """
        `PKey` takes no arguments and returns a new `PKey` instance.
        """
        key = PKey()
        assert isinstance(key, PKey)

    def test_pregeneration(self):
        """
        `PKey.bits` and `PKey.type` return `0` before the key is generated.
        `PKey.check` raises `TypeError` before the key is generated.
        """
        key = PKey()
        assert key.type() == 0
        assert key.bits() == 0
        with pytest.raises(TypeError):
            key.check()

    def test_failed_generation(self):
        """
        `PKey.generate_key` takes two arguments, the first giving the key type
        as one of `TYPE_RSA` or `TYPE_DSA` and the second giving the number of
        bits to generate.  If an invalid type is specified or generation fails,
        `Error` is raised.  If an invalid number of bits is specified,
        `ValueError` or `Error` is raised.
        """
        key = PKey()
        with pytest.raises(TypeError):
            key.generate_key("foo", "bar")
        with pytest.raises(Error):
            key.generate_key(-1, 0)

        with pytest.raises(ValueError):
            key.generate_key(TYPE_RSA, -1)
        with pytest.raises(ValueError):
            key.generate_key(TYPE_RSA, 0)

        with pytest.raises(TypeError):
            key.generate_key(TYPE_RSA, object())

        # XXX RSA generation for small values of bits is fairly buggy in a wide
        # range of OpenSSL versions.  I need to figure out what the safe lower
        # bound for a reasonable number of OpenSSL versions is and explicitly
        # check for that in the wrapper.  The failure behavior is typically an
        # infinite loop inside OpenSSL.

        # with pytest.raises(Error):
        #     key.generate_key(TYPE_RSA, 2)

        # XXX DSA generation seems happy with any number of bits.  The DSS
        # says bits must be between 512 and 1024 inclusive.  OpenSSL's DSA
        # generator doesn't seem to care about the upper limit at all.  For
        # the lower limit, it uses 512 if anything smaller is specified.
        # So, it doesn't seem possible to make generate_key fail for
        # TYPE_DSA with a bits argument which is at least an int.

        # with pytest.raises(Error):
        #     key.generate_key(TYPE_DSA, -7)

    def test_rsa_generation(self):
        """
        `PKey.generate_key` generates an RSA key when passed `TYPE_RSA` as a
        type and a reasonable number of bits.
        """
        bits = 128
        key = PKey()
        key.generate_key(TYPE_RSA, bits)
        assert key.type() == TYPE_RSA
        assert key.bits() == bits
        assert key.check()

    def test_dsa_generation(self):
        """
        `PKey.generate_key` generates a DSA key when passed `TYPE_DSA` as a
        type and a reasonable number of bits.
        """
        # 512 is a magic number.  The DSS (Digital Signature Standard)
        # allows a minimum of 512 bits for DSA.  DSA_generate_parameters
        # will silently promote any value below 512 to 512.
        bits = 512
        key = PKey()
        key.generate_key(TYPE_DSA, bits)
        assert key.type() == TYPE_DSA
        assert key.bits() == bits
        with pytest.raises(TypeError):
            key.check()

    def test_regeneration(self):
        """
        `PKey.generate_key` can be called multiple times on the same key to
        generate new keys.
        """
        key = PKey()
        for type, bits in [(TYPE_RSA, 512), (TYPE_DSA, 576)]:
            key.generate_key(type, bits)
            assert key.type() == type
            assert key.bits() == bits

    def test_inconsistent_key(self):
        """
        `PKey.check` returns `Error` if the key is not consistent.
        """
        key = load_privatekey(FILETYPE_PEM, inconsistentPrivateKeyPEM)
        with pytest.raises(Error):
            key.check()

    def test_check_public_key(self):
        """
        `PKey.check` raises `TypeError` if only the public part of the key
        is available.
        """
        # A trick to get a public-only key
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        cert = X509()
        cert.set_pubkey(key)
        pub = cert.get_pubkey()
        with pytest.raises(TypeError):
            pub.check()


def x509_name(**attrs):
    """
    Return a new X509Name with the given attributes.
    """
    # XXX There's no other way to get a new X509Name yet.
    name = X509().get_subject()
    attrs = list(attrs.items())

    # Make the order stable - order matters!
    def key(attr):
        return attr[1]
    attrs.sort(key=key)
    for k, v in attrs:
        setattr(name, k, v)
    return name


class TestX509Name(object):
    """
    Unit tests for `OpenSSL.crypto.X509Name`.
    """

    def test_type(self):
        """
        The type of X509Name objects is `X509NameType`.
        """
        assert X509Name is X509NameType
        assert X509NameType.__name__ == 'X509Name'
        assert isinstance(X509NameType, type)

        name = x509_name()
        assert isinstance(name, X509NameType)

    def test_only_string_attributes(self):
        """
        Attempting to set a non-`str` attribute name on an `X509Name` instance
        causes `TypeError` to be raised.
        """
        name = x509_name()
        # Beyond these cases, you may also think that unicode should be
        # rejected.  Sorry, you're wrong.  unicode is automatically converted
        # to str outside of the control of X509Name, so there's no way to
        # reject it.

        # Also, this used to test str subclasses, but that test is less
        # relevant now that the implementation is in Python instead of C.  Also
        # PyPy automatically converts str subclasses to str when they are
        # passed to setattr, so we can't test it on PyPy.  Apparently CPython
        # does this sometimes as well.
        with pytest.raises(TypeError):
            setattr(name, None, "hello")
        with pytest.raises(TypeError):
            setattr(name, 30, "hello")

    def test_set_invalid_attribute(self):
        """
        Attempting to set any attribute name on an `X509Name` instance for
        which no corresponding NID is defined causes `AttributeError` to be
        raised.
        """
        name = x509_name()
        with pytest.raises(AttributeError):
            setattr(name, "no such thing", None)

    def test_attributes(self):
        """
        `X509Name` instances have attributes for each standard (?)
        X509Name field.
        """
        name = x509_name()
        name.commonName = "foo"
        assert name.commonName == "foo"
        assert name.CN == "foo"

        name.CN = "baz"
        assert name.commonName == "baz"
        assert name.CN == "baz"

        name.commonName = "bar"
        assert name.commonName == "bar"
        assert name.CN == "bar"

        name.CN = "quux"
        assert name.commonName == "quux"
        assert name.CN == "quux"

        assert name.OU is None

        with pytest.raises(AttributeError):
            name.foobar

    def test_copy(self):
        """
        `X509Name` creates a new `X509Name` instance with all the same
        attributes as an existing `X509Name` instance when called with one.
        """
        name = x509_name(commonName="foo", emailAddress="bar@example.com")

        copy = X509Name(name)
        assert copy.commonName == "foo"
        assert copy.emailAddress == "bar@example.com"

        # Mutate the copy and ensure the original is unmodified.
        copy.commonName = "baz"
        assert name.commonName == "foo"

        # Mutate the original and ensure the copy is unmodified.
        name.emailAddress = "quux@example.com"
        assert copy.emailAddress == "bar@example.com"

    def test_repr(self):
        """
        `repr` passed an `X509Name` instance should return a string containing
        a description of the type and the NIDs which have been set on it.
        """
        name = x509_name(commonName="foo", emailAddress="bar")
        assert repr(name) == "<X509Name object '/emailAddress=bar/CN=foo'>"

    def test_comparison(self):
        """
        `X509Name` instances should compare based on their NIDs.
        """
        def _equality(a, b, assert_true, assert_false):
            assert_true(a == b)
            assert_false(a != b)
            assert_true(b == a)
            assert_false(b != a)

        def assert_true(x):
            assert x

        def assert_false(x):
            assert not x

        def assert_equal(a, b):
            _equality(a, b, assert_true, assert_false)

        # Instances compare equal to themselves.
        name = x509_name()
        assert_equal(name, name)

        # Empty instances should compare equal to each other.
        assert_equal(x509_name(), x509_name())

        # Instances with equal NIDs should compare equal to each other.
        assert_equal(x509_name(commonName="foo"),
                     x509_name(commonName="foo"))

        # Instance with equal NIDs set using different aliases should compare
        # equal to each other.
        assert_equal(x509_name(commonName="foo"),
                     x509_name(CN="foo"))

        # Instances with more than one NID with the same values should compare
        # equal to each other.
        assert_equal(x509_name(CN="foo", organizationalUnitName="bar"),
                     x509_name(commonName="foo", OU="bar"))

        def assert_not_equal(a, b):
            _equality(a, b, assert_false, assert_true)

        # Instances with different values for the same NID should not compare
        # equal to each other.
        assert_not_equal(x509_name(CN="foo"),
                         x509_name(CN="bar"))

        # Instances with different NIDs should not compare equal to each other.
        assert_not_equal(x509_name(CN="foo"),
                         x509_name(OU="foo"))

        assert_not_equal(x509_name(), object())

        def _inequality(a, b, assert_true, assert_false):
            assert_true(a < b)
            assert_true(a <= b)
            assert_true(b > a)
            assert_true(b >= a)
            assert_false(a > b)
            assert_false(a >= b)
            assert_false(b < a)
            assert_false(b <= a)

        def assert_less_than(a, b):
            _inequality(a, b, assert_true, assert_false)

        # An X509Name with a NID with a value which sorts less than the value
        # of the same NID on another X509Name compares less than the other
        # X509Name.
        assert_less_than(x509_name(CN="abc"),
                         x509_name(CN="def"))

        def assert_greater_than(a, b):
            _inequality(a, b, assert_false, assert_true)

        # An X509Name with a NID with a value which sorts greater than the
        # value of the same NID on another X509Name compares greater than the
        # other X509Name.
        assert_greater_than(x509_name(CN="def"),
                            x509_name(CN="abc"))

    def test_hash(self):
        """
        `X509Name.hash` returns an integer hash based on the value of the name.
        """
        a = x509_name(CN="foo")
        b = x509_name(CN="foo")
        assert a.hash() == b.hash()
        a.CN = "bar"
        assert a.hash() != b.hash()

    def test_der(self):
        """
        `X509Name.der` returns the DER encoded form of the name.
        """
        a = x509_name(CN="foo", C="US")
        assert (a.der() ==
                b'0\x1b1\x0b0\t\x06\x03U\x04\x06\x13\x02US'
                b'1\x0c0\n\x06\x03U\x04\x03\x0c\x03foo')

    def test_get_components(self):
        """
        `X509Name.get_components` returns a `list` of two-tuples of `str`
        giving the NIDs and associated values which make up the name.
        """
        a = x509_name()
        assert a.get_components() == []
        a.CN = "foo"
        assert a.get_components() == [(b"CN", b"foo")]
        a.organizationalUnitName = "bar"
        assert a.get_components() == [(b"CN", b"foo"), (b"OU", b"bar")]

    def test_load_nul_byte_attribute(self):
        """
        An `X509Name` from an `X509` instance loaded from a file can have a
        NUL byte in the value of one of its attributes.
        """
        cert = load_certificate(FILETYPE_PEM, nulbyteSubjectAltNamePEM)
        subject = cert.get_subject()
        assert "null.python.org\x00example.org" == subject.commonName

    def test_set_attribute_failure(self):
        """
        If the value of an attribute cannot be set for some reason then
        `Error` is raised.
        """
        name = x509_name()
        # This value is too long
        with pytest.raises(Error):
            setattr(name, "O", b"x" * 512)


class _PKeyInteractionTestsMixin:
    """
    Tests which involve another thing and a PKey.
    """

    def signable(self):
        """
        Return something with a `set_pubkey`, `set_pubkey`, and `sign` method.
        """
        raise NotImplementedError()

    def test_sign_with_ungenerated(self):
        """
        `X509Req.sign` raises `ValueError` when passed a `PKey` with no parts.
        """
        request = self.signable()
        key = PKey()
        with pytest.raises(ValueError):
            request.sign(key, GOOD_DIGEST)

    def test_sign_with_public_key(self):
        """
        `X509Req.sign` raises `ValueError` when passed a `PKey` with no private
        part as the signing key.
        """
        request = self.signable()
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        request.set_pubkey(key)
        pub = request.get_pubkey()
        with pytest.raises(ValueError):
            request.sign(pub, GOOD_DIGEST)

    def test_sign_with_unknown_digest(self):
        """
        `X509Req.sign` raises `ValueError` when passed a digest name which is
        not known.
        """
        request = self.signable()
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        with pytest.raises(ValueError):
            request.sign(key, BAD_DIGEST)

    def test_sign(self):
        """
        `X509Req.sign` succeeds when passed a private key object and a
        valid digest function. `X509Req.verify` can be used to check
        the signature.
        """
        request = self.signable()
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        request.set_pubkey(key)
        request.sign(key, GOOD_DIGEST)
        # If the type has a verify method, cover that too.
        if getattr(request, 'verify', None) is not None:
            pub = request.get_pubkey()
            assert request.verify(pub)
            # Make another key that won't verify.
            key = PKey()
            key.generate_key(TYPE_RSA, 512)
            with pytest.raises(Error):
                request.verify(key)


class TestX509Req(_PKeyInteractionTestsMixin):
    """
    Tests for `OpenSSL.crypto.X509Req`.
    """

    def signable(self):
        """
        Create and return a new `X509Req`.
        """
        return X509Req()

    def test_type(self):
        """
        `X509Req` and `X509ReqType` refer to the same type object and can be
        used to create instances of that type.
        """
        assert X509Req is X509ReqType
        assert is_consistent_type(X509Req, 'X509Req')

    def test_construction(self):
        """
        `X509Req` takes no arguments and returns an `X509ReqType` instance.
        """
        request = X509Req()
        assert isinstance(request, X509ReqType)

    def test_version(self):
        """
        `X509Req.set_version` sets the X.509 version of the certificate
        request. `X509Req.get_version` returns the X.509 version of the
        certificate request. The initial value of the version is 0.
        """
        request = X509Req()
        assert request.get_version() == 0
        request.set_version(1)
        assert request.get_version() == 1
        request.set_version(3)
        assert request.get_version() == 3

    def test_version_wrong_args(self):
        """
        `X509Req.set_version` raises `TypeError` if called with a non-`int`
        argument.
        """
        request = X509Req()
        with pytest.raises(TypeError):
            request.set_version("foo")

    def test_get_subject(self):
        """
        `X509Req.get_subject` returns an `X509Name` for the subject of the
        request and which is valid even after the request object is
        otherwise dead.
        """
        request = X509Req()
        subject = request.get_subject()
        assert isinstance(subject, X509NameType)
        subject.commonName = "foo"
        assert request.get_subject().commonName == "foo"
        del request
        subject.commonName = "bar"
        assert subject.commonName == "bar"

    def test_add_extensions(self):
        """
        `X509Req.add_extensions` accepts a `list` of `X509Extension` instances
        and adds them to the X509 request.
        """
        request = X509Req()
        request.add_extensions([
            X509Extension(b'basicConstraints', True, b'CA:false')])
        exts = request.get_extensions()
        assert len(exts) == 1
        assert exts[0].get_short_name() == b'basicConstraints'
        assert exts[0].get_critical() == 1
        assert exts[0].get_data() == b'0\x00'

    def test_get_extensions(self):
        """
        `X509Req.get_extensions` returns a `list` of extensions added to this
        X509 request.
        """
        request = X509Req()
        exts = request.get_extensions()
        assert exts == []
        request.add_extensions([
            X509Extension(b'basicConstraints', True, b'CA:true'),
            X509Extension(b'keyUsage', False, b'digitalSignature')])
        exts = request.get_extensions()
        assert len(exts) == 2
        assert exts[0].get_short_name() == b'basicConstraints'
        assert exts[0].get_critical() == 1
        assert exts[0].get_data() == b'0\x03\x01\x01\xff'
        assert exts[1].get_short_name() == b'keyUsage'
        assert exts[1].get_critical() == 0
        assert exts[1].get_data() == b'\x03\x02\x07\x80'

    def test_add_extensions_wrong_args(self):
        """
        `X509Req.add_extensions` raises `TypeError` if called with a
        non-`list`.  Or it raises `ValueError` if called with a `list`
        containing objects other than `X509Extension` instances.
        """
        request = X509Req()
        with pytest.raises(TypeError):
            request.add_extensions(object())
        with pytest.raises(ValueError):
            request.add_extensions([object()])

    def test_verify_wrong_args(self):
        """
        `X509Req.verify` raises `TypeError` if passed anything other than a
        `PKey` instance as its single argument.
        """
        request = X509Req()
        with pytest.raises(TypeError):
            request.verify(object())

    def test_verify_uninitialized_key(self):
        """
        `X509Req.verify` raises `OpenSSL.crypto.Error` if called with a
        `OpenSSL.crypto.PKey` which contains no key data.
        """
        request = X509Req()
        pkey = PKey()
        with pytest.raises(Error):
            request.verify(pkey)

    def test_verify_wrong_key(self):
        """
        `X509Req.verify` raises `OpenSSL.crypto.Error` if called with a
        `OpenSSL.crypto.PKey` which does not represent the public part of the
        key which signed the request.
        """
        request = X509Req()
        pkey = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        request.sign(pkey, GOOD_DIGEST)
        another_pkey = load_privatekey(FILETYPE_PEM, client_key_pem)
        with pytest.raises(Error):
            request.verify(another_pkey)

    def test_verify_success(self):
        """
        `X509Req.verify` returns `True` if called with a `OpenSSL.crypto.PKey`
        which represents the public part of the key which signed the request.
        """
        request = X509Req()
        pkey = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        request.sign(pkey, GOOD_DIGEST)
        assert request.verify(pkey)

    def test_convert_from_cryptography(self):
        crypto_req = x509.load_pem_x509_csr(
            cleartextCertificateRequestPEM, backend
        )
        req = X509Req.from_cryptography(crypto_req)
        assert isinstance(req, X509Req)

    def test_convert_from_cryptography_unsupported_type(self):
        with pytest.raises(TypeError):
            X509Req.from_cryptography(object())

    def test_convert_to_cryptography_key(self):
        req = load_certificate_request(
            FILETYPE_PEM, cleartextCertificateRequestPEM
        )
        crypto_req = req.to_cryptography()
        assert isinstance(crypto_req, x509.CertificateSigningRequest)


class TestX509(_PKeyInteractionTestsMixin):
    """
    Tests for `OpenSSL.crypto.X509`.
    """
    pemData = cleartextCertificatePEM + cleartextPrivateKeyPEM

    extpem = """
-----BEGIN CERTIFICATE-----
MIIC3jCCAkegAwIBAgIJAJHFjlcCgnQzMA0GCSqGSIb3DQEBBQUAMEcxCzAJBgNV
BAYTAlNFMRUwEwYDVQQIEwxXZXN0ZXJib3R0b20xEjAQBgNVBAoTCUNhdGFsb2dp
eDENMAsGA1UEAxMEUm9vdDAeFw0wODA0MjIxNDQ1MzhaFw0wOTA0MjIxNDQ1Mzha
MFQxCzAJBgNVBAYTAlNFMQswCQYDVQQIEwJXQjEUMBIGA1UEChMLT3Blbk1ldGFk
aXIxIjAgBgNVBAMTGW5vZGUxLm9tMi5vcGVubWV0YWRpci5vcmcwgZ8wDQYJKoZI
hvcNAQEBBQADgY0AMIGJAoGBAPIcQMrwbk2nESF/0JKibj9i1x95XYAOwP+LarwT
Op4EQbdlI9SY+uqYqlERhF19w7CS+S6oyqx0DRZSk4Y9dZ9j9/xgm2u/f136YS1u
zgYFPvfUs6PqYLPSM8Bw+SjJ+7+2+TN+Tkiof9WP1cMjodQwOmdsiRbR0/J7+b1B
hec1AgMBAAGjgcQwgcEwCQYDVR0TBAIwADAsBglghkgBhvhCAQ0EHxYdT3BlblNT
TCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwHQYDVR0OBBYEFIdHsBcMVVMbAO7j6NCj
03HgLnHaMB8GA1UdIwQYMBaAFL2h9Bf9Mre4vTdOiHTGAt7BRY/8MEYGA1UdEQQ/
MD2CDSouZXhhbXBsZS5vcmeCESoub20yLmV4bWFwbGUuY29thwSC7wgKgRNvbTJA
b3Blbm1ldGFkaXIub3JnMA0GCSqGSIb3DQEBBQUAA4GBALd7WdXkp2KvZ7/PuWZA
MPlIxyjS+Ly11+BNE0xGQRp9Wz+2lABtpgNqssvU156+HkKd02rGheb2tj7MX9hG
uZzbwDAZzJPjzDQDD7d3cWsrVcfIdqVU7epHqIadnOF+X0ghJ39pAm6VVadnSXCt
WpOdIpB8KksUTCzV591Nr1wd
-----END CERTIFICATE-----
    """

    def signable(self):
        """
        Create and return a new `X509`.
        """
        return X509()

    def test_type(self):
        """
        `X509` and `X509Type` refer to the same type object and can be used to
        create instances of that type.
        """
        assert X509 is X509Type
        assert is_consistent_type(X509, 'X509')

    def test_construction(self):
        """
        `X509` takes no arguments and returns an instance of `X509Type`.
        """
        certificate = X509()
        assert isinstance(certificate, X509Type)
        assert type(X509Type).__name__ == 'type'
        assert type(certificate).__name__ == 'X509'
        assert type(certificate) == X509Type
        assert type(certificate) == X509

    def test_set_version_wrong_args(self):
        """
        `X509.set_version` raises `TypeError` if invoked with an argument
        not of type `int`.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.set_version(None)

    def test_version(self):
        """
        `X509.set_version` sets the certificate version number.
        `X509.get_version` retrieves it.
        """
        cert = X509()
        cert.set_version(1234)
        assert cert.get_version() == 1234

    def test_serial_number(self):
        """
        The serial number of an `X509` can be retrieved and
        modified with `X509.get_serial_number` and
        `X509.set_serial_number`.
        """
        certificate = X509()
        with pytest.raises(TypeError):
            certificate.set_serial_number("1")
        assert certificate.get_serial_number() == 0
        certificate.set_serial_number(1)
        assert certificate.get_serial_number() == 1
        certificate.set_serial_number(2 ** 32 + 1)
        assert certificate.get_serial_number() == 2 ** 32 + 1
        certificate.set_serial_number(2 ** 64 + 1)
        assert certificate.get_serial_number() == 2 ** 64 + 1
        certificate.set_serial_number(2 ** 128 + 1)
        assert certificate.get_serial_number() == 2 ** 128 + 1

    def _setBoundTest(self, which):
        """
        `X509.set_notBefore` takes a string in the format of an
        ASN1 GENERALIZEDTIME and sets the beginning of the certificate's
        validity period to it.
        """
        certificate = X509()
        set = getattr(certificate, 'set_not' + which)
        get = getattr(certificate, 'get_not' + which)

        # Starts with no value.
        assert get() is None

        # GMT (Or is it UTC?) -exarkun
        when = b"20040203040506Z"
        set(when)
        assert get() == when

        # A plus two hours and thirty minutes offset
        when = b"20040203040506+0530"
        set(when)
        assert get() == when

        # A minus one hour fifteen minutes offset
        when = b"20040203040506-0115"
        set(when)
        assert get() == when

        # An invalid string results in a ValueError
        with pytest.raises(ValueError):
            set(b"foo bar")

        # The wrong number of arguments results in a TypeError.
        with pytest.raises(TypeError):
            set()
        with pytest.raises(TypeError):
            set(b"20040203040506Z", b"20040203040506Z")
        with pytest.raises(TypeError):
            get(b"foo bar")

    # XXX ASN1_TIME (not GENERALIZEDTIME)

    def test_set_notBefore(self):
        """
        `X509.set_notBefore` takes a string in the format of an
        ASN1 GENERALIZEDTIME and sets the beginning of the certificate's
        validity period to it.
        """
        self._setBoundTest("Before")

    def test_set_notAfter(self):
        """
        `X509.set_notAfter` takes a string in the format of an ASN1
        GENERALIZEDTIME and sets the end of the certificate's validity period
        to it.
        """
        self._setBoundTest("After")

    def test_get_notBefore(self):
        """
        `X509.get_notBefore` returns a string in the format of an
        ASN1 GENERALIZEDTIME even for certificates which store it as UTCTIME
        internally.
        """
        cert = load_certificate(FILETYPE_PEM, old_root_cert_pem)
        assert cert.get_notBefore() == b"20090325123658Z"

    def test_get_notAfter(self):
        """
        `X509.get_notAfter` returns a string in the format of an
        ASN1 GENERALIZEDTIME even for certificates which store it as UTCTIME
        internally.
        """
        cert = load_certificate(FILETYPE_PEM, old_root_cert_pem)
        assert cert.get_notAfter() == b"20170611123658Z"

    def test_gmtime_adj_notBefore_wrong_args(self):
        """
        `X509.gmtime_adj_notBefore` raises `TypeError` if called with a
        non-`int` argument.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.gmtime_adj_notBefore(None)

    @flaky.flaky
    def test_gmtime_adj_notBefore(self):
        """
        `X509.gmtime_adj_notBefore` changes the not-before timestamp to be the
        current time plus the number of seconds passed in.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        not_before_min = (
            datetime.utcnow().replace(microsecond=0) + timedelta(seconds=100)
        )
        cert.gmtime_adj_notBefore(100)
        not_before = datetime.strptime(
            cert.get_notBefore().decode(), "%Y%m%d%H%M%SZ"
        )
        not_before_max = datetime.utcnow() + timedelta(seconds=100)
        assert not_before_min <= not_before <= not_before_max

    def test_gmtime_adj_notAfter_wrong_args(self):
        """
        `X509.gmtime_adj_notAfter` raises `TypeError` if called with a
        non-`int` argument.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.gmtime_adj_notAfter(None)

    @flaky.flaky
    def test_gmtime_adj_notAfter(self):
        """
        `X509.gmtime_adj_notAfter` changes the not-after timestamp
        to be the current time plus the number of seconds passed in.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        not_after_min = (
            datetime.utcnow().replace(microsecond=0) + timedelta(seconds=100)
        )
        cert.gmtime_adj_notAfter(100)
        not_after = datetime.strptime(
            cert.get_notAfter().decode(), "%Y%m%d%H%M%SZ"
        )
        not_after_max = datetime.utcnow() + timedelta(seconds=100)
        assert not_after_min <= not_after <= not_after_max

    def test_has_expired(self):
        """
        `X509.has_expired` returns `True` if the certificate's not-after time
        is in the past.
        """
        cert = X509()
        cert.gmtime_adj_notAfter(-1)
        assert cert.has_expired()

    def test_has_not_expired(self):
        """
        `X509.has_expired` returns `False` if the certificate's not-after time
        is in the future.
        """
        cert = X509()
        cert.gmtime_adj_notAfter(2)
        assert not cert.has_expired()

    def test_root_has_not_expired(self):
        """
        `X509.has_expired` returns `False` if the certificate's not-after time
        is in the future.
        """
        cert = load_certificate(FILETYPE_PEM, root_cert_pem)
        assert not cert.has_expired()

    def test_digest(self):
        """
        `X509.digest` returns a string giving ":"-separated hex-encoded
        words of the digest of the certificate.
        """
        cert = load_certificate(FILETYPE_PEM, old_root_cert_pem)
        assert (
            # This is MD5 instead of GOOD_DIGEST because the digest algorithm
            # actually matters to the assertion (ie, another arbitrary, good
            # digest will not product the same digest).
            # Digest verified with the command:
            # openssl x509 -in root_cert.pem -noout -fingerprint -md5
            cert.digest("MD5") ==
            b"19:B3:05:26:2B:F8:F2:FF:0B:8F:21:07:A8:28:B8:75")

    def _extcert(self, pkey, extensions):
        cert = X509()
        cert.set_pubkey(pkey)
        cert.get_subject().commonName = "Unit Tests"
        cert.get_issuer().commonName = "Unit Tests"
        when = datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii")
        cert.set_notBefore(when)
        cert.set_notAfter(when)

        cert.add_extensions(extensions)
        cert.sign(pkey, 'sha1')
        return load_certificate(
            FILETYPE_PEM, dump_certificate(FILETYPE_PEM, cert))

    def test_extension_count(self):
        """
        `X509.get_extension_count` returns the number of extensions
        that are present in the certificate.
        """
        pkey = load_privatekey(FILETYPE_PEM, client_key_pem)
        ca = X509Extension(b'basicConstraints', True, b'CA:FALSE')
        key = X509Extension(b'keyUsage', True, b'digitalSignature')
        subjectAltName = X509Extension(
            b'subjectAltName', True, b'DNS:example.com')

        # Try a certificate with no extensions at all.
        c = self._extcert(pkey, [])
        assert c.get_extension_count() == 0

        # And a certificate with one
        c = self._extcert(pkey, [ca])
        assert c.get_extension_count() == 1

        # And a certificate with several
        c = self._extcert(pkey, [ca, key, subjectAltName])
        assert c.get_extension_count() == 3

    def test_get_extension(self):
        """
        `X509.get_extension` takes an integer and returns an
        `X509Extension` corresponding to the extension at that index.
        """
        pkey = load_privatekey(FILETYPE_PEM, client_key_pem)
        ca = X509Extension(b'basicConstraints', True, b'CA:FALSE')
        key = X509Extension(b'keyUsage', True, b'digitalSignature')
        subjectAltName = X509Extension(
            b'subjectAltName', False, b'DNS:example.com')

        cert = self._extcert(pkey, [ca, key, subjectAltName])

        ext = cert.get_extension(0)
        assert isinstance(ext, X509Extension)
        assert ext.get_critical()
        assert ext.get_short_name() == b'basicConstraints'

        ext = cert.get_extension(1)
        assert isinstance(ext, X509Extension)
        assert ext.get_critical()
        assert ext.get_short_name() == b'keyUsage'

        ext = cert.get_extension(2)
        assert isinstance(ext, X509Extension)
        assert not ext.get_critical()
        assert ext.get_short_name() == b'subjectAltName'

        with pytest.raises(IndexError):
            cert.get_extension(-1)
        with pytest.raises(IndexError):
            cert.get_extension(4)
        with pytest.raises(TypeError):
            cert.get_extension("hello")

    def test_nullbyte_subjectAltName(self):
        """
        The fields of a `subjectAltName` extension on an X509 may contain NUL
        bytes and this value is reflected in the string representation of the
        extension object.
        """
        cert = load_certificate(FILETYPE_PEM, nulbyteSubjectAltNamePEM)

        ext = cert.get_extension(3)
        assert ext.get_short_name() == b'subjectAltName'
        assert (
            b"DNS:altnull.python.org\x00example.com, "
            b"email:null@python.org\x00user@example.org, "
            b"URI:http://null.python.org\x00http://example.org, "
            b"IP Address:192.0.2.1, IP Address:2001:DB8:0:0:0:0:0:1\n" ==
            str(ext).encode("ascii"))

    def test_invalid_digest_algorithm(self):
        """
        `X509.digest` raises `ValueError` if called with an unrecognized hash
        algorithm.
        """
        cert = X509()
        with pytest.raises(ValueError):
            cert.digest(BAD_DIGEST)

    def test_get_subject(self):
        """
        `X509.get_subject` returns an `X509Name` instance.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        subj = cert.get_subject()
        assert isinstance(subj, X509Name)
        assert (
            subj.get_components() ==
            [(b'C', b'US'), (b'ST', b'IL'), (b'L', b'Chicago'),
             (b'O', b'Testing'), (b'CN', b'Testing Root CA')])

    def test_set_subject_wrong_args(self):
        """
        `X509.set_subject` raises a `TypeError` if called with an argument not
        of type `X509Name`.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.set_subject(None)

    def test_set_subject(self):
        """
        `X509.set_subject` changes the subject of the certificate to the one
        passed in.
        """
        cert = X509()
        name = cert.get_subject()
        name.C = 'AU'
        name.OU = 'Unit Tests'
        cert.set_subject(name)
        assert (
            cert.get_subject().get_components() ==
            [(b'C', b'AU'), (b'OU', b'Unit Tests')])

    def test_get_issuer(self):
        """
        `X509.get_issuer` returns an `X509Name` instance.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        subj = cert.get_issuer()
        assert isinstance(subj, X509Name)
        comp = subj.get_components()
        assert (
            comp ==
            [(b'C', b'US'), (b'ST', b'IL'), (b'L', b'Chicago'),
             (b'O', b'Testing'), (b'CN', b'Testing Root CA')])

    def test_set_issuer_wrong_args(self):
        """
        `X509.set_issuer` raises a `TypeError` if called with an argument not
        of type `X509Name`.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.set_issuer(None)

    def test_set_issuer(self):
        """
        `X509.set_issuer` changes the issuer of the certificate to the
        one passed in.
        """
        cert = X509()
        name = cert.get_issuer()
        name.C = 'AU'
        name.OU = 'Unit Tests'
        cert.set_issuer(name)
        assert (
            cert.get_issuer().get_components() ==
            [(b'C', b'AU'), (b'OU', b'Unit Tests')])

    def test_get_pubkey_uninitialized(self):
        """
        When called on a certificate with no public key, `X509.get_pubkey`
        raises `OpenSSL.crypto.Error`.
        """
        cert = X509()
        with pytest.raises(Error):
            cert.get_pubkey()

    def test_set_pubkey_wrong_type(self):
        """
        `X509.set_pubkey` raises `TypeError` when given an object of the
        wrong type.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.set_pubkey(object())

    def test_subject_name_hash(self):
        """
        `X509.subject_name_hash` returns the hash of the certificate's
        subject name.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        assert cert.subject_name_hash() in [
            3350047874,  # OpenSSL 0.9.8, MD5
            3278919224,  # OpenSSL 1.0.0, SHA1
        ]

    def test_get_signature_algorithm(self):
        """
        `X509.get_signature_algorithm` returns a string which means
        the algorithm used to sign the certificate.
        """
        cert = load_certificate(FILETYPE_PEM, self.pemData)
        assert b"sha1WithRSAEncryption" == cert.get_signature_algorithm()

    def test_get_undefined_signature_algorithm(self):
        """
        `X509.get_signature_algorithm` raises `ValueError` if the signature
        algorithm is undefined or unknown.
        """
        # This certificate has been modified to indicate a bogus OID in the
        # signature algorithm field so that OpenSSL does not recognize it.
        certPEM = b"""\
-----BEGIN CERTIFICATE-----
MIIC/zCCAmigAwIBAgIBATAGBgJ8BQUAMHsxCzAJBgNVBAYTAlNHMREwDwYDVQQK
EwhNMkNyeXB0bzEUMBIGA1UECxMLTTJDcnlwdG8gQ0ExJDAiBgNVBAMTG00yQ3J5
cHRvIENlcnRpZmljYXRlIE1hc3RlcjEdMBsGCSqGSIb3DQEJARYObmdwc0Bwb3N0
MS5jb20wHhcNMDAwOTEwMDk1MTMwWhcNMDIwOTEwMDk1MTMwWjBTMQswCQYDVQQG
EwJTRzERMA8GA1UEChMITTJDcnlwdG8xEjAQBgNVBAMTCWxvY2FsaG9zdDEdMBsG
CSqGSIb3DQEJARYObmdwc0Bwb3N0MS5jb20wXDANBgkqhkiG9w0BAQEFAANLADBI
AkEArL57d26W9fNXvOhNlZzlPOACmvwOZ5AdNgLzJ1/MfsQQJ7hHVeHmTAjM664V
+fXvwUGJLziCeBo1ysWLRnl8CQIDAQABo4IBBDCCAQAwCQYDVR0TBAIwADAsBglg
hkgBhvhCAQ0EHxYdT3BlblNTTCBHZW5lcmF0ZWQgQ2VydGlmaWNhdGUwHQYDVR0O
BBYEFM+EgpK+eyZiwFU1aOPSbczbPSpVMIGlBgNVHSMEgZ0wgZqAFPuHI2nrnDqT
FeXFvylRT/7tKDgBoX+kfTB7MQswCQYDVQQGEwJTRzERMA8GA1UEChMITTJDcnlw
dG8xFDASBgNVBAsTC00yQ3J5cHRvIENBMSQwIgYDVQQDExtNMkNyeXB0byBDZXJ0
aWZpY2F0ZSBNYXN0ZXIxHTAbBgkqhkiG9w0BCQEWDm5ncHNAcG9zdDEuY29tggEA
MA0GCSqGSIb3DQEBBAUAA4GBADv8KpPo+gfJxN2ERK1Y1l17sz/ZhzoGgm5XCdbx
jEY7xKfpQngV599k1xhl11IMqizDwu0855agrckg2MCTmOI9DZzDD77tAYb+Dk0O
PEVk0Mk/V0aIsDE9bolfCi/i/QWZ3N8s5nTWMNyBBBmoSliWCm4jkkRZRD0ejgTN
tgI5
-----END CERTIFICATE-----
"""
        cert = load_certificate(FILETYPE_PEM, certPEM)
        with pytest.raises(ValueError):
            cert.get_signature_algorithm()

    def test_sign_bad_pubkey_type(self):
        """
        `X509.sign` raises `TypeError` when called with the wrong type.
        """
        cert = X509()
        with pytest.raises(TypeError):
            cert.sign(object(), b"sha256")

    def test_convert_from_cryptography(self):
        crypto_cert = x509.load_pem_x509_certificate(
            intermediate_cert_pem, backend
        )
        cert = X509.from_cryptography(crypto_cert)

        assert isinstance(cert, X509)
        assert cert.get_version() == crypto_cert.version.value

    def test_convert_from_cryptography_unsupported_type(self):
        with pytest.raises(TypeError):
            X509.from_cryptography(object())

    def test_convert_to_cryptography_key(self):
        cert = load_certificate(FILETYPE_PEM, intermediate_cert_pem)
        crypto_cert = cert.to_cryptography()

        assert isinstance(crypto_cert, x509.Certificate)
        assert crypto_cert.version.value == cert.get_version()


class TestX509Store(object):
    """
    Test for `OpenSSL.crypto.X509Store`.
    """

    def test_type(self):
        """
        `X509Store` is a type object.
        """
        assert X509Store is X509StoreType
        assert is_consistent_type(X509Store, 'X509Store')

    def test_add_cert(self):
        """
        `X509Store.add_cert` adds a `X509` instance to the certificate store.
        """
        cert = load_certificate(FILETYPE_PEM, cleartextCertificatePEM)
        store = X509Store()
        store.add_cert(cert)

    @pytest.mark.parametrize('cert', [None, 1.0, 'cert', object()])
    def test_add_cert_wrong_args(self, cert):
        """
        `X509Store.add_cert` raises `TypeError` if passed a non-X509 object
        as its first argument.
        """
        store = X509Store()
        with pytest.raises(TypeError):
            store.add_cert(cert)

    def test_add_cert_rejects_duplicate(self):
        """
        `X509Store.add_cert` raises `OpenSSL.crypto.Error` if an attempt is
        made to add the same certificate to the store more than once.
        """
        cert = load_certificate(FILETYPE_PEM, cleartextCertificatePEM)
        store = X509Store()
        store.add_cert(cert)
        with pytest.raises(Error):
            store.add_cert(cert)


class TestPKCS12(object):
    """
    Test for `OpenSSL.crypto.PKCS12` and `OpenSSL.crypto.load_pkcs12`.
    """
    pemData = cleartextCertificatePEM + cleartextPrivateKeyPEM

    def test_type(self):
        """
        `PKCS12Type` is a type object.
        """
        assert PKCS12 is PKCS12Type
        assert is_consistent_type(PKCS12, 'PKCS12')

    def test_empty_construction(self):
        """
        `PKCS12` returns a new instance of `PKCS12` with no certificate,
        private key, CA certificates, or friendly name.
        """
        p12 = PKCS12()
        assert None is p12.get_certificate()
        assert None is p12.get_privatekey()
        assert None is p12.get_ca_certificates()
        assert None is p12.get_friendlyname()

    def test_type_errors(self):
        """
        The `PKCS12` setter functions (`set_certificate`, `set_privatekey`,
        `set_ca_certificates`, and `set_friendlyname`) raise `TypeError`
        when passed objects of types other than those expected.
        """
        p12 = PKCS12()
        for bad_arg in [3, PKey(), X509]:
            with pytest.raises(TypeError):
                p12.set_certificate(bad_arg)
        for bad_arg in [3, 'legbone', X509()]:
            with pytest.raises(TypeError):
                p12.set_privatekey(bad_arg)
        for bad_arg in [3, X509(), (3, 4), (PKey(),)]:
            with pytest.raises(TypeError):
                p12.set_ca_certificates(bad_arg)
        for bad_arg in [6, ('foo', 'bar')]:
            with pytest.raises(TypeError):
                p12.set_friendlyname(bad_arg)

    def test_key_only(self):
        """
        A `PKCS12` with only a private key can be exported using
        `PKCS12.export` and loaded again using `load_pkcs12`.
        """
        passwd = b"blah"
        p12 = PKCS12()
        pkey = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        p12.set_privatekey(pkey)
        assert None is p12.get_certificate()
        assert pkey == p12.get_privatekey()
        try:
            dumped_p12 = p12.export(passphrase=passwd, iter=2, maciter=3)
        except Error:
            # Some versions of OpenSSL will throw an exception
            # for this nearly useless PKCS12 we tried to generate:
            # [('PKCS12 routines', 'PKCS12_create', 'invalid null argument')]
            return
        p12 = load_pkcs12(dumped_p12, passwd)
        assert None is p12.get_ca_certificates()
        assert None is p12.get_certificate()

        # OpenSSL fails to bring the key back to us.  So sad.  Perhaps in the
        # future this will be improved.
        assert isinstance(p12.get_privatekey(), (PKey, type(None)))

    def test_cert_only(self):
        """
        A `PKCS12` with only a certificate can be exported using
        `PKCS12.export` and loaded again using `load_pkcs12`.
        """
        passwd = b"blah"
        p12 = PKCS12()
        cert = load_certificate(FILETYPE_PEM, cleartextCertificatePEM)
        p12.set_certificate(cert)
        assert cert == p12.get_certificate()
        assert None is p12.get_privatekey()
        try:
            dumped_p12 = p12.export(passphrase=passwd, iter=2, maciter=3)
        except Error:
            # Some versions of OpenSSL will throw an exception
            # for this nearly useless PKCS12 we tried to generate:
            # [('PKCS12 routines', 'PKCS12_create', 'invalid null argument')]
            return
        p12 = load_pkcs12(dumped_p12, passwd)
        assert None is p12.get_privatekey()

        # OpenSSL fails to bring the cert back to us.  Groany mcgroan.
        assert isinstance(p12.get_certificate(), (X509, type(None)))

        # Oh ho.  It puts the certificate into the ca certificates list, in
        # fact.  Totally bogus, I would think.  Nevertheless, let's exploit
        # that to check to see if it reconstructed the certificate we expected
        # it to.  At some point, hopefully this will change so that
        # p12.get_certificate() is actually what returns the loaded
        # certificate.
        assert (
            cleartextCertificatePEM ==
            dump_certificate(FILETYPE_PEM, p12.get_ca_certificates()[0]))

    def gen_pkcs12(self, cert_pem=None, key_pem=None, ca_pem=None,
                   friendly_name=None):
        """
        Generate a PKCS12 object with components from PEM.  Verify that the set
        functions return None.
        """
        p12 = PKCS12()
        if cert_pem:
            ret = p12.set_certificate(load_certificate(FILETYPE_PEM, cert_pem))
            assert ret is None
        if key_pem:
            ret = p12.set_privatekey(load_privatekey(FILETYPE_PEM, key_pem))
            assert ret is None
        if ca_pem:
            ret = p12.set_ca_certificates(
                (load_certificate(FILETYPE_PEM, ca_pem),)
            )
            assert ret is None
        if friendly_name:
            ret = p12.set_friendlyname(friendly_name)
            assert ret is None
        return p12

    def check_recovery(self, p12_str, key=None, cert=None, ca=None, passwd=b"",
                       extra=()):
        """
        Use openssl program to confirm three components are recoverable from a
        PKCS12 string.
        """
        if key:
            recovered_key = _runopenssl(
                p12_str, b"pkcs12", b"-nocerts", b"-nodes", b"-passin",
                b"pass:" + passwd, *extra)
            assert recovered_key[-len(key):] == key
        if cert:
            recovered_cert = _runopenssl(
                p12_str, b"pkcs12", b"-clcerts", b"-nodes", b"-passin",
                b"pass:" + passwd, b"-nokeys", *extra)
            assert recovered_cert[-len(cert):] == cert
        if ca:
            recovered_cert = _runopenssl(
                p12_str, b"pkcs12", b"-cacerts", b"-nodes", b"-passin",
                b"pass:" + passwd, b"-nokeys", *extra)
            assert recovered_cert[-len(ca):] == ca

    def verify_pkcs12_container(self, p12):
        """
        Verify that the PKCS#12 container contains the correct client
        certificate and private key.

        :param p12: The PKCS12 instance to verify.
        :type p12: `PKCS12`
        """
        cert_pem = dump_certificate(FILETYPE_PEM, p12.get_certificate())
        key_pem = dump_privatekey(FILETYPE_PEM, p12.get_privatekey())
        assert (
            (client_cert_pem, client_key_pem, None) ==
            (cert_pem, key_pem, p12.get_ca_certificates()))

    def test_load_pkcs12(self):
        """
        A PKCS12 string generated using the openssl command line can be loaded
        with `load_pkcs12` and its components extracted and examined.
        """
        passwd = b"whatever"
        pem = client_key_pem + client_cert_pem
        p12_str = _runopenssl(
            pem,
            b"pkcs12",
            b"-export",
            b"-clcerts",
            b"-passout",
            b"pass:" + passwd
        )
        p12 = load_pkcs12(p12_str, passphrase=passwd)
        self.verify_pkcs12_container(p12)

    def test_load_pkcs12_text_passphrase(self):
        """
        A PKCS12 string generated using the openssl command line can be loaded
        with `load_pkcs12` and its components extracted and examined.
        Using text as passphrase instead of bytes. DeprecationWarning expected.
        """
        pem = client_key_pem + client_cert_pem
        passwd = b"whatever"
        p12_str = _runopenssl(pem, b"pkcs12", b"-export", b"-clcerts",
                              b"-passout", b"pass:" + passwd)
        with pytest.warns(DeprecationWarning) as w:
            simplefilter("always")
            p12 = load_pkcs12(p12_str, passphrase=b"whatever".decode("ascii"))
            assert (
                "{0} for passphrase is no longer accepted, use bytes".format(
                    WARNING_TYPE_EXPECTED
                ) == str(w[-1].message))

        self.verify_pkcs12_container(p12)

    def test_load_pkcs12_no_passphrase(self):
        """
        A PKCS12 string generated using openssl command line can be loaded with
        `load_pkcs12` without a passphrase and its components extracted
        and examined.
        """
        pem = client_key_pem + client_cert_pem
        p12_str = _runopenssl(
            pem, b"pkcs12", b"-export", b"-clcerts", b"-passout", b"pass:")
        p12 = load_pkcs12(p12_str)
        self.verify_pkcs12_container(p12)

    def _dump_and_load(self, dump_passphrase, load_passphrase):
        """
        A helper method to dump and load a PKCS12 object.
        """
        p12 = self.gen_pkcs12(client_cert_pem, client_key_pem)
        dumped_p12 = p12.export(passphrase=dump_passphrase, iter=2, maciter=3)
        return load_pkcs12(dumped_p12, passphrase=load_passphrase)

    def test_load_pkcs12_null_passphrase_load_empty(self):
        """
        A PKCS12 string can be dumped with a null passphrase, loaded with an
        empty passphrase with `load_pkcs12`, and its components
        extracted and examined.
        """
        self.verify_pkcs12_container(
            self._dump_and_load(dump_passphrase=None, load_passphrase=b''))

    def test_load_pkcs12_null_passphrase_load_null(self):
        """
        A PKCS12 string can be dumped with a null passphrase, loaded with a
        null passphrase with `load_pkcs12`, and its components
        extracted and examined.
        """
        self.verify_pkcs12_container(
            self._dump_and_load(dump_passphrase=None, load_passphrase=None))

    def test_load_pkcs12_empty_passphrase_load_empty(self):
        """
        A PKCS12 string can be dumped with an empty passphrase, loaded with an
        empty passphrase with `load_pkcs12`, and its components
        extracted and examined.
        """
        self.verify_pkcs12_container(
            self._dump_and_load(dump_passphrase=b'', load_passphrase=b''))

    def test_load_pkcs12_empty_passphrase_load_null(self):
        """
        A PKCS12 string can be dumped with an empty passphrase, loaded with a
        null passphrase with `load_pkcs12`, and its components
        extracted and examined.
        """
        self.verify_pkcs12_container(
            self._dump_and_load(dump_passphrase=b'', load_passphrase=None))

    def test_load_pkcs12_garbage(self):
        """
        `load_pkcs12` raises `OpenSSL.crypto.Error` when passed
        a string which is not a PKCS12 dump.
        """
        passwd = 'whatever'
        with pytest.raises(Error) as err:
            load_pkcs12(b'fruit loops', passwd)
        assert err.value.args[0][0][0] == 'asn1 encoding routines'
        assert len(err.value.args[0][0]) == 3

    def test_replace(self):
        """
        `PKCS12.set_certificate` replaces the certificate in a PKCS12
        cluster. `PKCS12.set_privatekey` replaces the private key.
        `PKCS12.set_ca_certificates` replaces the CA certificates.
        """
        p12 = self.gen_pkcs12(client_cert_pem, client_key_pem, root_cert_pem)
        p12.set_certificate(load_certificate(FILETYPE_PEM, server_cert_pem))
        p12.set_privatekey(load_privatekey(FILETYPE_PEM, server_key_pem))
        root_cert = load_certificate(FILETYPE_PEM, root_cert_pem)
        client_cert = load_certificate(FILETYPE_PEM, client_cert_pem)
        p12.set_ca_certificates([root_cert])  # not a tuple
        assert 1 == len(p12.get_ca_certificates())
        assert root_cert == p12.get_ca_certificates()[0]
        p12.set_ca_certificates([client_cert, root_cert])
        assert 2 == len(p12.get_ca_certificates())
        assert client_cert == p12.get_ca_certificates()[0]
        assert root_cert == p12.get_ca_certificates()[1]

    def test_friendly_name(self):
        """
        The *friendlyName* of a PKCS12 can be set and retrieved via
        `PKCS12.get_friendlyname` and `PKCS12_set_friendlyname`, and a
        `PKCS12` with a friendly name set can be dumped with `PKCS12.export`.
        """
        passwd = b'Dogmeat[]{}!@#$%^&*()~`?/.,<>-_+=";:'
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)
        for friendly_name in [b'Serverlicious', None, b'###']:
            p12.set_friendlyname(friendly_name)
            assert p12.get_friendlyname() == friendly_name
            dumped_p12 = p12.export(passphrase=passwd, iter=2, maciter=3)
            reloaded_p12 = load_pkcs12(dumped_p12, passwd)
            assert p12.get_friendlyname() == reloaded_p12.get_friendlyname()
            # We would use the openssl program to confirm the friendly
            # name, but it is not possible.  The pkcs12 command
            # does not store the friendly name in the cert's
            # alias, which we could then extract.
            self.check_recovery(
                dumped_p12, key=server_key_pem, cert=server_cert_pem,
                ca=root_cert_pem, passwd=passwd)

    def test_various_empty_passphrases(self):
        """
        Test that missing, None, and '' passphrases are identical for PKCS12
        export.
        """
        p12 = self.gen_pkcs12(client_cert_pem, client_key_pem, root_cert_pem)
        passwd = b""
        dumped_p12_empty = p12.export(iter=2, maciter=0, passphrase=passwd)
        dumped_p12_none = p12.export(iter=3, maciter=2, passphrase=None)
        dumped_p12_nopw = p12.export(iter=9, maciter=4)
        for dumped_p12 in [dumped_p12_empty, dumped_p12_none, dumped_p12_nopw]:
            self.check_recovery(
                dumped_p12, key=client_key_pem, cert=client_cert_pem,
                ca=root_cert_pem, passwd=passwd)

    def test_removing_ca_cert(self):
        """
        Passing `None` to `PKCS12.set_ca_certificates` removes all CA
        certificates.
        """
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)
        p12.set_ca_certificates(None)
        assert None is p12.get_ca_certificates()

    def test_export_without_mac(self):
        """
        Exporting a PKCS12 with a `maciter` of `-1` excludes the MAC entirely.
        """
        passwd = b"Lake Michigan"
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)
        dumped_p12 = p12.export(maciter=-1, passphrase=passwd, iter=2)
        self.check_recovery(
            dumped_p12, key=server_key_pem, cert=server_cert_pem,
            passwd=passwd, extra=(b"-nomacver",))

    def test_load_without_mac(self):
        """
        Loading a PKCS12 without a MAC does something other than crash.
        """
        passwd = b"Lake Michigan"
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)
        dumped_p12 = p12.export(maciter=-1, passphrase=passwd, iter=2)
        try:
            recovered_p12 = load_pkcs12(dumped_p12, passwd)
            # The person who generated this PCKS12 should be flogged,
            # or better yet we should have a means to determine
            # whether a PCKS12 had a MAC that was verified.
            # Anyway, libopenssl chooses to allow it, so the
            # pyopenssl binding does as well.
            assert isinstance(recovered_p12, PKCS12)
        except Error:
            # Failing here with an exception is preferred as some openssl
            # versions do.
            pass

    def test_zero_len_list_for_ca(self):
        """
        A PKCS12 with an empty CA certificates list can be exported.
        """
        passwd = b'Hobie 18'
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem)
        p12.set_ca_certificates([])
        assert () == p12.get_ca_certificates()
        dumped_p12 = p12.export(passphrase=passwd, iter=3)
        self.check_recovery(
            dumped_p12, key=server_key_pem, cert=server_cert_pem,
            passwd=passwd)

    def test_export_without_args(self):
        """
        All the arguments to `PKCS12.export` are optional.
        """
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)
        dumped_p12 = p12.export()  # no args
        self.check_recovery(
            dumped_p12, key=server_key_pem, cert=server_cert_pem, passwd=b"")

    def test_export_without_bytes(self):
        """
        Test `PKCS12.export` with text not bytes as passphrase
        """
        p12 = self.gen_pkcs12(server_cert_pem, server_key_pem, root_cert_pem)

        with pytest.warns(DeprecationWarning) as w:
            simplefilter("always")
            dumped_p12 = p12.export(passphrase=b"randomtext".decode("ascii"))
            assert (
                "{0} for passphrase is no longer accepted, use bytes".format(
                    WARNING_TYPE_EXPECTED
                ) == str(w[-1].message))
        self.check_recovery(
            dumped_p12,
            key=server_key_pem,
            cert=server_cert_pem,
            passwd=b"randomtext"
        )

    def test_key_cert_mismatch(self):
        """
        `PKCS12.export` raises an exception when a key and certificate
        mismatch.
        """
        p12 = self.gen_pkcs12(server_cert_pem, client_key_pem, root_cert_pem)
        with pytest.raises(Error):
            p12.export()


def _runopenssl(pem, *args):
    """
    Run the command line openssl tool with the given arguments and write
    the given PEM to its stdin.  Not safe for quotes.
    """
    proc = Popen([b"openssl"] + list(args), stdin=PIPE, stdout=PIPE)
    proc.stdin.write(pem)
    proc.stdin.close()
    output = proc.stdout.read()
    proc.stdout.close()
    proc.wait()
    return output


class TestLoadPublicKey(object):
    """
    Tests for :func:`load_publickey`.
    """
    def test_loading_works(self):
        """
        load_publickey loads public keys and sets correct attributes.
        """
        key = load_publickey(FILETYPE_PEM, cleartextPublicKeyPEM)

        assert True is key._only_public
        assert 2048 == key.bits()
        assert TYPE_RSA == key.type()

    def test_invalid_type(self):
        """
        load_publickey doesn't support FILETYPE_TEXT.
        """
        with pytest.raises(ValueError):
            load_publickey(FILETYPE_TEXT, cleartextPublicKeyPEM)

    def test_invalid_key_format(self):
        """
        load_publickey explodes on incorrect keys.
        """
        with pytest.raises(Error):
            load_publickey(FILETYPE_ASN1, cleartextPublicKeyPEM)

    def test_tolerates_unicode_strings(self):
        """
        load_publickey works with text strings, not just bytes.
        """
        serialized = cleartextPublicKeyPEM.decode('ascii')
        key = load_publickey(FILETYPE_PEM, serialized)
        dumped_pem = dump_publickey(FILETYPE_PEM, key)

        assert dumped_pem == cleartextPublicKeyPEM


class TestFunction(object):
    """
    Tests for free-functions in the `OpenSSL.crypto` module.
    """

    def test_load_privatekey_invalid_format(self):
        """
        `load_privatekey` raises `ValueError` if passed an unknown filetype.
        """
        with pytest.raises(ValueError):
            load_privatekey(100, root_key_pem)

    def test_load_privatekey_invalid_passphrase_type(self):
        """
        `load_privatekey` raises `TypeError` if passed a passphrase that is
        neither a `str` nor a callable.
        """
        with pytest.raises(TypeError):
            load_privatekey(
                FILETYPE_PEM, encryptedPrivateKeyPEMPassphrase, object())

    def test_load_privatekey_wrongPassphrase(self):
        """
        `load_privatekey` raises `OpenSSL.crypto.Error` when it is passed an
        encrypted PEM and an incorrect passphrase.
        """
        with pytest.raises(Error) as err:
            load_privatekey(FILETYPE_PEM, encryptedPrivateKeyPEM, b"quack")
        assert err.value.args[0] != []

    def test_load_privatekey_passphraseWrongType(self):
        """
        `load_privatekey` raises `ValueError` when it is passeda passphrase
        with a private key encoded in a format, that doesn't support
        encryption.
        """
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        blob = dump_privatekey(FILETYPE_ASN1, key)
        with pytest.raises(ValueError):
            load_privatekey(FILETYPE_ASN1, blob, "secret")

    def test_load_privatekey_passphrase(self):
        """
        `load_privatekey` can create a `PKey` object from an encrypted PEM
        string if given the passphrase.
        """
        key = load_privatekey(
            FILETYPE_PEM, encryptedPrivateKeyPEM,
            encryptedPrivateKeyPEMPassphrase)
        assert isinstance(key, PKeyType)

    def test_load_privatekey_passphrase_exception(self):
        """
        If the passphrase callback raises an exception, that exception is
        raised by `load_privatekey`.
        """
        def cb(ignored):
            raise ArithmeticError

        with pytest.raises(ArithmeticError):
            load_privatekey(FILETYPE_PEM, encryptedPrivateKeyPEM, cb)

    def test_load_privatekey_wrongPassphraseCallback(self):
        """
        `load_privatekey` raises `OpenSSL.crypto.Error` when it
        is passed an encrypted PEM and a passphrase callback which returns an
        incorrect passphrase.
        """
        called = []

        def cb(*a):
            called.append(None)
            return b"quack"
        with pytest.raises(Error) as err:
            load_privatekey(FILETYPE_PEM, encryptedPrivateKeyPEM, cb)
        assert called
        assert err.value.args[0] != []

    def test_load_privatekey_passphraseCallback(self):
        """
        `load_privatekey` can create a `PKey` object from an encrypted PEM
        string if given a passphrase callback which returns the correct
        password.
        """
        called = []

        def cb(writing):
            called.append(writing)
            return encryptedPrivateKeyPEMPassphrase
        key = load_privatekey(FILETYPE_PEM, encryptedPrivateKeyPEM, cb)
        assert isinstance(key, PKeyType)
        assert called == [False]

    def test_load_privatekey_passphrase_wrong_return_type(self):
        """
        `load_privatekey` raises `ValueError` if the passphrase callback
        returns something other than a byte string.
        """
        with pytest.raises(ValueError):
            load_privatekey(
                FILETYPE_PEM, encryptedPrivateKeyPEM, lambda *args: 3)

    def test_dump_privatekey_wrong_args(self):
        """
        `dump_privatekey` raises `TypeError` if called with a `cipher`
        argument but no `passphrase` argument.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        with pytest.raises(TypeError):
            dump_privatekey(FILETYPE_PEM, key, cipher=GOOD_CIPHER)

    def test_dump_privatekey_not_rsa_key(self):
        """
        `dump_privatekey` raises `TypeError` if called with a key that is
        not RSA.
        """
        key = PKey()
        key.generate_key(TYPE_DSA, 512)
        with pytest.raises(TypeError):
            dump_privatekey(FILETYPE_TEXT, key)

    def test_dump_privatekey_invalid_pkey(self):
        with pytest.raises(TypeError):
            dump_privatekey(FILETYPE_TEXT, object())

    def test_dump_privatekey_unknown_cipher(self):
        """
        `dump_privatekey` raises `ValueError` if called with an unrecognized
        cipher name.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        with pytest.raises(ValueError):
            dump_privatekey(FILETYPE_PEM, key, BAD_CIPHER, "passphrase")

    def test_dump_privatekey_invalid_passphrase_type(self):
        """
        `dump_privatekey` raises `TypeError` if called with a passphrase which
        is neither a `str` nor a callable.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        with pytest.raises(TypeError):
            dump_privatekey(FILETYPE_PEM, key, GOOD_CIPHER, object())

    def test_dump_privatekey_invalid_filetype(self):
        """
        `dump_privatekey` raises `ValueError` if called with an unrecognized
        filetype.
        """
        key = PKey()
        key.generate_key(TYPE_RSA, 512)
        with pytest.raises(ValueError):
            dump_privatekey(100, key)

    def test_load_privatekey_passphrase_callback_length(self):
        """
        `crypto.load_privatekey` should raise an error when the passphrase
        provided by the callback is too long, not silently truncate it.
        """
        def cb(ignored):
            return "a" * 1025

        with pytest.raises(ValueError):
            load_privatekey(FILETYPE_PEM, encryptedPrivateKeyPEM, cb)

    def test_dump_privatekey_passphrase(self):
        """
        `dump_privatekey` writes an encrypted PEM when given a passphrase.
        """
        passphrase = b"foo"
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        pem = dump_privatekey(FILETYPE_PEM, key, GOOD_CIPHER, passphrase)
        assert isinstance(pem, binary_type)
        loadedKey = load_privatekey(FILETYPE_PEM, pem, passphrase)
        assert isinstance(loadedKey, PKeyType)
        assert loadedKey.type() == key.type()
        assert loadedKey.bits() == key.bits()

    def test_dump_privatekey_passphrase_wrong_type(self):
        """
        `dump_privatekey` raises `ValueError` when it is passed a passphrase
        with a private key encoded in a format, that doesn't support
        encryption.
        """
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        with pytest.raises(ValueError):
            dump_privatekey(FILETYPE_ASN1, key, GOOD_CIPHER, "secret")

    def test_dump_certificate(self):
        """
        `dump_certificate` writes PEM, DER, and text.
        """
        pemData = cleartextCertificatePEM + cleartextPrivateKeyPEM
        cert = load_certificate(FILETYPE_PEM, pemData)
        dumped_pem = dump_certificate(FILETYPE_PEM, cert)
        assert dumped_pem == cleartextCertificatePEM
        dumped_der = dump_certificate(FILETYPE_ASN1, cert)
        good_der = _runopenssl(dumped_pem, b"x509", b"-outform", b"DER")
        assert dumped_der == good_der
        cert2 = load_certificate(FILETYPE_ASN1, dumped_der)
        dumped_pem2 = dump_certificate(FILETYPE_PEM, cert2)
        assert dumped_pem2 == cleartextCertificatePEM
        dumped_text = dump_certificate(FILETYPE_TEXT, cert)
        good_text = _runopenssl(
            dumped_pem, b"x509", b"-noout", b"-text", b"-nameopt", b"")
        assert dumped_text == good_text

    def test_dump_certificate_bad_type(self):
        """
        `dump_certificate` raises a `ValueError` if it's called with
        a bad type.
        """
        cert = load_certificate(FILETYPE_PEM, cleartextCertificatePEM)
        with pytest.raises(ValueError):
            dump_certificate(object(), cert)

    def test_dump_privatekey_pem(self):
        """
        `dump_privatekey` writes a PEM
        """
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        assert key.check()
        dumped_pem = dump_privatekey(FILETYPE_PEM, key)
        assert dumped_pem == cleartextPrivateKeyPEM

    def test_dump_privatekey_asn1(self):
        """
        `dump_privatekey` writes a DER
        """
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        dumped_pem = dump_privatekey(FILETYPE_PEM, key)

        dumped_der = dump_privatekey(FILETYPE_ASN1, key)
        # XXX This OpenSSL call writes "writing RSA key" to standard out.  Sad.
        good_der = _runopenssl(dumped_pem, b"rsa", b"-outform", b"DER")
        assert dumped_der == good_der
        key2 = load_privatekey(FILETYPE_ASN1, dumped_der)
        dumped_pem2 = dump_privatekey(FILETYPE_PEM, key2)
        assert dumped_pem2 == cleartextPrivateKeyPEM

    def test_dump_privatekey_text(self):
        """
        `dump_privatekey` writes a text
        """
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        dumped_pem = dump_privatekey(FILETYPE_PEM, key)

        dumped_text = dump_privatekey(FILETYPE_TEXT, key)
        good_text = _runopenssl(dumped_pem, b"rsa", b"-noout", b"-text")
        assert dumped_text == good_text

    def test_dump_publickey_pem(self):
        """
        dump_publickey writes a PEM.
        """
        key = load_publickey(FILETYPE_PEM, cleartextPublicKeyPEM)
        dumped_pem = dump_publickey(FILETYPE_PEM, key)
        assert dumped_pem == cleartextPublicKeyPEM

    def test_dump_publickey_asn1(self):
        """
        dump_publickey writes a DER.
        """
        key = load_publickey(FILETYPE_PEM, cleartextPublicKeyPEM)
        dumped_der = dump_publickey(FILETYPE_ASN1, key)
        key2 = load_publickey(FILETYPE_ASN1, dumped_der)
        dumped_pem2 = dump_publickey(FILETYPE_PEM, key2)
        assert dumped_pem2 == cleartextPublicKeyPEM

    def test_dump_publickey_invalid_type(self):
        """
        dump_publickey doesn't support FILETYPE_TEXT.
        """
        key = load_publickey(FILETYPE_PEM, cleartextPublicKeyPEM)

        with pytest.raises(ValueError):
            dump_publickey(FILETYPE_TEXT, key)

    def test_dump_certificate_request(self):
        """
        `dump_certificate_request` writes a PEM, DER, and text.
        """
        req = load_certificate_request(
            FILETYPE_PEM, cleartextCertificateRequestPEM)
        dumped_pem = dump_certificate_request(FILETYPE_PEM, req)
        assert dumped_pem == cleartextCertificateRequestPEM
        dumped_der = dump_certificate_request(FILETYPE_ASN1, req)
        good_der = _runopenssl(dumped_pem, b"req", b"-outform", b"DER")
        assert dumped_der == good_der
        req2 = load_certificate_request(FILETYPE_ASN1, dumped_der)
        dumped_pem2 = dump_certificate_request(FILETYPE_PEM, req2)
        assert dumped_pem2 == cleartextCertificateRequestPEM
        dumped_text = dump_certificate_request(FILETYPE_TEXT, req)
        good_text = _runopenssl(
            dumped_pem, b"req", b"-noout", b"-text", b"-nameopt", b"")
        assert dumped_text == good_text
        with pytest.raises(ValueError):
            dump_certificate_request(100, req)

    def test_dump_privatekey_passphrase_callback(self):
        """
        `dump_privatekey` writes an encrypted PEM when given a callback
        which returns the correct passphrase.
        """
        passphrase = b"foo"
        called = []

        def cb(writing):
            called.append(writing)
            return passphrase
        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        pem = dump_privatekey(FILETYPE_PEM, key, GOOD_CIPHER, cb)
        assert isinstance(pem, binary_type)
        assert called == [True]
        loadedKey = load_privatekey(FILETYPE_PEM, pem, passphrase)
        assert isinstance(loadedKey, PKeyType)
        assert loadedKey.type() == key.type()
        assert loadedKey.bits() == key.bits()

    def test_dump_privatekey_passphrase_exception(self):
        """
        `dump_privatekey` should not overwrite the exception raised
        by the passphrase callback.
        """
        def cb(ignored):
            raise ArithmeticError

        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        with pytest.raises(ArithmeticError):
            dump_privatekey(FILETYPE_PEM, key, GOOD_CIPHER, cb)

    def test_dump_privatekey_passphraseCallbackLength(self):
        """
        `crypto.dump_privatekey` should raise an error when the passphrase
        provided by the callback is too long, not silently truncate it.
        """
        def cb(ignored):
            return "a" * 1025

        key = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)
        with pytest.raises(ValueError):
            dump_privatekey(FILETYPE_PEM, key, GOOD_CIPHER, cb)

    def test_load_pkcs7_data_pem(self):
        """
        `load_pkcs7_data` accepts a PKCS#7 string and returns an instance of
        `PKCS`.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert isinstance(pkcs7, PKCS7)

    def test_load_pkcs7_data_asn1(self):
        """
        `load_pkcs7_data` accepts a bytes containing ASN1 data representing
        PKCS#7 and returns an instance of `PKCS7`.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_ASN1, pkcs7DataASN1)
        assert isinstance(pkcs7, PKCS7)

    def test_load_pkcs7_data_invalid(self):
        """
        If the data passed to `load_pkcs7_data` is invalid, `Error` is raised.
        """
        with pytest.raises(Error):
            load_pkcs7_data(FILETYPE_PEM, b"foo")

    def test_load_pkcs7_type_invalid(self):
        """
        If the type passed to `load_pkcs7_data`, `ValueError` is raised.
        """
        with pytest.raises(ValueError):
            load_pkcs7_data(object(), b"foo")


class TestLoadCertificate(object):
    """
    Tests for `load_certificate_request`.
    """

    def test_bad_file_type(self):
        """
        If the file type passed to `load_certificate_request` is neither
        `FILETYPE_PEM` nor `FILETYPE_ASN1` then `ValueError` is raised.
        """
        with pytest.raises(ValueError):
            load_certificate_request(object(), b"")
        with pytest.raises(ValueError):
            load_certificate(object(), b"")

    def test_bad_certificate(self):
        """
        If the bytes passed to `load_certificate` are not a valid certificate,
        an exception is raised.
        """
        with pytest.raises(Error):
            load_certificate(FILETYPE_ASN1, b"lol")


class TestPKCS7(object):
    """
    Tests for `PKCS7`.
    """

    def test_type(self):
        """
        `PKCS7` is a type object.
        """
        assert isinstance(PKCS7, type)
        assert PKCS7Type.__name__ == 'PKCS7'
        assert PKCS7 is PKCS7Type

    def test_type_is_signed(self):
        """
        `PKCS7.type_is_signed` returns `True` if the PKCS7 object is of
        the type *signed*.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert pkcs7.type_is_signed()

    def test_type_is_enveloped(self):
        """
        `PKCS7.type_is_enveloped` returns `False` if the PKCS7 object is not
        of the type *enveloped*.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert not pkcs7.type_is_enveloped()

    def test_type_is_signed_and_enveloped(self):
        """
        `PKCS7.type_is_signedAndEnveloped` returns `False`
        if the PKCS7 object is not of the type *signed and enveloped*.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert not pkcs7.type_is_signedAndEnveloped()

    def test_type_is_data(self):
        """
        `PKCS7.type_is_data` returns `False` if the PKCS7 object is not of
        the type data.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert not pkcs7.type_is_data()

    def test_get_type_name(self):
        """
        `PKCS7.get_type_name` returns a `str` giving the
        type name.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        assert pkcs7.get_type_name() == b'pkcs7-signedData'

    def test_attribute(self):
        """
        If an attribute other than one of the methods tested here is accessed
        on an instance of `PKCS7`, `AttributeError` is raised.
        """
        pkcs7 = load_pkcs7_data(FILETYPE_PEM, pkcs7Data)
        with pytest.raises(AttributeError):
            pkcs7.foo


class TestNetscapeSPKI(_PKeyInteractionTestsMixin):
    """
    Tests for `OpenSSL.crypto.NetscapeSPKI`.
    """

    def signable(self):
        """
        Return a new `NetscapeSPKI` for use with signing tests.
        """
        return NetscapeSPKI()

    def test_type(self):
        """
        `NetscapeSPKI` and `NetscapeSPKIType` refer to the same type object
        and can be used to create instances of that type.
        """
        assert NetscapeSPKI is NetscapeSPKIType
        assert is_consistent_type(NetscapeSPKI, 'NetscapeSPKI')

    def test_construction(self):
        """
        `NetscapeSPKI` returns an instance of `NetscapeSPKIType`.
        """
        nspki = NetscapeSPKI()
        assert isinstance(nspki, NetscapeSPKIType)

    def test_invalid_attribute(self):
        """
        Accessing a non-existent attribute of a `NetscapeSPKI` instance
        causes an `AttributeError` to be raised.
        """
        nspki = NetscapeSPKI()
        with pytest.raises(AttributeError):
            nspki.foo

    def test_b64_encode(self):
        """
        `NetscapeSPKI.b64_encode` encodes the certificate to a base64 blob.
        """
        nspki = NetscapeSPKI()
        blob = nspki.b64_encode()
        assert isinstance(blob, binary_type)


class TestRevoked(object):
    """
    Tests for `OpenSSL.crypto.Revoked`.
    """
    def test_ignores_unsupported_revoked_cert_extension_get_reason(self):
        """
        The get_reason method on the Revoked class checks to see if the
        extension is NID_crl_reason and should skip it otherwise. This test
        loads a CRL with extensions it should ignore.
        """
        crl = load_crl(FILETYPE_PEM, crlDataUnsupportedExtension)
        revoked = crl.get_revoked()
        reason = revoked[1].get_reason()
        assert reason == b'Unspecified'

    def test_ignores_unsupported_revoked_cert_extension_set_new_reason(self):
        crl = load_crl(FILETYPE_PEM, crlDataUnsupportedExtension)
        revoked = crl.get_revoked()
        revoked[1].set_reason(None)
        reason = revoked[1].get_reason()
        assert reason is None

    def test_construction(self):
        """
        Confirm we can create `OpenSSL.crypto.Revoked`.  Check that it is
        empty.
        """
        revoked = Revoked()
        assert isinstance(revoked, Revoked)
        assert type(revoked) == Revoked
        assert revoked.get_serial() == b'00'
        assert revoked.get_rev_date() is None
        assert revoked.get_reason() is None

    def test_serial(self):
        """
        Confirm we can set and get serial numbers from
        `OpenSSL.crypto.Revoked`.  Confirm errors are handled with grace.
        """
        revoked = Revoked()
        ret = revoked.set_serial(b'10b')
        assert ret is None
        ser = revoked.get_serial()
        assert ser == b'010B'

        revoked.set_serial(b'31ppp')  # a type error would be nice
        ser = revoked.get_serial()
        assert ser == b'31'

        with pytest.raises(ValueError):
            revoked.set_serial(b'pqrst')
        with pytest.raises(TypeError):
            revoked.set_serial(100)

    def test_date(self):
        """
        Confirm we can set and get revocation dates from
        `OpenSSL.crypto.Revoked`.  Confirm errors are handled with grace.
        """
        revoked = Revoked()
        date = revoked.get_rev_date()
        assert date is None

        now = datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii")
        ret = revoked.set_rev_date(now)
        assert ret is None
        date = revoked.get_rev_date()
        assert date == now

    def test_reason(self):
        """
        Confirm we can set and get revocation reasons from
        `OpenSSL.crypto.Revoked`.  The "get" need to work as "set".
        Likewise, each reason of all_reasons() must work.
        """
        revoked = Revoked()
        for r in revoked.all_reasons():
            for x in range(2):
                ret = revoked.set_reason(r)
                assert ret is None
                reason = revoked.get_reason()
                assert (
                    reason.lower().replace(b' ', b'') ==
                    r.lower().replace(b' ', b''))
                r = reason  # again with the resp of get

        revoked.set_reason(None)
        assert revoked.get_reason() is None

    @pytest.mark.parametrize('reason', [object(), 1.0, u'foo'])
    def test_set_reason_wrong_args(self, reason):
        """
        `Revoked.set_reason` raises `TypeError` if called with an argument
        which is neither `None` nor a byte string.
        """
        revoked = Revoked()
        with pytest.raises(TypeError):
            revoked.set_reason(reason)

    def test_set_reason_invalid_reason(self):
        """
        Calling `OpenSSL.crypto.Revoked.set_reason` with an argument which
        isn't a valid reason results in `ValueError` being raised.
        """
        revoked = Revoked()
        with pytest.raises(ValueError):
            revoked.set_reason(b'blue')


class TestCRL(object):
    """
    Tests for `OpenSSL.crypto.CRL`.
    """
    cert = load_certificate(FILETYPE_PEM, cleartextCertificatePEM)
    pkey = load_privatekey(FILETYPE_PEM, cleartextPrivateKeyPEM)

    root_cert = load_certificate(FILETYPE_PEM, root_cert_pem)
    root_key = load_privatekey(FILETYPE_PEM, root_key_pem)
    intermediate_cert = load_certificate(FILETYPE_PEM, intermediate_cert_pem)
    intermediate_key = load_privatekey(FILETYPE_PEM, intermediate_key_pem)
    intermediate_server_cert = load_certificate(
        FILETYPE_PEM, intermediate_server_cert_pem)
    intermediate_server_key = load_privatekey(
        FILETYPE_PEM, intermediate_server_key_pem)

    def test_construction(self):
        """
        Confirm we can create `OpenSSL.crypto.CRL`.  Check
        that it is empty
        """
        crl = CRL()
        assert isinstance(crl, CRL)
        assert crl.get_revoked() is None

    def _get_crl(self):
        """
        Get a new ``CRL`` with a revocation.
        """
        crl = CRL()
        revoked = Revoked()
        now = datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii")
        revoked.set_rev_date(now)
        revoked.set_serial(b'3ab')
        revoked.set_reason(b'sUpErSeDEd')
        crl.add_revoked(revoked)
        return crl

    def test_export_pem(self):
        """
        If not passed a format, ``CRL.export`` returns a "PEM" format string
        representing a serial number, a revoked reason, and certificate issuer
        information.
        """
        crl = self._get_crl()
        # PEM format
        dumped_crl = crl.export(
            self.cert, self.pkey, days=20, digest=b"sha256"
        )
        text = _runopenssl(dumped_crl, b"crl", b"-noout", b"-text")

        # These magic values are based on the way the CRL above was constructed
        # and with what certificate it was exported.
        text.index(b'Serial Number: 03AB')
        text.index(b'Superseded')
        text.index(
            b'Issuer: /C=US/ST=IL/L=Chicago/O=Testing/CN=Testing Root CA'
        )

    def test_export_der(self):
        """
        If passed ``FILETYPE_ASN1`` for the format, ``CRL.export`` returns a
        "DER" format string representing a serial number, a revoked reason, and
        certificate issuer information.
        """
        crl = self._get_crl()

        # DER format
        dumped_crl = crl.export(
            self.cert, self.pkey, FILETYPE_ASN1, digest=b"md5"
        )
        text = _runopenssl(
            dumped_crl, b"crl", b"-noout", b"-text", b"-inform", b"DER"
        )
        text.index(b'Serial Number: 03AB')
        text.index(b'Superseded')
        text.index(
            b'Issuer: /C=US/ST=IL/L=Chicago/O=Testing/CN=Testing Root CA'
        )

    # Flaky because we compare the output of running commands which sometimes
    # varies by 1 second
    @flaky.flaky
    def test_export_text(self):
        """
        If passed ``FILETYPE_TEXT`` for the format, ``CRL.export`` returns a
        text format string like the one produced by the openssl command line
        tool.
        """
        crl = self._get_crl()

        dumped_crl = crl.export(
            self.cert, self.pkey, FILETYPE_ASN1, digest=b"md5"
        )
        text = _runopenssl(
            dumped_crl, b"crl", b"-noout", b"-text", b"-inform", b"DER"
        )

        # text format
        dumped_text = crl.export(
            self.cert, self.pkey, type=FILETYPE_TEXT, digest=b"md5"
        )
        assert text == dumped_text

    def test_export_custom_digest(self):
        """
        If passed the name of a digest function, ``CRL.export`` uses a
        signature algorithm based on that digest function.
        """
        crl = self._get_crl()
        dumped_crl = crl.export(self.cert, self.pkey, digest=b"sha1")
        text = _runopenssl(dumped_crl, b"crl", b"-noout", b"-text")
        text.index(b'Signature Algorithm: sha1')

    def test_export_md5_digest(self):
        """
        If passed md5 as the digest function, ``CRL.export`` uses md5 and does
        not emit a deprecation warning.
        """
        crl = self._get_crl()
        with pytest.warns(None) as catcher:
            simplefilter("always")
        assert 0 == len(catcher)
        dumped_crl = crl.export(self.cert, self.pkey, digest=b"md5")
        text = _runopenssl(dumped_crl, b"crl", b"-noout", b"-text")
        text.index(b'Signature Algorithm: md5')

    def test_export_default_digest(self):
        """
        If not passed the name of a digest function, ``CRL.export`` raises a
        ``TypeError``.
        """
        crl = self._get_crl()
        with pytest.raises(TypeError):
            crl.export(self.cert, self.pkey)

    def test_export_invalid(self):
        """
        If `CRL.export` is used with an uninitialized `X509` instance,
        `OpenSSL.crypto.Error` is raised.
        """
        crl = CRL()
        with pytest.raises(Error):
            crl.export(X509(), PKey(), digest=b"sha256")

    def test_add_revoked_keyword(self):
        """
        `OpenSSL.CRL.add_revoked` accepts its single argument as the
        ``revoked`` keyword argument.
        """
        crl = CRL()
        revoked = Revoked()
        revoked.set_serial(b"01")
        revoked.set_rev_date(b"20160310020145Z")
        crl.add_revoked(revoked=revoked)
        assert isinstance(crl.get_revoked()[0], Revoked)

    def test_export_wrong_args(self):
        """
        Calling `OpenSSL.CRL.export` with arguments other than the certificate,
        private key, integer file type, and integer number of days it
        expects, results in a `TypeError` being raised.
        """
        crl = CRL()
        with pytest.raises(TypeError):
            crl.export(None, self.pkey, FILETYPE_PEM, 10)
        with pytest.raises(TypeError):
            crl.export(self.cert, None, FILETYPE_PEM, 10)
        with pytest.raises(TypeError):
            crl.export(self.cert, self.pkey, None, 10)
        with pytest.raises(TypeError):
            crl.export(self.cert, FILETYPE_PEM, None)

    def test_export_unknown_filetype(self):
        """
        Calling `OpenSSL.CRL.export` with a file type other than
        `FILETYPE_PEM`, `FILETYPE_ASN1`, or
        `FILETYPE_TEXT` results in a `ValueError` being raised.
        """
        crl = CRL()
        with pytest.raises(ValueError):
            crl.export(self.cert, self.pkey, 100, 10, digest=b"sha256")

    def test_export_unknown_digest(self):
        """
        Calling `OpenSSL.CRL.export` with an unsupported digest results
        in a `ValueError` being raised.
        """
        crl = CRL()
        with pytest.raises(ValueError):
            crl.export(
                self.cert, self.pkey, FILETYPE_PEM, 10, b"strange-digest")

    def test_get_revoked(self):
        """
        Use python to create a simple CRL with two revocations. Get back the
        `Revoked` using `OpenSSL.CRL.get_revoked` and verify them.
        """
        crl = CRL()

        revoked = Revoked()
        now = datetime.now().strftime("%Y%m%d%H%M%SZ").encode("ascii")
        revoked.set_rev_date(now)
        revoked.set_serial(b'3ab')
        crl.add_revoked(revoked)
        revoked.set_serial(b'100')
        revoked.set_reason(b'sUpErSeDEd')
        crl.add_revoked(revoked)

        revs = crl.get_revoked()
        assert len(revs) == 2
        assert type(revs[0]) == Revoked
        assert type(revs[1]) == Revoked
        assert revs[0].get_serial() == b'03AB'
        assert revs[1].get_serial() == b'0100'
        assert revs[0].get_rev_date() == now
        assert revs[1].get_rev_date() == now

    def test_load_crl(self):
        """
        Load a known CRL and inspect its revocations.  Both EM and DER formats
        are loaded.
        """
        crl = load_crl(FILETYPE_PEM, crlData)
        revs = crl.get_revoked()
        assert len(revs) == 2
        assert revs[0].get_serial() == b'03AB'
        assert revs[0].get_reason() is None
        assert revs[1].get_serial() == b'0100'
        assert revs[1].get_reason() == b'Superseded'

        der = _runopenssl(crlData, b"crl", b"-outform", b"DER")
        crl = load_crl(FILETYPE_ASN1, der)
        revs = crl.get_revoked()
        assert len(revs) == 2
        assert revs[0].get_serial() == b'03AB'
        assert revs[0].get_reason() is None
        assert revs[1].get_serial() == b'0100'
        assert revs[1].get_reason() == b'Superseded'

    def test_load_crl_bad_filetype(self):
        """
        Calling `OpenSSL.crypto.load_crl` with an unknown file type raises a
        `ValueError`.
        """
        with pytest.raises(ValueError):
            load_crl(100, crlData)

    def test_load_crl_bad_data(self):
        """
        Calling `OpenSSL.crypto.load_crl` with file data which can't be loaded
        raises a `OpenSSL.crypto.Error`.
        """
        with pytest.raises(Error):
            load_crl(FILETYPE_PEM, b"hello, world")

    def test_get_issuer(self):
        """
        Load a known CRL and assert its issuer's common name is what we expect
        from the encoded crlData string.
        """
        crl = load_crl(FILETYPE_PEM, crlData)
        assert isinstance(crl.get_issuer(), X509Name)
        assert crl.get_issuer().CN == 'Testing Root CA'

    def test_dump_crl(self):
        """
        The dumped CRL matches the original input.
        """
        crl = load_crl(FILETYPE_PEM, crlData)
        buf = dump_crl(FILETYPE_PEM, crl)
        assert buf == crlData

    def _make_test_crl(self, issuer_cert, issuer_key, certs=()):
        """
        Create a CRL.

        :param list[X509] certs: A list of certificates to revoke.
        :rtype: CRL
        """
        crl = CRL()
        for cert in certs:
            revoked = Revoked()
            # FIXME: This string splicing is an unfortunate implementation
            # detail that has been reported in
            # https://github.com/pyca/pyopenssl/issues/258
            serial = hex(cert.get_serial_number())[2:].encode('utf-8')
            revoked.set_serial(serial)
            revoked.set_reason(b'unspecified')
            revoked.set_rev_date(b'20140601000000Z')
            crl.add_revoked(revoked)
        crl.set_version(1)
        crl.set_lastUpdate(b'20140601000000Z')
        crl.set_nextUpdate(b'20180601000000Z')
        crl.sign(issuer_cert, issuer_key, digest=b'sha512')
        return crl

    def test_verify_with_revoked(self):
        """
        `verify_certificate` raises error when an intermediate certificate is
        revoked.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store.add_cert(self.intermediate_cert)
        root_crl = self._make_test_crl(
            self.root_cert, self.root_key, certs=[self.intermediate_cert])
        intermediate_crl = self._make_test_crl(
            self.intermediate_cert, self.intermediate_key, certs=[])
        store.add_crl(root_crl)
        store.add_crl(intermediate_crl)
        store.set_flags(
            X509StoreFlags.CRL_CHECK | X509StoreFlags.CRL_CHECK_ALL)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)
        with pytest.raises(X509StoreContextError) as err:
            store_ctx.verify_certificate()
        assert err.value.args[0][2] == 'certificate revoked'

    def test_verify_with_missing_crl(self):
        """
        `verify_certificate` raises error when an intermediate certificate's
        CRL is missing.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store.add_cert(self.intermediate_cert)
        root_crl = self._make_test_crl(
            self.root_cert, self.root_key, certs=[self.intermediate_cert])
        store.add_crl(root_crl)
        store.set_flags(
            X509StoreFlags.CRL_CHECK | X509StoreFlags.CRL_CHECK_ALL)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)
        with pytest.raises(X509StoreContextError) as err:
            store_ctx.verify_certificate()
        assert err.value.args[0][2] == 'unable to get certificate CRL'
        assert err.value.certificate.get_subject().CN == 'intermediate-service'

    def test_convert_from_cryptography(self):
        crypto_crl = x509.load_pem_x509_crl(crlData, backend)
        crl = CRL.from_cryptography(crypto_crl)
        assert isinstance(crl, CRL)

    def test_convert_from_cryptography_unsupported_type(self):
        with pytest.raises(TypeError):
            CRL.from_cryptography(object())

    def test_convert_to_cryptography_key(self):
        crl = load_crl(FILETYPE_PEM, crlData)
        crypto_crl = crl.to_cryptography()
        assert isinstance(crypto_crl, x509.CertificateRevocationList)


class TestX509StoreContext(object):
    """
    Tests for `OpenSSL.crypto.X509StoreContext`.
    """
    root_cert = load_certificate(FILETYPE_PEM, root_cert_pem)
    intermediate_cert = load_certificate(FILETYPE_PEM, intermediate_cert_pem)
    intermediate_server_cert = load_certificate(
        FILETYPE_PEM, intermediate_server_cert_pem)

    def test_valid(self):
        """
        `verify_certificate` returns ``None`` when called with a certificate
        and valid chain.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store.add_cert(self.intermediate_cert)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)
        assert store_ctx.verify_certificate() is None

    def test_reuse(self):
        """
        `verify_certificate` can be called multiple times with the same
        ``X509StoreContext`` instance to produce the same result.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store.add_cert(self.intermediate_cert)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)
        assert store_ctx.verify_certificate() is None
        assert store_ctx.verify_certificate() is None

    def test_trusted_self_signed(self):
        """
        `verify_certificate` returns ``None`` when called with a self-signed
        certificate and itself in the chain.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store_ctx = X509StoreContext(store, self.root_cert)
        assert store_ctx.verify_certificate() is None

    def test_untrusted_self_signed(self):
        """
        `verify_certificate` raises error when a self-signed certificate is
        verified without itself in the chain.
        """
        store = X509Store()
        store_ctx = X509StoreContext(store, self.root_cert)
        with pytest.raises(X509StoreContextError) as exc:
            store_ctx.verify_certificate()

        assert exc.value.args[0][2] == 'self signed certificate'
        assert exc.value.certificate.get_subject().CN == 'Testing Root CA'

    def test_invalid_chain_no_root(self):
        """
        `verify_certificate` raises error when a root certificate is missing
        from the chain.
        """
        store = X509Store()
        store.add_cert(self.intermediate_cert)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)

        with pytest.raises(X509StoreContextError) as exc:
            store_ctx.verify_certificate()

        assert exc.value.args[0][2] == 'unable to get issuer certificate'
        assert exc.value.certificate.get_subject().CN == 'intermediate'

    def test_invalid_chain_no_intermediate(self):
        """
        `verify_certificate` raises error when an intermediate certificate is
        missing from the chain.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store_ctx = X509StoreContext(store, self.intermediate_server_cert)

        with pytest.raises(X509StoreContextError) as exc:
            store_ctx.verify_certificate()

        assert exc.value.args[0][2] == 'unable to get local issuer certificate'
        assert exc.value.certificate.get_subject().CN == 'intermediate-service'

    def test_modification_pre_verify(self):
        """
        `verify_certificate` can use a store context modified after
        instantiation.
        """
        store_bad = X509Store()
        store_bad.add_cert(self.intermediate_cert)
        store_good = X509Store()
        store_good.add_cert(self.root_cert)
        store_good.add_cert(self.intermediate_cert)
        store_ctx = X509StoreContext(store_bad, self.intermediate_server_cert)

        with pytest.raises(X509StoreContextError) as exc:
            store_ctx.verify_certificate()

        assert exc.value.args[0][2] == 'unable to get issuer certificate'
        assert exc.value.certificate.get_subject().CN == 'intermediate'

        store_ctx.set_store(store_good)
        assert store_ctx.verify_certificate() is None

    def test_verify_with_time(self):
        """
        `verify_certificate` raises error when the verification time is
        set at notAfter.
        """
        store = X509Store()
        store.add_cert(self.root_cert)
        store.add_cert(self.intermediate_cert)

        expire_time = self.intermediate_server_cert.get_notAfter()
        expire_datetime = datetime.strptime(
            expire_time.decode('utf-8'), '%Y%m%d%H%M%SZ'
        )
        store.set_time(expire_datetime)

        store_ctx = X509StoreContext(store, self.intermediate_server_cert)
        with pytest.raises(X509StoreContextError) as exc:
            store_ctx.verify_certificate()

        assert exc.value.args[0][2] == 'certificate has expired'


class TestSignVerify(object):
    """
    Tests for `OpenSSL.crypto.sign` and `OpenSSL.crypto.verify`.
    """

    def test_sign_verify(self):
        """
        `sign` generates a cryptographic signature which `verify` can check.
        """
        content = (
            b"It was a bright cold day in April, and the clocks were striking "
            b"thirteen. Winston Smith, his chin nuzzled into his breast in an "
            b"effort to escape the vile wind, slipped quickly through the "
            b"glass doors of Victory Mansions, though not quickly enough to "
            b"prevent a swirl of gritty dust from entering along with him.")

        # sign the content with this private key
        priv_key = load_privatekey(FILETYPE_PEM, root_key_pem)
        # verify the content with this cert
        good_cert = load_certificate(FILETYPE_PEM, root_cert_pem)
        # certificate unrelated to priv_key, used to trigger an error
        bad_cert = load_certificate(FILETYPE_PEM, server_cert_pem)

        for digest in ['md5', 'sha1']:
            sig = sign(priv_key, content, digest)

            # Verify the signature of content, will throw an exception if
            # error.
            verify(good_cert, sig, content, digest)

            # This should fail because the certificate doesn't match the
            # private key that was used to sign the content.
            with pytest.raises(Error):
                verify(bad_cert, sig, content, digest)

            # This should fail because we've "tainted" the content after
            # signing it.
            with pytest.raises(Error):
                verify(good_cert, sig, content + b"tainted", digest)

        # test that unknown digest types fail
        with pytest.raises(ValueError):
            sign(priv_key, content, "strange-digest")
        with pytest.raises(ValueError):
            verify(good_cert, sig, content, "strange-digest")

    def test_sign_verify_with_text(self):
        """
        `sign` generates a cryptographic signature which
        `verify` can check. Deprecation warnings raised because using
        text instead of bytes as content
        """
        content = (
            b"It was a bright cold day in April, and the clocks were striking "
            b"thirteen. Winston Smith, his chin nuzzled into his breast in an "
            b"effort to escape the vile wind, slipped quickly through the "
            b"glass doors of Victory Mansions, though not quickly enough to "
            b"prevent a swirl of gritty dust from entering along with him."
        ).decode("ascii")

        priv_key = load_privatekey(FILETYPE_PEM, root_key_pem)
        cert = load_certificate(FILETYPE_PEM, root_cert_pem)
        for digest in ['md5', 'sha1']:
            with pytest.warns(DeprecationWarning) as w:
                simplefilter("always")
                sig = sign(priv_key, content, digest)
            assert (
                "{0} for data is no longer accepted, use bytes".format(
                    WARNING_TYPE_EXPECTED
                ) == str(w[-1].message))

            with pytest.warns(DeprecationWarning) as w:
                simplefilter("always")
                verify(cert, sig, content, digest)
            assert (
                "{0} for data is no longer accepted, use bytes".format(
                    WARNING_TYPE_EXPECTED
                ) == str(w[-1].message))

    def test_sign_verify_ecdsa(self):
        """
        `sign` generates a cryptographic signature which `verify` can check.
        ECDSA Signatures in the X9.62 format may have variable length,
        different from the length of the private key.
        """
        content = (
            b"It was a bright cold day in April, and the clocks were striking "
            b"thirteen. Winston Smith, his chin nuzzled into his breast in an "
            b"effort to escape the vile wind, slipped quickly through the "
            b"glass doors of Victory Mansions, though not quickly enough to "
            b"prevent a swirl of gritty dust from entering along with him."
        ).decode("ascii")
        priv_key = load_privatekey(FILETYPE_PEM, ec_root_key_pem)
        cert = load_certificate(FILETYPE_PEM, ec_root_cert_pem)
        sig = sign(priv_key, content, "sha1")
        verify(cert, sig, content, "sha1")

    def test_sign_nulls(self):
        """
        `sign` produces a signature for a string with embedded nulls.
        """
        content = b"Watch out!  \0  Did you see it?"
        priv_key = load_privatekey(FILETYPE_PEM, root_key_pem)
        good_cert = load_certificate(FILETYPE_PEM, root_cert_pem)
        sig = sign(priv_key, content, "sha1")
        verify(good_cert, sig, content, "sha1")

    def test_sign_with_large_key(self):
        """
        `sign` produces a signature for a string when using a long key.
        """
        content = (
            b"It was a bright cold day in April, and the clocks were striking "
            b"thirteen. Winston Smith, his chin nuzzled into his breast in an "
            b"effort to escape the vile wind, slipped quickly through the "
            b"glass doors of Victory Mansions, though not quickly enough to "
            b"prevent a swirl of gritty dust from entering along with him.")

        priv_key = load_privatekey(FILETYPE_PEM, large_key_pem)
        sign(priv_key, content, "sha1")


class TestEllipticCurve(object):
    """
    Tests for `_EllipticCurve`, `get_elliptic_curve`, and
    `get_elliptic_curves`.
    """

    def test_set(self):
        """
        `get_elliptic_curves` returns a `set`.
        """
        assert isinstance(get_elliptic_curves(), set)

    def test_a_curve(self):
        """
        `get_elliptic_curve` can be used to retrieve a particular supported
        curve.
        """
        curves = get_elliptic_curves()
        curve = next(iter(curves))
        assert curve.name == get_elliptic_curve(curve.name).name

    def test_not_a_curve(self):
        """
        `get_elliptic_curve` raises `ValueError` if called with a name which
        does not identify a supported curve.
        """
        with pytest.raises(ValueError):
            get_elliptic_curve(u"this curve was just invented")

    def test_repr(self):
        """
        The string representation of a curve object includes simply states the
        object is a curve and what its name is.
        """
        curves = get_elliptic_curves()
        curve = next(iter(curves))
        assert "<Curve %r>" % (curve.name,) == repr(curve)

    def test_to_EC_KEY(self):
        """
        The curve object can export a version of itself as an EC_KEY* via the
        private `_EllipticCurve._to_EC_KEY`.
        """
        curves = get_elliptic_curves()
        curve = next(iter(curves))
        # It's not easy to assert anything about this object.  However, see
        # leakcheck/crypto.py for a test that demonstrates it at least does
        # not leak memory.
        curve._to_EC_KEY()


class EllipticCurveFactory(object):
    """
    A helper to get the names of two curves.
    """

    def __init__(self):
        curves = iter(get_elliptic_curves())
        self.curve_name = next(curves).name
        self.another_curve_name = next(curves).name


class TestEllipticCurveEquality(EqualityTestsMixin):
    """
    Tests `_EllipticCurve`\ 's implementation of ``==`` and ``!=``.
    """
    curve_factory = EllipticCurveFactory()

    if curve_factory.curve_name is None:
        skip = "There are no curves available there can be no curve objects."

    def anInstance(self):
        """
        Get the curve object for an arbitrary curve supported by the system.
        """
        return get_elliptic_curve(self.curve_factory.curve_name)

    def anotherInstance(self):
        """
        Get the curve object for an arbitrary curve supported by the system -
        but not the one returned by C{anInstance}.
        """
        return get_elliptic_curve(self.curve_factory.another_curve_name)


class TestEllipticCurveHash(object):
    """
    Tests for `_EllipticCurve`'s implementation of hashing (thus use as
    an item in a `dict` or `set`).
    """
    curve_factory = EllipticCurveFactory()

    if curve_factory.curve_name is None:
        skip = "There are no curves available there can be no curve objects."

    def test_contains(self):
        """
        The ``in`` operator reports that a `set` containing a curve does
        contain that curve.
        """
        curve = get_elliptic_curve(self.curve_factory.curve_name)
        curves = set([curve])
        assert curve in curves

    def test_does_not_contain(self):
        """
        The ``in`` operator reports that a `set` not containing a curve
        does not contain that curve.
        """
        curve = get_elliptic_curve(self.curve_factory.curve_name)
        curves = set([
            get_elliptic_curve(self.curve_factory.another_curve_name)
        ])
        assert curve not in curves
