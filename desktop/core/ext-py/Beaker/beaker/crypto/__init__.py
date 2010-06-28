from warnings import warn

from beaker.crypto.pbkdf2 import PBKDF2, strxor
from beaker.exceptions import InvalidCryptoBackendError

_implementations = ('pycrypto', 'jcecrypto')

keyLength = None
for impl_name in _implementations:
    try:
        package = 'beaker.crypto.%s' % impl_name
        module = __import__(package, fromlist=('aesEncrypt', 'getKeyLength'))
        keyLength = module.getKeyLength()
        aesEncrypt = module.aesEncrypt
        if keyLength >= 32:
            break
    except:
        pass

if not keyLength:
    raise InvalidCryptoBackendError

if keyLength < 32:
    warn('Crypto implementation only supports key lengths up to %d bits. '
         'Generated session cookies may be incompatible with other '
         'environments' % (keyLength * 8))

def generateCryptoKeys(master_key, salt, iterations):
    # NB: We XOR parts of the keystream into the randomly-generated parts, just
    # in case os.urandom() isn't as random as it should be.  Note that if
    # os.urandom() returns truly random data, this will have no effect on the
    # overall security.
    keystream = PBKDF2(master_key, salt, iterations=iterations)
    cipher_key = keystream.read(keyLength)
    return cipher_key
