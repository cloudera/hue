#!/usr/bin/env python

#
# Generated Fri May 27 17:30:44 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase

#import soapenv as S

NAMESPACE = 'urn:liberty:paos:2003-08'

class RequestType_(SamlBase):
    """The urn:liberty:paos:2003-08:RequestType element """

    c_tag = 'RequestType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['responseConsumerURL'] = ('response_consumer_url', 'anyURI', True)
    c_attributes['service'] = ('service', 'anyURI', True)
    c_attributes['messageID'] = ('message_id', 'None', False)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand'] = ('must_understand', 'None', True)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}actor'] = ('actor', 'None', True)

    def __init__(self,
            response_consumer_url=None,
            service=None,
            message_id=None,
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
        self.response_consumer_url=response_consumer_url
        self.service=service
        self.message_id=message_id
        self.must_understand=must_understand
        self.actor=actor

def request_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RequestType_, xml_string)


class ResponseType_(SamlBase):
    """The urn:liberty:paos:2003-08:ResponseType element """

    c_tag = 'ResponseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['refToMessageID'] = ('ref_to_message_id', 'None', False)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}mustUnderstand'] = ('must_understand', 'None', True)
    c_attributes['{http://schemas.xmlsoap.org/soap/envelope/}actor'] = ('actor', 'None', True)

    def __init__(self,
            ref_to_message_id=None,
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
        self.ref_to_message_id=ref_to_message_id
        self.must_understand=must_understand
        self.actor=actor

def response_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ResponseType_, xml_string)


class Request(RequestType_):
    """The urn:liberty:paos:2003-08:Request element """

    c_tag = 'Request'
    c_namespace = NAMESPACE
    c_children = RequestType_.c_children.copy()
    c_attributes = RequestType_.c_attributes.copy()
    c_child_order = RequestType_.c_child_order[:]
    c_cardinality = RequestType_.c_cardinality.copy()

def request_from_string(xml_string):
    return saml2.create_class_from_xml_string(Request, xml_string)


class Response(ResponseType_):
    """The urn:liberty:paos:2003-08:Response element """

    c_tag = 'Response'
    c_namespace = NAMESPACE
    c_children = ResponseType_.c_children.copy()
    c_attributes = ResponseType_.c_attributes.copy()
    c_child_order = ResponseType_.c_child_order[:]
    c_cardinality = ResponseType_.c_cardinality.copy()

def response_from_string(xml_string):
    return saml2.create_class_from_xml_string(Response, xml_string)


ELEMENT_FROM_STRING = {
    Request.c_tag: request_from_string,
    RequestType_.c_tag: request_type__from_string,
    Response.c_tag: response_from_string,
    ResponseType_.c_tag: response_type__from_string,
}

ELEMENT_BY_TAG = {
    'Request': Request,
    'RequestType': RequestType_,
    'Response': Response,
    'ResponseType': ResponseType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

