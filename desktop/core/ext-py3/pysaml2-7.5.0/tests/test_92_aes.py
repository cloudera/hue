import os

from saml2.cryptography.symmetric import AESCipher


class TestAES:
    def test_aes_defaults(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(16)
        aes = AESCipher(key)

        encrypted_msg = aes.encrypt(original_msg)
        decrypted_msg = aes.decrypt(encrypted_msg)
        assert decrypted_msg == original_msg

    def test_aes_128_cbc(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(16)
        aes = AESCipher(key)
        alg = "aes_128_cbc"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg

    def test_aes_128_cfb(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(16)
        aes = AESCipher(key)
        alg = "aes_128_cfb"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg

    def test_aes_192_cbc(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(24)
        aes = AESCipher(key)
        alg = "aes_192_cbc"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg

    def test_aes_192_cfb(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(24)
        aes = AESCipher(key)
        alg = "aes_192_cfb"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg

    def test_aes_256_cbc(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(32)
        aes = AESCipher(key)
        alg = "aes_256_cbc"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg

    def test_aes_256_cfb(self):
        original_msg = b"ToBeOrNotTobe W.S."
        key = os.urandom(32)
        aes = AESCipher(key)
        alg = "aes_256_cfb"

        encrypted_msg = aes.encrypt(original_msg, alg=alg)
        decrypted_msg = aes.decrypt(encrypted_msg, alg=alg)
        assert decrypted_msg == original_msg
