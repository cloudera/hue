#!/usr/bin/env python

import argparse

from saml2.attribute_converter import ac_factory
from saml2.httpbase import HTTPBase
from saml2.mdstore import MetaDataExtern
from saml2.mdstore import MetaDataFile
from saml2.sigver import SecurityContext
from saml2.sigver import _get_xmlsec_cryptobackend


__author__ = "rolandh"

"""
A script that imports and verifies metadata.
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", dest="type")
    parser.add_argument("-u", dest="url")
    parser.add_argument("-c", dest="cert")
    parser.add_argument("-a", dest="attrsmap")
    parser.add_argument("-o", dest="output")
    parser.add_argument("-x", dest="xmlsec")
    parser.add_argument("-i", dest="ignore_valid", action="store_true")
    parser.add_argument(dest="item")
    args = parser.parse_args()

    metad = None

    if args.ignore_valid:
        kwargs = {"check_validity": False}
    else:
        kwargs = {}

    if args.type == "local":
        if args.cert and args.xmlsec:
            crypto = _get_xmlsec_cryptobackend(args.xmlsec)
            sc = SecurityContext(crypto)
            metad = MetaDataFile(args.item, args.item, cert=args.cert, security=sc, **kwargs)
        else:
            metad = MetaDataFile(args.item, args.item, **kwargs)
    elif args.type == "external":
        ATTRCONV = ac_factory(args.attrsmap)
        httpc = HTTPBase()
        crypto = _get_xmlsec_cryptobackend(args.xmlsec)
        sc = SecurityContext(crypto)
        metad = MetaDataExtern(ATTRCONV, args.url, sc, cert=args.cert, http=httpc, **kwargs)

    if metad:
        metad.load()
        print("OK")


if __name__ == "__main__":
    main()
