#!/usr/bin/env python
#

"""
Contains a class that can do SAML ECP Authentication for other python
programs.
"""

from http import cookiejar as cookielib
import logging

from saml2 import BINDING_SOAP
from saml2 import SAMLError
from saml2 import saml
from saml2 import samlp
from saml2 import soap
from saml2.client_base import MIME_PAOS
from saml2.config import Config
from saml2.entity import Entity
from saml2.httpbase import dict2set_list
from saml2.httpbase import set_list2dict
from saml2.mdstore import MetadataStore
from saml2.profile import ecp
from saml2.profile import paos
from saml2.s_utils import BadRequest


SERVICE = "urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"
PAOS_HEADER_INFO = f'ver="{paos.NAMESPACE}";"{SERVICE}"'

logger = logging.getLogger(__name__)


class Client(Entity):
    """ECP-aware client that works on the client (application) side.

    You can use this class when you want to login user through
    ECP-aware SP and IdP.
    """

    def __init__(
        self,
        user,
        passwd,
        sp="",
        idp=None,
        metadata_file=None,
        xmlsec_binary=None,
        verbose=0,
        ca_certs="",
        disable_ssl_certificate_validation=True,
        key_file=None,
        cert_file=None,
        config=None,
    ):
        """
        :param user: user name
        :param passwd: user password
        :param sp: The SP URL
        :param idp: The IdP PAOS endpoint
        :param metadata_file: Where the metadata file is if used
        :param xmlsec_binary: Where the xmlsec1 binary can be found (*)
        :param verbose: Chatty or not
        :param ca_certs: is the path of a file containing root CA certificates
            for SSL server certificate validation (*)
        :param disable_ssl_certificate_validation: If
            disable_ssl_certificate_validation is true, SSL cert validation
            will not be performed (*)
        :param key_file: Private key filename (*)
        :param cert_file: Certificate filename (*)
        :param config: Config() instance, overrides all the parameters marked
            with an asterisk (*) above
        """
        if not config:
            config = Config()
            config.disable_ssl_certificate_validation = disable_ssl_certificate_validation
            config.key_file = key_file
            config.cert_file = cert_file
            config.ca_certs = ca_certs
            config.xmlsec_binary = xmlsec_binary

        Entity.__init__(self, "sp", config)
        self._idp = idp
        self._sp = sp
        self.user = user
        self.passwd = passwd
        self._verbose = verbose

        if metadata_file:
            self._metadata = MetadataStore([saml, samlp], None, config, http_client_timeout=config.http_client_timeout)
            self._metadata.load("local", metadata_file)
            logger.debug("Loaded metadata from '%s'", metadata_file)
        else:
            self._metadata = None

        self.metadata = self._metadata

        self.cookie_handler = None

        self.done_ecp = False
        self.cookie_jar = cookielib.LWPCookieJar()

    def phase2(
        self,
        authn_request,
        rc_url,
        idp_entity_id,
        headers=None,
        sign=False,
        sign_alg=None,
        **kwargs,
    ):
        """
        Doing the second phase of the ECP conversation, the conversation
        with the IdP happens.

        :param authn_request: The AuthenticationRequest
        :param rc_url: The assertion consumer service url of the SP
        :param idp_entity_id: The EntityID of the IdP
        :param headers: Possible extra headers
        :param sign: If the message should be signed
        :return: The response from the IdP
        """

        _, destination = self.pick_binding("single_sign_on_service", [BINDING_SOAP], "idpsso", entity_id=idp_entity_id)

        ht_args = self.apply_binding(BINDING_SOAP, authn_request, destination, sign=sign, sigalg=sign_alg)

        if headers:
            ht_args["headers"].extend(headers)

        logger.debug("[P2] Sending request: %s", ht_args["data"])

        # POST the request to the IdP
        response = self.send(**ht_args)

        logger.debug("[P2] Got IdP response: %s", response)

        if response.status_code != 200:
            raise SAMLError(f"Request to IdP failed ({response.status_code}): {response.text}")

        # SAMLP response in a SOAP envelope body, ecp response in headers
        respdict = self.parse_soap_message(response.text)

        if respdict is None:
            raise SAMLError("Unexpected reply from the IdP")

        logger.debug("[P2] IdP response dict: %s", respdict)

        idp_response = respdict["body"]

        expected_tag = "Response"
        if idp_response.c_tag != expected_tag:
            raise ValueError(
                "Invalid Response tag '{invalid}' should be '{valid}'".format(
                    invalid=idp_response.c_tag, valid=expected_tag
                )
            )

        logger.debug("[P2] IdP AUTHN response: %s", idp_response)

        _ecp_response = None
        for item in respdict["header"]:
            if item.c_tag == "Response" and item.c_namespace == ecp.NAMESPACE:
                _ecp_response = item

        _acs_url = _ecp_response.assertion_consumer_service_url
        if rc_url != _acs_url:
            error = (
                f"response_consumer_url '{rc_url}' does not match",
                f"assertion_consumer_service_url '{_acs_url}",
            )
            # Send an error message to the SP
            _ = self.send(rc_url, "POST", data=soap.soap_fault(error))
            # Raise an exception so the user knows something went wrong
            raise SAMLError(error)

        return idp_response

    @staticmethod
    def parse_sp_ecp_response(respdict):
        if respdict is None:
            raise SAMLError("Unexpected reply from the SP")

        logger.debug("[P1] SP response dict: %s", respdict)

        # AuthnRequest in the body or not
        authn_request = respdict["body"]

        expected_tag = "AuthnRequest"
        if authn_request.c_tag != expected_tag:
            raise ValueError(
                "Invalid AuthnRequest tag '{invalid}' should be '{valid}'".format(
                    invalid=authn_request.c_tag, valid=expected_tag
                )
            )

        # ecp.RelayState among headers
        _relay_state = None
        _paos_request = None
        for item in respdict["header"]:
            if item.c_tag == "RelayState" and item.c_namespace == ecp.NAMESPACE:
                _relay_state = item
            if item.c_tag == "Request" and item.c_namespace == paos.NAMESPACE:
                _paos_request = item

        if _paos_request is None:
            raise BadRequest("Missing request")

        _rc_url = _paos_request.response_consumer_url

        return {
            "authn_request": authn_request,
            "rc_url": _rc_url,
            "relay_state": _relay_state,
        }

    def ecp_conversation(self, respdict, idp_entity_id=None):
        """

        :param respdict:
        :param idp_entity_id:
        :return:
        """

        args = self.parse_sp_ecp_response(respdict)

        # **********************
        # Phase 2 - talk to the IdP
        # **********************

        idp_response = self.phase2(idp_entity_id=idp_entity_id, **args)

        # **********************************
        # Phase 3 - back to the SP
        # **********************************

        ht_args = self.use_soap(idp_response, args["rc_url"], [args["relay_state"]])
        ht_args["headers"][0] = ("Content-Type", MIME_PAOS)
        logger.debug("[P3] Post to SP: %s", ht_args["data"])

        # POST the package from the IdP to the SP
        response = self.send(**ht_args)

        if response.status_code == 302:
            # ignore where the SP is redirecting us to and go for the
            # url I started off with.
            pass
        else:
            raise SAMLError(f"Error POSTing package to SP: {response.text}")

        logger.debug("[P3] SP response: %s", response.text)

        self.done_ecp = True
        logger.debug("Done ECP")

        return None

    @staticmethod
    def add_paos_headers(headers=None):
        if headers:
            headers = set_list2dict(headers)
            headers["PAOS"] = PAOS_HEADER_INFO
            if "Accept" in headers:
                headers["Accept"] += f";{MIME_PAOS}"
            elif "accept" in headers:
                headers["Accept"] = headers["accept"]
                headers["Accept"] += f";{MIME_PAOS}"
                del headers["accept"]
            headers = dict2set_list(headers)
        else:
            headers = [("Accept", f"text/html; {MIME_PAOS}"), ("PAOS", PAOS_HEADER_INFO)]

        return headers

    def operation(self, url, idp_entity_id, op, **opargs):
        """
        This is the method that should be used by someone that wants
        to authenticate using SAML ECP

        :param url: The page that access is sought for
        :param idp_entity_id: The entity ID of the IdP that should be
            used for authentication
        :param op: Which HTTP operation (GET/POST/PUT/DELETE)
        :param opargs: Arguments to the HTTP call
        :return: The page
        """
        sp_url = self._sp

        # ********************************************
        # Phase 1 - First conversation with the SP
        # ********************************************
        # headers needed to indicate to the SP that I'm ECP enabled

        opargs["headers"] = self.add_paos_headers(opargs["headers"])
        response = self.send(sp_url, op, **opargs)
        logger.debug("[Op] SP response", extra={"response": response})
        print(response.text)

        if response.status_code != 200:
            raise SAMLError(f"Request to SP failed: {response.text}")

        # The response might be a AuthnRequest instance in a SOAP envelope
        # body. If so it's the start of the ECP conversation
        # Two SOAP header blocks; paos:Request and ecp:Request
        # may also contain a ecp:RelayState SOAP header block
        # If channel-binding was part of the PAOS header any number of
        # <cb:ChannelBindings> header blocks may also be present
        # if 'holder-of-key' option then one or more <ecp:SubjectConfirmation>
        # header blocks may also be present
        try:
            respdict = self.parse_soap_message(response.text)
            self.ecp_conversation(respdict, idp_entity_id)

            # should by now be authenticated so this should go smoothly
            response = self.send(url, op, **opargs)
        except (soap.XmlParseError, AssertionError, KeyError):
            raise

        if response.status_code >= 400:
            raise SAMLError(f"Error performing operation: {response.text}")

        return response

    # different HTTP operations
    def delete(self, url=None, idp_entity_id=None):
        return self.operation(url, idp_entity_id, "DELETE")

    def get(self, url=None, idp_entity_id=None, headers=None):
        return self.operation(url, idp_entity_id, "GET", headers=headers)

    def post(self, url=None, data="", idp_entity_id=None, headers=None):
        return self.operation(url, idp_entity_id, "POST", data=data, headers=headers)

    def put(self, url=None, data="", idp_entity_id=None, headers=None):
        return self.operation(url, idp_entity_id, "PUT", data=data, headers=headers)
