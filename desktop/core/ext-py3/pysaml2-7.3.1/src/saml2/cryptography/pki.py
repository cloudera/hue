"""This module provides methods for PKI operations."""

from logging import getLogger as get_logger

from cryptography.hazmat.primitives.serialization import Encoding as _cryptography_encoding
import cryptography.x509 as _x509


logger = get_logger(__name__)

DEFAULT_CERT_TYPE = "pem"


def load_pem_x509_certificate(data):
    """Load X.509 PEM certificate."""
    return _x509.load_pem_x509_certificate(data)


def load_der_x509_certificate(data):
    """Load X.509 DER certificate."""
    return _x509.load_der_x509_certificate(data)


def load_x509_certificate(data, cert_type="pem"):
    cert_reader = _x509_loaders.get(cert_type)

    if not cert_reader:
        cert_reader = _x509_loaders.get("pem")
        context = {
            "message": "Unknown cert_type, falling back to default",
            "cert_type": cert_type,
            "default": DEFAULT_CERT_TYPE,
        }
        logger.warning(context)

    cert = cert_reader(data)
    return cert


def get_public_bytes_from_cert(cert):
    data = cert.public_bytes(_cryptography_encoding.PEM).decode()
    return data


_x509_loaders = {
    "pem": load_pem_x509_certificate,
    "der": load_der_x509_certificate,
}
