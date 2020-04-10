import warnings as _warnings

from saml2.cryptography.symmetric import AESCipher as _AESCipher


_deprecation_msg = (
    '{name} {type} is deprecated. '
    'It will be removed in the next version. '
    'Use saml2.cryptography.symmetric instead.'
).format(name=__name__, type='module')
_warnings.warn(_deprecation_msg, DeprecationWarning)


AESCipher = _AESCipher
POSTFIX_MODE = _AESCipher.POSTFIX_MODE
AES_BLOCK_SIZE = _AESCipher.AES_BLOCK_SIZE
