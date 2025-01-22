#!/usr/bin/env python

#
# Generated Sun Jun 14 13:38:21 2015 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase


NAMESPACE = "http://www.w3.org/2005/08/addressing"


class ReferenceParametersType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:ReferenceParametersType element"""

    c_tag = "ReferenceParametersType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def reference_parameters_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ReferenceParametersType_, xml_string)


class MetadataType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:MetadataType element"""

    c_tag = "MetadataType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def metadata_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(MetadataType_, xml_string)


class RelationshipTypeOpenEnum_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:RelationshipTypeOpenEnum element"""

    c_tag = "RelationshipTypeOpenEnum"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def relationship_type_open_enum__from_string(xml_string):
    return saml2.create_class_from_xml_string(RelationshipTypeOpenEnum_, xml_string)


class RelationshipType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:RelationshipType element"""

    c_tag = "RelationshipType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "xs:anyURI", "enumeration": ["http://www.w3.org/2005/08/addressing/reply"]}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def relationship_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RelationshipType_, xml_string)


class AttributedURIType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:AttributedURIType element"""

    c_tag = "AttributedURIType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def attributed_uri_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedURIType_, xml_string)


class FaultCodesOpenEnumType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:FaultCodesOpenEnumType element"""

    c_tag = "FaultCodesOpenEnumType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def fault_codes_open_enum_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(FaultCodesOpenEnumType_, xml_string)


class FaultCodesType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:FaultCodesType element"""

    c_tag = "FaultCodesType"
    c_namespace = NAMESPACE
    c_value_type = {
        "base": "xs:QName",
        "enumeration": [
            "tns:InvalidAddressingHeader",
            "tns:InvalidAddress",
            "tns:InvalidEPR",
            "tns:InvalidCardinality",
            "tns:MissingAddressInEPR",
            "tns:DuplicateMessageID",
            "tns:ActionMismatch",
            "tns:MessageAddressingHeaderRequired",
            "tns:DestinationUnreachable",
            "tns:ActionNotSupported",
            "tns:EndpointUnavailable",
        ],
    }
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def fault_codes_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(FaultCodesType_, xml_string)


class AttributedUnsignedLongType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:AttributedUnsignedLongType element"""

    c_tag = "AttributedUnsignedLongType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "unsignedLong"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def attributed_unsigned_long_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedUnsignedLongType_, xml_string)


class AttributedQNameType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:AttributedQNameType element"""

    c_tag = "AttributedQNameType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "QName"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def attributed_q_name_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AttributedQNameType_, xml_string)


class ProblemIRI(AttributedURIType_):
    """The http://www.w3.org/2005/08/addressing:ProblemIRI element"""

    c_tag = "ProblemIRI"
    c_namespace = NAMESPACE
    c_children = AttributedURIType_.c_children.copy()
    c_attributes = AttributedURIType_.c_attributes.copy()
    c_child_order = AttributedURIType_.c_child_order[:]
    c_cardinality = AttributedURIType_.c_cardinality.copy()


def problem_iri_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProblemIRI, xml_string)


class EndpointReferenceType_Address(AttributedURIType_):

    c_tag = "Address"
    c_namespace = NAMESPACE
    c_children = AttributedURIType_.c_children.copy()
    c_attributes = AttributedURIType_.c_attributes.copy()
    c_child_order = AttributedURIType_.c_child_order[:]
    c_cardinality = AttributedURIType_.c_cardinality.copy()


def endpoint_reference_type__address_from_string(xml_string):
    return saml2.create_class_from_xml_string(EndpointReferenceType_Address, xml_string)


class ReferenceParameters(ReferenceParametersType_):
    """The http://www.w3.org/2005/08/addressing:ReferenceParameters element"""

    c_tag = "ReferenceParameters"
    c_namespace = NAMESPACE
    c_children = ReferenceParametersType_.c_children.copy()
    c_attributes = ReferenceParametersType_.c_attributes.copy()
    c_child_order = ReferenceParametersType_.c_child_order[:]
    c_cardinality = ReferenceParametersType_.c_cardinality.copy()


def reference_parameters_from_string(xml_string):
    return saml2.create_class_from_xml_string(ReferenceParameters, xml_string)


class Metadata(MetadataType_):
    """The http://www.w3.org/2005/08/addressing:Metadata element"""

    c_tag = "Metadata"
    c_namespace = NAMESPACE
    c_children = MetadataType_.c_children.copy()
    c_attributes = MetadataType_.c_attributes.copy()
    c_child_order = MetadataType_.c_child_order[:]
    c_cardinality = MetadataType_.c_cardinality.copy()


def metadata_from_string(xml_string):
    return saml2.create_class_from_xml_string(Metadata, xml_string)


class MessageID(AttributedURIType_):
    """The http://www.w3.org/2005/08/addressing:MessageID element"""

    c_tag = "MessageID"
    c_namespace = NAMESPACE
    c_children = AttributedURIType_.c_children.copy()
    c_attributes = AttributedURIType_.c_attributes.copy()
    c_child_order = AttributedURIType_.c_child_order[:]
    c_cardinality = AttributedURIType_.c_cardinality.copy()


def message_id_from_string(xml_string):
    return saml2.create_class_from_xml_string(MessageID, xml_string)


class RelatesToType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:RelatesToType element"""

    c_tag = "RelatesToType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["RelationshipType"] = ("relationship_type", RelationshipTypeOpenEnum_, False)

    def __init__(
        self,
        relationship_type="http://www.w3.org/2005/08/addressing/reply",
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
        self.relationship_type = relationship_type


def relates_to_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RelatesToType_, xml_string)


class To(AttributedURIType_):
    """The http://www.w3.org/2005/08/addressing:To element"""

    c_tag = "To"
    c_namespace = NAMESPACE
    c_children = AttributedURIType_.c_children.copy()
    c_attributes = AttributedURIType_.c_attributes.copy()
    c_child_order = AttributedURIType_.c_child_order[:]
    c_cardinality = AttributedURIType_.c_cardinality.copy()


def to_from_string(xml_string):
    return saml2.create_class_from_xml_string(To, xml_string)


class Action(AttributedURIType_):
    """The http://www.w3.org/2005/08/addressing:Action element"""

    c_tag = "Action"
    c_namespace = NAMESPACE
    c_children = AttributedURIType_.c_children.copy()
    c_attributes = AttributedURIType_.c_attributes.copy()
    c_child_order = AttributedURIType_.c_child_order[:]
    c_cardinality = AttributedURIType_.c_cardinality.copy()


def action_from_string(xml_string):
    return saml2.create_class_from_xml_string(Action, xml_string)


class RetryAfter(AttributedUnsignedLongType_):
    """The http://www.w3.org/2005/08/addressing:RetryAfter element"""

    c_tag = "RetryAfter"
    c_namespace = NAMESPACE
    c_children = AttributedUnsignedLongType_.c_children.copy()
    c_attributes = AttributedUnsignedLongType_.c_attributes.copy()
    c_child_order = AttributedUnsignedLongType_.c_child_order[:]
    c_cardinality = AttributedUnsignedLongType_.c_cardinality.copy()


def retry_after_from_string(xml_string):
    return saml2.create_class_from_xml_string(RetryAfter, xml_string)


class ProblemHeaderQName(AttributedQNameType_):
    """The http://www.w3.org/2005/08/addressing:ProblemHeaderQName element"""

    c_tag = "ProblemHeaderQName"
    c_namespace = NAMESPACE
    c_children = AttributedQNameType_.c_children.copy()
    c_attributes = AttributedQNameType_.c_attributes.copy()
    c_child_order = AttributedQNameType_.c_child_order[:]
    c_cardinality = AttributedQNameType_.c_cardinality.copy()


def problem_header_q_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProblemHeaderQName, xml_string)


class ProblemActionType_SoapAction(SamlBase):

    c_tag = "SoapAction"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def problem_action_type__soap_action_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProblemActionType_SoapAction, xml_string)


class ProblemActionType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:ProblemActionType element"""

    c_tag = "ProblemActionType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2005/08/addressing}Action"] = ("action", Action)
    c_cardinality["action"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2005/08/addressing}SoapAction"] = ("soap_action", ProblemActionType_SoapAction)
    c_cardinality["soap_action"] = {"min": 0, "max": 1}
    c_child_order.extend(["action", "soap_action"])

    def __init__(
        self,
        action=None,
        soap_action=None,
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
        self.action = action
        self.soap_action = soap_action


def problem_action_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ProblemActionType_, xml_string)


class EndpointReferenceType_(SamlBase):
    """The http://www.w3.org/2005/08/addressing:EndpointReferenceType element"""

    c_tag = "EndpointReferenceType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2005/08/addressing}Address"] = ("address", EndpointReferenceType_Address)
    c_children["{http://www.w3.org/2005/08/addressing}ReferenceParameters"] = (
        "reference_parameters",
        ReferenceParameters,
    )
    c_cardinality["reference_parameters"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2005/08/addressing}Metadata"] = ("metadata", Metadata)
    c_cardinality["metadata"] = {"min": 0, "max": 1}
    c_child_order.extend(["address", "reference_parameters", "metadata"])

    def __init__(
        self,
        address=None,
        reference_parameters=None,
        metadata=None,
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
        self.address = address
        self.reference_parameters = reference_parameters
        self.metadata = metadata


def endpoint_reference_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(EndpointReferenceType_, xml_string)


class RelatesTo(RelatesToType_):
    """The http://www.w3.org/2005/08/addressing:RelatesTo element"""

    c_tag = "RelatesTo"
    c_namespace = NAMESPACE
    c_children = RelatesToType_.c_children.copy()
    c_attributes = RelatesToType_.c_attributes.copy()
    c_child_order = RelatesToType_.c_child_order[:]
    c_cardinality = RelatesToType_.c_cardinality.copy()


def relates_to_from_string(xml_string):
    return saml2.create_class_from_xml_string(RelatesTo, xml_string)


class ReplyTo(EndpointReferenceType_):
    """The http://www.w3.org/2005/08/addressing:ReplyTo element"""

    c_tag = "ReplyTo"
    c_namespace = NAMESPACE
    c_children = EndpointReferenceType_.c_children.copy()
    c_attributes = EndpointReferenceType_.c_attributes.copy()
    c_child_order = EndpointReferenceType_.c_child_order[:]
    c_cardinality = EndpointReferenceType_.c_cardinality.copy()


def reply_to_from_string(xml_string):
    return saml2.create_class_from_xml_string(ReplyTo, xml_string)


class From(EndpointReferenceType_):
    """The http://www.w3.org/2005/08/addressing:From element"""

    c_tag = "From"
    c_namespace = NAMESPACE
    c_children = EndpointReferenceType_.c_children.copy()
    c_attributes = EndpointReferenceType_.c_attributes.copy()
    c_child_order = EndpointReferenceType_.c_child_order[:]
    c_cardinality = EndpointReferenceType_.c_cardinality.copy()


def from_from_string(xml_string):
    return saml2.create_class_from_xml_string(From, xml_string)


class FaultTo(EndpointReferenceType_):
    """The http://www.w3.org/2005/08/addressing:FaultTo element"""

    c_tag = "FaultTo"
    c_namespace = NAMESPACE
    c_children = EndpointReferenceType_.c_children.copy()
    c_attributes = EndpointReferenceType_.c_attributes.copy()
    c_child_order = EndpointReferenceType_.c_child_order[:]
    c_cardinality = EndpointReferenceType_.c_cardinality.copy()


def fault_to_from_string(xml_string):
    return saml2.create_class_from_xml_string(FaultTo, xml_string)


class ProblemAction(ProblemActionType_):
    """The http://www.w3.org/2005/08/addressing:ProblemAction element"""

    c_tag = "ProblemAction"
    c_namespace = NAMESPACE
    c_children = ProblemActionType_.c_children.copy()
    c_attributes = ProblemActionType_.c_attributes.copy()
    c_child_order = ProblemActionType_.c_child_order[:]
    c_cardinality = ProblemActionType_.c_cardinality.copy()


def problem_action_from_string(xml_string):
    return saml2.create_class_from_xml_string(ProblemAction, xml_string)


class EndpointReference(EndpointReferenceType_):
    """The http://www.w3.org/2005/08/addressing:EndpointReference element"""

    c_tag = "EndpointReference"
    c_namespace = NAMESPACE
    c_children = EndpointReferenceType_.c_children.copy()
    c_attributes = EndpointReferenceType_.c_attributes.copy()
    c_child_order = EndpointReferenceType_.c_child_order[:]
    c_cardinality = EndpointReferenceType_.c_cardinality.copy()


def endpoint_reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(EndpointReference, xml_string)


ELEMENT_FROM_STRING = {
    EndpointReference.c_tag: endpoint_reference_from_string,
    EndpointReferenceType_.c_tag: endpoint_reference_type__from_string,
    ReferenceParameters.c_tag: reference_parameters_from_string,
    ReferenceParametersType_.c_tag: reference_parameters_type__from_string,
    Metadata.c_tag: metadata_from_string,
    MetadataType_.c_tag: metadata_type__from_string,
    MessageID.c_tag: message_id_from_string,
    RelatesTo.c_tag: relates_to_from_string,
    RelatesToType_.c_tag: relates_to_type__from_string,
    RelationshipTypeOpenEnum_.c_tag: relationship_type_open_enum__from_string,
    RelationshipType_.c_tag: relationship_type__from_string,
    ReplyTo.c_tag: reply_to_from_string,
    From.c_tag: from_from_string,
    FaultTo.c_tag: fault_to_from_string,
    To.c_tag: to_from_string,
    Action.c_tag: action_from_string,
    AttributedURIType_.c_tag: attributed_uri_type__from_string,
    FaultCodesOpenEnumType_.c_tag: fault_codes_open_enum_type__from_string,
    FaultCodesType_.c_tag: fault_codes_type__from_string,
    RetryAfter.c_tag: retry_after_from_string,
    AttributedUnsignedLongType_.c_tag: attributed_unsigned_long_type__from_string,
    ProblemHeaderQName.c_tag: problem_header_q_name_from_string,
    AttributedQNameType_.c_tag: attributed_q_name_type__from_string,
    ProblemIRI.c_tag: problem_iri_from_string,
    ProblemAction.c_tag: problem_action_from_string,
    ProblemActionType_.c_tag: problem_action_type__from_string,
    EndpointReferenceType_Address.c_tag: endpoint_reference_type__address_from_string,
    ProblemActionType_SoapAction.c_tag: problem_action_type__soap_action_from_string,
}

ELEMENT_BY_TAG = {
    "EndpointReference": EndpointReference,
    "EndpointReferenceType": EndpointReferenceType_,
    "ReferenceParameters": ReferenceParameters,
    "ReferenceParametersType": ReferenceParametersType_,
    "Metadata": Metadata,
    "MetadataType": MetadataType_,
    "MessageID": MessageID,
    "RelatesTo": RelatesTo,
    "RelatesToType": RelatesToType_,
    "RelationshipTypeOpenEnum": RelationshipTypeOpenEnum_,
    "RelationshipType": RelationshipType_,
    "ReplyTo": ReplyTo,
    "From": From,
    "FaultTo": FaultTo,
    "To": To,
    "Action": Action,
    "AttributedURIType": AttributedURIType_,
    "FaultCodesOpenEnumType": FaultCodesOpenEnumType_,
    "FaultCodesType": FaultCodesType_,
    "RetryAfter": RetryAfter,
    "AttributedUnsignedLongType": AttributedUnsignedLongType_,
    "ProblemHeaderQName": ProblemHeaderQName,
    "AttributedQNameType": AttributedQNameType_,
    "ProblemIRI": ProblemIRI,
    "ProblemAction": ProblemAction,
    "ProblemActionType": ProblemActionType_,
    "Address": EndpointReferenceType_Address,
    "SoapAction": ProblemActionType_SoapAction,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
