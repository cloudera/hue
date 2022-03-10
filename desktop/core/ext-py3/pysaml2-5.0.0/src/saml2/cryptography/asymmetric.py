"""This module provides methods for asymmetric cryptography."""

import cryptography.hazmat.backends as _backends
import cryptography.hazmat.primitives.asymmetric as _asymmetric
import cryptography.hazmat.primitives.hashes as _hashes
import cryptography.hazmat.primitives.serialization as _serialization


def load_pem_private_key(data, password):
    """Load RSA PEM certificate."""
    key = _serialization.load_pem_private_key(
        data, password, _backends.default_backend())
    return key


def key_sign(rsakey, message, digest):
    """Sign the given message with the RSA key."""
    padding = _asymmetric.padding.PKCS1v15()
    signature = rsakey.sign(message, padding, digest)
    return signature


def key_verify(rsakey, signature, message, digest):
    """Verify the given signature with the RSA key."""
    padding = _asymmetric.padding.PKCS1v15()
    if isinstance(rsakey, _asymmetric.rsa.RSAPrivateKey):
        rsakey = rsakey.public_key()

    try:
        rsakey.verify(signature, message, padding, digest)
    except Exception as e:
        return False
    else:
        return True


hashes = _hashes
