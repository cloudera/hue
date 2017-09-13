from contextlib import closing
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import pytest
from saml2 import BINDING_HTTP_POST
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2.client import Saml2Client
from saml2.server import Server
from saml2.mongo_store import EptidMDB

__author__ = 'rolandh'


AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def _eq(l1, l2):
    return set(l1) == set(l2)


@pytest.mark.mongo
def test_flow():
    sp = Saml2Client(config_file="servera_conf")
    try:
        with closing(Server(config_file="idp_conf_mdb")) as idp1:
            with closing(Server(config_file="idp_conf_mdb")) as idp2:
                # clean out database
                idp1.ident.mdb.db.drop()

                # -- dummy request ---
                req_id, orig_req = sp.create_authn_request(idp1.config.entityid)

                # == Create an AuthnRequest response

                rinfo = idp1.response_args(orig_req, [BINDING_HTTP_POST])

                #name_id = idp1.ident.transient_nameid("id12", rinfo["sp_entity_id"])
                resp = idp1.create_authn_response(
                    {
                        "eduPersonEntitlement": "Short stop",
                        "surName": "Jeter",
                        "givenName": "Derek",
                        "mail": "derek.jeter@nyy.mlb.com",
                        "title": "The man"},
                    userid="jeter",
                    authn=AUTHN,
                    **rinfo)

                # What's stored away is the assertion
                a_info = idp2.session_db.get_assertion(resp.assertion.id)
                # Make sure what I got back from MongoDB is the same as I put in
                assert a_info["assertion"] == resp.assertion

                # By subject
                nid = resp.assertion.subject.name_id
                _assertion = idp2.session_db.get_assertions_by_subject(nid)
                assert len(_assertion) == 1
                assert _assertion[0] == resp.assertion

                nids = idp2.ident.find_nameid("jeter")
                assert len(nids) == 1
    except ConnectionFailure:
        pass


@pytest.mark.mongo
def test_eptid_mongo_db():
    try:
        edb = EptidMDB("secret", "idp")
    except ConnectionFailure:
        pass
    else:
        try:
            e1 = edb.get("idp_entity_id", "sp_entity_id", "user_id",
                         "some other data")
        except ServerSelectionTimeoutError:
            pass
        else:
            print(e1)
            assert e1.startswith("idp_entity_id!sp_entity_id!")
            e2 = edb.get("idp_entity_id", "sp_entity_id", "user_id",
                         "some other data")
            assert e1 == e2

            e3 = edb.get("idp_entity_id", "sp_entity_id", "user_2",
                         "some other data")
            print(e3)
            assert e1 != e3

            e4 = edb.get("idp_entity_id", "sp_entity_id2", "user_id",
                         "some other data")
            assert e4 != e1
            assert e4 != e3



if __name__ == "__main__":
    test_flow()
