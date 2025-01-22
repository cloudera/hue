from contextlib import closing

from saml2.client import Saml2Client
from saml2.saml import AuthnContextClassRef
from saml2.server import Server


def test_authn_request_with_acs_by_index():
    # ACS index and location from SP metadata in servera.xml.
    ACS_INDEX = "4"
    ACS_LOCATION = "http://lingon.catalogix.se:8087/another/path"

    # Create SP using the configuration found in servera_conf.py.
    sp = Saml2Client(config_file="servera_conf")

    # Generate an authn request object that uses AssertionConsumerServiceIndex
    # instead of AssertionConsumerServiceURL. The index with label ACS_INDEX
    # exists in the SP metadata in servera.xml.
    request_id, authn_request = sp.create_authn_request(sp.config.entityid, assertion_consumer_service_index=ACS_INDEX)

    assert authn_request.requested_authn_context.authn_context_class_ref == [
        AuthnContextClassRef(accr)
        for accr in sp.config.getattr("requested_authn_context").get("authn_context_class_ref")
    ]
    assert authn_request.requested_authn_context.comparison == (
        sp.config.getattr("requested_authn_context").get("comparison")
    )

    # Make sure the authn_request contains AssertionConsumerServiceIndex.
    acs_index = getattr(authn_request, "assertion_consumer_service_index", None)
    assert acs_index == ACS_INDEX

    # Create IdP.
    with closing(Server(config_file="idp_all_conf")) as idp:
        # Ask the IdP to pick out the binding and destination from the
        # authn_request.
        binding, destination = idp.pick_binding("assertion_consumer_service", request=authn_request)

        # Make sure the IdP pick_binding method picks the correct location
        # or destination based on the ACS index in the authn request.
        assert destination == ACS_LOCATION
