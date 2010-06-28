"""
Encryption module that uses pycryptopp.
"""
from pycryptopp.cipher import aes

def aesEncrypt(data, key):
    cipher = aes.AES(key)
    return cipher.process(data)


def getKeyLength():
    return 32
