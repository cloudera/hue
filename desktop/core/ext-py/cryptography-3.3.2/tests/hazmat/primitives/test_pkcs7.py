# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import os

import pytest

from cryptography import x509
from cryptography.exceptions import _Reasons
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import pkcs7

from .utils import load_vectors_from_file
from ...utils import raises_unsupported_algorithm


class TestPKCS7Loading(object):
    def test_load_invalid_der_pkcs7(self):
        with pytest.raises(ValueError):
            pkcs7.load_der_pkcs7_certificates(b"nonsense")

    def test_load_invalid_pem_pkcs7(self):
        with pytest.raises(ValueError):
            pkcs7.load_pem_pkcs7_certificates(b"nonsense")

    def test_not_bytes_der(self):
        with pytest.raises(TypeError):
            pkcs7.load_der_pkcs7_certificates(38)

    def test_not_bytes_pem(self):
        with pytest.raises(TypeError):
            pkcs7.load_pem_pkcs7_certificates(38)

    def test_load_pkcs7_pem(self):
        certs = load_vectors_from_file(
            os.path.join("pkcs7", "isrg.pem"),
            lambda pemfile: pkcs7.load_pem_pkcs7_certificates(pemfile.read()),
            mode="rb",
        )
        assert len(certs) == 1
        assert certs[0].subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        ) == [
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, u"ISRG Root X1")
        ]

    def test_load_pkcs7_der(self):
        certs = load_vectors_from_file(
            os.path.join("pkcs7", "amazon-roots.p7b"),
            lambda derfile: pkcs7.load_der_pkcs7_certificates(derfile.read()),
            mode="rb",
        )
        assert len(certs) == 2
        assert certs[0].subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        ) == [
            x509.NameAttribute(
                x509.oid.NameOID.COMMON_NAME, u"Amazon Root CA 3"
            )
        ]
        assert certs[1].subject.get_attributes_for_oid(
            x509.oid.NameOID.COMMON_NAME
        ) == [
            x509.NameAttribute(
                x509.oid.NameOID.COMMON_NAME, u"Amazon Root CA 2"
            )
        ]

    def test_load_pkcs7_unsupported_type(self):
        with raises_unsupported_algorithm(_Reasons.UNSUPPORTED_SERIALIZATION):
            load_vectors_from_file(
                os.path.join("pkcs7", "enveloped.pem"),
                lambda pemfile: pkcs7.load_pem_pkcs7_certificates(
                    pemfile.read()
                ),
                mode="rb",
            )


# We have no public verification API and won't be adding one until we get
# some requirements from users so this function exists to give us basic
# verification for the signing tests.
def _pkcs7_verify(encoding, sig, msg, certs, options, backend):
    sig_bio = backend._bytes_to_bio(sig)
    if encoding is serialization.Encoding.DER:
        p7 = backend._lib.d2i_PKCS7_bio(sig_bio.bio, backend._ffi.NULL)
    elif encoding is serialization.Encoding.PEM:
        p7 = backend._lib.PEM_read_bio_PKCS7(
            sig_bio.bio,
            backend._ffi.NULL,
            backend._ffi.NULL,
            backend._ffi.NULL,
        )
    else:
        p7 = backend._lib.SMIME_read_PKCS7(sig_bio.bio, backend._ffi.NULL)
    backend.openssl_assert(p7 != backend._ffi.NULL)
    p7 = backend._ffi.gc(p7, backend._lib.PKCS7_free)
    flags = 0
    for option in options:
        if option is pkcs7.PKCS7Options.Text:
            flags |= backend._lib.PKCS7_TEXT
    store = backend._lib.X509_STORE_new()
    backend.openssl_assert(store != backend._ffi.NULL)
    store = backend._ffi.gc(store, backend._lib.X509_STORE_free)
    for cert in certs:
        res = backend._lib.X509_STORE_add_cert(store, cert._x509)
        backend.openssl_assert(res == 1)
    if msg is None:
        res = backend._lib.PKCS7_verify(
            p7,
            backend._ffi.NULL,
            store,
            backend._ffi.NULL,
            backend._ffi.NULL,
            flags,
        )
    else:
        msg_bio = backend._bytes_to_bio(msg)
        res = backend._lib.PKCS7_verify(
            p7, backend._ffi.NULL, store, msg_bio.bio, backend._ffi.NULL, flags
        )
    backend.openssl_assert(res == 1)


def _load_cert_key():
    key = load_vectors_from_file(
        os.path.join("x509", "custom", "ca", "ca_key.pem"),
        lambda pemfile: serialization.load_pem_private_key(
            pemfile.read(), None
        ),
        mode="rb",
    )
    cert = load_vectors_from_file(
        os.path.join("x509", "custom", "ca", "ca.pem"),
        loader=lambda pemfile: x509.load_pem_x509_certificate(pemfile.read()),
        mode="rb",
    )
    return cert, key


class TestPKCS7Builder(object):
    def test_invalid_data(self):
        builder = pkcs7.PKCS7SignatureBuilder()
        with pytest.raises(TypeError):
            builder.set_data(u"not bytes")

    def test_set_data_twice(self):
        builder = pkcs7.PKCS7SignatureBuilder().set_data(b"test")
        with pytest.raises(ValueError):
            builder.set_data(b"test")

    def test_sign_no_signer(self):
        builder = pkcs7.PKCS7SignatureBuilder().set_data(b"test")
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.SMIME, [])

    def test_sign_no_data(self):
        cert, key = _load_cert_key()
        builder = pkcs7.PKCS7SignatureBuilder().add_signer(
            cert, key, hashes.SHA256()
        )
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.SMIME, [])

    def test_unsupported_hash_alg(self):
        cert, key = _load_cert_key()
        with pytest.raises(TypeError):
            pkcs7.PKCS7SignatureBuilder().add_signer(
                cert, key, hashes.SHA512_256()
            )

    def test_not_a_cert(self):
        cert, key = _load_cert_key()
        with pytest.raises(TypeError):
            pkcs7.PKCS7SignatureBuilder().add_signer(
                b"notacert", key, hashes.SHA256()
            )

    @pytest.mark.supported(
        only_if=lambda backend: backend.ed25519_supported(),
        skip_message="Does not support ed25519.",
    )
    def test_unsupported_key_type(self, backend):
        cert, _ = _load_cert_key()
        key = ed25519.Ed25519PrivateKey.generate()
        with pytest.raises(TypeError):
            pkcs7.PKCS7SignatureBuilder().add_signer(
                cert, key, hashes.SHA256()
            )

    def test_sign_invalid_options(self):
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"test")
            .add_signer(cert, key, hashes.SHA256())
        )
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.SMIME, [b"invalid"])

    def test_sign_invalid_encoding(self):
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"test")
            .add_signer(cert, key, hashes.SHA256())
        )
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.Raw, [])

    def test_sign_invalid_options_text_no_detached(self):
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"test")
            .add_signer(cert, key, hashes.SHA256())
        )
        options = [pkcs7.PKCS7Options.Text]
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.SMIME, options)

    def test_sign_invalid_options_text_der_encoding(self):
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"test")
            .add_signer(cert, key, hashes.SHA256())
        )
        options = [
            pkcs7.PKCS7Options.Text,
            pkcs7.PKCS7Options.DetachedSignature,
        ]
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.DER, options)

    def test_sign_invalid_options_no_attrs_and_no_caps(self):
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(b"test")
            .add_signer(cert, key, hashes.SHA256())
        )
        options = [
            pkcs7.PKCS7Options.NoAttributes,
            pkcs7.PKCS7Options.NoCapabilities,
        ]
        with pytest.raises(ValueError):
            builder.sign(serialization.Encoding.SMIME, options)

    def test_smime_sign_detached(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        options = [pkcs7.PKCS7Options.DetachedSignature]
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        sig = builder.sign(serialization.Encoding.SMIME, options)
        sig_binary = builder.sign(serialization.Encoding.DER, options)
        # We don't have a generic ASN.1 parser available to us so we instead
        # will assert on specific byte sequences being present based on the
        # parameters chosen above.
        assert b"sha-256" in sig
        # Detached signature means that the signed data is *not* embedded into
        # the PKCS7 structure itself, but is present in the SMIME serialization
        # as a separate section before the PKCS7 data. So we should expect to
        # have data in sig but not in sig_binary
        assert data in sig
        _pkcs7_verify(
            serialization.Encoding.SMIME, sig, data, [cert], options, backend
        )
        assert data not in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            data,
            [cert],
            options,
            backend,
        )

    def test_sign_byteslike(self):
        data = bytearray(b"hello world")
        cert, key = _load_cert_key()
        options = [pkcs7.PKCS7Options.DetachedSignature]
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        sig = builder.sign(serialization.Encoding.SMIME, options)
        assert bytes(data) in sig

    def test_sign_pem(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        options = []
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        sig = builder.sign(serialization.Encoding.PEM, options)
        _pkcs7_verify(
            serialization.Encoding.PEM,
            sig,
            None,
            [cert],
            options,
            backend,
        )

    @pytest.mark.parametrize(
        ("hash_alg", "expected_value"),
        [
            (hashes.SHA1(), b"\x06\x05+\x0e\x03\x02\x1a"),
            (hashes.SHA256(), b"\x06\t`\x86H\x01e\x03\x04\x02\x01"),
            (hashes.SHA384(), b"\x06\t`\x86H\x01e\x03\x04\x02\x02"),
            (hashes.SHA512(), b"\x06\t`\x86H\x01e\x03\x04\x02\x03"),
        ],
    )
    def test_sign_alternate_digests_der(
        self, hash_alg, expected_value, backend
    ):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hash_alg)
        )
        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        assert expected_value in sig
        _pkcs7_verify(
            serialization.Encoding.DER, sig, None, [cert], options, backend
        )

    @pytest.mark.parametrize(
        ("hash_alg", "expected_value"),
        [
            (hashes.SHA1(), b"sha1"),
            (hashes.SHA256(), b"sha-256"),
            (hashes.SHA384(), b"sha-384"),
            (hashes.SHA512(), b"sha-512"),
        ],
    )
    def test_sign_alternate_digests_detached(self, hash_alg, expected_value):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hash_alg)
        )
        options = [pkcs7.PKCS7Options.DetachedSignature]
        sig = builder.sign(serialization.Encoding.SMIME, options)
        # When in detached signature mode the hash algorithm is stored as a
        # byte string like "sha-384".
        assert expected_value in sig

    def test_sign_attached(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        options = []
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        sig_binary = builder.sign(serialization.Encoding.DER, options)
        # When not passing detached signature the signed data is embedded into
        # the PKCS7 structure itself
        assert data in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            None,
            [cert],
            options,
            backend,
        )

    def test_sign_binary(self, backend):
        data = b"hello\nworld"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )
        options = []
        sig_no_binary = builder.sign(serialization.Encoding.DER, options)
        sig_binary = builder.sign(
            serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary]
        )
        # Binary prevents translation of LF to CR+LF (SMIME canonical form)
        # so data should not be present in sig_no_binary, but should be present
        # in sig_binary
        assert data not in sig_no_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_no_binary,
            None,
            [cert],
            options,
            backend,
        )
        assert data in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            None,
            [cert],
            options,
            backend,
        )

    def test_sign_smime_canonicalization(self, backend):
        data = b"hello\nworld"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        options = []
        sig_binary = builder.sign(serialization.Encoding.DER, options)
        # LF gets converted to CR+LF (SMIME canonical form)
        # so data should not be present in the sig
        assert data not in sig_binary
        assert b"hello\r\nworld" in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            None,
            [cert],
            options,
            backend,
        )

    def test_sign_text(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        options = [
            pkcs7.PKCS7Options.Text,
            pkcs7.PKCS7Options.DetachedSignature,
        ]
        sig_pem = builder.sign(serialization.Encoding.SMIME, options)
        # The text option adds text/plain headers to the S/MIME message
        # These headers are only relevant in SMIME mode, not binary, which is
        # just the PKCS7 structure itself.
        assert b"text/plain" in sig_pem
        # When passing the Text option the header is prepended so the actual
        # signed data is this.
        signed_data = b"Content-Type: text/plain\r\n\r\nhello world"
        _pkcs7_verify(
            serialization.Encoding.SMIME,
            sig_pem,
            signed_data,
            [cert],
            options,
            backend,
        )

    def test_sign_no_capabilities(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        options = [pkcs7.PKCS7Options.NoCapabilities]
        sig_binary = builder.sign(serialization.Encoding.DER, options)
        # NoCapabilities removes the SMIMECapabilities attribute from the
        # PKCS7 structure. This is an ASN.1 sequence with the
        # OID 1.2.840.113549.1.9.15. It does NOT remove all authenticated
        # attributes, so we verify that by looking for the signingTime OID.

        # 1.2.840.113549.1.9.15 SMIMECapabilities as an ASN.1 DER encoded OID
        assert b"\x06\t*\x86H\x86\xf7\r\x01\t\x0f" not in sig_binary
        # 1.2.840.113549.1.9.5 signingTime as an ASN.1 DER encoded OID
        assert b"\x06\t*\x86H\x86\xf7\r\x01\t\x05" in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            None,
            [cert],
            options,
            backend,
        )

    def test_sign_no_attributes(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        options = [pkcs7.PKCS7Options.NoAttributes]
        sig_binary = builder.sign(serialization.Encoding.DER, options)
        # NoAttributes removes all authenticated attributes, so we shouldn't
        # find SMIMECapabilities or signingTime.

        # 1.2.840.113549.1.9.15 SMIMECapabilities as an ASN.1 DER encoded OID
        assert b"\x06\t*\x86H\x86\xf7\r\x01\t\x0f" not in sig_binary
        # 1.2.840.113549.1.9.5 signingTime as an ASN.1 DER encoded OID
        assert b"\x06\t*\x86H\x86\xf7\r\x01\t\x05" not in sig_binary
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig_binary,
            None,
            [cert],
            options,
            backend,
        )

    def test_sign_no_certs(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA256())
        )

        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        assert sig.count(cert.public_bytes(serialization.Encoding.DER)) == 1

        options = [pkcs7.PKCS7Options.NoCerts]
        sig_no = builder.sign(serialization.Encoding.DER, options)
        assert sig_no.count(cert.public_bytes(serialization.Encoding.DER)) == 0

    def test_multiple_signers(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        rsa_key = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_key.pem"),
            lambda pemfile: serialization.load_pem_private_key(
                pemfile.read(), None
            ),
            mode="rb",
        )
        rsa_cert = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_ca.pem"),
            loader=lambda pemfile: x509.load_pem_x509_certificate(
                pemfile.read()
            ),
            mode="rb",
        )
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA512())
            .add_signer(rsa_cert, rsa_key, hashes.SHA512())
        )
        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        # There should be three SHA512 OIDs in this structure
        assert sig.count(b"\x06\t`\x86H\x01e\x03\x04\x02\x03") == 3
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig,
            None,
            [cert, rsa_cert],
            options,
            backend,
        )

    def test_multiple_signers_different_hash_algs(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        rsa_key = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_key.pem"),
            lambda pemfile: serialization.load_pem_private_key(
                pemfile.read(), None
            ),
            mode="rb",
        )
        rsa_cert = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_ca.pem"),
            loader=lambda pemfile: x509.load_pem_x509_certificate(
                pemfile.read()
            ),
            mode="rb",
        )
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA384())
            .add_signer(rsa_cert, rsa_key, hashes.SHA512())
        )
        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        # There should be two SHA384 and two SHA512 OIDs in this structure
        assert sig.count(b"\x06\t`\x86H\x01e\x03\x04\x02\x02") == 2
        assert sig.count(b"\x06\t`\x86H\x01e\x03\x04\x02\x03") == 2
        _pkcs7_verify(
            serialization.Encoding.DER,
            sig,
            None,
            [cert, rsa_cert],
            options,
            backend,
        )

    def test_add_additional_cert_not_a_cert(self, backend):
        with pytest.raises(TypeError):
            pkcs7.PKCS7SignatureBuilder().add_certificate(b"notacert")

    def test_add_additional_cert(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        rsa_cert = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_ca.pem"),
            loader=lambda pemfile: x509.load_pem_x509_certificate(
                pemfile.read()
            ),
            mode="rb",
        )
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA384())
            .add_certificate(rsa_cert)
        )
        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        assert (
            sig.count(rsa_cert.public_bytes(serialization.Encoding.DER)) == 1
        )

    def test_add_multiple_additional_certs(self, backend):
        data = b"hello world"
        cert, key = _load_cert_key()
        rsa_cert = load_vectors_from_file(
            os.path.join("x509", "custom", "ca", "rsa_ca.pem"),
            loader=lambda pemfile: x509.load_pem_x509_certificate(
                pemfile.read()
            ),
            mode="rb",
        )
        builder = (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(data)
            .add_signer(cert, key, hashes.SHA384())
            .add_certificate(rsa_cert)
            .add_certificate(rsa_cert)
        )
        options = []
        sig = builder.sign(serialization.Encoding.DER, options)
        assert (
            sig.count(rsa_cert.public_bytes(serialization.Encoding.DER)) == 2
        )
