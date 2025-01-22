from contextlib import closing
import sys

from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.server import Server


if sys.version_info.major < 3:
    from HTMLParser import HTMLParser
else:
    from html.parser import HTMLParser

# Typical RelayState used by Shibboleth SP.
SHIB_SP_RELAY_STATE = """\
ss:mem:ab1e6a31f3bd040ffd1d64a2d0e15d61ce517f5e1a94a41ea4fae32cc8d70a04"""


class RelayStateHTMLParser(HTMLParser):
    """Class used to parse HTML from a HTTP-POST binding response
    and determine if the HTML includes the expected relay state."""

    def __init__(self, expected_relay_state):
        super().__init__()

        self.expected_relay_state = expected_relay_state
        self.expected_relay_state_found = False
        self.input_relay_state_element_found = False

    def handle_starttag(self, tag, attrs):
        """If the <input> tag is found and it includes the correct value
        for the relay state set the relay state found flag to true."""
        if tag == "input":
            if ("name", "RelayState") in attrs:
                self.input_relay_state_found = True
                if ("value", self.expected_relay_state) in attrs:
                    self.expected_relay_state_found = True


def test_relay_state():
    # Identity information about a mock user.
    identity = {
        "eduPersonEntitlement": "Short stop",
        "surName": "Jeter",
        "givenName": "Derek",
        "mail": "derek.jeter@nyy.mlb.com",
        "title": "The man",
    }

    # Create a service provider using the servera_conf.py configuration.
    sp = Saml2Client(config_file="servera_conf")

    # Create an identity providver using the idp_all_conf.py configuration.
    with closing(Server(config_file="idp_all_conf")) as idp:
        # Create a response to an authentication request as if
        # it came from the SP.

        name_id = idp.ident.transient_nameid(sp.config.entityid, "id12")
        binding, destination = idp.pick_binding(
            "assertion_consumer_service", bindings=[BINDING_HTTP_POST], entity_id=sp.config.entityid
        )
        resp = idp.create_authn_response(identity, "id-123456789", destination, sp.config.entityid, name_id=name_id)

        # Apply the HTTP_POST binding to the response with a relay state
        # typical from a Shibboleth SP to create the HTML that carries
        # the SAML response.
        relay_state = SHIB_SP_RELAY_STATE
        html = idp.apply_binding(BINDING_HTTP_POST, f"{resp}", destination, relay_state)["data"]

        # Parse the HTML and verify that it contains the correct relay state.
        parser = RelayStateHTMLParser(relay_state)
        parser.feed(html)
        assert parser.expected_relay_state_found

        # Apply the HTTP_POST binding to the response with relay state None.
        relay_state = None
        html = idp.apply_binding(BINDING_HTTP_POST, f"{resp}", destination, relay_state)["data"]

        # Parse the HTML and verify that it does not contain a relay state.
        parser = RelayStateHTMLParser(relay_state)
        parser.feed(html)
        assert not parser.input_relay_state_element_found

        # Apply the HTTP_POST binding to the response with empty
        # string relay state.
        relay_state = ""
        html = idp.apply_binding(BINDING_HTTP_POST, f"{resp}", destination, relay_state)["data"]

        # Parse the HTML and verify that it does not contain a relay state.
        parser = RelayStateHTMLParser(relay_state)
        parser.feed(html)
        assert not parser.input_relay_state_element_found


if __name__ == "__main__":
    test_relay_state()
