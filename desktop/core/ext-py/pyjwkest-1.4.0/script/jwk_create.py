#!/usr/bin/env python
import json
from Cryptodome.PublicKey import RSA
import argparse
import os
from jwkest.jwk import RSAKey

__author__ = 'rolandh'


def create_and_store_rsa_key_pair(name="pyoidc", path=".", size=1024):
    key = RSA.generate(size)

    keyfile = os.path.join(path, name)

    f = open("%s.key" % keyfile, "w")
    f.write(key.exportKey("PEM"))
    f.close()
    f = open("%s.pub" % keyfile, "w")
    f.write(key.publickey().exportKey("PEM"))
    f.close()

    rsa_key = RSAKey(key=key)
    rsa_key.serialize()
    # This will create JWK from the public RSA key
    jwk_spec = json.dumps(rsa_key.to_dict(), "enc")
    f = open(keyfile + ".jwk", "w")
    f.write(str(jwk_spec))
    f.close()

    return key

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', dest="name", default="pyoidc",
                        help="file names")
    parser.add_argument('-p', dest="path", default=".",
                        help="Path to the directory for the files")
    parser.add_argument('-s', dest="size", default=1024,
                        help="Key size", type=int)

    args = parser.parse_args()

    create_and_store_rsa_key_pair(args.name, args.path, args.size)
