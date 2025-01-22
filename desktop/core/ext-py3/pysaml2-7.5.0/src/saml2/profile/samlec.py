from saml2 import SamlBase


NAMESPACE = "urn:ietf:params:xml:ns:samlec"


class GeneratedKey(SamlBase):
    c_tag = "GeneratedKey"
    c_namespace = NAMESPACE


ELEMENT_BY_TAG = {
    "GeneratedKey": GeneratedKey,
}
