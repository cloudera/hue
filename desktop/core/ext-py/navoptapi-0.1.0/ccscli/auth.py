# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from base64 import urlsafe_b64encode
from email.utils import formatdate
import logging

from ccscli.compat import json
from ccscli.compat import OrderedDict
from ccscli.compat import urlsplit
from ccscli.exceptions import NoCredentialsError
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


LOG = logging.getLogger('ccscli.auth')


class BaseSigner(object):
    def add_auth(self, request):
        raise NotImplementedError("add_auth")


class RSAv1Auth(BaseSigner):
    """
    RSA signing with a SHA-256 hash returning a base64 encoded signature.
    """
    AUTH_METHOD_NAME = 'rsav1'

    def __init__(self, credentials):
        self.credentials = credentials

    def sign_string(self, string_to_sign):
        try:
            # We expect the private key to be the an PKCS8 pem formatted string.
            key = RSA.importKey(self.credentials.private_key)
        except:
            message = \
                "Failed to import private key from: '%s'. The private key is " \
                "corrupted or it is not in PKCS8 PEM format. The private key " \
                "was extracted either from 'env' (environment variables), " \
                "'shared-credentials-file' (a profile in the shared " \
                "credential file, by default under ~/.ccs/credentials), or " \
                "'auth-config-file' (a file containing the credentials whose " \
                "location was supplied on the command line.)" % \
                self.credentials.method
            LOG.debug(message, exc_info=True)
            raise Exception(message)
        # We sign the hash.
        h = SHA256.new(string_to_sign.encode('utf-8'))
        signer = PKCS1_v1_5.new(key)
        return urlsafe_b64encode(signer.sign(h)).strip().decode('utf-8')

    def canonical_standard_headers(self, headers):
        interesting_headers = ['content-type', 'x-ccs-date']
        hoi = []
        if 'x-ccs-date' in headers:
            raise Exception("x-ccs-date found in headers!")
        headers['x-ccs-date'] = self._get_date()
        for ih in interesting_headers:
            found = False
            for key in headers:
                lk = key.lower()
                if headers[key] is not None and lk == ih:
                    hoi.append(headers[key].strip())
                    found = True
            if not found:
                hoi.append('')
        return '\n'.join(hoi)

    def canonical_string(self, method, split, headers):
        cs = method.upper() + '\n'
        cs += self.canonical_standard_headers(headers) + '\n'
        cs += split.path + '\n'
        cs += RSAv1Auth.AUTH_METHOD_NAME
        return cs

    def get_signature(self, method, split, headers):
        string_to_sign = self.canonical_string(method, split, headers)
        LOG.debug('StringToSign:\n%s', string_to_sign)
        return self.sign_string(string_to_sign)

    def add_auth(self, request):
        if self.credentials is None:
            raise NoCredentialsError
        LOG.debug("Calculating signature using RSAv1Auth.")
        LOG.debug('HTTP request method: %s', request.method)
        split = urlsplit(request.url)
        signature = self.get_signature(request.method,
                                       split,
                                       request.headers)
        self._inject_signature(request, signature)

    def _get_date(self):
        return formatdate(usegmt=True)

    def _inject_signature(self, request, signature):
        if 'x-ccs-auth' in request.headers:
            raise Exception("x-ccs-auth found in headers!")
        request.headers['x-ccs-auth'] = self._get_signature_header(signature)

    def _get_signature_header(self, signature):
        auth_params = OrderedDict()
        auth_params['access_key_id'] = self.credentials.access_key_id
        auth_params['auth_method'] = RSAv1Auth.AUTH_METHOD_NAME
        encoded_auth_params = json.dumps(auth_params).encode('utf-8')
        return "%s.%s" % (
            urlsafe_b64encode(encoded_auth_params).strip().decode('utf-8'),
            signature)


AUTH_TYPE_MAPS = {
    RSAv1Auth.AUTH_METHOD_NAME: RSAv1Auth,
}
