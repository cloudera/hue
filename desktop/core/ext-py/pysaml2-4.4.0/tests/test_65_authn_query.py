from contextlib import closing
from six.moves.urllib.parse import urlparse, parse_qs
from saml2 import BINDING_SOAP, BINDING_HTTP_POST

__author__ = 'rolandh'

from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.authn_context import requested_authn_context
from saml2.samlp import AuthnRequest
from saml2.samlp import NameIDPolicy
from saml2.samlp import AuthnQuery
from saml2.client import Saml2Client
from saml2.saml import Subject
from saml2.saml import NameID
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.server import Server

TAG1 = "name=\"SAMLRequest\" value="


AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def get_msg(hinfo, binding):
    if binding == BINDING_SOAP:
        xmlstr = hinfo["data"]
    elif binding == BINDING_HTTP_POST:
        _inp = hinfo["data"][3]
        i = _inp.find(TAG1)
        i += len(TAG1) + 1
        j = _inp.find('"', i)
        xmlstr = _inp[i:j]
    else:  # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        xmlstr = parse_qs(parts.query)["SAMLRequest"][0]

    return xmlstr

# ------------------------------------------------------------------------


def test_basic():
    sp = Saml2Client(config_file="servera_conf")
    with closing(Server(config_file="idp_all_conf")) as idp:
        srvs = sp.metadata.authn_query_service(idp.config.entityid)

        destination = srvs[0]["location"]
        authn_context = requested_authn_context(INTERNETPROTOCOLPASSWORD)

        subject = Subject(text="abc",
                          name_id=NameID(format=NAMEID_FORMAT_TRANSIENT))

        _id, aq = sp.create_authn_query(subject, destination, authn_context)

        print(aq)

        assert isinstance(aq, AuthnQuery)


def test_flow():
    sp = Saml2Client(config_file="servera_conf")

    with closing(Server(config_file="idp_all_conf")) as idp:
        relay_state = "FOO"
        # -- dummy request ---
        orig_req = AuthnRequest(
            issuer=sp._issuer(),
            name_id_policy=NameIDPolicy(allow_create="true",
                                        format=NAMEID_FORMAT_TRANSIENT))

        # == Create an AuthnRequest response

        name_id = idp.ident.transient_nameid(sp.config.entityid, "id12")
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

        # ------- @SP ----------

        xmlstr = get_msg(hinfo, binding)
        aresp = sp.parse_authn_request_response(xmlstr, binding,
                                                {resp.in_response_to: "/"})

        binding, destination = sp.pick_binding("authn_query_service",
                                               entity_id=idp.config.entityid)

        authn_context = requested_authn_context(INTERNETPROTOCOLPASSWORD)

        subject = aresp.assertion.subject

        aq_id, aq = sp.create_authn_query(subject, destination, authn_context)

        print(aq)

        assert isinstance(aq, AuthnQuery)
        binding = BINDING_SOAP

        hinfo = sp.apply_binding(binding, "%s" % aq, destination, "state2")

        # -------- @IDP ----------

        xmlstr = get_msg(hinfo, binding)

        pm = idp.parse_authn_query(xmlstr, binding)

        msg = pm.message
        assert msg.id == aq.id

        p_res = idp.create_authn_query_response(msg.subject, msg.session_index,
                                                msg.requested_authn_context)

        print(p_res)

        hinfo = idp.apply_binding(binding, "%s" % p_res, "", "state2",
                                  response=True)

        # ------- @SP ----------

        xmlstr = get_msg(hinfo, binding)

        final = sp.parse_authn_query_response(xmlstr, binding)

        print(final)

        assert final.response.id == p_res.id

if __name__ == "__main__":
    test_flow()
