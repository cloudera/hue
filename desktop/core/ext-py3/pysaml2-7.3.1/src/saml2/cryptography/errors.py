from saml2 import Error


class CryptographyError(Error):
    """Generic error from saml2.cryptography modules"""


class SymmetricCryptographyError(CryptographyError):
    """Generic error from saml2.cryptography.symmetric modules"""


class AsymmetricCryptographyError(CryptographyError):
    """Generic error from saml2.cryptography.asymmetric modules"""


class PKICryptographyError(CryptographyError):
    """Generic error from saml2.cryptography.pki modules"""
