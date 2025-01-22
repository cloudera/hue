#!/usr/bin/env python

#
# Generated Mon May  2 14:23:33 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase
from saml2 import md


NAMESPACE = "urn:oasis:names:tc:SAML:metadata:ui"


class DisplayName(md.LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:DisplayName element"""

    c_tag = "DisplayName"
    c_namespace = NAMESPACE
    c_children = md.LocalizedNameType_.c_children.copy()
    c_attributes = md.LocalizedNameType_.c_attributes.copy()
    c_child_order = md.LocalizedNameType_.c_child_order[:]
    c_cardinality = md.LocalizedNameType_.c_cardinality.copy()


def display_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(DisplayName, xml_string)


class Description(md.LocalizedNameType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:Description element"""

    c_tag = "Description"
    c_namespace = NAMESPACE
    c_children = md.LocalizedNameType_.c_children.copy()
    c_attributes = md.LocalizedNameType_.c_attributes.copy()
    c_child_order = md.LocalizedNameType_.c_child_order[:]
    c_cardinality = md.LocalizedNameType_.c_cardinality.copy()


def description_from_string(xml_string):
    return saml2.create_class_from_xml_string(Description, xml_string)


class InformationURL(md.LocalizedURIType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:InformationURL element"""

    c_tag = "InformationURL"
    c_namespace = NAMESPACE
    c_children = md.LocalizedURIType_.c_children.copy()
    c_attributes = md.LocalizedURIType_.c_attributes.copy()
    c_child_order = md.LocalizedURIType_.c_child_order[:]
    c_cardinality = md.LocalizedURIType_.c_cardinality.copy()


def information_url_from_string(xml_string):
    return saml2.create_class_from_xml_string(InformationURL, xml_string)


class PrivacyStatementURL(md.LocalizedURIType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:PrivacyStatementURL element"""

    c_tag = "PrivacyStatementURL"
    c_namespace = NAMESPACE
    c_children = md.LocalizedURIType_.c_children.copy()
    c_attributes = md.LocalizedURIType_.c_attributes.copy()
    c_child_order = md.LocalizedURIType_.c_child_order[:]
    c_cardinality = md.LocalizedURIType_.c_cardinality.copy()


def privacy_statement_url_from_string(xml_string):
    return saml2.create_class_from_xml_string(PrivacyStatementURL, xml_string)


class ListOfStrings_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:listOfStrings element"""

    c_tag = "listOfStrings"
    c_namespace = NAMESPACE
    c_value_type = {"member": "string", "base": "list"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def list_of_strings__from_string(xml_string):
    return saml2.create_class_from_xml_string(ListOfStrings_, xml_string)


class KeywordsType_(ListOfStrings_):
    """The urn:oasis:names:tc:SAML:metadata:ui:KeywordsType element"""

    c_tag = "KeywordsType"
    c_namespace = NAMESPACE
    c_children = ListOfStrings_.c_children.copy()
    c_attributes = ListOfStrings_.c_attributes.copy()
    c_child_order = ListOfStrings_.c_child_order[:]
    c_cardinality = ListOfStrings_.c_cardinality.copy()
    c_attributes["{http://www.w3.org/XML/1998/namespace}lang"] = ("lang", "mdui:listOfStrings", True)

    def __init__(self, lang=None, text=None, extension_elements=None, extension_attributes=None):
        ListOfStrings_.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.lang = lang


def keywords_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeywordsType_, xml_string)


class LogoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:LogoType element"""

    c_tag = "LogoType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["height"] = ("height", "positiveInteger", True)
    c_attributes["width"] = ("width", "positiveInteger", True)
    c_attributes["{http://www.w3.org/XML/1998/namespace}lang"] = ("lang", "anyURI", False)

    def __init__(
        self, height=None, width=None, lang=None, text=None, extension_elements=None, extension_attributes=None
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.height = height
        self.width = width
        self.lang = lang


def logo_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(LogoType_, xml_string)


class IPHint(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:IPHint element"""

    c_tag = "IPHint"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def ip_hint_from_string(xml_string):
    return saml2.create_class_from_xml_string(IPHint, xml_string)


class DomainHint(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:DomainHint element"""

    c_tag = "DomainHint"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def domain_hint_from_string(xml_string):
    return saml2.create_class_from_xml_string(DomainHint, xml_string)


class GeolocationHint(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:GeolocationHint element"""

    c_tag = "GeolocationHint"
    c_namespace = NAMESPACE
    c_value_type = {"base": "anyURI"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def geolocation_hint_from_string(xml_string):
    return saml2.create_class_from_xml_string(GeolocationHint, xml_string)


class Keywords(KeywordsType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:Keywords element"""

    c_tag = "Keywords"
    c_namespace = NAMESPACE
    c_children = KeywordsType_.c_children.copy()
    c_attributes = KeywordsType_.c_attributes.copy()
    c_child_order = KeywordsType_.c_child_order[:]
    c_cardinality = KeywordsType_.c_cardinality.copy()


def keywords_from_string(xml_string):
    return saml2.create_class_from_xml_string(Keywords, xml_string)


class Logo(LogoType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:Logo element"""

    c_tag = "Logo"
    c_namespace = NAMESPACE
    c_children = LogoType_.c_children.copy()
    c_attributes = LogoType_.c_attributes.copy()
    c_child_order = LogoType_.c_child_order[:]
    c_cardinality = LogoType_.c_cardinality.copy()


def logo_from_string(xml_string):
    return saml2.create_class_from_xml_string(Logo, xml_string)


class DiscoHintsType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:DiscoHintsType element"""

    c_tag = "DiscoHintsType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}IPHint"] = ("ip_hint", [IPHint])
    c_cardinality["ip_hint"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}DomainHint"] = ("domain_hint", [DomainHint])
    c_cardinality["domain_hint"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}GeolocationHint"] = ("geolocation_hint", [GeolocationHint])
    c_cardinality["geolocation_hint"] = {"min": 0}
    c_child_order.extend(["ip_hint", "domain_hint", "geolocation_hint"])

    def __init__(
        self,
        ip_hint=None,
        domain_hint=None,
        geolocation_hint=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.ip_hint = ip_hint or []
        self.domain_hint = domain_hint or []
        self.geolocation_hint = geolocation_hint or []


def disco_hints_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DiscoHintsType_, xml_string)


class UIInfoType_(SamlBase):
    """The urn:oasis:names:tc:SAML:metadata:ui:UIInfoType element"""

    c_tag = "UIInfoType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}DisplayName"] = ("display_name", [DisplayName])
    c_cardinality["display_name"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}Description"] = ("description", [Description])
    c_cardinality["description"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}Keywords"] = ("keywords", [Keywords])
    c_cardinality["keywords"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}Logo"] = ("logo", [Logo])
    c_cardinality["logo"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}InformationURL"] = ("information_url", [InformationURL])
    c_cardinality["information_url"] = {"min": 0}
    c_children["{urn:oasis:names:tc:SAML:metadata:ui}PrivacyStatementURL"] = (
        "privacy_statement_url",
        [PrivacyStatementURL],
    )
    c_cardinality["privacy_statement_url"] = {"min": 0}
    c_child_order.extend(
        ["display_name", "description", "keywords", "logo", "information_url", "privacy_statement_url"]
    )

    def __init__(
        self,
        display_name=None,
        description=None,
        keywords=None,
        logo=None,
        information_url=None,
        privacy_statement_url=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.display_name = display_name or []
        self.description = description or []
        self.keywords = keywords or []
        self.logo = logo or []
        self.information_url = information_url or []
        self.privacy_statement_url = privacy_statement_url or []


def ui_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(UIInfoType_, xml_string)


class DiscoHints(DiscoHintsType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:DiscoHints element"""

    c_tag = "DiscoHints"
    c_namespace = NAMESPACE
    c_children = DiscoHintsType_.c_children.copy()
    c_attributes = DiscoHintsType_.c_attributes.copy()
    c_child_order = DiscoHintsType_.c_child_order[:]
    c_cardinality = DiscoHintsType_.c_cardinality.copy()


def disco_hints_from_string(xml_string):
    return saml2.create_class_from_xml_string(DiscoHints, xml_string)


class UIInfo(UIInfoType_):
    """The urn:oasis:names:tc:SAML:metadata:ui:UIInfo element"""

    c_tag = "UIInfo"
    c_namespace = NAMESPACE
    c_children = UIInfoType_.c_children.copy()
    c_attributes = UIInfoType_.c_attributes.copy()
    c_child_order = UIInfoType_.c_child_order[:]
    c_cardinality = UIInfoType_.c_cardinality.copy()


def ui_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(UIInfo, xml_string)


ELEMENT_FROM_STRING = {
    UIInfo.c_tag: ui_info_from_string,
    UIInfoType_.c_tag: ui_info_type__from_string,
    DisplayName.c_tag: display_name_from_string,
    Description.c_tag: description_from_string,
    InformationURL.c_tag: information_url_from_string,
    PrivacyStatementURL.c_tag: privacy_statement_url_from_string,
    Keywords.c_tag: keywords_from_string,
    KeywordsType_.c_tag: keywords_type__from_string,
    ListOfStrings_.c_tag: list_of_strings__from_string,
    Logo.c_tag: logo_from_string,
    LogoType_.c_tag: logo_type__from_string,
    DiscoHints.c_tag: disco_hints_from_string,
    DiscoHintsType_.c_tag: disco_hints_type__from_string,
    IPHint.c_tag: ip_hint_from_string,
    DomainHint.c_tag: domain_hint_from_string,
    GeolocationHint.c_tag: geolocation_hint_from_string,
}

ELEMENT_BY_TAG = {
    "UIInfo": UIInfo,
    "UIInfoType": UIInfoType_,
    "DisplayName": DisplayName,
    "Description": Description,
    "InformationURL": InformationURL,
    "PrivacyStatementURL": PrivacyStatementURL,
    "Keywords": Keywords,
    "KeywordsType": KeywordsType_,
    "listOfStrings": ListOfStrings_,
    "Logo": Logo,
    "LogoType": LogoType_,
    "DiscoHints": DiscoHints,
    "DiscoHintsType": DiscoHintsType_,
    "IPHint": IPHint,
    "DomainHint": DomainHint,
    "GeolocationHint": GeolocationHint,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
