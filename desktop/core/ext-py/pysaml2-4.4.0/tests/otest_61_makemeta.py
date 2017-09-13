import saml2
from saml2 import mdstore
from saml2 import md
from saml2 import BINDING_HTTP_POST
from saml2 import extension_elements_to_elements

from saml2.extension import shibmd
from saml2.extension import mdui
from saml2.extension import idpdisc

from saml2.attribute_converter import ac_factory
from saml2.saml import NAME_FORMAT_URI
from saml2.config import SPConfig, IdPConfig

def _eq(l1,l2):
    return set(l1) == set(l2)

SP = {
    "name" : "Rolands SP",
    "description": "One of the best SPs in business",
    "service": {
        "sp": {
            "endpoints": {
                "single_logout_service" : ["http://localhost:8087/logout"],
                "assertion_consumer_service" : [{"location":"http://localhost:8087/",
                                                "binding":BINDING_HTTP_POST},]
            },
            "required_attributes": ["sn", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": {
                "" : "https://example.com/saml2/idp/SSOService.php",
            },
        }
    },
    "metadata": {
        "local": ["foo.xml"],
    },
    "attribute_map_dir" : "attributemaps",
}

IDP = {
    "name" : "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service" : ["http://localhost:8088/sso"],
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "nameid_format": "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
                }
            },
            "scope": ["example.org"],
            "ui_info": {
                "privacy_statement_url":
                            "http://example.com/saml2/privacyStatement.html",
                "information_url": "http://example.com/saml2/info.html",
                "logo": {
                    "height": "40",
                    "width" : "30",
                    "text": "http://example.com/logo.jpg"
                },
                "display_name": "Example Co.",
                "description" : {"text":"Exempel bolag","lang":"se"},
                "keywords": {"lang":"en", "text":["foo", "bar"]}
            },
        }
    },
    "metadata": {
        "local": ["bar.xml"],
    },
}

def test_org_1():
    desc = {
        "name": [("Example Company","en"), ("Exempel AB","se"), "Example",],
        "display_name": ["Example AS", ("Voorbeeld AZ", "")],
        "url": [("http://example.com","en")],
    }
    org = metadata.do_organization_info(desc)
    print(org)
    assert isinstance(org, md.Organization)
    print(org.keyswv())
    assert _eq(org.keyswv(), ['organization_name',
                'organization_display_name','organization_url'])
    assert len(org.organization_name) == 3
    assert len(org.organization_display_name) == 2
    assert len(org.organization_url) == 1

def test_org_2():
    desc = {
        "name": [("Example Company","en"), ("Exempel AB","se"), "Example",],
        "display_name": "Example AS",
        "url": ("http://example.com","en"),
    }
    org = metadata.do_organization_info(desc)
    print(org)
    assert _eq(org.keyswv(), ['organization_name',
                'organization_display_name','organization_url'])
    assert len(org.organization_name) == 3
    assert len(org.organization_display_name) == 1
    assert org.organization_display_name[0].text == 'Example AS'
    assert len(org.organization_url) == 1
    assert isinstance(org.organization_url[0], md.OrganizationURL)
    assert org.organization_url[0].lang == "en"
    assert org.organization_url[0].text == 'http://example.com'

def test_org_3():
    desc = { "display_name": ["Rolands SAML"] }
    org = metadata.do_organization_info(desc)
    assert _eq(org.keyswv(), ['organization_display_name'])
    assert len(org.organization_display_name) == 1
                                                
def test_contact_0():
    conf = [{
        "given_name":"Roland",
        "sur_name": "Hedberg",
        "telephone_number": "+46 70 100 00 00",
        "email_address": ["foo@eample.com", "foo@example.org"],
        "contact_type": "technical"
        }]
    contact_person = metadata.do_contact_person_info(conf)
    assert _eq(contact_person[0].keyswv(), ['given_name', 'sur_name', 
                                            'contact_type', 'telephone_number',
                                            "email_address"])
    print(contact_person[0])
    person = contact_person[0]
    assert person.contact_type == "technical"
    assert isinstance(person.given_name, md.GivenName)
    assert person.given_name.text == "Roland"
    assert isinstance(person.sur_name, md.SurName)
    assert person.sur_name.text == "Hedberg"
    assert isinstance(person.telephone_number[0], md.TelephoneNumber)
    assert person.telephone_number[0].text == "+46 70 100 00 00"
    assert len(person.email_address) == 2
    assert isinstance(person.email_address[0], md.EmailAddress)
    assert person.email_address[0].text == "foo@eample.com"
    
def test_do_endpoints():
    eps = metadata.do_endpoints(SP["service"]["sp"]["endpoints"],
                                    metadata.ENDPOINTS["sp"])
    print(eps)
    assert _eq(eps.keys(), ["assertion_consumer_service", 
                            "single_logout_service"])
                            
    assert len(eps["single_logout_service"]) == 1
    sls = eps["single_logout_service"][0]
    assert sls.location == "http://localhost:8087/logout"
    assert sls.binding == BINDING_HTTP_POST
    
    assert len(eps["assertion_consumer_service"]) == 1
    acs = eps["assertion_consumer_service"][0]
    assert acs.location == "http://localhost:8087/"
    assert acs.binding == BINDING_HTTP_POST
    
    assert "artifact_resolution_service" not in eps
    assert "manage_name_id_service" not in eps
    
def test_required_attributes():
    attrconverters = ac_factory("../tests/attributemaps")
    ras = metadata.do_requested_attribute(
                                SP["service"]["sp"]["required_attributes"],
                                attrconverters, is_required="true")
    assert len(ras) == len(SP["service"]["sp"]["required_attributes"])
    print(ras[0])
    assert ras[0].name == 'urn:oid:2.5.4.4'
    assert ras[0].name_format == NAME_FORMAT_URI
    assert ras[0].is_required == "true"

def test_optional_attributes():
    attrconverters = ac_factory("../tests/attributemaps")
    ras = metadata.do_requested_attribute(
                                SP["service"]["sp"]["optional_attributes"],
                                attrconverters)
    assert len(ras) == len(SP["service"]["sp"]["optional_attributes"])
    print(ras[0])
    assert ras[0].name == 'urn:oid:2.5.4.12'
    assert ras[0].name_format == NAME_FORMAT_URI
    assert ras[0].is_required == "false"
    
def test_do_sp_sso_descriptor():
    conf = SPConfig().load(SP, metadata_construction=True)
    spsso = metadata.do_spsso_descriptor(conf)
    
    assert isinstance(spsso, md.SPSSODescriptor)
    assert _eq(spsso.keyswv(), ['authn_requests_signed', 
                                'attribute_consuming_service', 
                                'single_logout_service', 
                                'protocol_support_enumeration', 
                                'assertion_consumer_service', 
                                'want_assertions_signed'])
                                
    assert spsso.authn_requests_signed == "false"
    assert spsso.want_assertions_signed == "true"
    assert len (spsso.attribute_consuming_service) == 1
    acs = spsso.attribute_consuming_service[0]
    print(acs.keyswv())
    assert _eq(acs.keyswv(), ['requested_attribute', 'service_name',
                                 'service_description', 'index'])
    assert acs.service_name[0].text == SP["name"]
    assert acs.service_description[0].text == SP["description"]
    assert len(acs.requested_attribute) == 4
    assert acs.requested_attribute[0].friendly_name == "sn"
    assert acs.requested_attribute[0].name == 'urn:oid:2.5.4.4'
    assert acs.requested_attribute[0].name_format == NAME_FORMAT_URI
    assert acs.requested_attribute[0].is_required == "true"

def test_do_sp_sso_descriptor_2():
    SP["service"]["sp"]["discovery_response"] = "http://example.com/sp/ds"
    
    conf = SPConfig().load(SP, metadata_construction=True)
    spsso = metadata.do_spsso_descriptor(conf)

    assert isinstance(spsso, md.SPSSODescriptor)
    print(spsso.keyswv())
    assert _eq(spsso.keyswv(), ['authn_requests_signed',
                                'attribute_consuming_service',
                                'single_logout_service',
                                'protocol_support_enumeration',
                                'assertion_consumer_service',
                                'want_assertions_signed',
                                'extensions'])

    exts = spsso.extensions.extension_elements
    assert len(exts) == 1
    print(exts)
    idpd = saml2.extension_element_to_element(exts[0],
                                              idpdisc.ELEMENT_FROM_STRING,
                                              namespace=idpdisc.NAMESPACE)
    print(idpd)
    assert idpd.location == "http://example.com/sp/ds"
    assert idpd.index == "0"
    assert idpd.binding == "urn:oasis:names:tc:SAML:profiles:SSO:idp-discovery-protocol"

def test_entity_description():
    #confd = eval(open("../tests/server.config").read())
    confd = SPConfig().load_file("server_conf")
    print(confd.attribute_converters)
    entd = metadata.entity_descriptor(confd)
    assert entd is not None
    print(entd.keyswv())
    assert _eq(entd.keyswv(), ['valid_until', 'entity_id', 'contact_person',
                                'spsso_descriptor', 'organization'])
    print(entd)
    assert entd.entity_id == "urn:mace:example.com:saml:roland:sp"

def test_do_idp_sso_descriptor():
    conf = IdPConfig().load(IDP, metadata_construction=True)
    idpsso = metadata.do_idpsso_descriptor(conf)

    assert isinstance(idpsso, md.IDPSSODescriptor)
    assert _eq(idpsso.keyswv(), ['protocol_support_enumeration', 
                                'single_sign_on_service', 
                                'want_authn_requests_signed',
                                "extensions"])
    exts = idpsso.extensions.extension_elements
    assert len(exts) == 2
    print(exts)
    inst = saml2.extension_element_to_element(exts[0],
                                              shibmd.ELEMENT_FROM_STRING,
                                              namespace=shibmd.NAMESPACE)
    assert isinstance(inst, shibmd.Scope)
    assert inst.text == "example.org"
    assert inst.regexp == "false"

    uiinfo = saml2.extension_element_to_element(exts[1],
                                              mdui.ELEMENT_FROM_STRING,
                                              namespace=mdui.NAMESPACE)

    assert uiinfo
    assert _eq(uiinfo.keyswv(), ['display_name', 'description',
                                 'information_url', 'privacy_statement_url',
                                 'keywords', 'logo'])

    assert len(uiinfo.privacy_statement_url) == 1
    assert uiinfo.privacy_statement_url[0].text == "http://example.com/saml2/privacyStatement.html"
    assert len(uiinfo.description) == 1
    assert uiinfo.description[0].text == "Exempel bolag"
    assert uiinfo.description[0].lang == "se"

    res = extension_elements_to_elements(exts,[shibmd, mdui])

    assert len(res) == 2
    # one is a shibmd.Scope instance and the other a mdui.UIInfo instance
    if isinstance(res[0], shibmd.Scope):
        assert isinstance(res[1], mdui.UIInfo)
    elif isinstance(res[1], shibmd.Scope):
        assert isinstance(res[0], mdui.UIInfo)

    found = idpsso.extensions.find_extensions(mdui.UIInfo.c_tag,
                                              mdui.NAMESPACE)
    assert len(found) == 1

    elem = idpsso.extensions.extensions_as_elements(mdui.UIInfo.c_tag, mdui)
    assert len(elem) == 1
    assert isinstance(elem[0], mdui.UIInfo)

