"""
Store adapters to read/write data to from/to mongodb using pymongo.
"""

from oauth2.store import AccessTokenStore, AuthCodeStore, ClientStore
from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, AuthCodeNotFound, \
    ClientNotFoundError
import pymongo


class MongodbStore(object):
    """
    Base class extended by all concrete store adapters.
    """

    def __init__(self, collection):
        self.collection = collection


class AccessTokenStore(AccessTokenStore, MongodbStore):
    """
    Create a new instance like this::

        from pymongo import MongoClient

        client = MongoClient('localhost', 27017)

        db = client.test_database

        access_token_store = AccessTokenStore(collection=db["access_tokens"])

    """

    def fetch_by_refresh_token(self, refresh_token):
        data = self.collection.find_one({"refresh_token": refresh_token})

        if data is None:
            raise AccessTokenNotFound

        return AccessToken(client_id=data.get("client_id"),
                           grant_type=data.get("grant_type"),
                           token=data.get("token"),
                           data=data.get("data"),
                           expires_at=data.get("expires_at"),
                           refresh_token=data.get("refresh_token"),
                           refresh_expires_at=data.get("refresh_expires_at"),
                           scopes=data.get("scopes"))

    def delete_refresh_token(self, refresh_token):
        """
        Deletes (invalidates) an old refresh token after use
        :param refresh_token: The refresh token.
        """
        self.collection.remove({"refresh_token": refresh_token})

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        data = self.collection.find_one({"client_id": client_id,
                                         "grant_type": grant_type,
                                         "user_id": user_id},
                                        sort=[("expires_at",
                                               pymongo.DESCENDING)])

        if data is None:
            raise AccessTokenNotFound

        return AccessToken(client_id=data.get("client_id"),
                           grant_type=data.get("grant_type"),
                           token=data.get("token"),
                           data=data.get("data"),
                           expires_at=data.get("expires_at"),
                           refresh_token=data.get("refresh_token"),
                           refresh_expires_at=data.get("refresh_expires_at"),
                           scopes=data.get("scopes"),
                           user_id=data.get("user_id"))

    def save_token(self, access_token):
        self.collection.insert({
            "client_id": access_token.client_id,
            "grant_type": access_token.grant_type,
            "token": access_token.token,
            "data": access_token.data,
            "expires_at": access_token.expires_at,
            "refresh_token": access_token.refresh_token,
            "refresh_expires_at": access_token.refresh_expires_at,
            "scopes": access_token.scopes,
            "user_id": access_token.user_id})

        return True


class AuthCodeStore(AuthCodeStore, MongodbStore):
    """
    Create a new instance like this::

        from pymongo import MongoClient

        client = MongoClient('localhost', 27017)

        db = client.test_database

        access_token_store = AuthCodeStore(collection=db["auth_codes"])

    """

    def fetch_by_code(self, code):
        code_data = self.collection.find_one({"code": code})

        if code_data is None:
            raise AuthCodeNotFound

        return AuthorizationCode(client_id=code_data.get("client_id"),
                                 code=code_data.get("code"),
                                 expires_at=code_data.get("expires_at"),
                                 redirect_uri=code_data.get("redirect_uri"),
                                 scopes=code_data.get("scopes"),
                                 data=code_data.get("data"),
                                 user_id=code_data.get("user_id"))

    def save_code(self, authorization_code):
        self.collection.insert({
            "client_id": authorization_code.client_id,
            "code": authorization_code.code,
            "expires_at": authorization_code.expires_at,
            "redirect_uri": authorization_code.redirect_uri,
            "scopes": authorization_code.scopes,
            "data": authorization_code.data,
            "user_id": authorization_code.user_id})

        return True

    def delete_code(self, code):
        """
        Deletes an authorization code after use
        :param code: The authorization code.
        """
        self.collection.remove({"code": code})


class ClientStore(ClientStore, MongodbStore):
    """
    Create a new instance like this::

        from pymongo import MongoClient

        client = MongoClient('localhost', 27017)

        db = client.test_database

        access_token_store = ClientStore(collection=db["clients"])

    """

    def fetch_by_client_id(self, client_id):
        client_data = self.collection.find_one({"identifier": client_id})

        if client_data is None:
            raise ClientNotFoundError

        return Client(
            identifier=client_data.get("identifier"),
            secret=client_data.get("secret"),
            redirect_uris=client_data.get("redirect_uris"),
            authorized_grants=client_data.get("authorized_grants"),
            authorized_response_types=client_data.get(
                "authorized_response_types"
            ))
