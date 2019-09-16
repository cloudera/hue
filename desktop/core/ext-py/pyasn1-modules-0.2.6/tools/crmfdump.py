#!/usr/bin/env python
#
# This file is part of pyasn1-modules software.
#
# Copyright (c) 2005-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pyasn1/license.html
#
# Read ASN.1/PEM X.509 CRMF request on stdin, parse into
# plain text, then build substrate from it
#
import sys

from pyasn1.codec.der import decoder
from pyasn1.codec.der import encoder

from pyasn1_modules import pem
from pyasn1_modules import rfc2511

if len(sys.argv) != 1:
    print("""Usage:
$ cat crmf.pem | %s""" % sys.argv[0])
    sys.exit(-1)

certReq = rfc2511.CertReqMessages()

substrate = pem.readBase64FromFile(sys.stdin)
if not substrate:
    sys.exit(0)

cr, rest = decoder.decode(substrate, asn1Spec=certReq)

print(cr.prettyPrint())

assert encoder.encode(cr) == substrate, 'crmf recode fails'
