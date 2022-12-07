import sys as __sys

if __sys.version_info < (3, ):  # pragma: no cover
    print('WARNING, Python 2 is EOL and therefore py2 support in this '
          "package is deprecated. It won't be actively checked for"
          'correctness')

# list all the constants and export them
from .__internals import PAM_ACCT_EXPIRED
from .__internals import PAM_AUTHINFO_UNAVAIL
from .__internals import PAM_AUTHTOK_DISABLE_AGING
from .__internals import PAM_AUTHTOK_ERR
from .__internals import PAM_ABORT
from .__internals import PAM_AUTHTOK_EXPIRED
from .__internals import PAM_AUTHTOK_LOCK_BUSY
from .__internals import PAM_AUTHTOK_RECOVER_ERR
from .__internals import PAM_AUTH_ERR
from .__internals import PAM_BAD_ITEM
from .__internals import PAM_BUF_ERR
from .__internals import PAM_CHANGE_EXPIRED_AUTHTOK
from .__internals import PAM_CONV
from .__internals import PAM_CONV_ERR
from .__internals import PAM_CRED_ERR
from .__internals import PAM_CRED_EXPIRED
from .__internals import PAM_CRED_INSUFFICIENT
from .__internals import PAM_CRED_UNAVAIL
from .__internals import PAM_DATA_SILENT
from .__internals import PAM_DELETE_CRED
from .__internals import PAM_DISALLOW_NULL_AUTHTOK
from .__internals import PAM_ERROR_MSG
from .__internals import PAM_ESTABLISH_CRED
from .__internals import PAM_IGNORE
from .__internals import PAM_MAXTRIES
from .__internals import PAM_MODULE_UNKNOWN
from .__internals import PAM_NEW_AUTHTOK_REQD
from .__internals import PAM_NO_MODULE_DATA
from .__internals import PAM_OPEN_ERR
from .__internals import PAM_PERM_DENIED
from .__internals import PAM_PROMPT_ECHO_OFF
from .__internals import PAM_PROMPT_ECHO_ON
from .__internals import PAM_REFRESH_CRED
from .__internals import PAM_REINITIALIZE_CRED
from .__internals import PAM_RHOST
from .__internals import PAM_RUSER
from .__internals import PAM_SERVICE
from .__internals import PAM_SERVICE_ERR
from .__internals import PAM_SESSION_ERR
from .__internals import PAM_SILENT
from .__internals import PAM_SUCCESS
from .__internals import PAM_SYMBOL_ERR
from .__internals import PAM_SYSTEM_ERR
from .__internals import PAM_TEXT_INFO
from .__internals import PAM_TRY_AGAIN
from .__internals import PAM_TTY
from .__internals import PAM_USER
from .__internals import PAM_USER_PROMPT
from .__internals import PAM_USER_UNKNOWN
from .__internals import PAM_XDISPLAY
from .__internals import PamAuthenticator

__all__ = [
    'authenticate',
    'pam',
    'PAM_ACCT_EXPIRED',
    'PAM_AUTHINFO_UNAVAIL',
    'PAM_AUTHTOK_DISABLE_AGING',
    'PAM_AUTHTOK_ERR',
    'PAM_ABORT',
    'PAM_AUTHTOK_EXPIRED',
    'PAM_AUTHTOK_LOCK_BUSY',
    'PAM_AUTHTOK_RECOVER_ERR',
    'PAM_AUTH_ERR',
    'PAM_BAD_ITEM',
    'PAM_BUF_ERR',
    'PAM_CHANGE_EXPIRED_AUTHTOK',
    'PAM_CONV',
    'PAM_CONV_ERR',
    'PAM_CRED_ERR',
    'PAM_CRED_EXPIRED',
    'PAM_CRED_INSUFFICIENT',
    'PAM_CRED_UNAVAIL',
    'PAM_DATA_SILENT',
    'PAM_DELETE_CRED',
    'PAM_DISALLOW_NULL_AUTHTOK',
    'PAM_ERROR_MSG',
    'PAM_ESTABLISH_CRED',
    'PAM_IGNORE',
    'PAM_MAXTRIES',
    'PAM_MODULE_UNKNOWN',
    'PAM_NEW_AUTHTOK_REQD',
    'PAM_NO_MODULE_DATA',
    'PAM_OPEN_ERR',
    'PAM_PERM_DENIED',
    'PAM_PROMPT_ECHO_OFF',
    'PAM_PROMPT_ECHO_ON',
    'PAM_REFRESH_CRED',
    'PAM_REINITIALIZE_CRED',
    'PAM_RHOST',
    'PAM_RUSER',
    'PAM_SERVICE',
    'PAM_SERVICE_ERR',
    'PAM_SESSION_ERR',
    'PAM_SILENT',
    'PAM_SUCCESS',
    'PAM_SYMBOL_ERR',
    'PAM_SYSTEM_ERR',
    'PAM_TEXT_INFO',
    'PAM_TRY_AGAIN',
    'PAM_TTY',
    'PAM_USER',
    'PAM_USER_PROMPT',
    'PAM_USER_UNKNOWN',
    'PAM_XDISPLAY',
    ]

__PA = None


def authenticate(username,
                 password,
                 service='login',
                 env=None,
                 call_end=True,
                 encoding='utf-8',
                 resetcreds=True,
                 print_failure_messages=False):
    global __PA

    if __PA is None:  # pragma: no branch
        __PA = PamAuthenticator()

    return __PA.authenticate(username, password, service, env, call_end, encoding, resetcreds, print_failure_messages)


# legacy implementations used pam.pam()
pam = PamAuthenticator
authenticate.__doc__ = PamAuthenticator.authenticate.__doc__
