#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import re
from collections import OrderedDict

from future.backports.urllib.parse import quote_plus

from saml2.config import Config
from saml2.mdstore import MetadataStore
from saml2.mdstore import MetaDataMDX
from saml2.mdstore import SAML_METADATA_CONTENT_TYPE
from saml2.mdstore import destinations
from saml2.mdstore import name
from saml2 import sigver
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import config
from saml2.attribute_converter import ac_factory
from saml2.attribute_converter import d_to_local_name
from saml2.s_utils import UnknownPrincipal
from pathutils import full_path

import responses

sec_config = config.Config()
# sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])

TEST_CERT = """MIICsDCCAhmgAwIBAgIJAJrzqSSwmDY9MA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMDkxMDA2MTk0OTQxWhcNMDkxMTA1MTk0OTQxWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQDJg2cms7MqjniT8Fi/XkNHZNPbNVQyMUMXE9tXOdqwYCA1cc8vQdzkihscQMXy
3iPw2cMggBu6gjMTOSOxECkuvX5ZCclKr8pXAJM5cY6gVOaVO2PdTZcvDBKGbiaN
efiEw5hnoZomqZGp8wHNLAUkwtH9vjqqvxyS/vclc6k2ewIDAQABo4GnMIGkMB0G
A1UdDgQWBBRePsKHKYJsiojE78ZWXccK9K4aJTB1BgNVHSMEbjBsgBRePsKHKYJs
iojE78ZWXccK9K4aJaFJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUt
U3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAJrzqSSw
mDY9MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAJSrKOEzHO7TL5cy6
h3qh+3+JAk8HbGBW+cbX6KBCAw/mzU8flK25vnWwXS3dv2FF3Aod0/S7AWNfKib5
U/SA9nJaz/mWeF9S0farz9AQFc8/NSzAzaVq7YbM4F6f6N2FRl7GikdXRCed45j6
mrPzGzk3ECbupFnqyREH3+ZPSdk="""

TEST_METADATA_STRING = """
<EntitiesDescriptor
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:shibmeta="urn:mace:shibboleth:metadata:1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    Name="urn:mace:example.com:test-1.0">
  <EntityDescriptor
    entityID="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    xml:base="swamid-1.0/idp.umu.se-saml2.xml">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor>
      <ds:KeyInfo>
        <ds:X509Data>
          <ds:X509Certificate>
            {cert_data}
          </ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
    <SingleSignOnService
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        Location="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"/>
  </IDPSSODescriptor>
  <Organization>
    <OrganizationName xml:lang="en">Catalogix</OrganizationName>
    <OrganizationDisplayName xml:lang="en">Catalogix</OrganizationDisplayName>
    <OrganizationURL xml:lang="en">http://www.catalogix.se</OrganizationURL>
  </Organization>
  <ContactPerson contactType="technical">
    <SurName>Hedberg</SurName>
    <EmailAddress>datordrift@catalogix.se</EmailAddress>
  </ContactPerson>
</EntityDescriptor>
</EntitiesDescriptor>
""".format(cert_data=TEST_CERT)


ATTRCONV = ac_factory(full_path("attributemaps"))

METADATACONF = {
    "1": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("swamid-1.0.xml"),)],
    }],
    "2": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("InCommon-metadata.xml"),)],
    }],
    "3": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("extended.xml"),)],
    }],
    # "7": [{
    #     "class": "saml2.mdstore.MetaDataFile",
    #     "metadata": [(full_path("metadata_sp_1.xml"), ),
    #                  (full_path("InCommon-metadata.xml"), )], },
    #       {
    #     "class": "saml2.mdstore.MetaDataExtern",
    #     "metadata": [
    #         ("https://kalmar2.org/simplesaml/module.php/aggregator/?id
    # =kalmarcentral2&set=saml2",
    #          full_path("kalmar2.pem")), ],
    # }],
    "4": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("metadata_example.xml"),)],
    }],
    "5": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("metadata.aaitest.xml"),)],
    }],
    "8": [{
        "class": "saml2.mdstore.MetaDataMD",
        "metadata": [(full_path("swamid.md"),)],
    }],
    "9": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("metadata"),)]
    }],
    "10": [{
        "class": "saml2.mdstore.MetaDataExtern",
        "metadata": [
            ("http://md.incommon.org/InCommon/InCommon-metadata-export.xml",
             full_path("inc-md-cert.pem"))]
    }],
    "11": [{
        "class": "saml2.mdstore.InMemoryMetaData",
        "metadata": [(TEST_METADATA_STRING,)]
    }],
    "12": [{
        "class": "saml2.mdstore.MetaDataFile",
        "metadata": [(full_path("uu.xml"),)],
    }],
}


def _eq(l1, l2):
    return set(l1) == set(l2)


def _fix_valid_until(xmlstring):
    new_date = datetime.datetime.now() + datetime.timedelta(days=1)
    new_date = new_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return re.sub(r' validUntil=".*?"', ' validUntil="%s"' % new_date,
                  xmlstring)


def test_swami_1():
    UMU_IDP = 'https://idp.umu.se/saml2/idp/metadata.php'
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["1"])
    assert len(mds) == 1  # One source
    idps = mds.with_descriptor("idpsso")
    assert idps.keys()
    idpsso = mds.single_sign_on_service(UMU_IDP)
    assert len(idpsso) == 1
    assert destinations(idpsso) == [
        'https://idp.umu.se/saml2/idp/SSOService.php']

    _name = name(mds[UMU_IDP])
    assert _name == u'Umeå University (SAML2)'
    certs = mds.certs(UMU_IDP, "idpsso", "signing")
    assert len(certs) == 1

    sps = mds.with_descriptor("spsso")
    assert len(sps) == 108

    wants = mds.attribute_requirement('https://connect8.sunet.se/shibboleth')
    lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
    assert _eq(lnamn, ['eduPersonPrincipalName', 'mail', 'givenName', 'sn',
                       'eduPersonScopedAffiliation'])

    wants = mds.attribute_requirement('https://beta.lobber.se/shibboleth')
    assert wants["required"] == []
    lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
    assert _eq(lnamn, ['eduPersonPrincipalName', 'mail', 'givenName', 'sn',
                       'eduPersonScopedAffiliation', 'eduPersonEntitlement'])


def test_incommon_1():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["2"])

    print(mds.entities())
    assert mds.entities() > 1700
    idps = mds.with_descriptor("idpsso")
    print(idps.keys())
    assert len(idps) > 300  # ~ 18%
    try:
        _ = mds.single_sign_on_service('urn:mace:incommon:uiuc.edu')
    except UnknownPrincipal:
        pass

    idpsso = mds.single_sign_on_service('urn:mace:incommon:alaska.edu')
    assert len(idpsso) == 1
    print(idpsso)
    assert destinations(idpsso) == [
        'https://idp.alaska.edu/idp/profile/SAML2/Redirect/SSO']

    sps = mds.with_descriptor("spsso")

    acs_sp = []
    for nam, desc in sps.items():
        if "attribute_consuming_service" in desc:
            acs_sp.append(nam)

    assert len(acs_sp) == 0

    # Look for attribute authorities
    aas = mds.with_descriptor("attribute_authority")

    print(aas.keys())
    assert len(aas) == 180


def test_ext_2():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["3"])
    # No specific binding defined

    ents = mds.with_descriptor("spsso")
    for binding in [BINDING_SOAP, BINDING_HTTP_POST, BINDING_HTTP_ARTIFACT,
                    BINDING_HTTP_REDIRECT]:
        assert mds.single_logout_service(list(ents.keys())[0], binding, "spsso")


def test_example():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["4"])
    assert len(mds.keys()) == 1
    idps = mds.with_descriptor("idpsso")

    assert list(idps.keys()) == [
        'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php']
    certs = mds.certs(
        'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php',
        "idpsso", "signing")
    assert len(certs) == 1


def test_switch_1():
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["5"])
    assert len(mds.keys()) > 160
    idps = mds.with_descriptor("idpsso")
    print(idps.keys())
    idpsso = mds.single_sign_on_service(
        'https://aai-demo-idp.switch.ch/idp/shibboleth')
    assert len(idpsso) == 1
    print(idpsso)
    assert destinations(idpsso) == [
        'https://aai-demo-idp.switch.ch/idp/profile/SAML2/Redirect/SSO']
    assert len(idps) > 30
    aas = mds.with_descriptor("attribute_authority")
    print(aas.keys())
    aad = aas['https://aai-demo-idp.switch.ch/idp/shibboleth']
    print(aad.keys())
    assert len(aad["attribute_authority_descriptor"]) == 1
    assert len(aad["idpsso_descriptor"]) == 1

    sps = mds.with_descriptor("spsso")
    dual = [eid for eid, ent in idps.items() if eid in sps]
    print(len(dual))
    assert len(dual) == 0


def test_metadata_file():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["8"])
    print(len(mds.keys()))
    assert len(mds.keys()) == 560


@responses.activate
def test_mdx_service():
    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"

    url = "http://mdx.example.com/entities/{}".format(
        quote_plus(MetaDataMDX.sha1_entity_transform(entity_id)))
    responses.add(responses.GET, url, body=TEST_METADATA_STRING, status=200,
                  content_type=SAML_METADATA_CONTENT_TYPE)

    mdx = MetaDataMDX("http://mdx.example.com")
    sso_loc = mdx.service(entity_id, "idpsso_descriptor", "single_sign_on_service")
    assert sso_loc[BINDING_HTTP_REDIRECT][0]["location"] == "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    certs = mdx.certs(entity_id, "idpsso")
    assert len(certs) == 1


@responses.activate
def test_mdx_single_sign_on_service():
    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"

    url = "http://mdx.example.com/entities/{}".format(
        quote_plus(MetaDataMDX.sha1_entity_transform(entity_id)))
    responses.add(responses.GET, url, body=TEST_METADATA_STRING, status=200,
                  content_type=SAML_METADATA_CONTENT_TYPE)

    mdx = MetaDataMDX("http://mdx.example.com")
    sso_loc = mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert sso_loc[0]["location"] == "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"


# pyff-test not available
# def test_mdx_service():
#     sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
#     http = HTTPBase(verify=False, ca_bundle=None)
#
#     mdx = MetaDataMDX(quote_plus, ATTRCONV,
#                       "http://pyff-test.nordu.net",
#                       sec_config, None, http)
#     foo = mdx.service("https://idp.umu.se/saml2/idp/metadata.php",
#                       "idpsso_descriptor", "single_sign_on_service")
#
#     assert len(foo) == 1
#     assert foo.keys()[0] == BINDING_HTTP_REDIRECT
#
#
# def test_mdx_certs():
#     sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
#     http = HTTPBase(verify=False, ca_bundle=None)
#
#     mdx = MetaDataMDX(quote_plus, ATTRCONV,
#                       "http://pyff-test.nordu.net",
#                       sec_config, None, http)
#     foo = mdx.certs("https://idp.umu.se/saml2/idp/metadata.php", "idpsso")
#
#     assert len(foo) == 1


def test_load_local_dir():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["9"])
    print(mds)
    assert len(mds) == 3  # Three sources
    assert len(mds.keys()) == 4  # number of idps


def test_load_extern_incommon():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["10"])
    print(mds)
    assert mds
    assert len(mds.keys())


def test_load_local():
    # string representation of XML idp definition
    idp_metadata = open(full_path("metadata.xml")).read()

    saml_config = Config()

    config_dict = {
        "metadata": {"inline": [idp_metadata]}
    }
    cfg = saml_config.load(config_dict)
    assert cfg


def test_load_string():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config,
                        disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["11"])
    # print(mds)
    assert len(mds.keys()) == 1
    idps = mds.with_descriptor("idpsso")

    assert list(idps.keys()) == [
        'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php']
    certs = mds.certs(
        'http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php',
        "idpsso", "signing")
    assert len(certs) == 1


def test_get_certs_from_metadata():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["11"])
    certs1 = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "any")
    certs2 = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso")

    assert certs1[0] == certs2[0] == TEST_CERT


def test_get_certs_from_metadata_without_keydescriptor():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp([{
        "class": "saml2.mdstore.InMemoryMetaData",
        "metadata": [("""
<EntitiesDescriptor
    xmlns="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    xmlns:shibmeta="urn:mace:shibboleth:metadata:1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    Name="urn:mace:example.com:test-1.0">
  <EntityDescriptor
    entityID="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    xml:base="swamid-1.0/idp.umu.se-saml2.xml">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <NameIDFormat>urn:oasis:names:tc:SAML:2.0:nameid-format:transient</NameIDFormat>
    <SingleSignOnService
        Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        Location="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"/>
  </IDPSSODescriptor>
  <Organization>
    <OrganizationName xml:lang="en">Catalogix</OrganizationName>
    <OrganizationDisplayName xml:lang="en">Catalogix</OrganizationDisplayName>
    <OrganizationURL xml:lang="en">http://www.catalogix.se</OrganizationURL>
  </Organization>
  <ContactPerson contactType="technical">
    <SurName>Hedberg</SurName>
    <EmailAddress>datordrift@catalogix.se</EmailAddress>
  </ContactPerson>
</EntityDescriptor>
</EntitiesDescriptor>""",)]
    }])
    certs = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso")

    assert len(certs) == 0


def test_metadata_extension_algsupport():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["12"])
    mdf = mds.metadata[full_path("uu.xml")]
    assert mds


def test_extension():
    mds = MetadataStore(ATTRCONV, None)
    # use ordered dict to force expected entity to be last
    metadata = OrderedDict()
    metadata["1"] = {"entity1": {}}
    metadata["2"] = {"entity2": {"idpsso_descriptor": [{"extensions": {"extension_elements": [{"__class__": "test"}]}}]}}
    mds.metadata = metadata
    assert mds.extension("entity2", "idpsso_descriptor", "test")


if __name__ == "__main__":
    test_metadata_extension_algsupport()
