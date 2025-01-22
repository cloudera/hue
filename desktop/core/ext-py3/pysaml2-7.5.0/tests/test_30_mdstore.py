#!/usr/bin/env python
from collections import OrderedDict
import datetime
import os
import re
from re import compile as regex_compile
from unittest.mock import Mock
from unittest.mock import patch
from urllib import parse

from pathutils import full_path
from pytest import raises
import responses

from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2 import SAMLError
from saml2 import config
from saml2 import sigver
from saml2.attribute_converter import ac_factory
from saml2.attribute_converter import d_to_local_name
from saml2.config import Config
from saml2.httpbase import HTTPBase
from saml2.mdstore import SAML_METADATA_CONTENT_TYPE
from saml2.mdstore import MetaDataExtern
from saml2.mdstore import MetaDataMDX
from saml2.mdstore import MetadataStore
from saml2.mdstore import locations
from saml2.mdstore import name
from saml2.s_utils import UnknownPrincipal


TESTS_DIR = os.path.dirname(__file__)

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
    xmlns:alg="urn:oasis:names:tc:SAML:metadata:algsupport"
    xmlns:shibmeta="urn:mace:shibboleth:metadata:1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
    Name="urn:mace:example.com:test-1.0">
  <EntityDescriptor
    entityID="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    xml:base="swamid-1.0/idp.umu.se-saml2.xml">
    <md:Extensions>
        <alg:DigestMethod Algorithm="http://www.w3.org/2001/04/xmlenc#sha256"/>
        <alg:SigningMethod Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"/>
    </md:Extensions>
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
""".format(
    cert_data=TEST_CERT
)

ATTRCONV = ac_factory(full_path("attributemaps"))

METADATACONF = {
    "1": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("swamid-1.0.xml"),)],
        }
    ],
    "2": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("InCommon-metadata.xml"),)],
        }
    ],
    "3": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("extended.xml"),)],
        }
    ],
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
    "4": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("metadata_example.xml"),)],
        }
    ],
    "5": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("metadata.aaitest.xml"),)],
        }
    ],
    "8": [
        {
            "class": "saml2.mdstore.MetaDataMD",
            "metadata": [(full_path("swamid.md"),)],
        }
    ],
    "9": [{"class": "saml2.mdstore.MetaDataFile", "metadata": [(full_path("metadata"),)]}],
    "10": [
        {
            "class": "saml2.mdstore.MetaDataExtern",
            "metadata": [
                ("http://md.incommon.org/InCommon/InCommon-metadata-export.xml", full_path("inc-md-cert.pem"))
            ],
        }
    ],
    "11": [{"class": "saml2.mdstore.InMemoryMetaData", "metadata": [(TEST_METADATA_STRING,)]}],
    "12": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("uu.xml"),)],
        }
    ],
    "13": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("swamid-2.0.xml"),)],
        }
    ],
    "14": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("invalid_metadata_file.xml"),)],
        }
    ],
    "15": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("idp_uiinfo.xml"),)],
        }
    ],
    "16": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("empty_metadata_file.xml"),)],
        }
    ],
    "17": [
        {
            "class": "saml2.mdstore.MetaDataFile",
            "metadata": [(full_path("entity_esi_and_coco_sp.xml"),)],
        }
    ],
}


def _eq(l1, l2):
    return set(l1) == set(l2)


def _fix_valid_until(xmlstring):
    new_date = datetime.datetime.now() + datetime.timedelta(days=1)
    new_date = new_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return re.sub(r' validUntil=".*?"', f' validUntil="{new_date}"', xmlstring)


def test_invalid_metadata():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["14"])
    assert mds.entities() == 0


def test_empty_metadata():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    with raises(SAMLError):
        mds.imp(METADATACONF["16"])


def test_swami_1():
    UMU_IDP = "https://idp.umu.se/saml2/idp/metadata.php"
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["1"])
    assert len(mds) == 1  # One source
    idps = mds.with_descriptor("idpsso")
    assert idps.keys()
    idpsso = mds.single_sign_on_service(UMU_IDP)
    assert len(idpsso) == 1
    assert list(locations(idpsso)) == ["https://idp.umu.se/saml2/idp/SSOService.php"]

    _name = name(mds[UMU_IDP])
    assert _name == "Umeå University (SAML2)"
    certs = mds.certs(UMU_IDP, "idpsso", "signing")
    assert len(certs) == 1

    sps = mds.with_descriptor("spsso")
    assert len(sps) == 108

    wants = mds.attribute_requirement("https://connect8.sunet.se/shibboleth")
    lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
    assert _eq(lnamn, ["eduPersonPrincipalName", "mail", "givenName", "sn", "eduPersonScopedAffiliation"])

    wants = mds.attribute_requirement("https://beta.lobber.se/shibboleth")
    assert wants["required"] == []
    lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
    assert _eq(
        lnamn,
        ["eduPersonPrincipalName", "mail", "givenName", "sn", "eduPersonScopedAffiliation", "eduPersonEntitlement"],
    )


def test_incommon_1():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["2"])

    print(mds.entities())
    assert mds.entities() > 1700
    idps = mds.with_descriptor("idpsso")
    print(idps.keys())
    assert len(idps) > 300  # ~ 18%
    try:
        _ = mds.single_sign_on_service("urn:mace:incommon:uiuc.edu")
    except UnknownPrincipal:
        pass

    idpsso = mds.single_sign_on_service("urn:mace:incommon:alaska.edu")
    assert len(idpsso) == 1
    print(idpsso)
    assert list(locations(idpsso)) == ["https://idp.alaska.edu/idp/profile/SAML2/Redirect/SSO"]

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
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["3"])
    # No specific binding defined

    ents = mds.with_descriptor("spsso")
    for binding in [BINDING_SOAP, BINDING_HTTP_POST, BINDING_HTTP_ARTIFACT, BINDING_HTTP_REDIRECT]:
        assert mds.single_logout_service(list(ents.keys())[0], binding, "spsso")


def test_example():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["4"])
    assert len(mds.keys()) == 1
    idps = mds.with_descriptor("idpsso")

    assert list(idps.keys()) == ["http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"]
    certs = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso", "signing")
    assert len(certs) == 1


def test_switch_1():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["5"])
    assert len(mds.keys()) > 160
    idps = mds.with_descriptor("idpsso")
    print(idps.keys())
    idpsso = mds.single_sign_on_service("https://aai-demo-idp.switch.ch/idp/shibboleth")
    assert len(idpsso) == 1
    print(idpsso)
    assert list(locations(idpsso)) == ["https://aai-demo-idp.switch.ch/idp/profile/SAML2/Redirect/SSO"]
    assert len(idps) > 30
    aas = mds.with_descriptor("attribute_authority")
    print(aas.keys())
    aad = aas["https://aai-demo-idp.switch.ch/idp/shibboleth"]
    print(aad.keys())
    assert len(aad["attribute_authority_descriptor"]) == 1
    assert len(aad["idpsso_descriptor"]) == 1

    sps = mds.with_descriptor("spsso")
    dual = [eid for eid, ent in idps.items() if eid in sps]
    print(len(dual))
    assert len(dual) == 0


def test_metadata_file():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["8"])
    print(len(mds.keys()))
    assert len(mds.keys()) == 560


@responses.activate
def test_mdx_service():
    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"

    url = f"http://mdx.example.com/entities/{parse.quote_plus(MetaDataMDX.sha1_entity_transform(entity_id))}"
    responses.add(responses.GET, url, body=TEST_METADATA_STRING, status=200, content_type=SAML_METADATA_CONTENT_TYPE)

    mdx = MetaDataMDX("http://mdx.example.com")
    sso_loc = mdx.service(entity_id, "idpsso_descriptor", "single_sign_on_service")
    assert (
        sso_loc[BINDING_HTTP_REDIRECT][0]["location"]
        == "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    )
    certs = mdx.certs(entity_id, "idpsso")
    assert len(certs) == 1


@patch("saml2.httpbase.requests.get")
def test_mdx_service_request_timeout(mock_request):
    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    url = f"http://mdx.example.com/entities/{MetaDataMDX.sha1_entity_transform(entity_id)}"

    mdx = MetaDataMDX("http://mdx.example.com", http_client_timeout=10)
    mdx.service(entity_id, "idpsso_descriptor", "single_sign_on_service")
    mock_request.assert_called_with(url, headers={"Accept": "application/samlmetadata+xml"}, timeout=10)


@responses.activate
def test_mdx_single_sign_on_service():
    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"

    url = f"http://mdx.example.com/entities/{parse.quote_plus(MetaDataMDX.sha1_entity_transform(entity_id))}"
    responses.add(responses.GET, url, body=TEST_METADATA_STRING, status=200, content_type=SAML_METADATA_CONTENT_TYPE)

    mdx = MetaDataMDX("http://mdx.example.com")
    sso_loc = mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert sso_loc[0]["location"] == "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"


@responses.activate
def test_mdx_metadata_freshness_period_not_expired():
    """Ensure that metadata is not refreshed if not expired."""

    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    url = f"http://mdx.example.com/entities/{parse.quote_plus(MetaDataMDX.sha1_entity_transform(entity_id))}"

    responses.add(
        responses.GET,
        url,
        body=TEST_METADATA_STRING,
        status=200,
        content_type=SAML_METADATA_CONTENT_TYPE,
    )

    mdx = MetaDataMDX("http://mdx.example.com", freshness_period="P0Y0M0DT0H2M0S")
    mdx._is_metadata_fresh = Mock(return_value=True)

    mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert entity_id in mdx.entity

    mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert len(responses.calls) == 1


@responses.activate
def test_mdx_metadata_freshness_period_expired():
    """Ensure that metadata is not refreshed if not expired."""

    entity_id = "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"
    url = f"http://mdx.example.com/entities/{parse.quote_plus(MetaDataMDX.sha1_entity_transform(entity_id))}"

    responses.add(
        responses.GET,
        url,
        body=TEST_METADATA_STRING,
        status=200,
        content_type=SAML_METADATA_CONTENT_TYPE,
    )

    mdx = MetaDataMDX("http://mdx.example.com", freshness_period="P0Y0M0DT0H2M0S")
    mdx._is_metadata_fresh = Mock(return_value=False)

    mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert entity_id in mdx.entity

    mdx.single_sign_on_service(entity_id, BINDING_HTTP_REDIRECT)
    assert len(responses.calls) == 2


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
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["9"])
    print(mds)
    assert len(mds) == 3  # Three sources
    assert len(mds.keys()) == 4  # number of idps


@patch("saml2.httpbase.requests.request")
def test_load_extern_incommon(mock_request):
    filepath = os.path.join(TESTS_DIR, "remote_data/InCommon-metadata-export.xml")
    with open(filepath) as fd:
        data = fd.read()
    mock_request.return_value.ok = True
    mock_request.return_value.status_code = 200
    mock_request.return_value.content = data

    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True, http_client_timeout=10)

    mds.imp(METADATACONF["10"])
    print(mds)
    assert mds
    assert len(mds.keys())
    mock_request.assert_called_with(
        "GET",
        "http://md.incommon.org/InCommon/InCommon-metadata-export.xml",
        allow_redirects=False,
        verify=False,
        timeout=10,
    )


def test_load_local():
    # string representation of XML idp definition
    with open(full_path("metadata.xml")) as fp:
        idp_metadata = fp.read()

    saml_config = Config()

    config_dict = {"metadata": {"inline": [idp_metadata]}}
    cfg = saml_config.load(config_dict)
    assert cfg


@patch("saml2.httpbase.requests.request")
def test_load_remote_encoding(mock_request):
    filepath = os.path.join(TESTS_DIR, "remote_data/metadata.aaitest.xml")
    with open(filepath) as fd:
        data = fd.read()
    mock_request.return_value.ok = True
    mock_request.return_value.status_code = 200
    mock_request.return_value.content = data

    crypto = sigver._get_xmlsec_cryptobackend()
    sc = sigver.SecurityContext(crypto, key_type="", cert_type="")
    url = "http://metadata.aai.switch.ch/metadata.aaitest.xml"
    httpc = HTTPBase(http_client_timeout=10)
    mds = MetaDataExtern(ATTRCONV, url, sc, full_path("SWITCHaaiRootCA.crt.pem"), httpc)
    mds.load()

    mock_request.assert_called_with("GET", url, allow_redirects=False, verify=True, timeout=10)


def test_load_string():
    sec_config.xmlsec_binary = sigver.get_xmlsec_binary(["/opt/local/bin"])
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)

    mds.imp(METADATACONF["11"])
    # print(mds)
    assert len(mds.keys()) == 1
    idps = mds.with_descriptor("idpsso")

    assert list(idps.keys()) == ["http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php"]
    certs = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso", "signing")
    assert len(certs) == 1


def test_get_certs_from_metadata():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["11"])

    cert_any_name, cert_any = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "any")[0]
    cert_idpsso_name, cert_idpsso = mds.certs(
        "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso"
    )[0]

    assert cert_any_name is None
    assert cert_idpsso_name is None


def test_get_unnamed_certs_from_metadata():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["11"])

    cert_any_name, cert_any = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "any")[0]
    cert_idpsso_name, cert_idpsso = mds.certs(
        "http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso"
    )[0]

    assert cert_any_name is None
    assert cert_idpsso_name is None


def test_get_named_certs_from_metadata():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["3"])

    cert_sign_name, cert_sign = mds.certs("https://coip-test.sunet.se/shibboleth", "spsso", "signing")[0]
    cert_enc_name, cert_enc = mds.certs("https://coip-test.sunet.se/shibboleth", "spsso", "encryption")[0]

    assert cert_sign_name == cert_enc_name == "coip-test.sunet.se"


def test_get_certs_from_metadata_without_keydescriptor():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(
        [
            {
                "class": "saml2.mdstore.InMemoryMetaData",
                "metadata": [
                    (
                        """
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
</EntitiesDescriptor>""",
                    )
                ],
            }
        ]
    )
    certs = mds.certs("http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php", "idpsso")

    assert len(certs) == 0


def test_metadata_extension_algsupport():
    mds = MetadataStore(ATTRCONV, None)
    mds.imp(METADATACONF["12"])
    mdf = mds.metadata[full_path("uu.xml")]
    assert mds


def test_supported_algorithms():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["11"])
    algs = mds.supported_algorithms(entity_id="http://xenosmilus.umdc.umu.se/simplesaml/saml2/idp/metadata.php")
    assert "http://www.w3.org/2001/04/xmlenc#sha256" in algs["digest_methods"]
    assert "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256" in algs["signing_methods"]


def test_registration_info():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["13"])
    registration_info = mds.registration_info(entity_id="https://aai-idp.unibe.ch/idp/shibboleth")
    assert "http://rr.aai.switch.ch/" == registration_info["registration_authority"]
    assert "2013-06-15T18:15:03Z" == registration_info["registration_instant"]
    assert (
        "https://www.switch.ch/aai/federation/switchaai/metadata-registration-practice-statement-20110711.txt"
        == registration_info["registration_policy"]["en"]
    )


def test_registration_info_no_policy():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["13"])
    registration_info = mds.registration_info(entity_id="https://idp.szie.hu/idp/shibboleth")
    assert "http://eduid.hu" == registration_info["registration_authority"]
    assert registration_info["registration_instant"] is None
    assert registration_info["registration_policy"] == {}


def test_subject_id_requirement():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["17"])
    required_subject_id = mds.subject_id_requirement(entity_id="https://esi-coco.example.edu/saml2/metadata/")
    expected = [
        {
            "__class__": "urn:oasis:names:tc:SAML:2.0:metadata&RequestedAttribute",
            "name": "urn:oasis:names:tc:SAML:attribute:pairwise-id",
            "name_format": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            "friendly_name": "pairwise-id",
            "is_required": "true",
        },
        {
            "__class__": "urn:oasis:names:tc:SAML:2.0:metadata&RequestedAttribute",
            "name": "urn:oasis:names:tc:SAML:attribute:subject-id",
            "name_format": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
            "friendly_name": "subject-id",
            "is_required": "true",
        },
    ]
    assert required_subject_id
    assert all(e in expected for e in required_subject_id)


def test_extension():
    mds = MetadataStore(ATTRCONV, None)
    # use ordered dict to force expected entity to be last
    metadata = OrderedDict()
    metadata["1"] = {"entity1": {}}
    metadata["2"] = {
        "entity2": {"idpsso_descriptor": [{"extensions": {"extension_elements": [{"__class__": "test"}]}}]}
    }
    mds.metadata = metadata
    assert mds.extension("entity2", "idpsso_descriptor", "test")


def test_shibmd_scope_no_regex_no_descriptor_type():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["15"])

    scopes = mds.shibmd_scopes(entity_id="http://example.com/saml2/idp.xml")
    all_scopes = list(scopes)

    expected = [
        {
            "regexp": False,
            "text": "descriptor-example.org",
        },
        {
            "regexp": True,
            "text": regex_compile(r"descriptor-example[^0-9]*\.org"),
        },
    ]
    assert len(all_scopes) == 2
    assert all_scopes == expected


def test_shibmd_scope_no_regex_all_descriptors():
    mds = MetadataStore(ATTRCONV, sec_config, disable_ssl_certificate_validation=True)
    mds.imp(METADATACONF["15"])

    scopes = mds.shibmd_scopes(entity_id="http://example.com/saml2/idp.xml", typ="idpsso_descriptor")
    all_scopes = list(scopes)
    expected = [
        {
            "regexp": False,
            "text": "descriptor-example.org",
        },
        {
            "regexp": True,
            "text": regex_compile(r"descriptor-example[^0-9]*\.org"),
        },
        {
            "regexp": False,
            "text": "idpssodescriptor-example.org",
        },
    ]
    assert len(all_scopes) == 3
    assert all_scopes == expected


if __name__ == "__main__":
    test_metadata_extension_algsupport()
