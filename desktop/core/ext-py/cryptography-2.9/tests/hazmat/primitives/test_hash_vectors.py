# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import binascii
import os

import pytest

from cryptography.hazmat.backends.interfaces import HashBackend
from cryptography.hazmat.primitives import hashes

from .utils import _load_all_params, generate_hash_test
from ...utils import load_hash_vectors, load_nist_vectors


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA1()),
    skip_message="Does not support SHA1",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA1(object):
    test_sha1 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA1"),
        [
            "SHA1LongMsg.rsp",
            "SHA1ShortMsg.rsp",
        ],
        hashes.SHA1(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA224()),
    skip_message="Does not support SHA224",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA224(object):
    test_sha224 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA224LongMsg.rsp",
            "SHA224ShortMsg.rsp",
        ],
        hashes.SHA224(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA256()),
    skip_message="Does not support SHA256",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA256(object):
    test_sha256 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA256LongMsg.rsp",
            "SHA256ShortMsg.rsp",
        ],
        hashes.SHA256(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA384()),
    skip_message="Does not support SHA384",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA384(object):
    test_sha384 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA384LongMsg.rsp",
            "SHA384ShortMsg.rsp",
        ],
        hashes.SHA384(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA512()),
    skip_message="Does not support SHA512",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA512(object):
    test_sha512 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA512LongMsg.rsp",
            "SHA512ShortMsg.rsp",
        ],
        hashes.SHA512(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA512_224()),
    skip_message="Does not support SHA512/224",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA512224(object):
    test_sha512_224 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA512_224LongMsg.rsp",
            "SHA512_224ShortMsg.rsp",
        ],
        hashes.SHA512_224(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA512_256()),
    skip_message="Does not support SHA512/256",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA512256(object):
    test_sha512_256 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA2"),
        [
            "SHA512_256LongMsg.rsp",
            "SHA512_256ShortMsg.rsp",
        ],
        hashes.SHA512_256(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.MD5()),
    skip_message="Does not support MD5",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestMD5(object):
    test_md5 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "MD5"),
        [
            "rfc-1321.txt",
        ],
        hashes.MD5(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(
        hashes.BLAKE2b(digest_size=64)),
    skip_message="Does not support BLAKE2b",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestBLAKE2b(object):
    test_b2b = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "blake2"),
        [
            "blake2b.txt",
        ],
        hashes.BLAKE2b(digest_size=64),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(
        hashes.BLAKE2s(digest_size=32)),
    skip_message="Does not support BLAKE2s",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestBLAKE2s256(object):
    test_b2s = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "blake2"),
        [
            "blake2s.txt",
        ],
        hashes.BLAKE2s(digest_size=32),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA3_224()),
    skip_message="Does not support SHA3_224",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA3224(object):
    test_sha3_224 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA3"),
        [
            "SHA3_224LongMsg.rsp",
            "SHA3_224ShortMsg.rsp",
        ],
        hashes.SHA3_224(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA3_256()),
    skip_message="Does not support SHA3_256",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA3256(object):
    test_sha3_256 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA3"),
        [
            "SHA3_256LongMsg.rsp",
            "SHA3_256ShortMsg.rsp",
        ],
        hashes.SHA3_256(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA3_384()),
    skip_message="Does not support SHA3_384",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA3384(object):
    test_sha3_384 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA3"),
        [
            "SHA3_384LongMsg.rsp",
            "SHA3_384ShortMsg.rsp",
        ],
        hashes.SHA3_384(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(hashes.SHA3_512()),
    skip_message="Does not support SHA3_512",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHA3512(object):
    test_sha3_512 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHA3"),
        [
            "SHA3_512LongMsg.rsp",
            "SHA3_512ShortMsg.rsp",
        ],
        hashes.SHA3_512(),
    )


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(
        hashes.SHAKE128(digest_size=16)),
    skip_message="Does not support SHAKE128",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHAKE128(object):
    test_shake128 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHAKE"),
        [
            "SHAKE128LongMsg.rsp",
            "SHAKE128ShortMsg.rsp",
        ],
        hashes.SHAKE128(digest_size=16),
    )

    @pytest.mark.parametrize(
        "vector",
        _load_all_params(
            os.path.join("hashes", "SHAKE"),
            [
                "SHAKE128VariableOut.rsp",
            ],
            load_nist_vectors,
        )
    )
    def test_shake128_variable(self, vector, backend):
        output_length = int(vector['outputlen']) // 8
        msg = binascii.unhexlify(vector['msg'])
        shake = hashes.SHAKE128(digest_size=output_length)
        m = hashes.Hash(shake, backend=backend)
        m.update(msg)
        assert m.finalize() == binascii.unhexlify(vector['output'])


@pytest.mark.supported(
    only_if=lambda backend: backend.hash_supported(
        hashes.SHAKE256(digest_size=32)),
    skip_message="Does not support SHAKE256",
)
@pytest.mark.requires_backend_interface(interface=HashBackend)
class TestSHAKE256(object):
    test_shake256 = generate_hash_test(
        load_hash_vectors,
        os.path.join("hashes", "SHAKE"),
        [
            "SHAKE256LongMsg.rsp",
            "SHAKE256ShortMsg.rsp",
        ],
        hashes.SHAKE256(digest_size=32),
    )

    @pytest.mark.parametrize(
        "vector",
        _load_all_params(
            os.path.join("hashes", "SHAKE"),
            [
                "SHAKE256VariableOut.rsp",
            ],
            load_nist_vectors,
        )
    )
    def test_shake256_variable(self, vector, backend):
        output_length = int(vector['outputlen']) // 8
        msg = binascii.unhexlify(vector['msg'])
        shake = hashes.SHAKE256(digest_size=output_length)
        m = hashes.Hash(shake, backend=backend)
        m.update(msg)
        assert m.finalize() == binascii.unhexlify(vector['output'])
