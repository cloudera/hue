#!/usr/bin/env python
#

"""
Contains classes and functions that a SAML2.0 Service Provider (SP) may use
to do attribute aggregation.
"""
import logging

# from saml2 import client
from saml2 import BINDING_SOAP


logger = logging.getLogger(__name__)

DEFAULT_BINDING = BINDING_SOAP


class AttributeResolver:
    def __init__(self, saml2client, metadata=None, config=None):
        self.metadata = metadata
        self.saml2client = saml2client
        self.metadata = saml2client.config.metadata

    def extend(self, name_id, issuer, vo_members):
        """
        :param name_id: The identifier by which the subject is know
            among all the participents of the VO
        :param issuer: Who am I the poses the query
        :param vo_members: The entity IDs of the IdP who I'm going to ask
            for extra attributes
        :return: A dictionary with all the collected information about the
            subject
        """
        result = []
        for member in vo_members:
            for ass in self.metadata.attribute_consuming_service(member):
                for attr_serv in ass.attribute_service:
                    logger.info("Send attribute request to %s", attr_serv.location)
                    if attr_serv.binding != BINDING_SOAP:
                        continue
                    # attribute query assumes SOAP binding
                    session_info = self.saml2client.attribute_query(name_id, attr_serv.location, issuer_id=issuer)
                    if session_info:
                        result.append(session_info)
        return result
