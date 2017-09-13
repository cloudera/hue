from saml2.client import Saml2Client
from saml2.discovery import DiscoveryServer

from pathutils import dotname

__author__ = 'rolandh'


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_verify():
    ds = DiscoveryServer(config_file=dotname("disco_conf"))
    assert ds
    assert ds.verify_sp_in_metadata("urn:mace:example.com:saml:roland:sp")


def test_construct_0():
    sp = Saml2Client(config_file=dotname("servera_conf"))
    url = sp.create_discovery_service_request("http://example.com/saml/disco",
                                              "https://example.com/saml/sp.xml")

    assert url == "http://example.com/saml/disco?entityID=https%3A%2F%2Fexample.com%2Fsaml%2Fsp.xml"


def test_construct_1():
    sp = Saml2Client(config_file=dotname("servera_conf"))
    url = sp.create_discovery_service_request("http://example.com/saml/disco",
                                              "https://example.com/saml/sp.xml")

    assert url == "http://example.com/saml/disco?entityID=https%3A%2F%2Fexample.com%2Fsaml%2Fsp.xml"


def test_construct_deconstruct_request():
    sp = Saml2Client(config_file=dotname("servera_conf"))
    url = sp.create_discovery_service_request(
        "http://example.com/saml/disco",
        "https://example.com/saml/sp.xml",
        isPassive=True,
        returnIDParam="foo",
        return_url="https://example.com/saml/sp/disc")

    print(url)

    ds = DiscoveryServer(config_file=dotname("disco_conf"))
    dsr = ds.parse_discovery_service_request(url)
    # policy is added by the parsing and verifying method
    assert _eq(dsr.keys(), ["return", "entityID", "returnIDParam",
                            "isPassive", "policy"])


def test_construct_deconstruct_response():
    sp = Saml2Client(config_file=dotname("servera_conf"))
    url = sp.create_discovery_service_request("http://example.com/saml/disco",
                                              "https://example.com/saml/sp.xml",
                                              isPassive=True,
                                              returnIDParam="foo",
                                              return_url="https://example.com/saml/sp/disc")
    ds = DiscoveryServer(config_file=dotname("disco_conf"))
    dsr = ds.parse_discovery_service_request(url)
    args = dict([(key, dsr[key]) for key in ["returnIDParam", "return"]])
    url = ds.create_discovery_service_response(
        entity_id="https://example.com/saml/idp.xml",
        **args)

    idp_id = sp.parse_discovery_service_response(url, returnIDParam="foo")
    assert idp_id == "https://example.com/saml/idp.xml"


if __name__ == "__main__":
    test_verify()
