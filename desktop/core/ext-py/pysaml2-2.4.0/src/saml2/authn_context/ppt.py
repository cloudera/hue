#!/usr/bin/env python

#
# Generated Sun Apr 21 10:23:51 2013 by parse_xsd.py version 0.5.
#

"""The PasswordProtectedTransport class is applicable when a principal
authenticates to an authentication authority through the presentation of a
password over a protected session."""

import saml2
from saml2 import SamlBase


NAMESPACE = 'urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport'


class PhysicalVerification(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PhysicalVerification element """

    c_tag = 'PhysicalVerification'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['credentialLevel'] = ('credential_level', 'None', False)

    def __init__(self,
                 credential_level=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.credential_level = credential_level


def physical_verification_from_string(xml_string):
    return saml2.create_class_from_xml_string(PhysicalVerification, xml_string)


class Generation(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Generation element """

    c_tag = 'Generation'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['mechanism'] = ('mechanism', 'None', True)

    def __init__(self,
                 mechanism=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.mechanism = mechanism


def generation_from_string(xml_string):
    return saml2.create_class_from_xml_string(Generation, xml_string)


class NymType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:nymType element """

    c_tag = 'nymType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'xs:NMTOKEN',
                    'enumeration': ['anonymity', 'verinymity', 'pseudonymity']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def nym_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(NymType_, xml_string)


class GoverningAgreementRefType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:GoverningAgreementRefType element """

    c_tag = 'GoverningAgreementRefType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['governingAgreementRef'] = (
        'governing_agreement_ref', 'anyURI', True)

    def __init__(self,
                 governing_agreement_ref=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.governing_agreement_ref = governing_agreement_ref


def governing_agreement_ref_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(GoverningAgreementRefType_,
                                              xml_string)


class KeySharingType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeySharingType element """

    c_tag = 'KeySharingType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['sharing'] = ('sharing', 'boolean', True)

    def __init__(self,
                 sharing=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.sharing = sharing


def key_sharing_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeySharingType_, xml_string)


class RestrictedLengthType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:RestrictedLengthType element """

    c_tag = 'RestrictedLengthType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['min'] = ('min', 'None', True)
    c_attributes['max'] = ('max', 'integer', False)

    def __init__(self,
                 min=None,
                 max=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.min = min
        self.max = max


def restricted_length_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RestrictedLengthType_, xml_string)


class AlphabetType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AlphabetType element """

    c_tag = 'AlphabetType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['requiredChars'] = ('required_chars', 'string', True)
    c_attributes['excludedChars'] = ('excluded_chars', 'string', False)
    c_attributes['case'] = ('case', 'string', False)

    def __init__(self,
                 required_chars=None,
                 excluded_chars=None,
                 case=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.required_chars = required_chars
        self.excluded_chars = excluded_chars
        self.case = case


def alphabet_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AlphabetType_, xml_string)


class DeviceTypeType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:DeviceTypeType element """

    c_tag = 'DeviceTypeType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'xs:NMTOKEN',
                    'enumeration': ['hardware', 'software']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def device_type_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DeviceTypeType_, xml_string)


class BooleanType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:booleanType element """

    c_tag = 'booleanType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'xs:NMTOKEN', 'enumeration': ['true', 'false']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def boolean_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(BooleanType_, xml_string)


class TimeSyncTokenType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:TimeSyncTokenType element """

    c_tag = 'TimeSyncTokenType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['DeviceType'] = ('device_type', DeviceTypeType_, True)
    c_attributes['SeedLength'] = ('seed_length', 'integer', True)
    c_attributes['DeviceInHand'] = ('device_in_hand', BooleanType_, True)

    def __init__(self,
                 device_type=None,
                 seed_length=None,
                 device_in_hand=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.device_type = device_type
        self.seed_length = seed_length
        self.device_in_hand = device_in_hand


def time_sync_token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TimeSyncTokenType_, xml_string)


class ActivationLimitDurationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitDurationType element """

    c_tag = 'ActivationLimitDurationType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['duration'] = ('duration', 'duration', True)

    def __init__(self,
                 duration=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.duration = duration


def activation_limit_duration_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitDurationType_,
                                              xml_string)


class ActivationLimitUsagesType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitUsagesType element """

    c_tag = 'ActivationLimitUsagesType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['number'] = ('number', 'integer', True)

    def __init__(self,
                 number=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.number = number


def activation_limit_usages_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitUsagesType_,
                                              xml_string)


class ActivationLimitSessionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitSessionType element """

    c_tag = 'ActivationLimitSessionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def activation_limit_session_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitSessionType_,
                                              xml_string)


class LengthType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:LengthType element """

    c_tag = 'LengthType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['min'] = ('min', 'integer', True)
    c_attributes['max'] = ('max', 'integer', False)

    def __init__(self,
                 min=None,
                 max=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.min = min
        self.max = max


def length_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(LengthType_, xml_string)


class MediumType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:mediumType element """

    c_tag = 'mediumType'
    c_namespace = NAMESPACE
    c_value_type = {'base': 'xs:NMTOKEN',
                    'enumeration': ['memory', 'smartcard', 'token',
                                    'MobileDevice', 'MobileAuthCard']}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def medium_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(MediumType_, xml_string)


class KeyStorageType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeyStorageType element """

    c_tag = 'KeyStorageType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes['medium'] = ('medium', MediumType_, True)

    def __init__(self,
                 medium=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.medium = medium


def key_storage_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyStorageType_, xml_string)


class ExtensionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ExtensionType element """

    c_tag = 'ExtensionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def extension_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ExtensionType_, xml_string)


class KeySharing(KeySharingType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeySharing element """

    c_tag = 'KeySharing'
    c_namespace = NAMESPACE
    c_children = KeySharingType_.c_children.copy()
    c_attributes = KeySharingType_.c_attributes.copy()
    c_child_order = KeySharingType_.c_child_order[:]
    c_cardinality = KeySharingType_.c_cardinality.copy()


def key_sharing_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeySharing, xml_string)


class KeyStorage(KeyStorageType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeyStorage element """

    c_tag = 'KeyStorage'
    c_namespace = NAMESPACE
    c_children = KeyStorageType_.c_children.copy()
    c_attributes = KeyStorageType_.c_attributes.copy()
    c_child_order = KeyStorageType_.c_child_order[:]
    c_cardinality = KeyStorageType_.c_cardinality.copy()


def key_storage_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyStorage, xml_string)


class TimeSyncToken(TimeSyncTokenType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:TimeSyncToken element """

    c_tag = 'TimeSyncToken'
    c_namespace = NAMESPACE
    c_children = TimeSyncTokenType_.c_children.copy()
    c_attributes = TimeSyncTokenType_.c_attributes.copy()
    c_child_order = TimeSyncTokenType_.c_child_order[:]
    c_cardinality = TimeSyncTokenType_.c_cardinality.copy()


def time_sync_token_from_string(xml_string):
    return saml2.create_class_from_xml_string(TimeSyncToken, xml_string)


class Length(LengthType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Length element """

    c_tag = 'Length'
    c_namespace = NAMESPACE
    c_children = LengthType_.c_children.copy()
    c_attributes = LengthType_.c_attributes.copy()
    c_child_order = LengthType_.c_child_order[:]
    c_cardinality = LengthType_.c_cardinality.copy()


def length_from_string(xml_string):
    return saml2.create_class_from_xml_string(Length, xml_string)


class GoverningAgreementRef(GoverningAgreementRefType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:GoverningAgreementRef element """

    c_tag = 'GoverningAgreementRef'
    c_namespace = NAMESPACE
    c_children = GoverningAgreementRefType_.c_children.copy()
    c_attributes = GoverningAgreementRefType_.c_attributes.copy()
    c_child_order = GoverningAgreementRefType_.c_child_order[:]
    c_cardinality = GoverningAgreementRefType_.c_cardinality.copy()


def governing_agreement_ref_from_string(xml_string):
    return saml2.create_class_from_xml_string(GoverningAgreementRef, xml_string)


class GoverningAgreementsType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:GoverningAgreementsType element """

    c_tag = 'GoverningAgreementsType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreementRef'] = (
        'governing_agreement_ref', [GoverningAgreementRef])
    c_cardinality['governing_agreement_ref'] = {"min": 1}
    c_child_order.extend(['governing_agreement_ref'])

    def __init__(self,
                 governing_agreement_ref=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.governing_agreement_ref = governing_agreement_ref or []


def governing_agreements_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(GoverningAgreementsType_,
                                              xml_string)


class RestrictedPasswordType_Length(RestrictedLengthType_):
    c_tag = 'Length'
    c_namespace = NAMESPACE
    c_children = RestrictedLengthType_.c_children.copy()
    c_attributes = RestrictedLengthType_.c_attributes.copy()
    c_child_order = RestrictedLengthType_.c_child_order[:]
    c_cardinality = RestrictedLengthType_.c_cardinality.copy()


def restricted_password_type__length_from_string(xml_string):
    return saml2.create_class_from_xml_string(RestrictedPasswordType_Length,
                                              xml_string)


class Alphabet(AlphabetType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Alphabet element """

    c_tag = 'Alphabet'
    c_namespace = NAMESPACE
    c_children = AlphabetType_.c_children.copy()
    c_attributes = AlphabetType_.c_attributes.copy()
    c_child_order = AlphabetType_.c_child_order[:]
    c_cardinality = AlphabetType_.c_cardinality.copy()


def alphabet_from_string(xml_string):
    return saml2.create_class_from_xml_string(Alphabet, xml_string)


class ActivationLimitDuration(ActivationLimitDurationType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitDuration element """

    c_tag = 'ActivationLimitDuration'
    c_namespace = NAMESPACE
    c_children = ActivationLimitDurationType_.c_children.copy()
    c_attributes = ActivationLimitDurationType_.c_attributes.copy()
    c_child_order = ActivationLimitDurationType_.c_child_order[:]
    c_cardinality = ActivationLimitDurationType_.c_cardinality.copy()


def activation_limit_duration_from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitDuration,
                                              xml_string)


class ActivationLimitUsages(ActivationLimitUsagesType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitUsages element """

    c_tag = 'ActivationLimitUsages'
    c_namespace = NAMESPACE
    c_children = ActivationLimitUsagesType_.c_children.copy()
    c_attributes = ActivationLimitUsagesType_.c_attributes.copy()
    c_child_order = ActivationLimitUsagesType_.c_child_order[:]
    c_cardinality = ActivationLimitUsagesType_.c_cardinality.copy()


def activation_limit_usages_from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitUsages, xml_string)


class ActivationLimitSession(ActivationLimitSessionType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitSession element """

    c_tag = 'ActivationLimitSession'
    c_namespace = NAMESPACE
    c_children = ActivationLimitSessionType_.c_children.copy()
    c_attributes = ActivationLimitSessionType_.c_attributes.copy()
    c_child_order = ActivationLimitSessionType_.c_child_order[:]
    c_cardinality = ActivationLimitSessionType_.c_cardinality.copy()


def activation_limit_session_from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitSession,
                                              xml_string)


class Extension(ExtensionType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Extension element """

    c_tag = 'Extension'
    c_namespace = NAMESPACE
    c_children = ExtensionType_.c_children.copy()
    c_attributes = ExtensionType_.c_attributes.copy()
    c_child_order = ExtensionType_.c_child_order[:]
    c_cardinality = ExtensionType_.c_cardinality.copy()


def extension_from_string(xml_string):
    return saml2.create_class_from_xml_string(Extension, xml_string)


class SharedSecretChallengeResponseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SharedSecretChallengeResponseType element """

    c_tag = 'SharedSecretChallengeResponseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['method'] = ('method', 'anyURI', False)
    c_child_order.extend(['extension'])

    def __init__(self,
                 extension=None,
                 method=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.extension = extension or []
        self.method = method


def shared_secret_challenge_response_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(
        SharedSecretChallengeResponseType_, xml_string)


class PublicKeyType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PublicKeyType element """

    c_tag = 'PublicKeyType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['keyValidation'] = ('key_validation', 'None', False)
    c_child_order.extend(['extension'])

    def __init__(self,
                 extension=None,
                 key_validation=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.extension = extension or []
        self.key_validation = key_validation


def public_key_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PublicKeyType_, xml_string)


class GoverningAgreements(GoverningAgreementsType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:GoverningAgreements element """

    c_tag = 'GoverningAgreements'
    c_namespace = NAMESPACE
    c_children = GoverningAgreementsType_.c_children.copy()
    c_attributes = GoverningAgreementsType_.c_attributes.copy()
    c_child_order = GoverningAgreementsType_.c_child_order[:]
    c_cardinality = GoverningAgreementsType_.c_cardinality.copy()


def governing_agreements_from_string(xml_string):
    return saml2.create_class_from_xml_string(GoverningAgreements, xml_string)


class PasswordType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PasswordType element """

    c_tag = 'PasswordType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Length'] = (
        'length', Length)
    c_cardinality['length'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Alphabet'] = (
        'alphabet', Alphabet)
    c_cardinality['alphabet'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation'] = (
        'generation', Generation)
    c_cardinality['generation'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['ExternalVerification'] = (
        'external_verification', 'anyURI', False)
    c_child_order.extend(['length', 'alphabet', 'generation', 'extension'])

    def __init__(self,
                 length=None,
                 alphabet=None,
                 generation=None,
                 extension=None,
                 external_verification=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.length = length
        self.alphabet = alphabet
        self.generation = generation
        self.extension = extension or []
        self.external_verification = external_verification


def password_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PasswordType_, xml_string)


class RestrictedPasswordType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:RestrictedPasswordType element """

    c_tag = 'RestrictedPasswordType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Length'] = (
        'length', RestrictedPasswordType_Length)
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation'] = (
        'generation', Generation)
    c_cardinality['generation'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['ExternalVerification'] = (
        'external_verification', 'anyURI', False)
    c_child_order.extend(['length', 'generation', 'extension'])

    def __init__(self,
                 length=None,
                 generation=None,
                 extension=None,
                 external_verification=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.length = length
        self.generation = generation
        self.extension = extension or []
        self.external_verification = external_verification


def restricted_password_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RestrictedPasswordType_,
                                              xml_string)


class TokenType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:TokenType element """

    c_tag = 'TokenType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}TimeSyncToken'] = (
        'time_sync_token', TimeSyncToken)
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['time_sync_token', 'extension'])

    def __init__(self,
                 time_sync_token=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.time_sync_token = time_sync_token
        self.extension = extension or []


def token_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TokenType_, xml_string)


class ActivationLimitType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimitType element """

    c_tag = 'ActivationLimitType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitDuration'] = (
        'activation_limit_duration', ActivationLimitDuration)
    c_cardinality['activation_limit_duration'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitUsages'] = (
        'activation_limit_usages', ActivationLimitUsages)
    c_cardinality['activation_limit_usages'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimitSession'] = (
        'activation_limit_session', ActivationLimitSession)
    c_cardinality['activation_limit_session'] = {"min": 0, "max": 1}
    c_child_order.extend(
        ['activation_limit_duration', 'activation_limit_usages',
         'activation_limit_session'])

    def __init__(self,
                 activation_limit_duration=None,
                 activation_limit_usages=None,
                 activation_limit_session=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.activation_limit_duration = activation_limit_duration
        self.activation_limit_usages = activation_limit_usages
        self.activation_limit_session = activation_limit_session


def activation_limit_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimitType_, xml_string)


class ExtensionOnlyType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ExtensionOnlyType element """

    c_tag = 'ExtensionOnlyType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['extension'])

    def __init__(self,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.extension = extension or []


def extension_only_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ExtensionOnlyType_, xml_string)


class WrittenConsent(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:WrittenConsent element """

    c_tag = 'WrittenConsent'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def written_consent_from_string(xml_string):
    return saml2.create_class_from_xml_string(WrittenConsent, xml_string)


class SubscriberLineNumber(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SubscriberLineNumber element """

    c_tag = 'SubscriberLineNumber'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def subscriber_line_number_from_string(xml_string):
    return saml2.create_class_from_xml_string(SubscriberLineNumber, xml_string)


class UserSuffix(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:UserSuffix element """

    c_tag = 'UserSuffix'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def user_suffix_from_string(xml_string):
    return saml2.create_class_from_xml_string(UserSuffix, xml_string)


class Password(PasswordType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Password element """

    c_tag = 'Password'
    c_namespace = NAMESPACE
    c_children = PasswordType_.c_children.copy()
    c_attributes = PasswordType_.c_attributes.copy()
    c_child_order = PasswordType_.c_child_order[:]
    c_cardinality = PasswordType_.c_cardinality.copy()


def password_from_string(xml_string):
    return saml2.create_class_from_xml_string(Password, xml_string)


class Token(TokenType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Token element """

    c_tag = 'Token'
    c_namespace = NAMESPACE
    c_children = TokenType_.c_children.copy()
    c_attributes = TokenType_.c_attributes.copy()
    c_child_order = TokenType_.c_child_order[:]
    c_cardinality = TokenType_.c_cardinality.copy()


def token_from_string(xml_string):
    return saml2.create_class_from_xml_string(Token, xml_string)


class Smartcard(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Smartcard element """

    c_tag = 'Smartcard'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def smartcard_from_string(xml_string):
    return saml2.create_class_from_xml_string(Smartcard, xml_string)


class ActivationLimit(ActivationLimitType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationLimit element """

    c_tag = 'ActivationLimit'
    c_namespace = NAMESPACE
    c_children = ActivationLimitType_.c_children.copy()
    c_attributes = ActivationLimitType_.c_attributes.copy()
    c_child_order = ActivationLimitType_.c_child_order[:]
    c_cardinality = ActivationLimitType_.c_cardinality.copy()


def activation_limit_from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationLimit, xml_string)


class PreviousSession(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PreviousSession element """

    c_tag = 'PreviousSession'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def previous_session_from_string(xml_string):
    return saml2.create_class_from_xml_string(PreviousSession, xml_string)


class ResumeSession(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ResumeSession element """

    c_tag = 'ResumeSession'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def resume_session_from_string(xml_string):
    return saml2.create_class_from_xml_string(ResumeSession, xml_string)


class ZeroKnowledge(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ZeroKnowledge element """

    c_tag = 'ZeroKnowledge'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def zero_knowledge_from_string(xml_string):
    return saml2.create_class_from_xml_string(ZeroKnowledge, xml_string)


class SharedSecretChallengeResponse(SharedSecretChallengeResponseType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SharedSecretChallengeResponse element """

    c_tag = 'SharedSecretChallengeResponse'
    c_namespace = NAMESPACE
    c_children = SharedSecretChallengeResponseType_.c_children.copy()
    c_attributes = SharedSecretChallengeResponseType_.c_attributes.copy()
    c_child_order = SharedSecretChallengeResponseType_.c_child_order[:]
    c_cardinality = SharedSecretChallengeResponseType_.c_cardinality.copy()


def shared_secret_challenge_response_from_string(xml_string):
    return saml2.create_class_from_xml_string(SharedSecretChallengeResponse,
                                              xml_string)


class DigSig(PublicKeyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:DigSig element """

    c_tag = 'DigSig'
    c_namespace = NAMESPACE
    c_children = PublicKeyType_.c_children.copy()
    c_attributes = PublicKeyType_.c_attributes.copy()
    c_child_order = PublicKeyType_.c_child_order[:]
    c_cardinality = PublicKeyType_.c_cardinality.copy()


def dig_sig_from_string(xml_string):
    return saml2.create_class_from_xml_string(DigSig, xml_string)


class AsymmetricDecryption(PublicKeyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AsymmetricDecryption element """

    c_tag = 'AsymmetricDecryption'
    c_namespace = NAMESPACE
    c_children = PublicKeyType_.c_children.copy()
    c_attributes = PublicKeyType_.c_attributes.copy()
    c_child_order = PublicKeyType_.c_child_order[:]
    c_cardinality = PublicKeyType_.c_cardinality.copy()


def asymmetric_decryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(AsymmetricDecryption, xml_string)


class AsymmetricKeyAgreement(PublicKeyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AsymmetricKeyAgreement element """

    c_tag = 'AsymmetricKeyAgreement'
    c_namespace = NAMESPACE
    c_children = PublicKeyType_.c_children.copy()
    c_attributes = PublicKeyType_.c_attributes.copy()
    c_child_order = PublicKeyType_.c_child_order[:]
    c_cardinality = PublicKeyType_.c_cardinality.copy()


def asymmetric_key_agreement_from_string(xml_string):
    return saml2.create_class_from_xml_string(AsymmetricKeyAgreement,
                                              xml_string)


class IPAddress(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:IPAddress element """

    c_tag = 'IPAddress'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def ip_address_from_string(xml_string):
    return saml2.create_class_from_xml_string(IPAddress, xml_string)


class SharedSecretDynamicPlaintext(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SharedSecretDynamicPlaintext element """

    c_tag = 'SharedSecretDynamicPlaintext'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def shared_secret_dynamic_plaintext_from_string(xml_string):
    return saml2.create_class_from_xml_string(SharedSecretDynamicPlaintext,
                                              xml_string)


class HTTP(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:HTTP element """

    c_tag = 'HTTP'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def http_from_string(xml_string):
    return saml2.create_class_from_xml_string(HTTP, xml_string)


class IPSec(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:IPSec element """

    c_tag = 'IPSec'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def ip_sec_from_string(xml_string):
    return saml2.create_class_from_xml_string(IPSec, xml_string)


class WTLS(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:WTLS element """

    c_tag = 'WTLS'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def wtls_from_string(xml_string):
    return saml2.create_class_from_xml_string(WTLS, xml_string)


class MobileNetworkNoEncryption(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:MobileNetworkNoEncryption element """

    c_tag = 'MobileNetworkNoEncryption'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def mobile_network_no_encryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(MobileNetworkNoEncryption,
                                              xml_string)


class MobileNetworkRadioEncryption(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:MobileNetworkRadioEncryption element """

    c_tag = 'MobileNetworkRadioEncryption'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def mobile_network_radio_encryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(MobileNetworkRadioEncryption,
                                              xml_string)


class MobileNetworkEndToEndEncryption(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:MobileNetworkEndToEndEncryption element """

    c_tag = 'MobileNetworkEndToEndEncryption'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def mobile_network_end_to_end_encryption_from_string(xml_string):
    return saml2.create_class_from_xml_string(MobileNetworkEndToEndEncryption,
                                              xml_string)


class SSL(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SSL element """

    c_tag = 'SSL'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def ssl_from_string(xml_string):
    return saml2.create_class_from_xml_string(SSL, xml_string)


class PSTN(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PSTN element """

    c_tag = 'PSTN'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def pstn_from_string(xml_string):
    return saml2.create_class_from_xml_string(PSTN, xml_string)


class ISDN(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ISDN element """

    c_tag = 'ISDN'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def isdn_from_string(xml_string):
    return saml2.create_class_from_xml_string(ISDN, xml_string)


class ADSL(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ADSL element """

    c_tag = 'ADSL'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def adsl_from_string(xml_string):
    return saml2.create_class_from_xml_string(ADSL, xml_string)


class SwitchAudit(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SwitchAudit element """

    c_tag = 'SwitchAudit'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def switch_audit_from_string(xml_string):
    return saml2.create_class_from_xml_string(SwitchAudit, xml_string)


class DeactivationCallCenter(ExtensionOnlyType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:DeactivationCallCenter element """

    c_tag = 'DeactivationCallCenter'
    c_namespace = NAMESPACE
    c_children = ExtensionOnlyType_.c_children.copy()
    c_attributes = ExtensionOnlyType_.c_attributes.copy()
    c_child_order = ExtensionOnlyType_.c_child_order[:]
    c_cardinality = ExtensionOnlyType_.c_cardinality.copy()


def deactivation_call_center_from_string(xml_string):
    return saml2.create_class_from_xml_string(DeactivationCallCenter,
                                              xml_string)


class IdentificationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:IdentificationType element """

    c_tag = 'IdentificationType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PhysicalVerification'] = (
        'physical_verification', PhysicalVerification)
    c_cardinality['physical_verification'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}WrittenConsent'] = (
        'written_consent', WrittenConsent)
    c_cardinality['written_consent'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreements'] = (
        'governing_agreements', GoverningAgreements)
    c_cardinality['governing_agreements'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['nym'] = ('nym', NymType_, False)
    c_child_order.extend(
        ['physical_verification', 'written_consent', 'governing_agreements',
         'extension'])

    def __init__(self,
                 physical_verification=None,
                 written_consent=None,
                 governing_agreements=None,
                 extension=None,
                 nym=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.physical_verification = physical_verification
        self.written_consent = written_consent
        self.governing_agreements = governing_agreements
        self.extension = extension or []
        self.nym = nym


def identification_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(IdentificationType_, xml_string)


class RestrictedPassword(RestrictedPasswordType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:RestrictedPassword element """

    c_tag = 'RestrictedPassword'
    c_namespace = NAMESPACE
    c_children = RestrictedPasswordType_.c_children.copy()
    c_attributes = RestrictedPasswordType_.c_attributes.copy()
    c_child_order = RestrictedPasswordType_.c_child_order[:]
    c_cardinality = RestrictedPasswordType_.c_cardinality.copy()


def restricted_password_from_string(xml_string):
    return saml2.create_class_from_xml_string(RestrictedPassword, xml_string)


class ActivationPinType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationPinType element """

    c_tag = 'ActivationPinType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Length'] = (
        'length', Length)
    c_cardinality['length'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Alphabet'] = (
        'alphabet', Alphabet)
    c_cardinality['alphabet'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Generation'] = (
        'generation', Generation)
    c_cardinality['generation'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationLimit'] = (
        'activation_limit', ActivationLimit)
    c_cardinality['activation_limit'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(
        ['length', 'alphabet', 'generation', 'activation_limit', 'extension'])

    def __init__(self,
                 length=None,
                 alphabet=None,
                 generation=None,
                 activation_limit=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.length = length
        self.alphabet = alphabet
        self.generation = generation
        self.activation_limit = activation_limit
        self.extension = extension or []


def activation_pin_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationPinType_, xml_string)


class SecurityAuditType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SecurityAuditType element """

    c_tag = 'SecurityAuditType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SwitchAudit'] = (
        'switch_audit', SwitchAudit)
    c_cardinality['switch_audit'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['switch_audit', 'extension'])

    def __init__(self,
                 switch_audit=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.switch_audit = switch_audit
        self.extension = extension or []


def security_audit_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SecurityAuditType_, xml_string)


class AuthenticatorBaseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthenticatorBaseType element """

    c_tag = 'AuthenticatorBaseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword'] = (
        'restricted_password', RestrictedPassword)
    c_child_order.extend(['restricted_password'])

    def __init__(self,
                 restricted_password=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.restricted_password = restricted_password


def authenticator_base_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticatorBaseType_,
                                              xml_string)


class AuthenticatorTransportProtocolType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthenticatorTransportProtocolType element """

    c_tag = 'AuthenticatorTransportProtocolType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SSL'] = (
        'ssl', SSL)
    c_cardinality['ssl'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}MobileNetworkRadioEncryption'] = (
        'mobile_network_radio_encryption', MobileNetworkRadioEncryption)
    c_cardinality['mobile_network_radio_encryption'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}MobileNetworkEndToEndEncryption'] = (
        'mobile_network_end_to_end_encryption', MobileNetworkEndToEndEncryption)
    c_cardinality['mobile_network_end_to_end_encryption'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}WTLS'] = (
        'wtls', WTLS)
    c_cardinality['wtls'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}IPSec'] = (
        'ip_sec', IPSec)
    c_cardinality['ip_sec'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['ssl', 'mobile_network_radio_encryption',
                          'mobile_network_end_to_end_encryption', 'wtls',
                          'ip_sec', 'extension'])

    def __init__(self,
                 ssl=None,
                 mobile_network_radio_encryption=None,
                 mobile_network_end_to_end_encryption=None,
                 wtls=None,
                 ip_sec=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.ssl = ssl
        self.mobile_network_radio_encryption = mobile_network_radio_encryption
        self.mobile_network_end_to_end_encryption = mobile_network_end_to_end_encryption
        self.wtls = wtls
        self.ip_sec = ip_sec
        self.extension = extension or []


def authenticator_transport_protocol_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(
        AuthenticatorTransportProtocolType_, xml_string)


class Identification(IdentificationType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Identification element """

    c_tag = 'Identification'
    c_namespace = NAMESPACE
    c_children = IdentificationType_.c_children.copy()
    c_attributes = IdentificationType_.c_attributes.copy()
    c_child_order = IdentificationType_.c_child_order[:]
    c_cardinality = IdentificationType_.c_cardinality.copy()


def identification_from_string(xml_string):
    return saml2.create_class_from_xml_string(Identification, xml_string)


class ActivationPin(ActivationPinType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ActivationPin element """

    c_tag = 'ActivationPin'
    c_namespace = NAMESPACE
    c_children = ActivationPinType_.c_children.copy()
    c_attributes = ActivationPinType_.c_attributes.copy()
    c_child_order = ActivationPinType_.c_child_order[:]
    c_cardinality = ActivationPinType_.c_cardinality.copy()


def activation_pin_from_string(xml_string):
    return saml2.create_class_from_xml_string(ActivationPin, xml_string)


class Authenticator(AuthenticatorBaseType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:Authenticator element """

    c_tag = 'Authenticator'
    c_namespace = NAMESPACE
    c_children = AuthenticatorBaseType_.c_children.copy()
    c_attributes = AuthenticatorBaseType_.c_attributes.copy()
    c_child_order = AuthenticatorBaseType_.c_child_order[:]
    c_cardinality = AuthenticatorBaseType_.c_cardinality.copy()


def authenticator_from_string(xml_string):
    return saml2.create_class_from_xml_string(Authenticator, xml_string)


class AuthenticatorTransportProtocol(AuthenticatorTransportProtocolType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthenticatorTransportProtocol element """

    c_tag = 'AuthenticatorTransportProtocol'
    c_namespace = NAMESPACE
    c_children = AuthenticatorTransportProtocolType_.c_children.copy()
    c_attributes = AuthenticatorTransportProtocolType_.c_attributes.copy()
    c_child_order = AuthenticatorTransportProtocolType_.c_child_order[:]
    c_cardinality = AuthenticatorTransportProtocolType_.c_cardinality.copy()


def authenticator_transport_protocol_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticatorTransportProtocol,
                                              xml_string)


class SecurityAudit(SecurityAuditType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SecurityAudit element """

    c_tag = 'SecurityAudit'
    c_namespace = NAMESPACE
    c_children = SecurityAuditType_.c_children.copy()
    c_attributes = SecurityAuditType_.c_attributes.copy()
    c_child_order = SecurityAuditType_.c_child_order[:]
    c_cardinality = SecurityAuditType_.c_cardinality.copy()


def security_audit_from_string(xml_string):
    return saml2.create_class_from_xml_string(SecurityAudit, xml_string)


class OperationalProtectionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:OperationalProtectionType element """

    c_tag = 'OperationalProtectionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SecurityAudit'] = (
        'security_audit', SecurityAudit)
    c_cardinality['security_audit'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}DeactivationCallCenter'] = (
        'deactivation_call_center', DeactivationCallCenter)
    c_cardinality['deactivation_call_center'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(
        ['security_audit', 'deactivation_call_center', 'extension'])

    def __init__(self,
                 security_audit=None,
                 deactivation_call_center=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.security_audit = security_audit
        self.deactivation_call_center = deactivation_call_center
        self.extension = extension or []


def operational_protection_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(OperationalProtectionType_,
                                              xml_string)


class PrincipalAuthenticationMechanismType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PrincipalAuthenticationMechanismType element """

    c_tag = 'PrincipalAuthenticationMechanismType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Password'] = (
        'password', Password)
    c_cardinality['password'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword'] = (
        'restricted_password', RestrictedPassword)
    c_cardinality['restricted_password'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Token'] = (
        'token', Token)
    c_cardinality['token'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Smartcard'] = (
        'smartcard', Smartcard)
    c_cardinality['smartcard'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationPin'] = (
        'activation_pin', ActivationPin)
    c_cardinality['activation_pin'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['preauth'] = ('preauth', 'integer', False)
    c_child_order.extend(
        ['password', 'restricted_password', 'token', 'smartcard',
         'activation_pin', 'extension'])

    def __init__(self,
                 password=None,
                 restricted_password=None,
                 token=None,
                 smartcard=None,
                 activation_pin=None,
                 extension=None,
                 preauth=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.password = password
        self.restricted_password = restricted_password
        self.token = token
        self.smartcard = smartcard
        self.activation_pin = activation_pin
        self.extension = extension or []
        self.preauth = preauth


def principal_authentication_mechanism_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(
        PrincipalAuthenticationMechanismType_, xml_string)


class KeyActivationType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeyActivationType element """

    c_tag = 'KeyActivationType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ActivationPin'] = (
        'activation_pin', ActivationPin)
    c_cardinality['activation_pin'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['activation_pin', 'extension'])

    def __init__(self,
                 activation_pin=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.activation_pin = activation_pin
        self.extension = extension or []


def key_activation_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyActivationType_, xml_string)


class KeyActivation(KeyActivationType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:KeyActivation element """

    c_tag = 'KeyActivation'
    c_namespace = NAMESPACE
    c_children = KeyActivationType_.c_children.copy()
    c_attributes = KeyActivationType_.c_attributes.copy()
    c_child_order = KeyActivationType_.c_child_order[:]
    c_cardinality = KeyActivationType_.c_cardinality.copy()


def key_activation_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyActivation, xml_string)


class PrincipalAuthenticationMechanism(PrincipalAuthenticationMechanismType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PrincipalAuthenticationMechanism element """

    c_tag = 'PrincipalAuthenticationMechanism'
    c_namespace = NAMESPACE
    c_children = PrincipalAuthenticationMechanismType_.c_children.copy()
    c_attributes = PrincipalAuthenticationMechanismType_.c_attributes.copy()
    c_child_order = PrincipalAuthenticationMechanismType_.c_child_order[:]
    c_cardinality = PrincipalAuthenticationMechanismType_.c_cardinality.copy()


def principal_authentication_mechanism_from_string(xml_string):
    return saml2.create_class_from_xml_string(PrincipalAuthenticationMechanism,
                                              xml_string)


class OperationalProtection(OperationalProtectionType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:OperationalProtection element """

    c_tag = 'OperationalProtection'
    c_namespace = NAMESPACE
    c_children = OperationalProtectionType_.c_children.copy()
    c_attributes = OperationalProtectionType_.c_attributes.copy()
    c_child_order = OperationalProtectionType_.c_child_order[:]
    c_cardinality = OperationalProtectionType_.c_cardinality.copy()


def operational_protection_from_string(xml_string):
    return saml2.create_class_from_xml_string(OperationalProtection, xml_string)


class PrivateKeyProtectionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PrivateKeyProtectionType element """

    c_tag = 'PrivateKeyProtectionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyActivation'] = (
        'key_activation', KeyActivation)
    c_cardinality['key_activation'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyStorage'] = (

        'key_storage', KeyStorage)
    c_cardinality['key_storage'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeySharing'] = (
        'key_sharing', KeySharing)
    c_cardinality['key_sharing'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport' \
        '}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(
        ['key_activation', 'key_storage', 'key_sharing', 'extension'])

    def __init__(self,
                 key_activation=None,
                 key_storage=None,
                 key_sharing=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.key_activation = key_activation
        self.key_storage = key_storage
        self.key_sharing = key_sharing
        self.extension = extension or []


def private_key_protection_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PrivateKeyProtectionType_,
                                              xml_string)


class SecretKeyProtectionType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SecretKeyProtectionType element """

    c_tag = 'SecretKeyProtectionType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyActivation'] = (
        'key_activation', KeyActivation)
    c_cardinality['key_activation'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}KeyStorage'] = (
        'key_storage', KeyStorage)
    c_cardinality['key_storage'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['key_activation', 'key_storage', 'extension'])

    def __init__(self,
                 key_activation=None,
                 key_storage=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.key_activation = key_activation
        self.key_storage = key_storage
        self.extension = extension or []


def secret_key_protection_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SecretKeyProtectionType_,
                                              xml_string)


class AuthnMethodBaseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthnMethodBaseType element """

    c_tag = 'AuthnMethodBaseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PrincipalAuthenticationMechanism'] = (
        'principal_authentication_mechanism', PrincipalAuthenticationMechanism)
    c_cardinality['principal_authentication_mechanism'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Authenticator'] = (
        'authenticator', Authenticator)
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AuthenticatorTransportProtocol'] = (
        'authenticator_transport_protocol', AuthenticatorTransportProtocol)
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(['principal_authentication_mechanism', 'authenticator',
                          'authenticator_transport_protocol', 'extension'])

    def __init__(self,
                 principal_authentication_mechanism=None,
                 authenticator=None,
                 authenticator_transport_protocol=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.principal_authentication_mechanism = principal_authentication_mechanism
        self.authenticator = authenticator
        self.authenticator_transport_protocol = authenticator_transport_protocol
        self.extension = extension or []


def authn_method_base_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnMethodBaseType_, xml_string)


class SecretKeyProtection(SecretKeyProtectionType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:SecretKeyProtection element """

    c_tag = 'SecretKeyProtection'
    c_namespace = NAMESPACE
    c_children = SecretKeyProtectionType_.c_children.copy()
    c_attributes = SecretKeyProtectionType_.c_attributes.copy()
    c_child_order = SecretKeyProtectionType_.c_child_order[:]
    c_cardinality = SecretKeyProtectionType_.c_cardinality.copy()


def secret_key_protection_from_string(xml_string):
    return saml2.create_class_from_xml_string(SecretKeyProtection, xml_string)


class PrivateKeyProtection(PrivateKeyProtectionType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:PrivateKeyProtection element """

    c_tag = 'PrivateKeyProtection'
    c_namespace = NAMESPACE
    c_children = PrivateKeyProtectionType_.c_children.copy()
    c_attributes = PrivateKeyProtectionType_.c_attributes.copy()
    c_child_order = PrivateKeyProtectionType_.c_child_order[:]
    c_cardinality = PrivateKeyProtectionType_.c_cardinality.copy()


def private_key_protection_from_string(xml_string):
    return saml2.create_class_from_xml_string(PrivateKeyProtection, xml_string)


class AuthnMethod(AuthnMethodBaseType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthnMethod element """

    c_tag = 'AuthnMethod'
    c_namespace = NAMESPACE
    c_children = AuthnMethodBaseType_.c_children.copy()
    c_attributes = AuthnMethodBaseType_.c_attributes.copy()
    c_child_order = AuthnMethodBaseType_.c_child_order[:]
    c_cardinality = AuthnMethodBaseType_.c_cardinality.copy()


def authn_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnMethod, xml_string)


class TechnicalProtectionBaseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:TechnicalProtectionBaseType element """

    c_tag = 'TechnicalProtectionBaseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PrivateKeyProtection'] = (
        'private_key_protection', PrivateKeyProtection)
    c_cardinality['private_key_protection'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SecretKeyProtection'] = (
        'secret_key_protection', SecretKeyProtection)
    c_cardinality['secret_key_protection'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport' \
        '}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(
        ['private_key_protection', 'secret_key_protection', 'extension'])

    def __init__(self,
                 private_key_protection=None,
                 secret_key_protection=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.private_key_protection = private_key_protection
        self.secret_key_protection = secret_key_protection
        self.extension = extension or []


def technical_protection_base_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TechnicalProtectionBaseType_,
                                              xml_string)


class TechnicalProtection(TechnicalProtectionBaseType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:TechnicalProtection element """

    c_tag = 'TechnicalProtection'
    c_namespace = NAMESPACE
    c_children = TechnicalProtectionBaseType_.c_children.copy()
    c_attributes = TechnicalProtectionBaseType_.c_attributes.copy()
    c_child_order = TechnicalProtectionBaseType_.c_child_order[:]
    c_cardinality = TechnicalProtectionBaseType_.c_cardinality.copy()


def technical_protection_from_string(xml_string):
    return saml2.create_class_from_xml_string(TechnicalProtection, xml_string)


class AuthnContextDeclarationBaseType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthnContextDeclarationBaseType element """

    c_tag = 'AuthnContextDeclarationBaseType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Identification'] = (
        'identification', Identification)
    c_cardinality['identification'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}TechnicalProtection'] = (
        'technical_protection', TechnicalProtection)
    c_cardinality['technical_protection'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}OperationalProtection'] = (
        'operational_protection', OperationalProtection)
    c_cardinality['operational_protection'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AuthnMethod'] = (
        'authn_method', AuthnMethod)
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}GoverningAgreements'] = (
        'governing_agreements', GoverningAgreements)
    c_cardinality['governing_agreements'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_attributes['ID'] = ('id', 'ID', False)
    c_child_order.extend(
        ['identification', 'technical_protection', 'operational_protection',
         'authn_method', 'governing_agreements', 'extension'])

    def __init__(self,
                 identification=None,
                 technical_protection=None,
                 operational_protection=None,
                 authn_method=None,
                 governing_agreements=None,
                 extension=None,
                 id=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.identification = identification
        self.technical_protection = technical_protection
        self.operational_protection = operational_protection
        self.authn_method = authn_method
        self.governing_agreements = governing_agreements
        self.extension = extension or []
        self.id = id


def authn_context_declaration_base_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthnContextDeclarationBaseType_,
                                              xml_string)


class AuthenticationContextDeclaration(AuthnContextDeclarationBaseType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:AuthenticationContextDeclaration element """

    c_tag = 'AuthenticationContextDeclaration'
    c_namespace = NAMESPACE
    c_children = AuthnContextDeclarationBaseType_.c_children.copy()
    c_attributes = AuthnContextDeclarationBaseType_.c_attributes.copy()
    c_child_order = AuthnContextDeclarationBaseType_.c_child_order[:]
    c_cardinality = AuthnContextDeclarationBaseType_.c_cardinality.copy()


def authentication_context_declaration_from_string(xml_string):
    return saml2.create_class_from_xml_string(AuthenticationContextDeclaration,
                                              xml_string)


class ComplexAuthenticatorType_(SamlBase):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ComplexAuthenticatorType element """

    c_tag = 'ComplexAuthenticatorType'
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}PreviousSession'] = (

        'previous_session', PreviousSession)
    c_cardinality['previous_session'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ResumeSession'] = (
        'resume_session', ResumeSession)
    c_cardinality['resume_session'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}DigSig'] = (
        'dig_sig', DigSig)
    c_cardinality['dig_sig'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Password'] = (
        'password', Password)
    c_cardinality['password'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}RestrictedPassword'] = (
        'restricted_password', RestrictedPassword)
    c_cardinality['restricted_password'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ZeroKnowledge'] = (
        'zero_knowledge', ZeroKnowledge)
    c_cardinality['zero_knowledge'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SharedSecretChallengeResponse'] = (
        'shared_secret_challenge_response', SharedSecretChallengeResponse)
    c_cardinality['shared_secret_challenge_response'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SharedSecretDynamicPlaintext'] = (
        'shared_secret_dynamic_plaintext', SharedSecretDynamicPlaintext)
    c_cardinality['shared_secret_dynamic_plaintext'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}IPAddress'] = (
        'ip_address', IPAddress)
    c_cardinality['ip_address'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AsymmetricDecryption'] = (
        'asymmetric_decryption', AsymmetricDecryption)
    c_cardinality['asymmetric_decryption'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}AsymmetricKeyAgreement'] = (
        'asymmetric_key_agreement', AsymmetricKeyAgreement)
    c_cardinality['asymmetric_key_agreement'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}SubscriberLineNumber'] = (
        'subscriber_line_number', SubscriberLineNumber)
    c_cardinality['subscriber_line_number'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}UserSuffix'] = (
        'user_suffix', UserSuffix)
    c_cardinality['user_suffix'] = {"min": 0, "max": 1}
    c_cardinality['complex_authenticator'] = {"min": 0, "max": 1}
    c_children[
        '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}Extension'] = (
        'extension', [Extension])
    c_cardinality['extension'] = {"min": 0}
    c_child_order.extend(
        ['previous_session', 'resume_session', 'dig_sig', 'password',
         'restricted_password', 'zero_knowledge',
         'shared_secret_challenge_response', 'shared_secret_dynamic_plaintext',
         'ip_address', 'asymmetric_decryption', 'asymmetric_key_agreement',
         'subscriber_line_number', 'user_suffix', 'complex_authenticator',
         'extension'])

    def __init__(self,
                 previous_session=None,
                 resume_session=None,
                 dig_sig=None,
                 password=None,
                 restricted_password=None,
                 zero_knowledge=None,
                 shared_secret_challenge_response=None,
                 shared_secret_dynamic_plaintext=None,
                 ip_address=None,
                 asymmetric_decryption=None,
                 asymmetric_key_agreement=None,
                 subscriber_line_number=None,
                 user_suffix=None,
                 complex_authenticator=None,
                 extension=None,
                 text=None,
                 extension_elements=None,
                 extension_attributes=None,
    ):
        SamlBase.__init__(self,
                          text=text,
                          extension_elements=extension_elements,
                          extension_attributes=extension_attributes,
        )
        self.previous_session = previous_session
        self.resume_session = resume_session
        self.dig_sig = dig_sig
        self.password = password
        self.restricted_password = restricted_password
        self.zero_knowledge = zero_knowledge
        self.shared_secret_challenge_response = shared_secret_challenge_response
        self.shared_secret_dynamic_plaintext = shared_secret_dynamic_plaintext
        self.ip_address = ip_address
        self.asymmetric_decryption = asymmetric_decryption
        self.asymmetric_key_agreement = asymmetric_key_agreement
        self.subscriber_line_number = subscriber_line_number
        self.user_suffix = user_suffix
        self.complex_authenticator = complex_authenticator
        self.extension = extension or []


def complex_authenticator_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ComplexAuthenticatorType_,
                                              xml_string)


class ComplexAuthenticator(ComplexAuthenticatorType_):
    """The urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport:ComplexAuthenticator element """

    c_tag = 'ComplexAuthenticator'
    c_namespace = NAMESPACE
    c_children = ComplexAuthenticatorType_.c_children.copy()
    c_attributes = ComplexAuthenticatorType_.c_attributes.copy()
    c_child_order = ComplexAuthenticatorType_.c_child_order[:]
    c_cardinality = ComplexAuthenticatorType_.c_cardinality.copy()


def complex_authenticator_from_string(xml_string):
    return saml2.create_class_from_xml_string(ComplexAuthenticator, xml_string)


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
ComplexAuthenticatorType_.c_children[
    '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ComplexAuthenticator'] = (
    'complex_authenticator', ComplexAuthenticator)
ComplexAuthenticator.c_children[
    '{urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport}ComplexAuthenticator'] = (
    'complex_authenticator', ComplexAuthenticator)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ELEMENT_FROM_STRING = {
    AuthenticationContextDeclaration.c_tag: authentication_context_declaration_from_string,
    Identification.c_tag: identification_from_string,
    PhysicalVerification.c_tag: physical_verification_from_string,
    WrittenConsent.c_tag: written_consent_from_string,
    TechnicalProtection.c_tag: technical_protection_from_string,
    SecretKeyProtection.c_tag: secret_key_protection_from_string,
    PrivateKeyProtection.c_tag: private_key_protection_from_string,
    KeyActivation.c_tag: key_activation_from_string,
    KeySharing.c_tag: key_sharing_from_string,
    KeyStorage.c_tag: key_storage_from_string,
    SubscriberLineNumber.c_tag: subscriber_line_number_from_string,
    UserSuffix.c_tag: user_suffix_from_string,
    Password.c_tag: password_from_string,
    ActivationPin.c_tag: activation_pin_from_string,
    Token.c_tag: token_from_string,
    TimeSyncToken.c_tag: time_sync_token_from_string,
    Smartcard.c_tag: smartcard_from_string,
    Length.c_tag: length_from_string,
    ActivationLimit.c_tag: activation_limit_from_string,
    Generation.c_tag: generation_from_string,
    AuthnMethod.c_tag: authn_method_from_string,
    PrincipalAuthenticationMechanism.c_tag: principal_authentication_mechanism_from_string,
    Authenticator.c_tag: authenticator_from_string,
    ComplexAuthenticator.c_tag: complex_authenticator_from_string,
    PreviousSession.c_tag: previous_session_from_string,
    ResumeSession.c_tag: resume_session_from_string,
    ZeroKnowledge.c_tag: zero_knowledge_from_string,
    SharedSecretChallengeResponse.c_tag: shared_secret_challenge_response_from_string,
    SharedSecretChallengeResponseType_.c_tag: shared_secret_challenge_response_type__from_string,
    DigSig.c_tag: dig_sig_from_string,
    AsymmetricDecryption.c_tag: asymmetric_decryption_from_string,
    AsymmetricKeyAgreement.c_tag: asymmetric_key_agreement_from_string,
    PublicKeyType_.c_tag: public_key_type__from_string,
    IPAddress.c_tag: ip_address_from_string,
    SharedSecretDynamicPlaintext.c_tag: shared_secret_dynamic_plaintext_from_string,
    AuthenticatorTransportProtocol.c_tag: authenticator_transport_protocol_from_string,
    HTTP.c_tag: http_from_string,
    IPSec.c_tag: ip_sec_from_string,
    WTLS.c_tag: wtls_from_string,
    MobileNetworkNoEncryption.c_tag: mobile_network_no_encryption_from_string,
    MobileNetworkRadioEncryption.c_tag: mobile_network_radio_encryption_from_string,
    MobileNetworkEndToEndEncryption.c_tag: mobile_network_end_to_end_encryption_from_string,
    SSL.c_tag: ssl_from_string,
    PSTN.c_tag: pstn_from_string,
    ISDN.c_tag: isdn_from_string,
    ADSL.c_tag: adsl_from_string,
    OperationalProtection.c_tag: operational_protection_from_string,
    SecurityAudit.c_tag: security_audit_from_string,
    SwitchAudit.c_tag: switch_audit_from_string,
    DeactivationCallCenter.c_tag: deactivation_call_center_from_string,
    GoverningAgreements.c_tag: governing_agreements_from_string,
    GoverningAgreementRef.c_tag: governing_agreement_ref_from_string,
    NymType_.c_tag: nym_type__from_string,
    IdentificationType_.c_tag: identification_type__from_string,
    TechnicalProtectionBaseType_.c_tag: technical_protection_base_type__from_string,
    OperationalProtectionType_.c_tag: operational_protection_type__from_string,
    GoverningAgreementsType_.c_tag: governing_agreements_type__from_string,
    GoverningAgreementRefType_.c_tag: governing_agreement_ref_type__from_string,
    PrincipalAuthenticationMechanismType_.c_tag: principal_authentication_mechanism_type__from_string,
    ComplexAuthenticatorType_.c_tag: complex_authenticator_type__from_string,
    KeyActivationType_.c_tag: key_activation_type__from_string,
    KeySharingType_.c_tag: key_sharing_type__from_string,
    PrivateKeyProtectionType_.c_tag: private_key_protection_type__from_string,
    PasswordType_.c_tag: password_type__from_string,
    RestrictedPassword.c_tag: restricted_password_from_string,
    RestrictedPasswordType_.c_tag: restricted_password_type__from_string,
    RestrictedLengthType_.c_tag: restricted_length_type__from_string,
    ActivationPinType_.c_tag: activation_pin_type__from_string,
    Alphabet.c_tag: alphabet_from_string,
    AlphabetType_.c_tag: alphabet_type__from_string,
    TokenType_.c_tag: token_type__from_string,
    DeviceTypeType_.c_tag: device_type_type__from_string,
    BooleanType_.c_tag: boolean_type__from_string,
    TimeSyncTokenType_.c_tag: time_sync_token_type__from_string,
    ActivationLimitType_.c_tag: activation_limit_type__from_string,
    ActivationLimitDuration.c_tag: activation_limit_duration_from_string,
    ActivationLimitUsages.c_tag: activation_limit_usages_from_string,
    ActivationLimitSession.c_tag: activation_limit_session_from_string,
    ActivationLimitDurationType_.c_tag: activation_limit_duration_type__from_string,
    ActivationLimitUsagesType_.c_tag: activation_limit_usages_type__from_string,
    ActivationLimitSessionType_.c_tag: activation_limit_session_type__from_string,
    LengthType_.c_tag: length_type__from_string,
    MediumType_.c_tag: medium_type__from_string,
    KeyStorageType_.c_tag: key_storage_type__from_string,
    SecretKeyProtectionType_.c_tag: secret_key_protection_type__from_string,
    SecurityAuditType_.c_tag: security_audit_type__from_string,
    ExtensionOnlyType_.c_tag: extension_only_type__from_string,
    Extension.c_tag: extension_from_string,
    ExtensionType_.c_tag: extension_type__from_string,
    AuthnContextDeclarationBaseType_.c_tag: authn_context_declaration_base_type__from_string,
    AuthnMethodBaseType_.c_tag: authn_method_base_type__from_string,
    AuthenticatorBaseType_.c_tag: authenticator_base_type__from_string,
    AuthenticatorTransportProtocolType_.c_tag: authenticator_transport_protocol_type__from_string,
}

ELEMENT_BY_TAG = {
    'AuthenticationContextDeclaration': AuthenticationContextDeclaration,
    'Identification': Identification,
    'PhysicalVerification': PhysicalVerification,
    'WrittenConsent': WrittenConsent,
    'TechnicalProtection': TechnicalProtection,
    'SecretKeyProtection': SecretKeyProtection,
    'PrivateKeyProtection': PrivateKeyProtection,
    'KeyActivation': KeyActivation,
    'KeySharing': KeySharing,
    'KeyStorage': KeyStorage,
    'SubscriberLineNumber': SubscriberLineNumber,
    'UserSuffix': UserSuffix,
    'Password': Password,
    'ActivationPin': ActivationPin,
    'Token': Token,
    'TimeSyncToken': TimeSyncToken,
    'Smartcard': Smartcard,
    'Length': Length,
    'ActivationLimit': ActivationLimit,
    'Generation': Generation,
    'AuthnMethod': AuthnMethod,
    'PrincipalAuthenticationMechanism': PrincipalAuthenticationMechanism,
    'Authenticator': Authenticator,
    'ComplexAuthenticator': ComplexAuthenticator,
    'PreviousSession': PreviousSession,
    'ResumeSession': ResumeSession,
    'ZeroKnowledge': ZeroKnowledge,
    'SharedSecretChallengeResponse': SharedSecretChallengeResponse,
    'SharedSecretChallengeResponseType': SharedSecretChallengeResponseType_,
    'DigSig': DigSig,
    'AsymmetricDecryption': AsymmetricDecryption,
    'AsymmetricKeyAgreement': AsymmetricKeyAgreement,
    'PublicKeyType': PublicKeyType_,
    'IPAddress': IPAddress,
    'SharedSecretDynamicPlaintext': SharedSecretDynamicPlaintext,
    'AuthenticatorTransportProtocol': AuthenticatorTransportProtocol,
    'HTTP': HTTP,
    'IPSec': IPSec,
    'WTLS': WTLS,
    'MobileNetworkNoEncryption': MobileNetworkNoEncryption,
    'MobileNetworkRadioEncryption': MobileNetworkRadioEncryption,
    'MobileNetworkEndToEndEncryption': MobileNetworkEndToEndEncryption,
    'SSL': SSL,
    'PSTN': PSTN,
    'ISDN': ISDN,
    'ADSL': ADSL,
    'OperationalProtection': OperationalProtection,
    'SecurityAudit': SecurityAudit,
    'SwitchAudit': SwitchAudit,
    'DeactivationCallCenter': DeactivationCallCenter,
    'GoverningAgreements': GoverningAgreements,
    'GoverningAgreementRef': GoverningAgreementRef,
    'nymType': NymType_,
    'IdentificationType': IdentificationType_,
    'TechnicalProtectionBaseType': TechnicalProtectionBaseType_,
    'OperationalProtectionType': OperationalProtectionType_,
    'GoverningAgreementsType': GoverningAgreementsType_,
    'GoverningAgreementRefType': GoverningAgreementRefType_,
    'PrincipalAuthenticationMechanismType': PrincipalAuthenticationMechanismType_,
    'ComplexAuthenticatorType': ComplexAuthenticatorType_,
    'KeyActivationType': KeyActivationType_,
    'KeySharingType': KeySharingType_,
    'PrivateKeyProtectionType': PrivateKeyProtectionType_,
    'PasswordType': PasswordType_,
    'RestrictedPassword': RestrictedPassword,
    'RestrictedPasswordType': RestrictedPasswordType_,
    'RestrictedLengthType': RestrictedLengthType_,
    'ActivationPinType': ActivationPinType_,
    'Alphabet': Alphabet,
    'AlphabetType': AlphabetType_,
    'TokenType': TokenType_,
    'DeviceTypeType': DeviceTypeType_,
    'booleanType': BooleanType_,
    'TimeSyncTokenType': TimeSyncTokenType_,
    'ActivationLimitType': ActivationLimitType_,
    'ActivationLimitDuration': ActivationLimitDuration,
    'ActivationLimitUsages': ActivationLimitUsages,
    'ActivationLimitSession': ActivationLimitSession,
    'ActivationLimitDurationType': ActivationLimitDurationType_,
    'ActivationLimitUsagesType': ActivationLimitUsagesType_,
    'ActivationLimitSessionType': ActivationLimitSessionType_,
    'LengthType': LengthType_,
    'mediumType': MediumType_,
    'KeyStorageType': KeyStorageType_,
    'SecretKeyProtectionType': SecretKeyProtectionType_,
    'SecurityAuditType': SecurityAuditType_,
    'ExtensionOnlyType': ExtensionOnlyType_,
    'Extension': Extension,
    'ExtensionType': ExtensionType_,
    'AuthnContextDeclarationBaseType': AuthnContextDeclarationBaseType_,
    'AuthnMethodBaseType': AuthnMethodBaseType_,
    'AuthenticatorBaseType': AuthenticatorBaseType_,
    'AuthenticatorTransportProtocolType': AuthenticatorTransportProtocolType_,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)

