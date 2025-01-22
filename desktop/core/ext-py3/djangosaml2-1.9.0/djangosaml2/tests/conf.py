# Copyright (C) 2011-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path

import saml2


def create_conf(
    sp_host="sp.example.com",
    idp_hosts=None,
    metadata_file="remote_metadata.xml",
    authn_requests_signed=None,
    sp_kwargs: dict = None,
):
    if idp_hosts is None:
        idp_hosts = ["idp.example.com"]

    try:
        from saml2.sigver import get_xmlsec_binary
    except ImportError:
        get_xmlsec_binary = None

    if get_xmlsec_binary:
        xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
    else:
        xmlsec_path = "/usr/bin/xmlsec1"

    BASEDIR = os.path.dirname(os.path.abspath(__file__))
    config = {
        "xmlsec_binary": xmlsec_path,
        "entityid": "http://%s/saml2/metadata/" % sp_host,
        "attribute_map_dir": os.path.join(BASEDIR, "attribute-maps"),
        "service": {
            "sp": {
                "name": "Test SP",
                "name_id_format": saml2.saml.NAMEID_FORMAT_PERSISTENT,
                "endpoints": {
                    "assertion_consumer_service": [
                        ("http://%s/saml2/acs/" % sp_host, saml2.BINDING_HTTP_POST),
                    ],
                    "single_logout_service": [
                        ("http://%s/saml2/ls/" % sp_host, saml2.BINDING_HTTP_REDIRECT),
                    ],
                },
                "required_attributes": ["uid"],
                "optional_attributes": ["eduPersonAffiliation"],
                "idp": {},  # this is filled later
                "want_response_signed": False,
            },
        },
        "metadata": {
            "local": [os.path.join(BASEDIR, metadata_file)],
        },
        "debug": 1,
        # certificates
        "key_file": os.path.join(BASEDIR, "mycert.key"),
        "cert_file": os.path.join(BASEDIR, "mycert.pem"),
        # These fields are only used when generating the metadata
        "contact_person": [
            {
                "given_name": "Technical givenname",
                "sur_name": "Technical surname",
                "company": "Example Inc.",
                "email_address": "technical@sp.example.com",
                "contact_type": "technical",
            },
            {
                "given_name": "Administrative givenname",
                "sur_name": "Administrative surname",
                "company": "Example Inc.",
                "email_address": "administrative@sp.example.ccom",
                "contact_type": "administrative",
            },
        ],
        "organization": {
            "name": [("Ejemplo S.A.", "es"), ("Example Inc.", "en")],
            "display_name": [("Ejemplo", "es"), ("Example", "en")],
            "url": [("http://www.example.es", "es"), ("http://www.example.com", "en")],
        },
        "valid_for": 24,
    }
    if sp_kwargs is not None:
        config["service"]["sp"].update(**sp_kwargs)

    if authn_requests_signed is not None:
        config["service"]["sp"]["authn_requests_signed"] = authn_requests_signed

    for idp in idp_hosts:
        entity_id = "https://%s/simplesaml/saml2/idp/metadata.php" % idp
        config["service"]["sp"]["idp"][entity_id] = {
            "single_sign_on_service": {
                saml2.BINDING_HTTP_REDIRECT: "https://%s/simplesaml/saml2/idp/SSOService.php"
                % idp,
            },
            "single_logout_service": {
                saml2.BINDING_HTTP_REDIRECT: "https://%s/simplesaml/saml2/idp/SingleLogoutService.php"
                % idp,
            },
        }

    return config
