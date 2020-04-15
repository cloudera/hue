"""This module provides methods for symmetric cryptography.

The default symmetric cryptography method used is Fernet by the cryptography
library. Reference: https://cryptography.io/en/latest/fernet/
"""

import base64 as _base64
import os as _os
import warnings as _warnings

import cryptography.fernet as _fernet
import cryptography.hazmat.backends as _backends
import cryptography.hazmat.primitives.ciphers as _ciphers


class Default(object):
    """The default symmetric cryptography method."""

    @staticmethod
    def generate_key():
        """Return a key suitable for use by this method.

        :return: byte data representing the encyption/decryption key
        """
        key = _fernet.Fernet.generate_key()
        return key

    def __init__(self, key=None):
        """Initialize this method by optionally providing a key.

        :param key: byte data representing the encyption/decryption key
        """
        self._symmetric = _fernet.Fernet(key or self.__class__.generate_key())

    def encrypt(self, plaintext):
        """Encrypt the given plaintext.

        :param plaintext: byte data representing the plaintext
        :return: byte data representing the ciphertext
        """
        ciphertext = self._symmetric.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext):
        """Decrypt the given ciphertext.

        :param ciphertext: byte data representing the ciphertext
        :return: byte data representing the plaintext
        """
        plaintext = self._symmetric.decrypt(ciphertext)
        return plaintext


class AESCipher(object):
    """[deprecated] Symmetric cryptography method using AES.

    The default parameter set is AES 128bit in CBC mode.
    """

    POSTFIX_MODE = {
        'cbc': _ciphers.modes.CBC,
        'cfb': _ciphers.modes.CFB,
    }

    AES_BLOCK_SIZE = int(_ciphers.algorithms.AES.block_size / 8)

    @classmethod
    def _deprecation_notice(cls):
        """Warn about deprecation of this class."""
        _deprecation_msg = (
            '{name} {type} is deprecated. '
            'It will be removed in the next version. '
            'Use saml2.cryptography.symmetric instead.'
        ).format(name=cls.__name__, type=type(cls).__name__)
        _warnings.warn(_deprecation_msg, DeprecationWarning)

    def __init__(self, key):
        """
        :param key: The encryption key
        :return: AESCipher instance
        """
        self.__class__._deprecation_notice()
        self.key = key

    def build_cipher(self, alg='aes_128_cbc'):
        """
        :param alg: cipher algorithm
        :return: A Cipher instance
        """
        self.__class__._deprecation_notice()
        typ, bits, cmode = alg.lower().split('_')
        bits = int(bits)
        iv = _os.urandom(self.AES_BLOCK_SIZE)

        if len(iv) != self.AES_BLOCK_SIZE:
            raise Exception('Wrong iv size: {}'.format(len(iv)))

        if bits not in _ciphers.algorithms.AES.key_sizes:
            raise Exception('Unsupported key length: {}'.format(bits))

        if len(self.key) != bits / 8:
            raise Exception('Wrong Key length: {}'.format(len(self.key)))

        try:
            mode = self.POSTFIX_MODE[cmode]
        except KeyError:
            raise Exception('Unsupported chaining mode: {}'.format(cmode))

        cipher = _ciphers.Cipher(
                _ciphers.algorithms.AES(self.key),
                mode(iv),
                backend=_backends.default_backend())

        return cipher, iv

    def encrypt(self, msg, alg='aes_128_cbc', padding='PKCS#7', b64enc=True,
                block_size=AES_BLOCK_SIZE):
        """
        :param key: The encryption key
        :param msg: Message to be encrypted
        :param padding: Which padding that should be used
        :param b64enc: Whether the result should be base64encoded
        :param block_size: If PKCS#7 padding which block size to use
        :return: The encrypted message
        """
        self.__class__._deprecation_notice()
        if padding == 'PKCS#7':
            _block_size = block_size
        elif padding == 'PKCS#5':
            _block_size = 8
        else:
            _block_size = 0

        if _block_size:
            plen = _block_size - (len(msg) % _block_size)
            c = chr(plen).encode()
            msg += c * plen

        cipher, iv = self.build_cipher(alg)
        encryptor = cipher.encryptor()
        cmsg = iv + encryptor.update(msg) + encryptor.finalize()

        if b64enc:
            enc_msg = _base64.b64encode(cmsg)
        else:
            enc_msg = cmsg

        return enc_msg

    def decrypt(self, msg, alg='aes_128_cbc', padding='PKCS#7', b64dec=True):
        """
        :param key: The encryption key
        :param msg: Base64 encoded message to be decrypted
        :return: The decrypted message
        """
        self.__class__._deprecation_notice()
        data = _base64.b64decode(msg) if b64dec else msg

        cipher, iv = self.build_cipher(alg=alg)
        decryptor = cipher.decryptor()
        res = decryptor.update(data)[self.AES_BLOCK_SIZE:]
        res += decryptor.finalize()
        if padding in ['PKCS#5', 'PKCS#7']:
            idx = bytearray(res)[-1]
            res = res[:-idx]
        return res
