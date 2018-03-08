# Copyright (C) Jean-Paul Calderone
# See LICENSE for details.

"""
Unit tests for `OpenSSL.tsafe`.
"""

from OpenSSL.SSL import TLSv1_METHOD, Context
from OpenSSL.tsafe import Connection


class TestConnection(object):
    """
    Tests for `OpenSSL.tsafe.Connection`.
    """
    def test_instantiation(self):
        """
        `OpenSSL.tsafe.Connection` can be instantiated.
        """
        # The following line should not throw an error.  This isn't an ideal
        # test.  It would be great to refactor the other Connection tests so
        # they could automatically be applied to this class too.
        Connection(Context(TLSv1_METHOD), None)
