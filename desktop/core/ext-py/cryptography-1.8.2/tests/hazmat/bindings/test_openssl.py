# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

from __future__ import absolute_import, division, print_function

import pytest

from cryptography.exceptions import InternalError
from cryptography.hazmat.bindings.openssl.binding import (
    Binding, _OpenSSLErrorWithText, _consume_errors, _openssl_assert
)


class TestOpenSSL(object):
    def test_binding_loads(self):
        binding = Binding()
        assert binding
        assert binding.lib
        assert binding.ffi

    def test_crypto_lock_init(self):
        b = Binding()
        if (
            b.lib.CRYPTOGRAPHY_OPENSSL_110_OR_GREATER and
            not b.lib.CRYPTOGRAPHY_IS_LIBRESSL
        ):
            pytest.skip("Requires an older OpenSSL. Must be < 1.1.0")

        b.init_static_locks()
        lock_cb = b.lib.CRYPTO_get_locking_callback()
        assert lock_cb != b.ffi.NULL

    def test_add_engine_more_than_once(self):
        b = Binding()
        b._register_osrandom_engine()
        assert b.lib.ERR_get_error() == 0

    def test_ssl_ctx_options(self):
        # Test that we're properly handling 32-bit unsigned on all platforms.
        b = Binding()
        assert b.lib.SSL_OP_ALL > 0
        ctx = b.lib.SSL_CTX_new(b.lib.TLSv1_method())
        ctx = b.ffi.gc(ctx, b.lib.SSL_CTX_free)
        current_options = b.lib.SSL_CTX_get_options(ctx)
        resp = b.lib.SSL_CTX_set_options(ctx, b.lib.SSL_OP_ALL)
        expected_options = current_options | b.lib.SSL_OP_ALL
        assert resp == expected_options
        assert b.lib.SSL_CTX_get_options(ctx) == expected_options

    def test_ssl_options(self):
        # Test that we're properly handling 32-bit unsigned on all platforms.
        b = Binding()
        assert b.lib.SSL_OP_ALL > 0
        ctx = b.lib.SSL_CTX_new(b.lib.TLSv1_method())
        ctx = b.ffi.gc(ctx, b.lib.SSL_CTX_free)
        ssl = b.lib.SSL_new(ctx)
        ssl = b.ffi.gc(ssl, b.lib.SSL_free)
        current_options = b.lib.SSL_get_options(ssl)
        resp = b.lib.SSL_set_options(ssl, b.lib.SSL_OP_ALL)
        expected_options = current_options | b.lib.SSL_OP_ALL
        assert resp == expected_options
        assert b.lib.SSL_get_options(ssl) == expected_options

    def test_ssl_mode(self):
        # Test that we're properly handling 32-bit unsigned on all platforms.
        b = Binding()
        assert b.lib.SSL_OP_ALL > 0
        ctx = b.lib.SSL_CTX_new(b.lib.TLSv1_method())
        ctx = b.ffi.gc(ctx, b.lib.SSL_CTX_free)
        ssl = b.lib.SSL_new(ctx)
        ssl = b.ffi.gc(ssl, b.lib.SSL_free)
        current_options = b.lib.SSL_get_mode(ssl)
        resp = b.lib.SSL_set_mode(ssl, b.lib.SSL_OP_ALL)
        expected_options = current_options | b.lib.SSL_OP_ALL
        assert resp == expected_options
        assert b.lib.SSL_get_mode(ssl) == expected_options

    def test_conditional_removal(self):
        b = Binding()

        if (
            b.lib.CRYPTOGRAPHY_OPENSSL_110_OR_GREATER and
            not b.lib.CRYPTOGRAPHY_IS_LIBRESSL
        ):
            assert b.lib.TLS_ST_OK
        else:
            with pytest.raises(AttributeError):
                b.lib.TLS_ST_OK

    def test_openssl_assert_error_on_stack(self):
        b = Binding()
        b.lib.ERR_put_error(
            b.lib.ERR_LIB_EVP,
            b.lib.EVP_F_EVP_ENCRYPTFINAL_EX,
            b.lib.EVP_R_DATA_NOT_MULTIPLE_OF_BLOCK_LENGTH,
            b"",
            -1
        )
        with pytest.raises(InternalError) as exc_info:
            _openssl_assert(b.lib, False)

        assert exc_info.value.err_code == [_OpenSSLErrorWithText(
            code=101183626,
            lib=b.lib.ERR_LIB_EVP,
            func=b.lib.EVP_F_EVP_ENCRYPTFINAL_EX,
            reason=b.lib.EVP_R_DATA_NOT_MULTIPLE_OF_BLOCK_LENGTH,
            reason_text=(
                b'error:0607F08A:digital envelope routines:EVP_EncryptFinal_'
                b'ex:data not multiple of block length'
            )
        )]

    def test_check_startup_errors_are_allowed(self):
        b = Binding()
        b.lib.ERR_put_error(
            b.lib.ERR_LIB_EVP,
            b.lib.EVP_F_EVP_ENCRYPTFINAL_EX,
            b.lib.EVP_R_DATA_NOT_MULTIPLE_OF_BLOCK_LENGTH,
            b"",
            -1
        )
        b._register_osrandom_engine()
        assert _consume_errors(b.lib) == []
