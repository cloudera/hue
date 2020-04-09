#!/usr/bin/env python

#
# Generated Fri May 27 17:26:51 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase

NAMESPACE = 'http://schemas.xmlsoap.org/soap/envelope/'

class Header_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:Header element """

    c_tag = 'Header'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def header__from_string(xml_string):
    return saml2.create_class_from_xml_string(Header_, xml_string)


class Body_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:Body element """

    c_tag = 'Body'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def body__from_string(xml_string):
    return saml2.create_class_from_xml_string(Body_, xml_string)


class EncodingStyle_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:encodingStyle element """

    c_tag = 'encodingStyle'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def encoding_style__from_string(xml_string):
    return saml2.create_class_from_xml_string(EncodingStyle_, xml_string)


class Fault_faultcode(SamlBase):

    c_tag = 'faultcode'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'QName'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def fault_faultcode_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault_faultcode, xml_string)


class Fault_faultstring(SamlBase):

    c_tag = 'faultstring'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'string'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def fault_faultstring_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault_faultstring, xml_string)


class Fault_faultactor(SamlBase):

    c_tag = 'faultactor'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'anyURI'}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def fault_faultactor_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault_faultactor, xml_string)


class Detail_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:detail element """

    c_tag = 'detail'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def detail__from_string(xml_string):
    return saml2.create_class_from_xml_string(Detail_, xml_string)


class Envelope_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:Envelope element """

    c_tag = 'Envelope'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}Header'] = ('header', Header_)
    c_cardinality['header'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}Body'] = ('body', Body_)
    c_child_order.extend(['header', 'body'])

    def __init__(self,
            header=None,
            body=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.header=header
        self.body=body

def envelope__from_string(xml_string):
    return saml2.create_class_from_xml_string(Envelope_, xml_string)


class Header(Header_):
    """The http://schemas.xmlsoap.org/soap/envelope/:Header element """

    c_tag = 'Header'
    c_namespace = NAMESPACE
    c_children = Header_.c_children.copy()
    c_attributes = Header_.c_attributes.copy()
    c_child_order = Header_.c_child_order[:]
    c_cardinality = Header_.c_cardinality.copy()

def header_from_string(xml_string):
    return saml2.create_class_from_xml_string(Header, xml_string)


class Body(Body_):
    """The http://schemas.xmlsoap.org/soap/envelope/:Body element """

    c_tag = 'Body'
    c_namespace = NAMESPACE
    c_children = Body_.c_children.copy()
    c_attributes = Body_.c_attributes.copy()
    c_child_order = Body_.c_child_order[:]
    c_cardinality = Body_.c_cardinality.copy()

def body_from_string(xml_string):
    return saml2.create_class_from_xml_string(Body, xml_string)


class Fault_detail(Detail_):

    c_tag = 'detail'
    c_namespace = NAMESPACE
    c_children = Detail_.c_children.copy()
    c_attributes = Detail_.c_attributes.copy()
    c_child_order = Detail_.c_child_order[:]
    c_cardinality = Detail_.c_cardinality.copy()

def fault_detail_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault_detail, xml_string)


class Fault_(SamlBase):
    """The http://schemas.xmlsoap.org/soap/envelope/:Fault element """

    c_tag = 'Fault'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}faultcode'] = ('faultcode', Fault_faultcode)
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}faultstring'] = ('faultstring', Fault_faultstring)
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}faultactor'] = ('faultactor', Fault_faultactor)
    c_cardinality['faultactor'] = {"min":0, "max":1}
    c_children['{http://schemas.xmlsoap.org/soap/envelope/}detail'] = ('detail', Fault_detail)
    c_cardinality['detail'] = {"min":0, "max":1}
    c_child_order.extend(['faultcode', 'faultstring', 'faultactor', 'detail'])

    def __init__(self,
            faultcode=None,
            faultstring=None,
            faultactor=None,
            detail=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.faultcode=faultcode
        self.faultstring=faultstring
        self.faultactor=faultactor
        self.detail=detail

def fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault_, xml_string)


class Envelope(Envelope_):
    """The http://schemas.xmlsoap.org/soap/envelope/:Envelope element """

    c_tag = 'Envelope'
    c_namespace = NAMESPACE
    c_children = Envelope_.c_children.copy()
    c_attributes = Envelope_.c_attributes.copy()
    c_child_order = Envelope_.c_child_order[:]
    c_cardinality = Envelope_.c_cardinality.copy()

def envelope_from_string(xml_string):
    return saml2.create_class_from_xml_string(Envelope, xml_string)


class Fault(Fault_):
    """The http://schemas.xmlsoap.org/soap/envelope/:Fault element """

    c_tag = 'Fault'
    c_namespace = NAMESPACE
    c_children = Fault_.c_children.copy()
    c_attributes = Fault_.c_attributes.copy()
    c_child_order = Fault_.c_child_order[:]
    c_cardinality = Fault_.c_cardinality.copy()

def fault_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault, xml_string)


#..................
# []
AG_encodingStyle = [
    ('encodingStyle', '', False),
]

ELEMENT_FROM_STRING = {
    Envelope.c_tag: envelope_from_string,
    Envelope_.c_tag: envelope__from_string,
    Header.c_tag: header_from_string,
    Header_.c_tag: header__from_string,
    Body.c_tag: body_from_string,
    Body_.c_tag: body__from_string,
    EncodingStyle_.c_tag: encoding_style__from_string,
    Fault.c_tag: fault_from_string,
    Fault_.c_tag: fault__from_string,
    Detail_.c_tag: detail__from_string,
    Fault_faultcode.c_tag: fault_faultcode_from_string,
    Fault_faultstring.c_tag: fault_faultstring_from_string,
    Fault_faultactor.c_tag: fault_faultactor_from_string,
}

ELEMENT_BY_TAG = {
    'Envelope': Envelope,
    'Envelope': Envelope_,
    'Header': Header,
    'Header': Header_,
    'Body': Body,
    'Body': Body_,
    'encodingStyle': EncodingStyle_,
    'Fault': Fault,
    'Fault': Fault_,
    'detail': Detail_,
    'faultcode': Fault_faultcode,
    'faultstring': Fault_faultstring,
    'faultactor': Fault_faultactor,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

