#!/usr/bin/env python
import os
import argparse
from jwkest.jwk import RSAKey
from jwkest.jwk import rsa_load
from jwkest.jwk import dump_jwks

__author__ = 'rolandh'

parser = argparse.ArgumentParser()
parser.add_argument('-n', dest="name", default="pyoidc",
                    help="file names")
parser.add_argument('-p', dest="path", default=".",
                    help="Path to the directory for the files")
parser.add_argument('-k', dest="key", help="Key file")

args = parser.parse_args()

rsa_key = RSAKey(key=rsa_load(args.key))

keyfile = os.path.join(args.path, args.name)

f = open(keyfile + ".jwk", "w")
f.write(dump_jwks([rsa_key]))
f.close()
