#!/usr/bin/env python

#
# Generated Fri May 27 17:23:42 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2.schema import wsdl


NAMESPACE = "http://schemas.xmlsoap.org/wsdl/soap/"


class EncodingStyle_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/soap/:encodingStyle element"""

    c_tag = "encodingStyle"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def encoding_style__from_string(xml_string):
    return saml2.create_class_from_xml_string(EncodingStyle_, xml_string)


class TStyleChoice_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tStyleChoice element"""

    c_tag = "tStyleChoice"
    c_namespace = NAMESPACE
    c_value_type = {"base": "xs:string", "enumeration": ["rpc", "document"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def t_style_choice__from_string(xml_string):
    return saml2.create_class_from_xml_string(TStyleChoice_, xml_string)


class TOperation_(wsdl.TExtensibilityElement_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tOperation element"""

    c_tag = "tOperation"
    c_namespace = NAMESPACE
    c_children = wsdl.TExtensibilityElement_.c_children.copy()
    c_attributes = wsdl.TExtensibilityElement_.c_attributes.copy()
    c_child_order = wsdl.TExtensibilityElement_.c_child_order[:]
    c_cardinality = wsdl.TExtensibilityElement_.c_cardinality.copy()
    c_attributes["soapAction"] = ("soap_action", "anyURI", False)
    c_attributes["style"] = ("style", TStyleChoice_, False)

    def __init__(
        self,
        soap_action=None,
        style=None,
        required=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        wsdl.TExtensibilityElement_.__init__(
            self,
            required=required,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.soap_action = soap_action
        self.style = style


def t_operation__from_string(xml_string):
    return saml2.create_class_from_xml_string(TOperation_, xml_string)


class UseChoice_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/soap/:useChoice element"""

    c_tag = "useChoice"
    c_namespace = NAMESPACE
    c_value_type = {"base": "xs:string", "enumeration": ["literal", "encoded"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def use_choice__from_string(xml_string):
    return saml2.create_class_from_xml_string(UseChoice_, xml_string)


class TFaultRes_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tFaultRes element"""

    c_tag = "tFaultRes"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["{http://schemas.xmlsoap.org/wsdl/}required"] = ("required", "None", False)
    c_attributes["parts"] = ("parts", "NMTOKENS", False)
    c_attributes["encodingStyle"] = ("encoding_style", EncodingStyle_, False)
    c_attributes["use"] = ("use", UseChoice_, False)
    c_attributes["namespace"] = ("namespace", "anyURI", False)

    def __init__(
        self,
        required=None,
        parts=None,
        encoding_style=None,
        use=None,
        namespace=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.required = required
        self.parts = parts
        self.encoding_style = encoding_style
        self.use = use
        self.namespace = namespace


class TFault_(TFaultRes_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tFault element"""

    c_tag = "tFault"
    c_namespace = NAMESPACE
    c_children = TFaultRes_.c_children.copy()
    c_attributes = TFaultRes_.c_attributes.copy()
    c_child_order = TFaultRes_.c_child_order[:]
    c_cardinality = TFaultRes_.c_cardinality.copy()
    c_attributes["name"] = ("name", "NCName", True)

    def __init__(
        self,
        name=None,
        required=None,
        parts=None,
        encoding_style=None,
        use=None,
        namespace=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        TFaultRes_.__init__(
            self,
            required=required,
            parts=parts,
            encoding_style=encoding_style,
            use=use,
            namespace=namespace,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.name = name


def t_fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(TFault_, xml_string)


class THeaderFault_(SamlBase):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tHeaderFault element"""

    c_tag = "tHeaderFault"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["message"] = ("message", "QName", True)
    c_attributes["part"] = ("part", "NMTOKEN", True)
    c_attributes["use"] = ("use", UseChoice_, True)
    c_attributes["encodingStyle"] = ("encoding_style", EncodingStyle_, False)
    c_attributes["namespace"] = ("namespace", "anyURI", False)

    def __init__(
        self,
        message=None,
        part=None,
        use=None,
        encoding_style=None,
        namespace=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.message = message
        self.part = part
        self.use = use
        self.encoding_style = encoding_style
        self.namespace = namespace


def t_header_fault__from_string(xml_string):
    return saml2.create_class_from_xml_string(THeaderFault_, xml_string)


class TAddress_(wsdl.TExtensibilityElement_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tAddress element"""

    c_tag = "tAddress"
    c_namespace = NAMESPACE
    c_children = wsdl.TExtensibilityElement_.c_children.copy()
    c_attributes = wsdl.TExtensibilityElement_.c_attributes.copy()
    c_child_order = wsdl.TExtensibilityElement_.c_child_order[:]
    c_cardinality = wsdl.TExtensibilityElement_.c_cardinality.copy()
    c_attributes["location"] = ("location", "anyURI", True)

    def __init__(
        self,
        location=None,
        required=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        wsdl.TExtensibilityElement_.__init__(
            self,
            required=required,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.location = location


def t_address__from_string(xml_string):
    return saml2.create_class_from_xml_string(TAddress_, xml_string)


class TBinding_(wsdl.TExtensibilityElement_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tBinding element"""

    c_tag = "tBinding"
    c_namespace = NAMESPACE
    c_children = wsdl.TExtensibilityElement_.c_children.copy()
    c_attributes = wsdl.TExtensibilityElement_.c_attributes.copy()
    c_child_order = wsdl.TExtensibilityElement_.c_child_order[:]
    c_cardinality = wsdl.TExtensibilityElement_.c_cardinality.copy()
    c_attributes["transport"] = ("transport", "anyURI", True)
    c_attributes["style"] = ("style", TStyleChoice_, False)

    def __init__(
        self,
        transport=None,
        style=None,
        required=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        wsdl.TExtensibilityElement_.__init__(
            self,
            required=required,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.transport = transport
        self.style = style


def t_binding__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBinding_, xml_string)


class Operation(TOperation_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:operation element"""

    c_tag = "operation"
    c_namespace = NAMESPACE
    c_children = TOperation_.c_children.copy()
    c_attributes = TOperation_.c_attributes.copy()
    c_child_order = TOperation_.c_child_order[:]
    c_cardinality = TOperation_.c_cardinality.copy()


def operation_from_string(xml_string):
    return saml2.create_class_from_xml_string(Operation, xml_string)


class TBody_(wsdl.TExtensibilityElement_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tBody element"""

    c_tag = "tBody"
    c_namespace = NAMESPACE
    c_children = wsdl.TExtensibilityElement_.c_children.copy()
    c_attributes = wsdl.TExtensibilityElement_.c_attributes.copy()
    c_child_order = wsdl.TExtensibilityElement_.c_child_order[:]
    c_cardinality = wsdl.TExtensibilityElement_.c_cardinality.copy()
    c_attributes["parts"] = ("parts", "NMTOKENS", False)
    c_attributes["encodingStyle"] = ("encoding_style", EncodingStyle_, False)
    c_attributes["use"] = ("use", UseChoice_, False)
    c_attributes["namespace"] = ("namespace", "anyURI", False)

    def __init__(
        self,
        parts=None,
        encoding_style=None,
        use=None,
        namespace=None,
        required=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        wsdl.TExtensibilityElement_.__init__(
            self,
            required=required,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.parts = parts
        self.encoding_style = encoding_style
        self.use = use
        self.namespace = namespace


def t_body__from_string(xml_string):
    return saml2.create_class_from_xml_string(TBody_, xml_string)


class Fault(TFault_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:fault element"""

    c_tag = "fault"
    c_namespace = NAMESPACE
    c_children = TFault_.c_children.copy()
    c_attributes = TFault_.c_attributes.copy()
    c_child_order = TFault_.c_child_order[:]
    c_cardinality = TFault_.c_cardinality.copy()


def fault_from_string(xml_string):
    return saml2.create_class_from_xml_string(Fault, xml_string)


class Headerfault(THeaderFault_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:headerfault element"""

    c_tag = "headerfault"
    c_namespace = NAMESPACE
    c_children = THeaderFault_.c_children.copy()
    c_attributes = THeaderFault_.c_attributes.copy()
    c_child_order = THeaderFault_.c_child_order[:]
    c_cardinality = THeaderFault_.c_cardinality.copy()


def headerfault_from_string(xml_string):
    return saml2.create_class_from_xml_string(Headerfault, xml_string)


class Address(TAddress_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:address element"""

    c_tag = "address"
    c_namespace = NAMESPACE
    c_children = TAddress_.c_children.copy()
    c_attributes = TAddress_.c_attributes.copy()
    c_child_order = TAddress_.c_child_order[:]
    c_cardinality = TAddress_.c_cardinality.copy()


def address_from_string(xml_string):
    return saml2.create_class_from_xml_string(Address, xml_string)


class Binding(TBinding_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:binding element"""

    c_tag = "binding"
    c_namespace = NAMESPACE
    c_children = TBinding_.c_children.copy()
    c_attributes = TBinding_.c_attributes.copy()
    c_child_order = TBinding_.c_child_order[:]
    c_cardinality = TBinding_.c_cardinality.copy()


def binding_from_string(xml_string):
    return saml2.create_class_from_xml_string(Binding, xml_string)


class Body(TBody_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:body element"""

    c_tag = "body"
    c_namespace = NAMESPACE
    c_children = TBody_.c_children.copy()
    c_attributes = TBody_.c_attributes.copy()
    c_child_order = TBody_.c_child_order[:]
    c_cardinality = TBody_.c_cardinality.copy()


def body_from_string(xml_string):
    return saml2.create_class_from_xml_string(Body, xml_string)


class THeader_(wsdl.TExtensibilityElement_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:tHeader element"""

    c_tag = "tHeader"
    c_namespace = NAMESPACE
    c_children = wsdl.TExtensibilityElement_.c_children.copy()
    c_attributes = wsdl.TExtensibilityElement_.c_attributes.copy()
    c_child_order = wsdl.TExtensibilityElement_.c_child_order[:]
    c_cardinality = wsdl.TExtensibilityElement_.c_cardinality.copy()
    c_children["{http://schemas.xmlsoap.org/wsdl/soap/}headerfault"] = ("headerfault", [Headerfault])
    c_cardinality["headerfault"] = {"min": 0}
    c_attributes["message"] = ("message", "QName", True)
    c_attributes["part"] = ("part", "NMTOKEN", True)
    c_attributes["use"] = ("use", UseChoice_, True)
    c_attributes["encodingStyle"] = ("encoding_style", EncodingStyle_, False)
    c_attributes["namespace"] = ("namespace", "anyURI", False)
    c_child_order.extend(["headerfault"])

    def __init__(
        self,
        headerfault=None,
        message=None,
        part=None,
        use=None,
        encoding_style=None,
        namespace=None,
        required=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        wsdl.TExtensibilityElement_.__init__(
            self,
            required=required,
            text=text,
            extension_elements=extension_elements,
            extension_attributes=extension_attributes,
        )
        self.headerfault = headerfault or []
        self.message = message
        self.part = part
        self.use = use
        self.encoding_style = encoding_style
        self.namespace = namespace


def t_header__from_string(xml_string):
    return saml2.create_class_from_xml_string(THeader_, xml_string)


class Header(THeader_):
    """The http://schemas.xmlsoap.org/wsdl/soap/:header element"""

    c_tag = "header"
    c_namespace = NAMESPACE
    c_children = THeader_.c_children.copy()
    c_attributes = THeader_.c_attributes.copy()
    c_child_order = THeader_.c_child_order[:]
    c_cardinality = THeader_.c_cardinality.copy()


def header_from_string(xml_string):
    return saml2.create_class_from_xml_string(Header, xml_string)


AG_tBodyAttributes = [
    ("encodingStyle", EncodingStyle_, False),
    ("use", UseChoice_, False),
    ("namespace", "anyURI", False),
]

AG_tHeaderAttributes = [
    ("message", "QName", True),
    ("part", "NMTOKEN", True),
    ("use", UseChoice_, True),
    ("encodingStyle", EncodingStyle_, False),
    ("namespace", "anyURI", False),
]

ELEMENT_FROM_STRING = {
    EncodingStyle_.c_tag: encoding_style__from_string,
    Binding.c_tag: binding_from_string,
    TBinding_.c_tag: t_binding__from_string,
    TStyleChoice_.c_tag: t_style_choice__from_string,
    Operation.c_tag: operation_from_string,
    TOperation_.c_tag: t_operation__from_string,
    Body.c_tag: body_from_string,
    TBody_.c_tag: t_body__from_string,
    UseChoice_.c_tag: use_choice__from_string,
    Fault.c_tag: fault_from_string,
    TFault_.c_tag: t_fault__from_string,
    Header.c_tag: header_from_string,
    THeader_.c_tag: t_header__from_string,
    Headerfault.c_tag: headerfault_from_string,
    THeaderFault_.c_tag: t_header_fault__from_string,
    Address.c_tag: address_from_string,
    TAddress_.c_tag: t_address__from_string,
}

ELEMENT_BY_TAG = {
    "encodingStyle": EncodingStyle_,
    "binding": Binding,
    "tBinding": TBinding_,
    "tStyleChoice": TStyleChoice_,
    "operation": Operation,
    "tOperation": TOperation_,
    "body": Body,
    "tBody": TBody_,
    "useChoice": UseChoice_,
    "fault": Fault,
    "tFault": TFault_,
    "header": Header,
    "tHeader": THeader_,
    "headerfault": Headerfault,
    "tHeaderFault": THeaderFault_,
    "address": Address,
    "tAddress": TAddress_,
    "tFaultRes": TFaultRes_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
