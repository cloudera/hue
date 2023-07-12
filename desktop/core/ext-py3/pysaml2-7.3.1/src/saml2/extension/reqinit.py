#!/usr/bin/env python

#
# Generated Thu May 15 13:58:36 2014 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import md


NAMESPACE = "urn:oasis:names:tc:SAML:profiles:SSO:request-init"


class RequestInitiator(md.EndpointType_):
    """The urn:oasis:names:tc:SAML:profiles:SSO:request-init:RequestInitiator
    element"""

    c_tag = "RequestInitiator"
    c_namespace = NAMESPACE
    c_children = md.EndpointType_.c_children.copy()
    c_attributes = md.EndpointType_.c_attributes.copy()
    c_child_order = md.EndpointType_.c_child_order[:]
    c_cardinality = md.EndpointType_.c_cardinality.copy()


def request_initiator_from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestInitiator, xml_string)


ELEMENT_FROM_STRING = {
    RequestInitiator.c_tag: request_initiator_from_string,
}

ELEMENT_BY_TAG = {
    "RequestInitiator": RequestInitiator,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
