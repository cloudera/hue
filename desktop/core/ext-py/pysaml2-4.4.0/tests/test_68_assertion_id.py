from contextlib import closing
from six.moves.urllib.parse import parse_qs
from six.moves.urllib.parse import urlparse
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.samlp import AuthnRequest
from saml2.samlp import NameIDPolicy
from saml2.saml import Assertion
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_URI
from saml2 import BINDING_SOAP
from saml2.client import Saml2Client
from saml2.server import Server

__author__ = 'rolandh'

TAG1 = "name=\"SAMLRequest\" value="


AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def get_msg(hinfo, binding, response=False):
    if binding == BINDING_SOAP:
        msg = hinfo["data"]
    elif binding == BINDING_HTTP_POST:
        _inp = hinfo["data"][3]
        i = _inp.find(TAG1)
        i += len(TAG1) + 1
        j = _inp.find('"', i)
        msg = _inp[i:j]
    elif binding == BINDING_URI:
        if response:
            msg = hinfo["data"]
        else:
            msg = ""
            return parse_qs(hinfo["url"].split("?")[1])["ID"][0]
    else:  # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        msg = parse_qs(parts.query)["SAMLRequest"][0]

    return msg


def test_basic_flow():
    sp = Saml2Client(config_file="servera_conf")
    with closing(Server(config_file="idp_all_conf")) as idp:
        # -------- @IDP -------------

        relay_state = "FOO"
        # -- dummy request ---
        orig_req = AuthnRequest(
            issuer=sp._issuer(), name_id_policy=NameIDPolicy(
                allow_create="true", format=NAMEID_FORMAT_TRANSIENT))

        # == Create an AuthnRequest response

        name_id = idp.ident.transient_nameid("id12", sp.config.entityid)

        binding, destination = idp.pick_binding("assertion_consumer_service",
                                                entity_id=sp.config.entityid)
        resp = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                          "surName": "Jeter",
                                          "givenName": "Derek",
                                          "mail": "derek.jeter@nyy.mlb.com",
                                          "title": "The man"},
                                         "id-123456789",
                                         destination,
                                         sp.config.entityid,
                                         name_id=name_id,
                                         authn=AUTHN)

        hinfo = idp.apply_binding(binding, "%s" % resp, destination, relay_state)

        # --------- @SP -------------

        xmlstr = get_msg(hinfo, binding)

        aresp = sp.parse_authn_request_response(xmlstr, binding,
                                                {resp.in_response_to: "/"})

        # == Look for assertion X

        asid = aresp.assertion.id

        binding, destination = sp.pick_binding("assertion_id_request_service",
                                               entity_id=idp.config.entityid)

        hinfo = sp.apply_binding(binding, asid, destination)

        # ---------- @IDP ------------

        aid = get_msg(hinfo, binding, response=False)

        # == construct response

        resp = idp.create_assertion_id_request_response(aid)

        hinfo = idp.apply_binding(binding, "%s" % resp, None, "", response=True)

        # ----------- @SP -------------

        xmlstr = get_msg(hinfo, binding, response=True)

        final = sp.parse_assertion_id_request_response(xmlstr, binding)

        print(final.response)
        assert isinstance(final.response, Assertion)
