#!/usr/bin/env python
# -*- coding: utf-8 -*-
from saml2.cert import OpenSSLWrapper

__author__ = 'haho0032'


cert_info_ca = {
    "cn": "localhost.ca",
    "country_code": "se",
    "state": "ac",
    "city": "umea",
    "organization": "ITS Umea University",
    "organization_unit": "DIRG"
}

osw = OpenSSLWrapper()

ca_cert, ca_key = osw.create_certificate(cert_info_ca, request=False, write_to_file=True,
                                                cert_dir="./")