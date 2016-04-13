#!/usr/bin/env python
from saml2.sigver import _get_xmlsec_cryptobackend, SecurityContext
from saml2.httpbase import HTTPBase

from saml2 import saml
from saml2 import md
from saml2.attribute_converter import ac_factory
from saml2.extension import dri
from saml2.extension import idpdisc
from saml2.extension import mdattr
from saml2.extension import mdrpi
from saml2.extension import mdui
from saml2.extension import shibmd
from saml2.extension import ui
import xmldsig
import xmlenc

import argparse

from saml2.mdstore import MetaDataFile, MetaDataExtern

__author__ = 'rolandh'

"""
A script that imports and verifies metadata and then dumps it in a basic
dictionary format.
"""


ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    mdrpi.NAMESPACE: mdrpi,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc,
    shibmd.NAMESPACE: shibmd
}


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
    metad = MetaDataFile(ONTS.values(), args.item, args.item)
elif args.type == "external":
    ATTRCONV = ac_factory(args.attrsmap)
    httpc = HTTPBase()
    crypto = _get_xmlsec_cryptobackend(args.xmlsec)
    sc = SecurityContext(crypto)
    metad = MetaDataExtern(ONTS.values(), ATTRCONV, args.url,
                           sc, cert=args.cert, http=httpc)

if metad is not None:
    metad.load()
    txt = metad.dumps()
    if args.output:
        f = open(args.output, "w")
        f.write(txt)
        f.close()
    else:
        print txt
