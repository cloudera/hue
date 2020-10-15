"""
requests_gssapi.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of exceptions.

"""
from requests.exceptions import RequestException


class MutualAuthenticationError(RequestException):
    """Mutual Authentication Error"""


class SPNEGOExchangeError(RequestException):
    """SPNEGO Exchange Failed Error"""


""" Deprecated compatability shim """
KerberosExchangeError = SPNEGOExchangeError
