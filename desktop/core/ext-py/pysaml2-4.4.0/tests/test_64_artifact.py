import base64
from contextlib import closing
from hashlib import sha1
from six.moves.urllib.parse import urlparse
from six.moves.urllib.parse import parse_qs
from saml2 import BINDING_HTTP_ARTIFACT
from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_POST
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.client import Saml2Client

from saml2.entity import create_artifact
from saml2.entity import ARTIFACT_TYPECODE
from saml2.s_utils import sid
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
    elif binding == BINDING_HTTP_ARTIFACT:
        # either by POST or by redirect
        if hinfo["data"]:
            _inp = hinfo["data"][3]
            i = _inp.find(TAG1)
            i += len(TAG1) + 1
            j = _inp.find('"', i)
            msg = _inp[i:j]
        else:
            parts = urlparse(hinfo["url"])
            msg = parse_qs(parts.query)["SAMLart"][0]
    else: # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        msg = parse_qs(parts.query)["SAMLRequest"][0]

    return msg


def test_create_artifact():
    b64art = create_artifact("http://sp.example.com/saml.xml",
                             b"aabbccddeeffgghhiijj")

    art = base64.b64decode(b64art.encode('ascii'))

    assert art[:2] == ARTIFACT_TYPECODE
    assert int(art[2:4]) == 0

    s = sha1(b"http://sp.example.com/saml.xml")
    assert art[4:24] == s.digest()

SP = 'urn:mace:example.com:saml:roland:sp'


def test_create_artifact_resolve():
    b64art = create_artifact(SP, "aabbccddeeffgghhiijj", 1)
    artifact = base64.b64decode(b64art)

    #assert artifact[:2] == '\x00\x04'
    #assert int(artifact[2:4]) == 0
    #
    s = sha1(SP.encode('ascii'))
    assert artifact[4:24] == s.digest()

    with closing(Server(config_file="idp_all_conf")) as idp:
        typecode = artifact[:2]
        assert typecode == ARTIFACT_TYPECODE

        destination = idp.artifact2destination(b64art, "spsso")

        msg_id, msg = idp.create_artifact_resolve(b64art, destination, sid())

        print(msg)

        args = idp.use_soap(msg, destination, None, False)

        sp = Saml2Client(config_file="servera_conf")

        ar = sp.parse_artifact_resolve(args["data"])

        print(ar)

        assert ar.artifact.text == b64art


def test_artifact_flow():
    #SP = 'urn:mace:example.com:saml:roland:sp'
    sp = Saml2Client(config_file="servera_conf")

    with closing(Server(config_file="idp_all_conf")) as idp:
        # original request

        binding, destination = sp.pick_binding("single_sign_on_service",
                                               entity_id=idp.config.entityid)
        relay_state = "RS0"
        req_id, req = sp.create_authn_request(destination, id="id1")

        artifact = sp.use_artifact(req, 1)

        binding, destination = sp.pick_binding("single_sign_on_service",
                                               [BINDING_HTTP_ARTIFACT],
                                               entity_id=idp.config.entityid)

        hinfo = sp.apply_binding(binding, artifact, destination, relay_state)

        # ========== @IDP ============

        artifact2 = get_msg(hinfo, binding)

        assert artifact == artifact2

        # The IDP now wants to replace the artifact with the real request

        destination = idp.artifact2destination(artifact2, "spsso")

        msg_id, msg = idp.create_artifact_resolve(artifact2, destination, sid())

        hinfo = idp.use_soap(msg, destination, None, False)

        # ======== @SP ==========

        msg = get_msg(hinfo, BINDING_SOAP)

        ar = sp.parse_artifact_resolve(msg)

        assert ar.artifact.text == artifact

        # The SP picks the request out of the repository with the artifact as the key
        oreq = sp.artifact[ar.artifact.text]
        # Should be the same as req above

        # Returns the information over the existing SOAP connection so
        # no transport information needed

        msg = sp.create_artifact_response(ar, ar.artifact.text)
        hinfo = sp.use_soap(msg, destination)

        # ========== @IDP ============

        msg = get_msg(hinfo, BINDING_SOAP)

        # The IDP untangles the request from the artifact resolve response
        spreq = idp.parse_artifact_resolve_response(msg)

        # should be the same as req above

        assert spreq.id == req.id

        # That was one way, the Request from the SP
        # ---------------------------------------------#
        # Now for the other, the response from the IDP

        name_id = idp.ident.transient_nameid(sp.config.entityid, "derek")

        resp_args = idp.response_args(spreq, [BINDING_HTTP_POST])

        response = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                              "surName": "Jeter", "givenName": "Derek",
                                              "mail": "derek.jeter@nyy.mlb.com",
                                              "title": "The man"},
                                             name_id=name_id,
                                             authn=AUTHN,
                                             **resp_args)

        print(response)

        # with the response in hand create an artifact

        artifact = idp.use_artifact(response, 1)

        binding, destination = sp.pick_binding("single_sign_on_service",
                                               [BINDING_HTTP_ARTIFACT],
                                               entity_id=idp.config.entityid)

        hinfo = sp.apply_binding(binding, "%s" % artifact, destination, relay_state,
                                 response=True)

        # ========== SP =========

        artifact3 = get_msg(hinfo, binding)

        assert artifact == artifact3

        destination = sp.artifact2destination(artifact3, "idpsso")

        # Got an artifact want to replace it with the real message
        msg_id, msg = sp.create_artifact_resolve(artifact3, destination, sid())

        print(msg)

        hinfo = sp.use_soap(msg, destination, None, False)

        # ======== IDP ==========

        msg = get_msg(hinfo, BINDING_SOAP)

        ar = idp.parse_artifact_resolve(msg)

        print(ar)

        assert ar.artifact.text == artifact3

        # The IDP retrieves the response from the database using the artifact as the key
        #oreq = idp.artifact[ar.artifact.text]

        binding, destination = idp.pick_binding("artifact_resolution_service",
                                                entity_id=sp.config.entityid)

        resp = idp.create_artifact_response(ar, ar.artifact.text)
        hinfo = idp.use_soap(resp, destination)

        # ========== SP ============

        msg = get_msg(hinfo, BINDING_SOAP)
        sp_resp = sp.parse_artifact_resolve_response(msg)

        assert sp_resp.id == response.id
