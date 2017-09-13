from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.client import Saml2Client
from saml2 import config, BINDING_HTTP_POST
from saml2 import saml
from saml2 import samlp

__author__ = 'roland'


def test_nsprefix():
    status_message = samlp.StatusMessage()
    status_message.text = "OK"

    txt = "%s" % status_message

    assert "ns0:StatusMessage" in txt

    status_message.register_prefix({"saml2": saml.NAMESPACE,
                                    "saml2p": samlp.NAMESPACE})

    txt = "%s" % status_message

    assert "saml2p:StatusMessage" in txt


def test_nsprefix2():
    conf = config.SPConfig()
    conf.load_file("servera_conf")
    client = Saml2Client(conf)

    selected_idp = "urn:mace:example.com:saml:roland:idp"

    destination = client._sso_location(selected_idp, BINDING_HTTP_POST)

    reqid, req = client.create_authn_request(
        destination, nameid_format=NAMEID_FORMAT_TRANSIENT,
        nsprefix={"saml2": saml.NAMESPACE, "saml2p": samlp.NAMESPACE})

    txt = "%s" % req

    assert "saml2p:AuthnRequest" in txt
    assert "saml2:Issuer" in txt

if __name__ == "__main__":
    test_nsprefix2()