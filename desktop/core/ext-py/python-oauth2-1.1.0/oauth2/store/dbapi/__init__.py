# -*- coding: utf-8 -*-
"""
`DBApi 2.0 <http://legacy.python.org/dev/peps/pep-0249/>`_ (PEP249) compatible
implementation of data stores.
"""

from oauth2.datatype import AccessToken, AuthorizationCode, Client
from oauth2.error import AccessTokenNotFound, ClientNotFoundError, \
    AuthCodeNotFound
from oauth2.store import AccessTokenStore, AuthCodeStore, ClientStore


class DatabaseStore(object):
    """
    Base class providing functionality used by a variety of store classes.
    """
    def __init__(self, connection):
        """
        Initialize a new store class.

        :param connection: An instance of a `connection class <http://legacy.python.org/dev/peps/pep-0249/#connection-objects>`_.
        """
        self.connection = connection

    def execute(self, query, *params):
        """
        Executes a query and returns the identifier of the modified row.

        :param query: The query to be executed as a `str`.
        :param params: A `tuple` of parameters that will be replaced for
                       placeholders in the query.
        :return: A `long` identifying the last altered row.
        """
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)

            self.connection.commit()

            return cursor.lastrowid
        finally:
            cursor.close()

    def fetchone(self, query, *args):
        """
        Returns the first result of the given query.

        :param query: The query to be executed as a `str`.
        :param params: A `tuple` of parameters that will be replaced for
                       placeholders in the query.
        :return: The retrieved row with each field being one element in a
                 `tuple`.
        """
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, args)

            return cursor.fetchone()
        finally:
            cursor.close()

    def fetchall(self, query, *args):
        """
        Returns all results of the given query.

        :param query: The query to be executed as a `str`.
        :param params: A `tuple` of parameters that will be replaced for
                       placeholders in the query.
        :return: A `list` of `tuple`s with each field being one element in the
                 `tuple`.
        """
        cursor = self.connection.cursor()

        try:
            cursor.execute(query, args)

            return cursor.fetchall()
        finally:
            cursor.close()


class DbApiAccessTokenStore(DatabaseStore, AccessTokenStore):
    """
    Base class of a DBApi 2.0 compatible
    :class:`oauth2.store.AccessTokenStore`.

    A concrete implementation extends this class and defines all or a subset
    of the \*_query class attributes.
    """
    #: Insert an access token.
    create_access_token_query = None
    #: Insert one entry of additional data associated with an access token.
    create_data_query = None
    #: Insert one scope associated with an access token.
    create_scope_query = None
    #: Delete an access token by its refresh token.
    delete_refresh_token_query = None
    #: Retrieve an access token by its refresh token.
    fetch_by_refresh_token_query = None
    #: Retrieve all scopes associated with an access token.
    fetch_scopes_by_access_token_query = None
    #: Retrieve all data associated with an access token.
    fetch_data_by_access_token_query = None
    #: Retrieve an access token issued to a client and user for a specific
    #: grant.
    fetch_existing_token_of_user_query = None

    def delete_refresh_token(self, refresh_token):
        """
        Deletes an access token by its refresh token.

        :param refresh_token: The refresh token of an access token as a `str`.
        """
        self.execute(self.delete_refresh_token_query, refresh_token)

    def fetch_by_refresh_token(self, refresh_token):
        """
        Retrieves an access token by its refresh token.

        :param refresh_token: The refresh token of an access token as a `str`.

        :return: An instance of :class:`oauth2.datatype.AccessToken`.

        :raises: :class:`oauth2.error.AccessTokenNotFound` if not access token
                 could be retrieved.
        """
        row = self.fetchone(self.fetch_by_refresh_token_query, refresh_token)

        if row is None:
            raise AccessTokenNotFound

        scopes = self._fetch_scopes(access_token_id=row[0])

        data = self._fetch_data(access_token_id=row[0])

        return self._row_to_token(data=data, scopes=scopes, row=row)

    def fetch_existing_token_of_user(self, client_id, grant_type, user_id):
        """
        Retrieve an access token issued to a client and user for a specific
        grant.

        :param client_id: The identifier of a client as a `str`.
        :param grant_type: The type of grant.
        :param user_id: The identifier of the user the access token has been
                        issued to.

        :return: An instance of :class:`oauth2.datatype.AccessToken`.

        :raises: :class:`oauth2.error.AccessTokenNotFound` if not access token
                 could be retrieved.
        """
        token_data = self.fetchone(self.fetch_existing_token_of_user_query,
                                   client_id, grant_type, user_id)

        if token_data is None:
            raise AccessTokenNotFound

        scopes = self._fetch_scopes(access_token_id=token_data[0])

        data = self._fetch_data(access_token_id=token_data[0])

        return self._row_to_token(data=data, scopes=scopes, row=token_data)

    def save_token(self, access_token):
        """
        Creates a new entry for an access token in the database.

        :param access_token: An instance of
                             :class:`oauth2.datatype.AccessToken`.

         :return: `True`.
        """
        access_token_id = self.execute(self.create_access_token_query,
                                       access_token.client_id,
                                       access_token.grant_type,
                                       access_token.token,
                                       access_token.expires_at,
                                       access_token.refresh_token,
                                       access_token.refresh_expires_at,
                                       access_token.user_id)

        for key, value in list(access_token.data.items()):
            self.execute(self.create_data_query, key, value,
                         access_token_id)

        for scope in access_token.scopes:
            self.execute(self.create_scope_query, scope, access_token_id)

        return True

    def _fetch_data(self, access_token_id):
        result = self.fetchall(self.fetch_data_by_access_token_query,
                               access_token_id)
        data = {}
        if result is not None:
            for dataset in result:
                data[dataset[0]] = dataset[1]
        return data

    def _fetch_scopes(self, access_token_id):
        result = self.fetchall(self.fetch_scopes_by_access_token_query,
                               access_token_id)
        scopes = []
        if result is not None:
            for scope_data in result:
                scopes.append(scope_data[0])

        return scopes

    def _row_to_token(self, data, scopes, row):
        return AccessToken(client_id=row[1], grant_type=row[2], token=row[3],
                           data=data, expires_at=row[4], refresh_token=row[5],
                           refresh_expires_at=row[6], scopes=scopes,
                           user_id=row[7])


class DbApiAuthCodeStore(DatabaseStore, AuthCodeStore):
    """
    Base class of a DBApi 2.0 compatible :class:`oauth2.store.AuthCodeStore`.

    A concrete implementation extends this class and defines all or a subset
    of the \*_query class attributes.
    """
    #: Insert an auth code.
    create_auth_code_query = None
    #: Insert one entry of additional data associated with an auth code.
    create_data_query = None
    #: Insert one scope associated with an auth code.
    create_scope_query = None
    #: Delete an auth code.
    delete_code_query = None
    #: Retrieve an auth code by its code.
    fetch_code_query = None
    #: Retrieve all data associated with an auth code.
    fetch_data_query = None
    #: Retrieve all scopes associated with an auth code.
    fetch_scopes_query = None

    def delete_code(self, code):
        """
        Delete an auth code identified by its code.

        :param code: The code of an auth code.
        """
        self.execute(self.delete_code_query, code)

    def fetch_by_code(self, code):
        """
        Retrieves an auth code by its code.

        :param code: The code of an auth code.

        :return: An instance of :class:`oauth2.datatype.AuthorizationCode`.

        :raises: :class:`oauth2.error.AuthCodeNotFound` if no auth code could
                 be retrieved.
        """
        auth_code_data = self.fetchone(self.fetch_code_query, code)

        if auth_code_data is None:
            raise AuthCodeNotFound

        data = dict()
        data_result = self.fetchall(self.fetch_data_query, auth_code_data[0])
        if data_result is not None:
            for dataset in data_result:
                data[dataset[0]] = dataset[1]

        scopes = []
        scope_result = self.fetchall(self.fetch_scopes_query,
                                     auth_code_data[0])
        if scope_result is not None:
            for scope_set in scope_result:
                scopes.append(scope_set[0])

        return AuthorizationCode(client_id=auth_code_data[1],
                                 code=auth_code_data[2],
                                 expires_at=auth_code_data[3],
                                 redirect_uri=auth_code_data[4],
                                 scopes=scopes, data=data,
                                 user_id=auth_code_data[5])

    def save_code(self, authorization_code):
        """
        Creates a new entry of an auth code in the database.

        :param authorization_code: An instance of
                                   :class:`oauth2.datatype.AuthorizationCode`.

        :return: `True` if everything went fine.
        """
        auth_code_id = self.execute(self.create_auth_code_query,
                                    authorization_code.client_id,
                                    authorization_code.code,
                                    authorization_code.expires_at,
                                    authorization_code.redirect_uri,
                                    authorization_code.user_id)

        for key, value in list(authorization_code.data.items()):
            self.execute(self.create_data_query, key, value, auth_code_id)

        for scope in authorization_code.scopes:
            self.execute(self.create_scope_query, scope, auth_code_id)

        return True


class DbApiClientStore(DatabaseStore, ClientStore):
    """
    Base class of a DBApi 2.0 compatible :class:`oauth2.store.ClientStore`.

    A concrete implementation extends this class and defines all or a subset
    of the \*_query class attributes.
    """
    #: Retrieve a client by its identifier.
    fetch_client_query = None
    #: Retrieve all grants that a client is allowed to use.
    fetch_grants_query = None
    #: Retrieve all redirect URIs of a client.
    fetch_redirect_uris_query = None
    #: Retrieve all response types that a client supports.
    fetch_response_types_query = None

    def fetch_by_client_id(self, client_id):
        """
        Retrieves a client by its identifier.

        :param client_id: The identifier of a client.

        :return: An instance of :class:`oauth2.datatype.Client`.

        :raises: :class:`oauth2.error.ClientError` if no client could be
                 retrieved.
        """
        grants = None
        redirect_uris = None
        response_types = None

        client_data = self.fetchone(self.fetch_client_query, client_id)

        if client_data is None:
            raise ClientNotFoundError

        grant_data = self.fetchall(self.fetch_grants_query, client_data[0])
        if grant_data:
            grants = []
            for grant in grant_data:
                grants.append(grant[0])

        redirect_uris_data = self.fetchall(self.fetch_redirect_uris_query,
                                           client_data[0])
        if redirect_uris_data:
            redirect_uris = []
            for redirect_uri in redirect_uris_data:
                redirect_uris.append(redirect_uri[0])

        response_types_data = self.fetchall(self.fetch_response_types_query,
                                            client_data[0])
        if response_types_data:
            response_types = []
            for response_type in response_types_data:
                response_types.append(response_type[0])

        return Client(identifier=client_data[1], secret=client_data[2],
                      authorized_grants=grants,
                      authorized_response_types=response_types,
                      redirect_uris=redirect_uris)
