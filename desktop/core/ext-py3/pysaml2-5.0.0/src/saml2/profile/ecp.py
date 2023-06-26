#!/usr/bin/env python

#
# Generated Fri May 27 23:08:21 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase

from saml2 import saml
from saml2 import samlp
#import soapenv as S

NAMESPACE = 'urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp'

class RequestType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:RequestType element """

    c_tag = 'RequestType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{urn:oasis:names:tc:SAML:2.0:assertion}Issuer'] = ('issuer', saml.Issuer)
    c_children['{urn:oasis:names:tc:SAML:2.0:protocol}IDPList'] = ('idp_list', samlp.IDPList)
    c_cardinality['idp_list'] = {"min":0, "max":1}
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand'] = ('must_understand', 'None', True)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}actor'] = ('actor', 'None', True)
    c_attributes['ProviderName'] = ('provider_name', 'string', False)
    c_attributes['IsPassive'] = ('is_passive', 'boolean', False)
    c_child_order.extend(['issuer', 'idp_list'])

    def __init__(self,
            issuer=None,
            idp_list=None,
            must_understand=None,
            actor=None,
            provider_name=None,
            is_passive=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.issuer=issuer
        self.idp_list=idp_list
        self.must_understand=must_understand
        self.actor=actor
        self.provider_name=provider_name
        self.is_passive=is_passive

def request_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestType_, xml_string)


class ResponseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:ResponseType element """

    c_tag = 'ResponseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand'] = ('must_understand', 'None', True)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}actor'] = ('actor', 'None', True)
    c_attributes['AssertionConsumerServiceURL'] = ('assertion_consumer_service_url', 'anyURI', True)

    def __init__(self,
            must_understand=None,
            actor=None,
            assertion_consumer_service_url=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.must_understand=must_understand
        self.actor=actor
        self.assertion_consumer_service_url=assertion_consumer_service_url

def response_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ResponseType_, xml_string)


class RelayStateType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:RelayStateType element """

    c_tag = 'RelayStateType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand'] = ('must_understand', 'string', True)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}actor'] = ('actor', 'string', True)

    def __init__(self,
            must_understand=None,
            actor=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.must_understand=must_understand
        self.actor=actor

def relay_state_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RelayStateType_, xml_string)


class Request(RequestType_):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:Request element """

    c_tag = 'Request'
    c_namespace = NAMESPACE
    c_children = RequestType_.c_children.copy()
    c_attributes = RequestType_.c_attributes.copy()
    c_child_order = RequestType_.c_child_order[:]
    c_cardinality = RequestType_.c_cardinality.copy()

def request_from_string(xml_string):
    return saml2.create_class_from_xml_string(Request, xml_string)


class Response(ResponseType_):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:Response element """

    c_tag = 'Response'
    c_namespace = NAMESPACE
    c_children = ResponseType_.c_children.copy()
    c_attributes = ResponseType_.c_attributes.copy()
    c_child_order = ResponseType_.c_child_order[:]
    c_cardinality = ResponseType_.c_cardinality.copy()

def response_from_string(xml_string):
    return saml2.create_class_from_xml_string(Response, xml_string)


class RelayState(RelayStateType_):
    """The urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp:RelayState element """

    c_tag = 'RelayState'
    c_namespace = NAMESPACE
    c_children = RelayStateType_.c_children.copy()
    c_attributes = RelayStateType_.c_attributes.copy()
    c_child_order = RelayStateType_.c_child_order[:]
    c_cardinality = RelayStateType_.c_cardinality.copy()

def relay_state_from_string(xml_string):
    return saml2.create_class_from_xml_string(RelayState, xml_string)


ELEMENT_FROM_STRING = {
    Request.c_tag: request_from_string,
    RequestType_.c_tag: request_type__from_string,
    Response.c_tag: response_from_string,
    ResponseType_.c_tag: response_type__from_string,
    RelayState.c_tag: relay_state_from_string,
    RelayStateType_.c_tag: relay_state_type__from_string,
}

ELEMENT_BY_TAG = {
    'Request': Request,
    'RequestType': RequestType_,
    'Response': Response,
    'ResponseType': ResponseType_,
    'RelayState': RelayState,
    'RelayStateType': RelayStateType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

