#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

"""
Contains classes used in the SAML ECP profile
"""
import logging
from saml2.client_base import ACTOR, MIME_PAOS
from saml2.ecp_client import SERVICE

from saml2 import element_to_extension_element
from saml2 import samlp
from saml2 import soap
from saml2 import BINDING_SOAP, BINDING_PAOS

from saml2.profile import paos
from saml2.profile import ecp

#from saml2.client import Saml2Client
from saml2.server import Server

from saml2.schema import soapenv

from saml2.response import authn_response

from saml2 import saml

logger = logging.getLogger(__name__)


def ecp_capable(headers):
    if MIME_PAOS in headers["Accept"]:
        if "PAOS" in headers:
            if 'ver="%s";"%s"' % (paos.NAMESPACE,
                                  SERVICE) in headers["PAOS"]:
                return True

    return False


#noinspection PyUnusedLocal
def ecp_auth_request(cls, entityid=None, relay_state="", sign=False):
    """ Makes an authentication request.

    :param entityid: The entity ID of the IdP to send the request to
    :param relay_state: To where the user should be returned after
        successfull log in.
    :param sign: Whether the request should be signed or not.
    :return: AuthnRequest response
    """

    eelist = []

    # ----------------------------------------
    # <paos:Request>
    # ----------------------------------------
    my_url = cls.service_urls(BINDING_PAOS)[0]

    # must_understand and actor according to the standard
    #
    paos_request = paos.Request(must_understand="1", actor=ACTOR,
                                response_consumer_url=my_url,
                                service=SERVICE)

    eelist.append(element_to_extension_element(paos_request))

    # ----------------------------------------
    # <samlp:AuthnRequest>
    # ----------------------------------------

    logger.info("entityid: %s, binding: %s" % (entityid, BINDING_SOAP))

    location = cls._sso_location(entityid, binding=BINDING_SOAP)
    req_id, authn_req = cls.create_authn_request(
        location, binding=BINDING_PAOS, service_url_binding=BINDING_PAOS)

    body = soapenv.Body()
    body.extension_elements = [element_to_extension_element(authn_req)]

    # ----------------------------------------
    # <ecp:Request>
    # ----------------------------------------

#        idp = samlp.IDPEntry(
#            provider_id = "https://idp.example.org/entity",
#            name = "Example identity provider",
#            loc = "https://idp.example.org/saml2/sso",
#            )
#
#        idp_list = samlp.IDPList(idp_entry= [idp])

    idp_list = None
    ecp_request = ecp.Request(
        actor=ACTOR,
        must_understand="1",
        provider_name=None,
        issuer=saml.Issuer(text=authn_req.issuer.text),
        idp_list=idp_list)

    eelist.append(element_to_extension_element(ecp_request))

    # ----------------------------------------
    # <ecp:RelayState>
    # ----------------------------------------

    relay_state = ecp.RelayState(actor=ACTOR, must_understand="1",
                                 text=relay_state)

    eelist.append(element_to_extension_element(relay_state))

    header = soapenv.Header()
    header.extension_elements = eelist

    # ----------------------------------------
    # The SOAP envelope
    # ----------------------------------------

    soap_envelope = soapenv.Envelope(header=header, body=body)

    return req_id, "%s" % soap_envelope


def handle_ecp_authn_response(cls, soap_message, outstanding=None):
    rdict = soap.class_instances_from_soap_enveloped_saml_thingies(
        soap_message, [paos, ecp, samlp])

    _relay_state = None
    for item in rdict["header"]:
        if item.c_tag == "RelayState" and item.c_namespace == ecp.NAMESPACE:
            _relay_state = item

    response = authn_response(cls.config, cls.service_urls(), outstanding,
                              allow_unsolicited=True)

    response.loads("%s" % rdict["body"], False, soap_message)
    response.verify()
    cls.users.add_information_about_person(response.session_info())

    return response, _relay_state


def ecp_response(target_url, response):

    # ----------------------------------------
    # <ecp:Response
    # ----------------------------------------

    ecp_response = ecp.Response(assertion_consumer_service_url=target_url)
    header = soapenv.Header()
    header.extension_elements = [element_to_extension_element(ecp_response)]

    # ----------------------------------------
    # <samlp:Response
    # ----------------------------------------

    body = soapenv.Body()
    body.extension_elements = [element_to_extension_element(response)]

    soap_envelope = soapenv.Envelope(header=header, body=body)

    return "%s" % soap_envelope


class ECPServer(Server):
    """ This deals with what the IdP has to do

    TODO: Still tentative
    """
    def __init__(self, config_file="", config=None, cache=None):
        Server.__init__(self, config_file, config, cache)

    def parse_ecp_authn_query(self):
        pass

    def ecp_response(self):

        # ----------------------------------------
        # <ecp:Response
        # ----------------------------------------
        target_url = ""

        ecp_response = ecp.Response(assertion_consumer_service_url=target_url)
        header = soapenv.Body()
        header.extension_elements = [element_to_extension_element(ecp_response)]

        # ----------------------------------------
        # <samlp:Response
        # ----------------------------------------

        response = samlp.Response()
        body = soapenv.Body()
        body.extension_elements = [element_to_extension_element(response)]

        soap_envelope = soapenv.Envelope(header=header, body=body)

        return "%s" % soap_envelope
