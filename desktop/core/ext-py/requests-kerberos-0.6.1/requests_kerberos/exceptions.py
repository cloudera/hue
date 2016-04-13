"""
requests_kerberos.exceptions
~~~~~~~~~~~~~~~~~~~

This module contains the set of exceptions.

"""
from requests.exceptions import RequestException


class MutualAuthenticationError(RequestException):
    """Mutual Authentication Error"""
