#!/usr/bin/env python

#
# Generated Mon May  2 14:23:33 2011 by parse_xsd.py version 0.4.
#

import saml2
from saml2 import SamlBase


NAMESPACE = "http://www.w3.org/2000/09/xmldsig#"

ENCODING_BASE64 = "http://www.w3.org/2000/09/xmldsig#base64"

# digest and signature algorithms (not implemented = commented out)
DIGEST_MD5 = "http://www.w3.org/2001/04/xmldsig-more#md5"  # test framework
# only!
DIGEST_SHA1 = "http://www.w3.org/2000/09/xmldsig#sha1"
DIGEST_SHA224 = "http://www.w3.org/2001/04/xmldsig-more#sha224"
DIGEST_SHA256 = "http://www.w3.org/2001/04/xmlenc#sha256"
DIGEST_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#sha384"
DIGEST_SHA512 = "http://www.w3.org/2001/04/xmlenc#sha512"
DIGEST_RIPEMD160 = "http://www.w3.org/2001/04/xmlenc#ripemd160"
digest_default = DIGEST_SHA1
DIGEST_ALLOWED_ALG = (
    ("DIGEST_SHA1", DIGEST_SHA1),
    ("DIGEST_SHA224", DIGEST_SHA224),
    ("DIGEST_SHA256", DIGEST_SHA256),
    ("DIGEST_SHA384", DIGEST_SHA384),
    ("DIGEST_SHA512", DIGEST_SHA512),
    ("DIGEST_RIPEMD160", DIGEST_RIPEMD160),
)
DIGEST_AVAIL_ALG = DIGEST_ALLOWED_ALG + (("DIGEST_MD5", DIGEST_MD5),)

SIG_DSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#dsa-sha1"
SIG_DSA_SHA256 = "http://www.w3.org/2009/xmldsig11#dsa-sha256"
SIG_ECDSA_SHA1 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha1"
SIG_ECDSA_SHA224 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha224"
SIG_ECDSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256"
SIG_ECDSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha384"
SIG_ECDSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha512"
SIG_RSA_MD5 = "http://www.w3.org/2001/04/xmldsig-more#rsa-md5"  # test framework
SIG_RSA_SHA1 = "http://www.w3.org/2000/09/xmldsig#rsa-sha1"
SIG_RSA_SHA224 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha224"
SIG_RSA_SHA256 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
SIG_RSA_SHA384 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha384"
SIG_RSA_SHA512 = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha512"
SIG_RSA_RIPEMD160 = "http://www.w3.org/2001/04/xmldsig-more#rsa-ripemd160"
sig_default = SIG_RSA_SHA1
SIG_ALLOWED_ALG = (
    ("SIG_RSA_SHA1", SIG_RSA_SHA1),
    ("SIG_RSA_SHA224", SIG_RSA_SHA224),
    ("SIG_RSA_SHA256", SIG_RSA_SHA256),
    ("SIG_RSA_SHA384", SIG_RSA_SHA384),
    ("SIG_RSA_SHA512", SIG_RSA_SHA512),
)
SIG_AVAIL_ALG = SIG_ALLOWED_ALG + (("SIG_RSA_MD5", SIG_RSA_MD5),)

MAC_SHA1 = "http://www.w3.org/2000/09/xmldsig#hmac-sha1"

TRANSFORM_XSLT = "http://www.w3.org/TR/1999/REC-xslt-19991116"
TRANSFORM_XPATH = "http://www.w3.org/TR/1999/REC-xpath-19991116"
TRANSFORM_ENVELOPED = "http://www.w3.org/2000/09/xmldsig#enveloped-signature"
TRANSFORM_C14N = "http://www.w3.org/2001/10/xml-exc-c14n#"
TRANSFORM_C14N_WITH_COMMENTS = "http://www.w3.org/2001/10/xml-exc-c14n#WithComments"

ALLOWED_CANONICALIZATIONS = {
    TRANSFORM_C14N,
    TRANSFORM_C14N_WITH_COMMENTS,
}
ALLOWED_TRANSFORMS = {
    TRANSFORM_ENVELOPED,
    TRANSFORM_C14N,
    TRANSFORM_C14N_WITH_COMMENTS,
}


class DefaultSignature:
    class _DefaultSignature:
        def __init__(self, sign_alg=None, digest_alg=None):
            if sign_alg is None:
                self.sign_alg = sig_default
            else:
                self.sign_alg = sign_alg
            if digest_alg is None:
                self.digest_alg = digest_default
            else:
                self.digest_alg = digest_alg

        def __str__(self):
            return repr(self) + self.sign_alg

    instance = None

    def __init__(self, sign_alg=None, digest_alg=None):
        if not DefaultSignature.instance:
            DefaultSignature.instance = DefaultSignature._DefaultSignature(sign_alg, digest_alg)

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def get_sign_alg(self):
        return self.sign_alg

    def get_digest_alg(self):
        return self.digest_alg


class CryptoBinary_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:CryptoBinary element"""

    c_tag = "CryptoBinary"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def crypto_binary__from_string(xml_string):
    return saml2.create_class_from_xml_string(CryptoBinary_, xml_string)


class SignatureValueType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureValueType element"""

    c_tag = "SignatureValueType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Id"] = ("id", "ID", False)

    def __init__(
        self,
        id=None,
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
        self.id = id


def signature_value_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureValueType_, xml_string)


class CanonicalizationMethodType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:CanonicalizationMethodType
    element"""

    c_tag = "CanonicalizationMethodType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Algorithm"] = ("algorithm", "anyURI", True)

    def __init__(
        self,
        algorithm=None,
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
        self.algorithm = algorithm


def canonicalization_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(CanonicalizationMethodType_, xml_string)


class TransformType_XPath(SamlBase):
    c_tag = "XPath"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def transform_type__x_path_from_string(xml_string):
    return saml2.create_class_from_xml_string(TransformType_XPath, xml_string)


class TransformType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:TransformType element"""

    c_tag = "TransformType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}XPath"] = ("x_path", [TransformType_XPath])
    c_cardinality["x_path"] = {"min": 0}
    c_attributes["Algorithm"] = ("algorithm", "anyURI", True)
    c_child_order.extend(["x_path"])

    def __init__(
        self,
        x_path=None,
        algorithm=None,
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
        self.x_path = x_path or []
        self.algorithm = algorithm


def transform_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TransformType_, xml_string)


class DigestMethodType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:DigestMethodType element"""

    c_tag = "DigestMethodType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Algorithm"] = ("algorithm", "anyURI", True)

    def __init__(
        self,
        algorithm=None,
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
        self.algorithm = algorithm


def digest_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestMethodType_, xml_string)


class DigestValueType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:DigestValueType element"""

    c_tag = "DigestValueType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def digest_value_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestValueType_, xml_string)


class KeyName(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:KeyName element"""

    c_tag = "KeyName"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def key_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyName, xml_string)


class MgmtData(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:MgmtData element"""

    c_tag = "MgmtData"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def mgmt_data_from_string(xml_string):
    return saml2.create_class_from_xml_string(MgmtData, xml_string)


class X509IssuerName(SamlBase):
    c_tag = "X509IssuerName"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_issuer_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509IssuerName, xml_string)


class X509SerialNumber(SamlBase):
    c_tag = "X509SerialNumber"
    c_namespace = NAMESPACE
    c_value_type = {"base": "integer"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_serial_number_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509SerialNumber, xml_string)


class X509IssuerSerialType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:X509IssuerSerialType element"""

    c_tag = "X509IssuerSerialType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509IssuerName"] = ("x509_issuer_name", X509IssuerName)
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509SerialNumber"] = ("x509_serial_number", X509SerialNumber)
    c_child_order.extend(["x509_issuer_name", "x509_serial_number"])

    def __init__(
        self,
        x509_issuer_name=None,
        x509_serial_number=None,
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
        self.x509_issuer_name = x509_issuer_name
        self.x509_serial_number = x509_serial_number


def x509_issuer_serial_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(X509IssuerSerialType_, xml_string)


class PGPKeyID(SamlBase):
    c_tag = "PGPKeyID"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def pgp_key_id_from_string(xml_string):
    return saml2.create_class_from_xml_string(PGPKeyID, xml_string)


class PGPKeyPacket(SamlBase):
    c_tag = "PGPKeyPacket"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def pgp_key_packet_from_string(xml_string):
    return saml2.create_class_from_xml_string(PGPKeyPacket, xml_string)


class PGPDataType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:PGPDataType element"""

    c_tag = "PGPDataType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}PGPKeyID"] = ("pgp_key_id", PGPKeyID)
    c_children["{http://www.w3.org/2000/09/xmldsig#}PGPKeyPacket"] = ("pgp_key_packet", PGPKeyPacket)
    c_cardinality["pgp_key_packet"] = {"min": 0, "max": 1}
    c_child_order.extend(["pgp_key_id", "pgp_key_packet"])

    def __init__(
        self,
        pgp_key_id=None,
        pgp_key_packet=None,
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
        self.pgp_key_id = pgp_key_id
        self.pgp_key_packet = pgp_key_packet


def pgp_data_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(PGPDataType_, xml_string)


class SPKISexp(SamlBase):
    c_tag = "SPKISexp"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def spki_sexp_from_string(xml_string):
    return saml2.create_class_from_xml_string(SPKISexp, xml_string)


class SPKIDataType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SPKIDataType element"""

    c_tag = "SPKIDataType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}SPKISexp"] = ("spki_sexp", [SPKISexp])
    c_cardinality["spki_sexp"] = {"min": 1}
    c_child_order.extend(["spki_sexp"])

    def __init__(
        self,
        spki_sexp=None,
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
        self.spki_sexp = spki_sexp or []


def spki_data_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SPKIDataType_, xml_string)


class ObjectType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:ObjectType element"""

    c_tag = "ObjectType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Id"] = ("id", "ID", False)
    c_attributes["MimeType"] = ("mime_type", "string", False)
    c_attributes["Encoding"] = ("encoding", "anyURI", False)

    def __init__(
        self,
        id=None,
        mime_type=None,
        encoding=None,
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
        self.id = id
        self.mime_type = mime_type
        self.encoding = encoding


def object_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ObjectType_, xml_string)


class SignaturePropertyType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignaturePropertyType element"""

    c_tag = "SignaturePropertyType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_attributes["Target"] = ("target", "anyURI", True)
    c_attributes["Id"] = ("id", "ID", False)

    def __init__(
        self,
        target=None,
        id=None,
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
        self.target = target
        self.id = id


def signature_property_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignaturePropertyType_, xml_string)


class HMACOutputLengthType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:HMACOutputLengthType element"""

    c_tag = "HMACOutputLengthType"
    c_namespace = NAMESPACE
    c_value_type = {"base": "integer"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def hmac_output_length_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(HMACOutputLengthType_, xml_string)


class P(CryptoBinary_):
    c_tag = "P"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def p_from_string(xml_string):
    return saml2.create_class_from_xml_string(P, xml_string)


class Q(CryptoBinary_):
    c_tag = "Q"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def q_from_string(xml_string):
    return saml2.create_class_from_xml_string(Q, xml_string)


class G(CryptoBinary_):
    c_tag = "G"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def g_from_string(xml_string):
    return saml2.create_class_from_xml_string(G, xml_string)


class Y(CryptoBinary_):
    c_tag = "Y"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def y_from_string(xml_string):
    return saml2.create_class_from_xml_string(Y, xml_string)


class J(CryptoBinary_):
    c_tag = "J"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def j_from_string(xml_string):
    return saml2.create_class_from_xml_string(J, xml_string)


class Seed(CryptoBinary_):
    c_tag = "Seed"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def seed_from_string(xml_string):
    return saml2.create_class_from_xml_string(Seed, xml_string)


class PgenCounter(CryptoBinary_):
    c_tag = "PgenCounter"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def pgen_counter_from_string(xml_string):
    return saml2.create_class_from_xml_string(PgenCounter, xml_string)


class DSAKeyValueType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:DSAKeyValueType element"""

    c_tag = "DSAKeyValueType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}P"] = ("p", P)
    c_cardinality["p"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}Q"] = ("q", Q)
    c_cardinality["q"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}G"] = ("g", G)
    c_cardinality["g"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}Y"] = ("y", Y)
    c_children["{http://www.w3.org/2000/09/xmldsig#}J"] = ("j", J)
    c_cardinality["j"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}Seed"] = ("seed", Seed)
    c_cardinality["seed"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}PgenCounter"] = ("pgen_counter", PgenCounter)
    c_cardinality["pgen_counter"] = {"min": 0, "max": 1}
    c_child_order.extend(["p", "q", "g", "y", "j", "seed", "pgen_counter"])

    def __init__(
        self,
        p=None,
        q=None,
        g=None,
        y=None,
        j=None,
        seed=None,
        pgen_counter=None,
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
        self.p = p
        self.q = q
        self.g = g
        self.y = y
        self.j = j
        self.seed = seed
        self.pgen_counter = pgen_counter


def dsa_key_value_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(DSAKeyValueType_, xml_string)


class Modulus(CryptoBinary_):
    c_tag = "Modulus"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def modulus_from_string(xml_string):
    return saml2.create_class_from_xml_string(Modulus, xml_string)


class Exponent(CryptoBinary_):
    c_tag = "Exponent"
    c_namespace = NAMESPACE
    c_children = CryptoBinary_.c_children.copy()
    c_attributes = CryptoBinary_.c_attributes.copy()
    c_child_order = CryptoBinary_.c_child_order[:]
    c_cardinality = CryptoBinary_.c_cardinality.copy()


def exponent_from_string(xml_string):
    return saml2.create_class_from_xml_string(Exponent, xml_string)


class RSAKeyValueType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:RSAKeyValueType element"""

    c_tag = "RSAKeyValueType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Modulus"] = ("modulus", Modulus)
    c_children["{http://www.w3.org/2000/09/xmldsig#}Exponent"] = ("exponent", Exponent)
    c_child_order.extend(["modulus", "exponent"])

    def __init__(
        self,
        modulus=None,
        exponent=None,
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
        self.modulus = modulus
        self.exponent = exponent


def rsa_key_value_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RSAKeyValueType_, xml_string)


class SignatureValue(SignatureValueType_):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureValue element"""

    c_tag = "SignatureValue"
    c_namespace = NAMESPACE
    c_children = SignatureValueType_.c_children.copy()
    c_attributes = SignatureValueType_.c_attributes.copy()
    c_child_order = SignatureValueType_.c_child_order[:]
    c_cardinality = SignatureValueType_.c_cardinality.copy()


def signature_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureValue, xml_string)


class CanonicalizationMethod(CanonicalizationMethodType_):
    """The http://www.w3.org/2000/09/xmldsig#:CanonicalizationMethod element"""

    c_tag = "CanonicalizationMethod"
    c_namespace = NAMESPACE
    c_children = CanonicalizationMethodType_.c_children.copy()
    c_attributes = CanonicalizationMethodType_.c_attributes.copy()
    c_child_order = CanonicalizationMethodType_.c_child_order[:]
    c_cardinality = CanonicalizationMethodType_.c_cardinality.copy()


def canonicalization_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(CanonicalizationMethod, xml_string)


class HMACOutputLength(HMACOutputLengthType_):
    c_tag = "HMACOutputLength"
    c_namespace = NAMESPACE
    c_children = HMACOutputLengthType_.c_children.copy()
    c_attributes = HMACOutputLengthType_.c_attributes.copy()
    c_child_order = HMACOutputLengthType_.c_child_order[:]
    c_cardinality = HMACOutputLengthType_.c_cardinality.copy()


def hmac_output_length_from_string(xml_string):
    return saml2.create_class_from_xml_string(HMACOutputLength, xml_string)


class SignatureMethodType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureMethodType element"""

    c_tag = "SignatureMethodType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}HMACOutputLength"] = ("hmac_output_length", HMACOutputLength)
    c_cardinality["hmac_output_length"] = {"min": 0, "max": 1}
    c_attributes["Algorithm"] = ("algorithm", "anyURI", True)
    c_child_order.extend(["hmac_output_length"])

    def __init__(
        self,
        hmac_output_length=None,
        algorithm=None,
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
        self.hmac_output_length = hmac_output_length
        self.algorithm = algorithm


def signature_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureMethodType_, xml_string)


class Transform(TransformType_):
    """The http://www.w3.org/2000/09/xmldsig#:Transform element"""

    c_tag = "Transform"
    c_namespace = NAMESPACE
    c_children = TransformType_.c_children.copy()
    c_attributes = TransformType_.c_attributes.copy()
    c_child_order = TransformType_.c_child_order[:]
    c_cardinality = TransformType_.c_cardinality.copy()


def transform_from_string(xml_string):
    return saml2.create_class_from_xml_string(Transform, xml_string)


class DigestMethod(DigestMethodType_):
    """The http://www.w3.org/2000/09/xmldsig#:DigestMethod element"""

    c_tag = "DigestMethod"
    c_namespace = NAMESPACE
    c_children = DigestMethodType_.c_children.copy()
    c_attributes = DigestMethodType_.c_attributes.copy()
    c_child_order = DigestMethodType_.c_child_order[:]
    c_cardinality = DigestMethodType_.c_cardinality.copy()


def digest_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestMethod, xml_string)


class DigestValue(DigestValueType_):
    """The http://www.w3.org/2000/09/xmldsig#:DigestValue element"""

    c_tag = "DigestValue"
    c_namespace = NAMESPACE
    c_children = DigestValueType_.c_children.copy()
    c_attributes = DigestValueType_.c_attributes.copy()
    c_child_order = DigestValueType_.c_child_order[:]
    c_cardinality = DigestValueType_.c_cardinality.copy()


def digest_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(DigestValue, xml_string)


class X509IssuerSerial(X509IssuerSerialType_):
    c_tag = "X509IssuerSerial"
    c_namespace = NAMESPACE
    c_children = X509IssuerSerialType_.c_children.copy()
    c_attributes = X509IssuerSerialType_.c_attributes.copy()
    c_child_order = X509IssuerSerialType_.c_child_order[:]
    c_cardinality = X509IssuerSerialType_.c_cardinality.copy()


def x509_issuer_serial_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509IssuerSerial, xml_string)


class X509SKI(SamlBase):
    c_tag = "X509SKI"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_ski_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509SKI, xml_string)


class X509SubjectName(SamlBase):
    c_tag = "X509SubjectName"
    c_namespace = NAMESPACE
    c_value_type = {"base": "string"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_subject_name_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509SubjectName, xml_string)


class X509Certificate(SamlBase):
    c_tag = "X509Certificate"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_certificate_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509Certificate, xml_string)


class X509CRL(SamlBase):
    c_tag = "X509CRL"
    c_namespace = NAMESPACE
    c_value_type = {"base": "base64Binary"}
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()


def x509_crl_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509CRL, xml_string)


class X509DataType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:X509DataType element"""

    c_tag = "X509DataType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509IssuerSerial"] = ("x509_issuer_serial", X509IssuerSerial)
    c_cardinality["x509_issuer_serial"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509SKI"] = ("x509_ski", X509SKI)
    c_cardinality["x509_ski"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509SubjectName"] = ("x509_subject_name", X509SubjectName)
    c_cardinality["x509_subject_name"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509Certificate"] = ("x509_certificate", X509Certificate)
    c_cardinality["x509_certificate"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509CRL"] = ("x509_crl", X509CRL)
    c_cardinality["x509_crl"] = {"min": 0, "max": 1}
    c_child_order.extend(["x509_issuer_serial", "x509_ski", "x509_subject_name", "x509_certificate", "x509_crl"])

    def __init__(
        self,
        x509_issuer_serial=None,
        x509_ski=None,
        x509_subject_name=None,
        x509_certificate=None,
        x509_crl=None,
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
        self.x509_issuer_serial = x509_issuer_serial
        self.x509_ski = x509_ski
        self.x509_subject_name = x509_subject_name
        self.x509_certificate = x509_certificate
        self.x509_crl = x509_crl


def x509_data_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(X509DataType_, xml_string)


class PGPData(PGPDataType_):
    """The http://www.w3.org/2000/09/xmldsig#:PGPData element"""

    c_tag = "PGPData"
    c_namespace = NAMESPACE
    c_children = PGPDataType_.c_children.copy()
    c_attributes = PGPDataType_.c_attributes.copy()
    c_child_order = PGPDataType_.c_child_order[:]
    c_cardinality = PGPDataType_.c_cardinality.copy()


def pgp_data_from_string(xml_string):
    return saml2.create_class_from_xml_string(PGPData, xml_string)


class SPKIData(SPKIDataType_):
    """The http://www.w3.org/2000/09/xmldsig#:SPKIData element"""

    c_tag = "SPKIData"
    c_namespace = NAMESPACE
    c_children = SPKIDataType_.c_children.copy()
    c_attributes = SPKIDataType_.c_attributes.copy()
    c_child_order = SPKIDataType_.c_child_order[:]
    c_cardinality = SPKIDataType_.c_cardinality.copy()


def spki_data_from_string(xml_string):
    return saml2.create_class_from_xml_string(SPKIData, xml_string)


class Object(ObjectType_):
    """The http://www.w3.org/2000/09/xmldsig#:Object element"""

    c_tag = "Object"
    c_namespace = NAMESPACE
    c_children = ObjectType_.c_children.copy()
    c_attributes = ObjectType_.c_attributes.copy()
    c_child_order = ObjectType_.c_child_order[:]
    c_cardinality = ObjectType_.c_cardinality.copy()


def object_from_string(xml_string):
    return saml2.create_class_from_xml_string(Object, xml_string)


class SignatureProperty(SignaturePropertyType_):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureProperty element"""

    c_tag = "SignatureProperty"
    c_namespace = NAMESPACE
    c_children = SignaturePropertyType_.c_children.copy()
    c_attributes = SignaturePropertyType_.c_attributes.copy()
    c_child_order = SignaturePropertyType_.c_child_order[:]
    c_cardinality = SignaturePropertyType_.c_cardinality.copy()


def signature_property_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureProperty, xml_string)


class DSAKeyValue(DSAKeyValueType_):
    """The http://www.w3.org/2000/09/xmldsig#:DSAKeyValue element"""

    c_tag = "DSAKeyValue"
    c_namespace = NAMESPACE
    c_children = DSAKeyValueType_.c_children.copy()
    c_attributes = DSAKeyValueType_.c_attributes.copy()
    c_child_order = DSAKeyValueType_.c_child_order[:]
    c_cardinality = DSAKeyValueType_.c_cardinality.copy()


def dsa_key_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(DSAKeyValue, xml_string)


class RSAKeyValue(RSAKeyValueType_):
    """The http://www.w3.org/2000/09/xmldsig#:RSAKeyValue element"""

    c_tag = "RSAKeyValue"
    c_namespace = NAMESPACE
    c_children = RSAKeyValueType_.c_children.copy()
    c_attributes = RSAKeyValueType_.c_attributes.copy()
    c_child_order = RSAKeyValueType_.c_child_order[:]
    c_cardinality = RSAKeyValueType_.c_cardinality.copy()


def rsa_key_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(RSAKeyValue, xml_string)


class SignatureMethod(SignatureMethodType_):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureMethod element"""

    c_tag = "SignatureMethod"
    c_namespace = NAMESPACE
    c_children = SignatureMethodType_.c_children.copy()
    c_attributes = SignatureMethodType_.c_attributes.copy()
    c_child_order = SignatureMethodType_.c_child_order[:]
    c_cardinality = SignatureMethodType_.c_cardinality.copy()


def signature_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureMethod, xml_string)


class TransformsType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:TransformsType element"""

    c_tag = "TransformsType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Transform"] = ("transform", [Transform])
    c_cardinality["transform"] = {"min": 1}
    c_child_order.extend(["transform"])

    def __init__(
        self,
        transform=None,
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
        self.transform = transform or []


def transforms_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(TransformsType_, xml_string)


class KeyValueType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:KeyValueType element"""

    c_tag = "KeyValueType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}DSAKeyValue"] = ("dsa_key_value", DSAKeyValue)
    c_cardinality["dsa_key_value"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}RSAKeyValue"] = ("rsa_key_value", RSAKeyValue)
    c_cardinality["rsa_key_value"] = {"min": 0, "max": 1}
    c_child_order.extend(["dsa_key_value", "rsa_key_value"])

    def __init__(
        self,
        dsa_key_value=None,
        rsa_key_value=None,
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
        self.dsa_key_value = dsa_key_value
        self.rsa_key_value = rsa_key_value


def key_value_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyValueType_, xml_string)


class X509Data(X509DataType_):
    """The http://www.w3.org/2000/09/xmldsig#:X509Data element"""

    c_tag = "X509Data"
    c_namespace = NAMESPACE
    c_children = X509DataType_.c_children.copy()
    c_attributes = X509DataType_.c_attributes.copy()
    c_child_order = X509DataType_.c_child_order[:]
    c_cardinality = X509DataType_.c_cardinality.copy()


def x509_data_from_string(xml_string):
    return saml2.create_class_from_xml_string(X509Data, xml_string)


class SignaturePropertiesType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignaturePropertiesType element"""

    c_tag = "SignaturePropertiesType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}SignatureProperty"] = ("signature_property", [SignatureProperty])
    c_cardinality["signature_property"] = {"min": 1}
    c_attributes["Id"] = ("id", "ID", False)
    c_child_order.extend(["signature_property"])

    def __init__(
        self,
        signature_property=None,
        id=None,
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
        self.signature_property = signature_property or []
        self.id = id


def signature_properties_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignaturePropertiesType_, xml_string)


class Transforms(TransformsType_):
    """The http://www.w3.org/2000/09/xmldsig#:Transforms element"""

    c_tag = "Transforms"
    c_namespace = NAMESPACE
    c_children = TransformsType_.c_children.copy()
    c_attributes = TransformsType_.c_attributes.copy()
    c_child_order = TransformsType_.c_child_order[:]
    c_cardinality = TransformsType_.c_cardinality.copy()


def transforms_from_string(xml_string):
    return saml2.create_class_from_xml_string(Transforms, xml_string)


class KeyValue(KeyValueType_):
    """The http://www.w3.org/2000/09/xmldsig#:KeyValue element"""

    c_tag = "KeyValue"
    c_namespace = NAMESPACE
    c_children = KeyValueType_.c_children.copy()
    c_attributes = KeyValueType_.c_attributes.copy()
    c_child_order = KeyValueType_.c_child_order[:]
    c_cardinality = KeyValueType_.c_cardinality.copy()


def key_value_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyValue, xml_string)


class RetrievalMethodType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:RetrievalMethodType element"""

    c_tag = "RetrievalMethodType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Transforms"] = ("transforms", Transforms)
    c_cardinality["transforms"] = {"min": 0, "max": 1}
    c_attributes["URI"] = ("uri", "anyURI", False)
    c_attributes["Type"] = ("type", "anyURI", False)
    c_child_order.extend(["transforms"])

    def __init__(
        self,
        transforms=None,
        uri=None,
        type=None,
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
        self.transforms = transforms
        self.uri = uri
        self.type = type


def retrieval_method_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(RetrievalMethodType_, xml_string)


class SignatureProperties(SignaturePropertiesType_):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureProperties element"""

    c_tag = "SignatureProperties"
    c_namespace = NAMESPACE
    c_children = SignaturePropertiesType_.c_children.copy()
    c_attributes = SignaturePropertiesType_.c_attributes.copy()
    c_child_order = SignaturePropertiesType_.c_child_order[:]
    c_cardinality = SignaturePropertiesType_.c_cardinality.copy()


def signature_properties_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureProperties, xml_string)


class ReferenceType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:ReferenceType element"""

    c_tag = "ReferenceType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Transforms"] = ("transforms", Transforms)
    c_cardinality["transforms"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}DigestMethod"] = ("digest_method", DigestMethod)
    c_children["{http://www.w3.org/2000/09/xmldsig#}DigestValue"] = ("digest_value", DigestValue)
    c_attributes["Id"] = ("id", "ID", False)
    c_attributes["URI"] = ("uri", "anyURI", False)
    c_attributes["Type"] = ("type", "anyURI", False)
    c_child_order.extend(["transforms", "digest_method", "digest_value"])

    def __init__(
        self,
        transforms=None,
        digest_method=None,
        digest_value=None,
        id=None,
        uri=None,
        type=None,
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
        self.transforms = transforms
        self.digest_method = digest_method
        self.digest_value = digest_value
        self.id = id
        self.uri = uri
        self.type = type


def reference_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ReferenceType_, xml_string)


class RetrievalMethod(RetrievalMethodType_):
    """The http://www.w3.org/2000/09/xmldsig#:RetrievalMethod element"""

    c_tag = "RetrievalMethod"
    c_namespace = NAMESPACE
    c_children = RetrievalMethodType_.c_children.copy()
    c_attributes = RetrievalMethodType_.c_attributes.copy()
    c_child_order = RetrievalMethodType_.c_child_order[:]
    c_cardinality = RetrievalMethodType_.c_cardinality.copy()


def retrieval_method_from_string(xml_string):
    return saml2.create_class_from_xml_string(RetrievalMethod, xml_string)


class Reference(ReferenceType_):
    """The http://www.w3.org/2000/09/xmldsig#:Reference element"""

    c_tag = "Reference"
    c_namespace = NAMESPACE
    c_children = ReferenceType_.c_children.copy()
    c_attributes = ReferenceType_.c_attributes.copy()
    c_child_order = ReferenceType_.c_child_order[:]
    c_cardinality = ReferenceType_.c_cardinality.copy()


def reference_from_string(xml_string):
    return saml2.create_class_from_xml_string(Reference, xml_string)


# import xmlenc as enc


class KeyInfoType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:KeyInfoType element"""

    c_tag = "KeyInfoType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}KeyName"] = ("key_name", [KeyName])
    c_cardinality["key_name"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}KeyValue"] = ("key_value", [KeyValue])
    c_cardinality["key_value"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}RetrievalMethod"] = ("retrieval_method", [RetrievalMethod])
    c_cardinality["retrieval_method"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}X509Data"] = ("x509_data", [X509Data])
    c_cardinality["x509_data"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}PGPData"] = ("pgp_data", [PGPData])
    c_cardinality["pgp_data"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}SPKIData"] = ("spki_data", [SPKIData])
    c_cardinality["spki_data"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmldsig#}MgmtData"] = ("mgmt_data", [MgmtData])
    c_cardinality["mgmt_data"] = {"min": 0}
    c_children["{http://www.w3.org/2000/09/xmlenc#}EncryptedKey"] = ("encrypted_key", None)
    c_cardinality["key_info"] = {"min": 0, "max": 1}

    c_attributes["Id"] = ("id", "ID", False)
    c_child_order.extend(
        [
            "key_name",
            "key_value",
            "retrieval_method",
            "x509_data",
            "pgp_data",
            "spki_data",
            "mgmt_data",
            "encrypted_key",
        ]
    )

    def __init__(
        self,
        key_name=None,
        key_value=None,
        retrieval_method=None,
        x509_data=None,
        pgp_data=None,
        spki_data=None,
        mgmt_data=None,
        encrypted_key=None,
        id=None,
        text=None,
        extension_elements=None,
        extension_attributes=None,
    ):
        SamlBase.__init__(
            self, text=text, extension_elements=extension_elements, extension_attributes=extension_attributes
        )
        self.key_name = key_name or []
        self.key_value = key_value or []
        self.retrieval_method = retrieval_method or []
        self.x509_data = x509_data or []
        self.pgp_data = pgp_data or []
        self.spki_data = spki_data or []
        self.mgmt_data = mgmt_data or []
        self.encrypted_key = encrypted_key
        self.id = id


def key_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyInfoType_, xml_string)


class ManifestType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:ManifestType element"""

    c_tag = "ManifestType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}Reference"] = ("reference", [Reference])
    c_cardinality["reference"] = {"min": 1}
    c_attributes["Id"] = ("id", "ID", False)
    c_child_order.extend(["reference"])

    def __init__(
        self,
        reference=None,
        id=None,
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
        self.reference = reference or []
        self.id = id


def manifest_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(ManifestType_, xml_string)


class SignedInfoType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignedInfoType element"""

    c_tag = "SignedInfoType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}CanonicalizationMethod"] = (
        "canonicalization_method",
        CanonicalizationMethod,
    )
    c_children["{http://www.w3.org/2000/09/xmldsig#}SignatureMethod"] = ("signature_method", SignatureMethod)
    c_children["{http://www.w3.org/2000/09/xmldsig#}Reference"] = ("reference", [Reference])
    c_cardinality["reference"] = {"min": 1}
    c_attributes["Id"] = ("id", "ID", False)
    c_child_order.extend(["canonicalization_method", "signature_method", "reference"])

    def __init__(
        self,
        canonicalization_method=None,
        signature_method=None,
        reference=None,
        id=None,
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
        self.canonicalization_method = canonicalization_method
        self.signature_method = signature_method
        self.reference = reference or []
        self.id = id


def signed_info_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignedInfoType_, xml_string)


class KeyInfo(KeyInfoType_):
    """The http://www.w3.org/2000/09/xmldsig#:KeyInfo element"""

    c_tag = "KeyInfo"
    c_namespace = NAMESPACE
    c_children = KeyInfoType_.c_children.copy()
    c_attributes = KeyInfoType_.c_attributes.copy()
    c_child_order = KeyInfoType_.c_child_order[:]
    c_cardinality = KeyInfoType_.c_cardinality.copy()


def key_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(KeyInfo, xml_string)


class Manifest(ManifestType_):
    """The http://www.w3.org/2000/09/xmldsig#:Manifest element"""

    c_tag = "Manifest"
    c_namespace = NAMESPACE
    c_children = ManifestType_.c_children.copy()
    c_attributes = ManifestType_.c_attributes.copy()
    c_child_order = ManifestType_.c_child_order[:]
    c_cardinality = ManifestType_.c_cardinality.copy()


def manifest_from_string(xml_string):
    return saml2.create_class_from_xml_string(Manifest, xml_string)


class SignedInfo(SignedInfoType_):
    """The http://www.w3.org/2000/09/xmldsig#:SignedInfo element"""

    c_tag = "SignedInfo"
    c_namespace = NAMESPACE
    c_children = SignedInfoType_.c_children.copy()
    c_attributes = SignedInfoType_.c_attributes.copy()
    c_child_order = SignedInfoType_.c_child_order[:]
    c_cardinality = SignedInfoType_.c_cardinality.copy()


def signed_info_from_string(xml_string):
    return saml2.create_class_from_xml_string(SignedInfo, xml_string)


class SignatureType_(SamlBase):
    """The http://www.w3.org/2000/09/xmldsig#:SignatureType element"""

    c_tag = "SignatureType"
    c_namespace = NAMESPACE
    c_children = SamlBase.c_children.copy()
    c_attributes = SamlBase.c_attributes.copy()
    c_child_order = SamlBase.c_child_order[:]
    c_cardinality = SamlBase.c_cardinality.copy()
    c_children["{http://www.w3.org/2000/09/xmldsig#}SignedInfo"] = ("signed_info", SignedInfo)
    c_children["{http://www.w3.org/2000/09/xmldsig#}SignatureValue"] = ("signature_value", SignatureValue)
    c_children["{http://www.w3.org/2000/09/xmldsig#}KeyInfo"] = ("key_info", KeyInfo)
    c_cardinality["key_info"] = {"min": 0, "max": 1}
    c_children["{http://www.w3.org/2000/09/xmldsig#}Object"] = ("object", [Object])
    c_cardinality["object"] = {"min": 0}
    c_attributes["Id"] = ("id", "ID", False)
    c_child_order.extend(["signed_info", "signature_value", "key_info", "object"])

    def __init__(
        self,
        signed_info=None,
        signature_value=None,
        key_info=None,
        object=None,
        id=None,
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
        self.signed_info = signed_info
        self.signature_value = signature_value
        self.key_info = key_info
        self.object = object or []
        self.id = id


def signature_type__from_string(xml_string):
    return saml2.create_class_from_xml_string(SignatureType_, xml_string)


class Signature(SignatureType_):
    """The http://www.w3.org/2000/09/xmldsig#:Signature element"""

    c_tag = "Signature"
    c_namespace = NAMESPACE
    c_children = SignatureType_.c_children.copy()
    c_attributes = SignatureType_.c_attributes.copy()
    c_child_order = SignatureType_.c_child_order[:]
    c_cardinality = SignatureType_.c_cardinality.copy()


def signature_from_string(xml_string):
    return saml2.create_class_from_xml_string(Signature, xml_string)


ELEMENT_FROM_STRING = {
    CryptoBinary_.c_tag: crypto_binary__from_string,
    Signature.c_tag: signature_from_string,
    SignatureType_.c_tag: signature_type__from_string,
    SignatureValue.c_tag: signature_value_from_string,
    SignatureValueType_.c_tag: signature_value_type__from_string,
    SignedInfo.c_tag: signed_info_from_string,
    SignedInfoType_.c_tag: signed_info_type__from_string,
    CanonicalizationMethod.c_tag: canonicalization_method_from_string,
    CanonicalizationMethodType_.c_tag: canonicalization_method_type__from_string,
    SignatureMethod.c_tag: signature_method_from_string,
    SignatureMethodType_.c_tag: signature_method_type__from_string,
    Reference.c_tag: reference_from_string,
    ReferenceType_.c_tag: reference_type__from_string,
    Transforms.c_tag: transforms_from_string,
    TransformsType_.c_tag: transforms_type__from_string,
    Transform.c_tag: transform_from_string,
    TransformType_.c_tag: transform_type__from_string,
    DigestMethod.c_tag: digest_method_from_string,
    DigestMethodType_.c_tag: digest_method_type__from_string,
    DigestValue.c_tag: digest_value_from_string,
    DigestValueType_.c_tag: digest_value_type__from_string,
    KeyInfo.c_tag: key_info_from_string,
    KeyInfoType_.c_tag: key_info_type__from_string,
    KeyName.c_tag: key_name_from_string,
    MgmtData.c_tag: mgmt_data_from_string,
    KeyValue.c_tag: key_value_from_string,
    KeyValueType_.c_tag: key_value_type__from_string,
    RetrievalMethod.c_tag: retrieval_method_from_string,
    RetrievalMethodType_.c_tag: retrieval_method_type__from_string,
    X509Data.c_tag: x509_data_from_string,
    X509DataType_.c_tag: x509_data_type__from_string,
    X509IssuerSerialType_.c_tag: x509_issuer_serial_type__from_string,
    PGPData.c_tag: pgp_data_from_string,
    PGPDataType_.c_tag: pgp_data_type__from_string,
    SPKIData.c_tag: spki_data_from_string,
    SPKIDataType_.c_tag: spki_data_type__from_string,
    Object.c_tag: object_from_string,
    ObjectType_.c_tag: object_type__from_string,
    Manifest.c_tag: manifest_from_string,
    ManifestType_.c_tag: manifest_type__from_string,
    SignatureProperties.c_tag: signature_properties_from_string,
    SignaturePropertiesType_.c_tag: signature_properties_type__from_string,
    SignatureProperty.c_tag: signature_property_from_string,
    SignaturePropertyType_.c_tag: signature_property_type__from_string,
    HMACOutputLengthType_.c_tag: hmac_output_length_type__from_string,
    DSAKeyValue.c_tag: dsa_key_value_from_string,
    DSAKeyValueType_.c_tag: dsa_key_value_type__from_string,
    RSAKeyValue.c_tag: rsa_key_value_from_string,
    RSAKeyValueType_.c_tag: rsa_key_value_type__from_string,
    TransformType_XPath.c_tag: transform_type__x_path_from_string,
    X509IssuerName.c_tag: x509_issuer_name_from_string,
    X509SerialNumber.c_tag: x509_serial_number_from_string,
    PGPKeyID.c_tag: pgp_key_id_from_string,
    PGPKeyPacket.c_tag: pgp_key_packet_from_string,
    SPKISexp.c_tag: spki_sexp_from_string,
    P.c_tag: p_from_string,
    Q.c_tag: q_from_string,
    G.c_tag: g_from_string,
    Y.c_tag: y_from_string,
    J.c_tag: j_from_string,
    Seed.c_tag: seed_from_string,
    PgenCounter.c_tag: pgen_counter_from_string,
    Modulus.c_tag: modulus_from_string,
    Exponent.c_tag: exponent_from_string,
    HMACOutputLength.c_tag: hmac_output_length_from_string,
    X509IssuerSerial.c_tag: x509_issuer_serial_from_string,
    X509SKI.c_tag: x509_ski_from_string,
    X509SubjectName.c_tag: x509_subject_name_from_string,
    X509Certificate.c_tag: x509_certificate_from_string,
    X509CRL.c_tag: x509_crl_from_string,
}

ELEMENT_BY_TAG = {
    "CryptoBinary": CryptoBinary_,
    "Signature": Signature,
    "SignatureType": SignatureType_,
    "SignatureValue": SignatureValue,
    "SignatureValueType": SignatureValueType_,
    "SignedInfo": SignedInfo,
    "SignedInfoType": SignedInfoType_,
    "CanonicalizationMethod": CanonicalizationMethod,
    "CanonicalizationMethodType": CanonicalizationMethodType_,
    "SignatureMethod": SignatureMethod,
    "SignatureMethodType": SignatureMethodType_,
    "Reference": Reference,
    "ReferenceType": ReferenceType_,
    "Transforms": Transforms,
    "TransformsType": TransformsType_,
    "Transform": Transform,
    "TransformType": TransformType_,
    "DigestMethod": DigestMethod,
    "DigestMethodType": DigestMethodType_,
    "DigestValue": DigestValue,
    "DigestValueType": DigestValueType_,
    "KeyInfo": KeyInfo,
    "KeyInfoType": KeyInfoType_,
    "KeyName": KeyName,
    "MgmtData": MgmtData,
    "KeyValue": KeyValue,
    "KeyValueType": KeyValueType_,
    "RetrievalMethod": RetrievalMethod,
    "RetrievalMethodType": RetrievalMethodType_,
    "X509Data": X509Data,
    "X509DataType": X509DataType_,
    "X509IssuerSerialType": X509IssuerSerialType_,
    "PGPData": PGPData,
    "PGPDataType": PGPDataType_,
    "SPKIData": SPKIData,
    "SPKIDataType": SPKIDataType_,
    "Object": Object,
    "ObjectType": ObjectType_,
    "Manifest": Manifest,
    "ManifestType": ManifestType_,
    "SignatureProperties": SignatureProperties,
    "SignaturePropertiesType": SignaturePropertiesType_,
    "SignatureProperty": SignatureProperty,
    "SignaturePropertyType": SignaturePropertyType_,
    "HMACOutputLengthType": HMACOutputLengthType_,
    "DSAKeyValue": DSAKeyValue,
    "DSAKeyValueType": DSAKeyValueType_,
    "RSAKeyValue": RSAKeyValue,
    "RSAKeyValueType": RSAKeyValueType_,
    "XPath": TransformType_XPath,
    "X509IssuerName": X509IssuerName,
    "X509SerialNumber": X509SerialNumber,
    "PGPKeyID": PGPKeyID,
    "PGPKeyPacket": PGPKeyPacket,
    "SPKISexp": SPKISexp,
    "P": P,
    "Q": Q,
    "G": G,
    "Y": Y,
    "J": J,
    "Seed": Seed,
    "PgenCounter": PgenCounter,
    "Modulus": Modulus,
    "Exponent": Exponent,
    "HMACOutputLength": HMACOutputLength,
    "X509IssuerSerial": X509IssuerSerial,
    "X509SKI": X509SKI,
    "X509SubjectName": X509SubjectName,
    "X509Certificate": X509Certificate,
    "X509CRL": X509CRL,
}


def factory(tag, **kwargs):
    return ELEMENT_BY_TAG[tag](**kwargs)
