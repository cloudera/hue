__author__ = 'rolandh'

from contextlib import closing
from saml2.client import Saml2Client
from saml2.saml import NameID, NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.server import Server
from saml2.samlp import NameIDPolicy
from saml2.samlp import NameIDMappingRequest


def test_base_request():
    sp = Saml2Client(config_file="servera_conf")

    with closing(Server(config_file="idp_all_conf")) as idp:
        binding, destination = sp.pick_binding("name_id_mapping_service",
                                               entity_id=idp.config.entityid)

        policy = NameIDPolicy(format=NAMEID_FORMAT_TRANSIENT,
                              sp_name_qualifier="urn:mace:swamid:junk",
                              allow_create="true")

        nameid = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")

        mid, nmr = sp.create_name_id_mapping_request(policy, nameid, destination)

        print(nmr)

        assert isinstance(nmr, NameIDMappingRequest)


def test_request_response():
    sp = Saml2Client(config_file="servera_conf")

    with closing(Server(config_file="idp_all_conf")) as idp:
        binding, destination = sp.pick_binding("name_id_mapping_service",
                                               entity_id=idp.config.entityid)

        policy = NameIDPolicy(format=NAMEID_FORMAT_TRANSIENT,
                              sp_name_qualifier="urn:mace:swamid:junk",
                              allow_create="true")

        nameid = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")

        mid, nmr = sp.create_name_id_mapping_request(policy, nameid, destination)

        print(nmr)

        args = sp.use_soap(nmr, destination)

        # ------- IDP ------------

        req = idp.parse_name_id_mapping_request(args["data"], binding)

        in_response_to = req.message.id
        name_id = NameID(format=NAMEID_FORMAT_PERSISTENT, text="foobar")

        idp_response = idp.create_name_id_mapping_response(
            name_id, in_response_to=in_response_to)

        print(idp_response)

        ht_args = sp.use_soap(idp_response)

        # ------- SP ------------

        _resp = sp.parse_name_id_mapping_request_response(ht_args["data"], binding)

        print(_resp.response)

        r_name_id = _resp.response.name_id

        assert r_name_id.format == NAMEID_FORMAT_PERSISTENT
        assert r_name_id.text == "foobar"
