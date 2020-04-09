#!/usr/bin/env python
from saml2.sigver import _get_xmlsec_cryptobackend, SecurityContext
from saml2.httpbase import HTTPBase
from saml2.attribute_converter import ac_factory
import argparse

from saml2.mdstore import MetaDataFile, MetaDataExtern, MetadataStore

__author__ = 'rolandh'

"""
A script that imports and verifies metadata.
"""

parser = argparse.ArgumentParser()
parser.add_argument('-a', dest='attrsmap')
parser.add_argument('-o', dest='output', default="local")
parser.add_argument('-x', dest='xmlsec')
parser.add_argument('-i', dest='ignore_valid', action='store_true')
parser.add_argument(dest="conf")
args = parser.parse_args()

metad = None

# config file format
#
# local <local file name>
# remote <url> <local file name for certificate use to verify signature>
#
# for instance
#
#local metadata_sp_1.xml
#local InCommon-metadata.xml
#remote https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2 kalmar2.pem
#

ATTRCONV = ac_factory(args.attrsmap)

mds = MetadataStore(None, None)

for line in open(args.conf).readlines():
    line = line.strip()
    if len(line) == 0:
        continue
    elif line[0] == "#":
        continue
    spec = line.split(" ")

    if args.ignore_valid:
        kwargs = {"check_validity": False}
    else:
        kwargs = {}

    if spec[0] == "local":
        metad = MetaDataFile(spec[1], spec[1], **kwargs)
    elif spec[0] == "remote":
        ATTRCONV = ac_factory(args.attrsmap)
        httpc = HTTPBase()
        crypto = _get_xmlsec_cryptobackend(args.xmlsec)
        sc = SecurityContext(crypto, key_type="", cert_type="")
        metad = MetaDataExtern(ATTRCONV, spec[1], sc, cert=spec[2], http=httpc,
                               **kwargs)

    if metad is not None:
        try:
            metad.load()
        except:
            raise

    mds.metadata[spec[1]] = metad

print(mds.dumps(args.output))


