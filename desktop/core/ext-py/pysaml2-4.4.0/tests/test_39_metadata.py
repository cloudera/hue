import copy
from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from saml2.saml import NAME_FORMAT_URI, NAME_FORMAT_BASIC

__author__ = 'roland'

sp_conf = {
    "entityid": "urn:mace:umu.se:saml:roland:sp",
    "name": "Rolands SP",
    "service": {
        "sp": {
            "endpoints": {
                "assertion_consumer_service": [
                    "http://lingon.catalogix.se:8087/"],
            },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": {
                "": "https://example.com/saml2/idp/SSOService.php",
            },
            "authn_requests_signed": True,
            "logout_requests_signed": True,
        }
    },
}


def test_requested_attribute_name_format():
    cnf = SPConfig().load(sp_conf, metadata_construction=True)
    ed = entity_descriptor(cnf)

    assert len(ed.spsso_descriptor.attribute_consuming_service) == 1
    acs = ed.spsso_descriptor.attribute_consuming_service[0]
    assert len(acs.requested_attribute) == 4
    for req_attr in acs.requested_attribute:
        assert req_attr.name_format == NAME_FORMAT_URI

    sp2 = copy.copy(sp_conf)
    sp2["service"]["sp"]["requested_attribute_name_format"] = NAME_FORMAT_BASIC

    cnf2 = SPConfig().load(sp2, metadata_construction=True)
    ed = entity_descriptor(cnf2)
    acs = ed.spsso_descriptor.attribute_consuming_service[0]
    assert len(acs.requested_attribute) == 4
    for req_attr in acs.requested_attribute:
        assert req_attr.name_format == NAME_FORMAT_BASIC


if __name__ == '__main__':
    test_requested_attribute_name_format()