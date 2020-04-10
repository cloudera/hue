#!/usr/bin/env python

#
# Generated Sun Jun 14 13:35:32 2015 by parse_xsd.py version 0.5.
#

import saml2
from saml2 import SamlBase

from saml2.ws import wssec as wsse
from saml2.ws import wsutil as wsu

NAMESPACE = 'http://schemas.xmlsoap.org/ws/2004/09/policy'

class PolicyReference(SamlBase):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:PolicyReference element """

    c_tag = 'PolicyReference'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['URI'] = ('uri', 'anyURI', True)
    c_attributes['Digest'] = ('digest', 'base64Binary', False)
    c_attributes['DigestAlgorithm'] = ('digest_algorithm', 'anyURI', False)

    def __init__(self,
            uri=None,
            digest=None,
            digest_algorithm='http://schemas.xmlsoap.org/ws/2004/09/policy/Sha1Exc',
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.uri=uri
        self.digest=digest
        self.digest_algorithm=digest_algorithm

def policy_reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(PolicyReference, xml_string)


class AppliesTo(SamlBase):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:AppliesTo element """

    c_tag = 'AppliesTo'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()

def applies_to_from_string(xml_string):
    return saml2.create_class_from_xml_string(AppliesTo, xml_string)


class PolicyAttachment(SamlBase):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:PolicyAttachment element """

    c_tag = 'PolicyAttachment'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}AppliesTo'] = ('applies_to', AppliesTo)
    c_cardinality['policy'] = {"min":0}
    c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}PolicyReference'] = ('policy_reference', [PolicyReference])
    c_cardinality['policy_reference'] = {"min":0}
    c_child_order.extend(['applies_to', 'policy', 'policy_reference'])

    def __init__(self,
            applies_to=None,
            policy=None,
            policy_reference=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.applies_to=applies_to
        self.policy=policy or []
        self.policy_reference=policy_reference or []

def policy_attachment_from_string(xml_string):
    return saml2.create_class_from_xml_string(PolicyAttachment, xml_string)


class OperatorContentType_(SamlBase):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:OperatorContentType element """

    c_tag = 'OperatorContentType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_cardinality['policy'] = {"min":0}
    c_cardinality['all'] = {"min":0}
    c_cardinality['exactly_one'] = {"min":0}
    c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}PolicyReference'] = ('policy_reference', [PolicyReference])
    c_cardinality['policy_reference'] = {"min":0}
    c_child_order.extend(['policy', 'all', 'exactly_one', 'policy_reference'])

    def __init__(self,
            policy=None,
            all=None,
            exactly_one=None,
            policy_reference=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        SamlBase.__init__(self, 
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.policy=policy or []
        self.all=all or []
        self.exactly_one=exactly_one or []
        self.policy_reference=policy_reference or []

def operator_content_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(OperatorContentType_, xml_string)


class Policy(OperatorContentType_):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:Policy element """

    c_tag = 'Policy'
    c_namespace = NAMESPACE
    c_children = OperatorContentType_.c_children.copy()
    c_attributes = OperatorContentType_.c_attributes.copy()
    c_child_order = OperatorContentType_.c_child_order[:]
    c_cardinality = OperatorContentType_.c_cardinality.copy()
    c_attributes['Name'] = ('name', 'anyURI', False)
    c_attributes['{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id'] = ('Id', 'tns:OperatorContentType', False)

    def __init__(self,
            name=None,
            Id=None,
            policy=None,
            all=None,
            exactly_one=None,
            policy_reference=None,
            text=None,
            extension_elements=None,
            extension_attributes=None,
        ):
        OperatorContentType_.__init__(self, 
                policy=policy,
                all=all,
                exactly_one=exactly_one,
                policy_reference=policy_reference,
                text=text,
                extension_elements=extension_elements,
                extension_attributes=extension_attributes,
                )
        self.name=name
        self.Id=Id

def policy_from_string(xml_string):
    return saml2.create_class_from_xml_string(Policy, xml_string)


class All(OperatorContentType_):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:All element """

    c_tag = 'All'
    c_namespace = NAMESPACE
    c_children = OperatorContentType_.c_children.copy()
    c_attributes = OperatorContentType_.c_attributes.copy()
    c_child_order = OperatorContentType_.c_child_order[:]
    c_cardinality = OperatorContentType_.c_cardinality.copy()

def all_from_string(xml_string):
    return saml2.create_class_from_xml_string(All, xml_string)


class ExactlyOne(OperatorContentType_):
    """The http://schemas.xmlsoap.org/ws/2004/09/policy:ExactlyOne element """

    c_tag = 'ExactlyOne'
    c_namespace = NAMESPACE
    c_children = OperatorContentType_.c_children.copy()
    c_attributes = OperatorContentType_.c_attributes.copy()
    c_child_order = OperatorContentType_.c_child_order[:]
    c_cardinality = OperatorContentType_.c_cardinality.copy()

def exactly_one_from_string(xml_string):
    return saml2.create_class_from_xml_string(ExactlyOne, xml_string)

PolicyAttachment.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}Policy'] = ('policy', [Policy])
OperatorContentType_.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}Policy'] = ('policy', [Policy])
Policy.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}Policy'] = ('policy', [Policy])
ExactlyOne.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}Policy'] = ('policy', [Policy])
All.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}Policy'] = ('policy', [Policy])
OperatorContentType_.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}All'] = ('all', [All])
Policy.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}All'] = ('all', [All])
ExactlyOne.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}All'] = ('all', [All])
All.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}All'] = ('all', [All])
OperatorContentType_.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}ExactlyOne'] = ('exactly_one', [ExactlyOne])
Policy.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}ExactlyOne'] = ('exactly_one', [ExactlyOne])
ExactlyOne.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}ExactlyOne'] = ('exactly_one', [ExactlyOne])
All.c_children['{http://schemas.xmlsoap.org/ws/2004/09/policy}ExactlyOne'] = ('exactly_one', [ExactlyOne])

ELEMENT_FROM_STRING = {
    Policy.c_tag: policy_from_string,
    All.c_tag: all_from_string,
    ExactlyOne.c_tag: exactly_one_from_string,
    OperatorContentType_.c_tag: operator_content_type__from_string,
    PolicyReference.c_tag: policy_reference_from_string,
    PolicyAttachment.c_tag: policy_attachment_from_string,
    AppliesTo.c_tag: applies_to_from_string,
}

ELEMENT_BY_TAG = {
    'Policy': Policy,
    'All': All,
    'ExactlyOne': ExactlyOne,
    'OperatorContentType': OperatorContentType_,
    'PolicyReference': PolicyReference,
    'PolicyAttachment': PolicyAttachment,
    'AppliesTo': AppliesTo,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

