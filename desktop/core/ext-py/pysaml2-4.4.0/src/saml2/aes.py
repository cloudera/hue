#!/usr/bin/env python
import os
from base64 import b64encode
from base64 import b64decode

from Cryptodome import Random
from Cryptodome.Cipher import AES

__author__ = 'rolandh'

POSTFIX_MODE = {
    "cbc": AES.MODE_CBC,
    "cfb": AES.MODE_CFB,
    "ecb": AES.MODE_CFB,
}

BLOCK_SIZE = 16


class AESCipher(object):
    def __init__(self, key, iv=""):
        """

        :param key: The encryption key
        :param iv: Init vector
        :return: AESCipher instance
        """
        self.key = key
        self.iv = iv

    def build_cipher(self, iv="", alg="aes_128_cbc"):
        """
        :param iv: init vector
        :param alg: cipher algorithm
        :return: A Cipher instance
        """
        typ, bits, cmode = alg.split("_")

        if not iv:
            if self.iv:
                iv = self.iv
            else:
                iv = Random.new().read(AES.block_size)
        else:
            assert len(iv) == AES.block_size

        if bits not in ["128", "192", "256"]:
            raise Exception("Unsupported key length")
        try:
            assert len(self.key) == int(bits) >> 3
        except AssertionError:
            raise Exception("Wrong Key length")

        try:
            return AES.new(self.key, POSTFIX_MODE[cmode], iv), iv
        except KeyError:
            raise Exception("Unsupported chaining mode")


    def encrypt(self, msg, iv=None, alg="aes_128_cbc", padding="PKCS#7",
                b64enc=True, block_size=BLOCK_SIZE):
        """
        :param key: The encryption key
        :param iv: init vector
        :param msg: Message to be encrypted
        :param padding: Which padding that should be used
        :param b64enc: Whether the result should be base64encoded
        :param block_size: If PKCS#7 padding which block size to use
        :return: The encrypted message
        """

        if padding == "PKCS#7":
            _block_size = block_size
        elif padding == "PKCS#5":
            _block_size = 8
        else:
            _block_size = 0

        if _block_size:
            plen = _block_size - (len(msg) % _block_size)
            c = chr(plen)
            msg += c*plen

        cipher, iv = self.build_cipher(iv, alg)
        cmsg = iv + cipher.encrypt(msg)
        if b64enc:
            return b64encode(cmsg)
        else:
            return cmsg


    def decrypt(self, msg, iv=None, alg="aes_128_cbc", padding="PKCS#7", b64dec=True):
        """
        :param key: The encryption key
        :param iv: init vector
        :param msg: Base64 encoded message to be decrypted
        :return: The decrypted message
        """
        if b64dec:
            data = b64decode(msg)
        else:
            data = msg

        _iv = data[:AES.block_size]
        if iv:
            assert iv == _iv
        cipher, iv = self.build_cipher(iv, alg=alg)
        res = cipher.decrypt(data)[AES.block_size:]
        if padding in ["PKCS#5", "PKCS#7"]:
            res = res[:-ord(res[-1])]
        return res

if __name__ == "__main__":
    key_ = "1234523451234545"  # 16 byte key
    # Iff padded, the message doesn't have to be multiple of 16 in length
    msg_ = "ToBeOrNotTobe W.S."
    aes = AESCipher(key_)
    iv_ = os.urandom(16)
    encrypted_msg = aes.encrypt(key_, msg_, iv_)
    txt = aes.decrypt(key_, encrypted_msg, iv_)
    assert txt == msg_

    encrypted_msg = aes.encrypt(key_, msg_, 0)
    txt = aes.decrypt(key_, encrypted_msg, 0)
    assert txt == msg_
