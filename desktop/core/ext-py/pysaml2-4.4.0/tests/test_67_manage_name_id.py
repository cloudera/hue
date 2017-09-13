from contextlib import closing
from saml2 import BINDING_SOAP
from saml2.samlp import NewID
from saml2.saml import NameID, NAMEID_FORMAT_TRANSIENT
from saml2.client import Saml2Client
from saml2.server import Server

__author__ = 'rolandh'


def test_basic():
    sp = Saml2Client(config_file="servera_conf")
    with closing(Server(config_file="idp_all_conf")) as idp:
        # -------- @SP ------------
        binding, destination = sp.pick_binding("manage_name_id_service",
                                               entity_id=idp.config.entityid)

        nameid = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
        newid = NewID(text="Barfoo")

        mid, mreq = sp.create_manage_name_id_request(destination, name_id=nameid,
                                                     new_id=newid)

        print(mreq)
        rargs = sp.apply_binding(binding, "%s" % mreq, destination, "")

        # --------- @IDP --------------

        _req = idp.parse_manage_name_id_request(rargs["data"], binding)

        print(_req.message)

        assert mid == _req.message.id


def test_flow():
    sp = Saml2Client(config_file="servera_conf")
    with closing(Server(config_file="idp_all_conf")) as idp:
        binding, destination = sp.pick_binding("manage_name_id_service",
                                               entity_id=idp.config.entityid)

        nameid = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
        newid = NewID(text="Barfoo")

        mid, midq = sp.create_manage_name_id_request(destination, name_id=nameid,
                                                     new_id=newid)

        print(midq)
        rargs = sp.apply_binding(binding, "%s" % midq, destination, "")

        # --------- @IDP --------------

        _req = idp.parse_manage_name_id_request(rargs["data"], binding)

        print(_req.message)

        mnir = idp.create_manage_name_id_response(_req.message, [binding])

        if binding != BINDING_SOAP:
            binding, destination = idp.pick_binding("manage_name_id_service",
                                                    entity_id=sp.config.entityid)
        else:
            destination = ""

        respargs = idp.apply_binding(binding, "%s" % mnir, destination, "")

        print(respargs)

        # ---------- @SP ---------------

        _response = sp.parse_manage_name_id_request_response(respargs["data"],
                                                             binding)

        print(_response.response)

        assert _response.response.id == mnir.id


if __name__ == "__main__":
    test_flow()
