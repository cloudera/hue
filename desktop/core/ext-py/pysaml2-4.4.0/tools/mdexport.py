#!/usr/bin/env python
from saml2.sigver import _get_xmlsec_cryptobackend
from saml2.sigver import SecurityContext
from saml2.httpbase import HTTPBase

from saml2 import saml
from saml2 import md
from saml2.attribute_converter import ac_factory
from saml2 import xmldsig
from saml2 import xmlenc

import argparse

from saml2.mdstore import MetaDataFile, MetaDataExtern, load_extensions

__author__ = 'rolandh'

"""
A script that imports and verifies metadata and then dumps it in a basic
dictionary format.
"""

parser = argparse.ArgumentParser()
parser.add_argument('-t', dest='type')
parser.add_argument('-u', dest='url')
parser.add_argument('-c', dest='cert')
parser.add_argument('-a', dest='attrsmap')
parser.add_argument('-o', dest='output')
parser.add_argument('-x', dest='xmlsec')
parser.add_argument(dest="item")
args = parser.parse_args()


metad = None

if args.type == "local":
    metad = MetaDataFile(args.item, args.item)
elif args.type == "external":
    ATTRCONV = ac_factory(args.attrsmap)
    httpc = HTTPBase()
    crypto = _get_xmlsec_cryptobackend(args.xmlsec)
    sc = SecurityContext(crypto)
    metad = MetaDataExtern(ATTRCONV, args.url, sc, cert=args.cert, http=httpc)

if metad is not None:
    metad.load()
    txt = metad.dumps()
    if args.output:
        f = open(args.output, "w")
        f.write(txt)
        f.close()
    else:
        print(txt)
