#! /usr/bin/env
import json
import random
import string

import argparse

from jwkest.jwk import SYMKey

__author__ = 'regu0004'


def rndstr(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new symmetric key and print it to stdout.")
    parser.add_argument("-n", dest="key_length", default=48, type=int,
                        help="Length of the random string used as key.")
    parser.add_argument("--kid", dest="kid", help="Key id.")
    args = parser.parse_args()

    key = SYMKey(key=rndstr(args.key_length), kid=args.kid).serialize()
    jwks = dict(keys=[key])
    print(json.dumps(jwks))


if __name__ == "__main__":
    main()
