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

import datetime


def auth_response(
    session_id,
    uid,
    audience="http://sp.example.com/saml2/metadata/",
    acs_url="http://sp.example.com/saml2/acs/",
    metadata_url="http://sp.example.com/saml2/metadata/",
    attribute_statements=None,
):
    """Generates a fresh signed authentication response

    Params:
        session_id: The session ID to generate the reponse for. Login set an
            outstanding session ID, i.e. djangosaml2 waits for a response for
            that session.
        uid: Unique identifier for a User (will be present as an attribute in
            the answer). Ignored when attribute_statements is not ``None``.
        audience: SP entityid (used when PySAML validates the response
            audience).
        acs_url: URL where the response has been posted back.
        metadata_url: URL where the SP metadata can be queried.
        attribute_statements: An alternative XML AttributeStatement to use in
            lieu of the default (uid). The uid argument is ignored when
            attribute_statements is not ``None``.
    """
    timestamp = datetime.datetime.now() - datetime.timedelta(seconds=10)
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

    if attribute_statements is None:
        attribute_statements = (
            "<saml:AttributeStatement>"
            '<saml:Attribute FriendlyName="uid" Name="urn:oid:0.9.2342.19200300.100.1.1" NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:uri">'
            '<saml:AttributeValue xsi:nil="true" xsi:type="xs:string">'
            "%(uid)s"
            "</saml:AttributeValue>"
            "</saml:Attribute>"
            "</saml:AttributeStatement>"
        ) % {"uid": uid}

    saml_response_tpl = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<samlp:Response xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Destination="%(acs_url)s" ID="id-88b9f586a2a3a639f9327485cc37c40a" InResponseTo="%(session_id)s" IssueInstant="%(timestamp)s" Version="2.0">'
        '<saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">'
        "https://idp.example.com/simplesaml/saml2/idp/metadata.php"
        "</saml:Issuer>"
        "<samlp:Status>"
        '<samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" />'
        "</samlp:Status>"
        '<saml:Assertion ID="id-093952102ceb73436e49cb91c58b0578" IssueInstant="%(timestamp)s" Version="2.0">'
        '<saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">'
        "https://idp.example.com/simplesaml/saml2/idp/metadata.php"
        "</saml:Issuer>"
        "<saml:Subject>"
        '<saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient" NameQualifier="" SPNameQualifier="%(metadata_url)s">'
        "1f87035b4c1325b296a53d92097e6b3fa36d7e30ee82e3fcb0680d60243c1f03"
        "</saml:NameID>"
        '<saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">'
        '<saml:SubjectConfirmationData InResponseTo="%(session_id)s" NotOnOrAfter="%(tomorrow)s" Recipient="%(acs_url)s" />'
        "</saml:SubjectConfirmation>"
        "</saml:Subject>"
        '<saml:Conditions NotBefore="%(yesterday)s" NotOnOrAfter="%(tomorrow)s">'
        "<saml:AudienceRestriction>"
        "<saml:Audience>"
        "%(audience)s"
        "</saml:Audience>"
        "</saml:AudienceRestriction>"
        "</saml:Conditions>"
        '<saml:AuthnStatement AuthnInstant="%(timestamp)s" SessionIndex="%(session_id)s">'
        "<saml:AuthnContext>"
        "<saml:AuthnContextClassRef>"
        "urn:oasis:names:tc:SAML:2.0:ac:classes:Password"
        "</saml:AuthnContextClassRef>"
        "</saml:AuthnContext>"
        "</saml:AuthnStatement>"
        "%(attribute_statements)s"
        "</saml:Assertion>"
        "</samlp:Response>"
    )
    return saml_response_tpl % {
        "session_id": session_id,
        "audience": audience,
        "acs_url": acs_url,
        "metadata_url": metadata_url,
        "attribute_statements": attribute_statements,
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tomorrow": tomorrow.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "yesterday": yesterday.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
