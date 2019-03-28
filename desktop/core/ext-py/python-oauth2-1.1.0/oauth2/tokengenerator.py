"""
Provides various implementations of algorithms to generate an Access Token or
Refresh Token.
"""

import hashlib
import os
import uuid


class TokenGenerator(object):
    """
    Base class of every token generator.
    """
    def __init__(self):
        """
        Create a new instance of a token generator.
        """
        self.expires_in = {}
        self.refresh_expires_in = 0

    def create_access_token_data(self, grant_type):
        """
        Create data needed by an access token.

        :param grant_type:
        :type grant_type: str

        :return: A ``dict`` containing he ``access_token`` and the
                 ``token_type``. If the value of ``TokenGenerator.expires_in``
                 is larger than 0, a ``refresh_token`` will be generated too.
        :rtype: dict
        """
        result = {"access_token": self.generate(), "token_type": "Bearer"}

        if self.expires_in.get(grant_type, 0) > 0:
            result["refresh_token"] = self.generate()

            result["expires_in"] = self.expires_in[grant_type]

        return result

    def generate(self):
        """
        Implemented by generators extending this base class.

        :raises NotImplementedError:
        """
        raise NotImplementedError


class URandomTokenGenerator(TokenGenerator):
    """
    Create a token using ``os.urandom()``.
    """
    def __init__(self, length=40):
        self.token_length = length
        TokenGenerator.__init__(self)

    def generate(self):
        """
        :return: A new token
        :rtype: str
        """
        random_data = os.urandom(100)

        hash_gen = hashlib.new("sha512")
        hash_gen.update(random_data)

        return hash_gen.hexdigest()[:self.token_length]


class Uuid4(TokenGenerator):
    """
    Generate a token using uuid4.
    """
    def generate(self):
        """
        :return: A new token
        :rtype: str
        """
        return str(uuid.uuid4())
