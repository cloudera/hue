#!/usr/bin/env python
from __future__ import print_function
import argparse

import sys

__author__ = 'rohe0002'

import requests
from jwkest.jwk import load_jwks_from_url, RSAKey
from jwkest.jwk import rsa_load
from jwkest.jwk import load_x509_cert
from jwkest.jwk import load_jwks
from jwkest.jwe import SUPPORTED
from jwkest.jwe import JWE
from jwkest.jwk import import_rsa_key_from_file


def assign(lst):
    _keys = {}
    for key in lst:
        try:
            _keys[key.kty].append(key)
        except KeyError:
            _keys[key.kty] = [key]
    return _keys


def lrequest(url, method="GET", **kwargs):
    return requests.request(method, url, **kwargs)


# arg can be RSA-OAEP
# enc for instance A128CBC+HS256

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='debug', action='store_true',
                        help="Print debug information")
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help="Print runtime information")
    parser.add_argument('-x', dest="x509_file",
                        help="File containing a X509 certificate")
    parser.add_argument('-X', dest="x509_url",
                        help="URL pointing to a file containing a X509 "
                             "certificate")
    parser.add_argument('-j', dest="jwk_file",
                        help="File containing a JWK")
    parser.add_argument('-J', dest="jwk_url",
                        help="URL pointing to a file containing a JWK")
    parser.add_argument('-r', dest="rsa_file",
                        help="A file containing a RSA key")
    parser.add_argument('-a', dest="alg",
                        help="The encryption algorithm")
    parser.add_argument("-e", dest="enc", help="The encryption method")
    parser.add_argument("-m", dest="mode", default="public",
                        help="Whether a public or private key should be used")
    parser.add_argument("-f", dest="file",
                        help="File to be encrypted")
    parser.add_argument("message", nargs="?", help="The message to encrypt")

    args = parser.parse_args()

    keys = {}
    if args.jwk_url:
        keys = load_jwks_from_url(args.jwk_url)
    elif args.jwk_file:
        keys = load_jwks(open(args.jwk_file).read())
    elif args.x509_url:
        # load_x509_cert returns list of 2-tuples
        keys = [RSAKey(key=x) for x, y in load_x509_cert(lrequest,
                                                         args.x509_url)]
        for key in keys:
            key.serialize()
    elif args.x509_file:
        # import_rsa_key_from_file returns RSA key instance
        _key = RSAKey(key=import_rsa_key_from_file(args.x509_file))
        _key.serialize()
        keys = [_key]
    elif args.rsa_file:
        _key = RSAKey(key=rsa_load(args.rsa_file))
        _key.serialize()
        keys = [_key]
    else:
        print("Needs encryption key", file=sys.stderr)
        exit()

    if not args.enc or not args.alg:
        print("There are no default encryption methods", file=sys.stderr)
        exit()

    if args.enc not in SUPPORTED["enc"]:
        print("Encryption method %s not supported", args.enc, file=sys.stderr)
        print("Methods supported: %s", SUPPORTED["enc"], file=sys.stderr)
        exit()

    if args.alg not in SUPPORTED["alg"]:
        print("Encryption algorithm %s not supported", args.alg,
              file=sys.stderr)
        print("Algorithms supported: %s", SUPPORTED["alg"], file=sys.stderr)
        exit()

    if args.file:
        message = open(args.file).read()
    elif args.message == "-":
        message = sys.stdin.read()
    else:
        message = args.message

    jwe = JWE(message, alg=args.alg, enc=args.enc)
    print(jwe.encrypt(keys))
