import os
import redis
from wsgiref.simple_server import WSGIRequestHandler
from pymongo import MongoClient
import mysql.connector
import oauth2.store.mongodb
import oauth2.store.memory
import oauth2.store.dbapi.mysql
import oauth2.store.redisdb


class NoLoggingHandler(WSGIRequestHandler):
    """
    Turn off logging access to STDERR in the standard WSGI request handler.
    """
    def log_message(self, format, *args):
        pass


def store_factory(client_identifier, client_secret, redirect_uris):
    stores = {"access_token_store": None, "auth_code_store": None,
              "client_store": None}

    database = os.environ.get("DB")

    if database == "mongodb":
        creator_class = MongoDbStoreCreator
    elif database == "mysql":
        creator_class = MysqlStoreCreator
    elif database == "redis-server":
        creator_class = RedisStoreCreator
    else:
        creator_class = MemoryStoreCreator

    creator = creator_class(client_identifier, client_secret, redirect_uris)

    creator.initialize()

    creator.before_create()

    stores["access_token_store"] = creator.create_access_token_store()
    stores["auth_code_store"] = creator.create_auth_code_store()
    stores["client_store"] = creator.create_client_store()

    creator.after_create()

    return stores


class StoreCreator(object):
    def __init__(self, client_identifier, client_secret, redirect_uris):
        self.client_identifier = client_identifier
        self.client_secret = client_secret
        self.redirect_uris = redirect_uris

    def initialize(self):
        pass

    def after_create(self):
        pass

    def before_create(self):
        pass

    def create_access_token_store(self):
        raise NotImplementedError

    def create_auth_code_store(self):
        raise NotImplementedError

    def create_client_store(self):
        raise NotImplementedError


class MemoryStoreCreator(StoreCreator):
    def initialize(self):
        self.client_store = oauth2.store.memory.ClientStore()
        self.token_store = oauth2.store.memory.TokenStore()

    def create_access_token_store(self):
        return self.token_store

    def create_auth_code_store(self):
        return self.token_store

    def create_client_store(self):
        return self.client_store

    def after_create(self):
        self.client_store.add_client(client_id=self.client_identifier,
                                     client_secret=self.client_secret,
                                     redirect_uris=self.redirect_uris)


class MongoDbStoreCreator(StoreCreator):
    def initialize(self):
        client = MongoClient('127.0.0.1', 27017)

        self.db = client.test_database

    def create_access_token_store(self):
        return oauth2.store.mongodb.AccessTokenStore(
            collection=self.db["access_tokens"]
        )

    def create_auth_code_store(self):
        return oauth2.store.mongodb.AuthCodeStore(
            collection=self.db["auth_codes"]
        )

    def create_client_store(self):
        return oauth2.store.mongodb.ClientStore(collection=self.db["clients"])

    def after_create(self):
        self.db["clients"].insert({
            "identifier": "abc",
            "secret": "xyz",
            "redirect_uris": ["http://127.0.0.1:15487/callback"]
        })


class MysqlStoreCreator(StoreCreator):
    create_tables = """
DROP TABLE IF EXISTS `access_tokens`;
CREATE TABLE IF NOT EXISTS `access_tokens` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT 'Unique identifier',
  `client_id` VARCHAR(32) NOT NULL COMMENT 'The identifier of a client. Assuming it is an arbitrary text which is a maximum of 32 characters long.',
  `grant_type` ENUM('authorization_code', 'implicit', 'password', 'client_credentials', 'refresh_token') NOT NULL COMMENT 'The type of a grant for which a token has been issued.',
  `token` CHAR(36) NOT NULL COMMENT 'The access token.',
  `expires_at` TIMESTAMP NULL COMMENT 'The timestamp at which the token expires.',
  `refresh_token` CHAR(36) NULL COMMENT 'The refresh token.',
  `refresh_expires_at` TIMESTAMP NULL COMMENT 'The timestamp at which the refresh token expires.',
  `user_id` INT NULL COMMENT 'The identifier of the user this token belongs to.',
  PRIMARY KEY (`id`),
  INDEX `fetch_by_refresh_token` (`refresh_token` ASC),
  INDEX `fetch_existing_token_of_user` (`client_id` ASC, `grant_type` ASC, `user_id` ASC))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `access_token_scopes`;
CREATE TABLE IF NOT EXISTS `access_token_scopes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(32) NOT NULL COMMENT 'The name of scope.',
  `access_token_id` INT NOT NULL COMMENT 'The unique identifier of the access token this scope belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `access_token_data`;
CREATE TABLE IF NOT EXISTS `access_token_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(32) NOT NULL COMMENT 'The key of an entry converted to the key in a Python dict.',
  `value` VARCHAR(32) NOT NULL COMMENT 'The value of an entry converted to the value in a Python dict.',
  `access_token_id` INT NOT NULL COMMENT 'The unique identifier of the access token a row  belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `auth_codes`;
CREATE TABLE IF NOT EXISTS `auth_codes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `client_id` VARCHAR(32) NOT NULL COMMENT 'The identifier of a client. Assuming it is an arbitrary text which is a maximum of 32 characters long.',
  `code` CHAR(36) NOT NULL COMMENT 'The authorisation code.',
  `expires_at` TIMESTAMP NOT NULL COMMENT 'The timestamp at which the token expires.',
  `redirect_uri` VARCHAR(128) NULL COMMENT 'The redirect URI send by the client during the request of an authorisation code.',
  `user_id` INT NULL COMMENT 'The identifier of the user this authorisation code belongs to.',
  PRIMARY KEY (`id`),
  INDEX `fetch_code` (`code` ASC))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `auth_code_data`;
CREATE TABLE IF NOT EXISTS `auth_code_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(32) NOT NULL COMMENT 'The key of an entry converted to the key in a Python dict.',
  `value` VARCHAR(32) NOT NULL COMMENT 'The value of an entry converted to the value in a Python dict.',
  `auth_code_id` INT NOT NULL COMMENT 'The identifier of the authorisation code that this row belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `auth_code_scopes`;
CREATE TABLE IF NOT EXISTS `auth_code_scopes` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(32) NOT NULL,
  `auth_code_id` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `clients`;
CREATE TABLE IF NOT EXISTS `clients` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `identifier` VARCHAR(32) NOT NULL COMMENT 'The identifier of a client.',
  `secret` VARCHAR(32) NOT NULL COMMENT 'The secret of a client.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `client_grants`;
CREATE TABLE IF NOT EXISTS `client_grants` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(32) NOT NULL,
  `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `client_redirect_uris`;
CREATE TABLE IF NOT EXISTS `client_redirect_uris` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `redirect_uri` VARCHAR(128) NOT NULL COMMENT 'A URI of a client.',
  `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

DROP TABLE IF EXISTS `client_response_types`;
CREATE TABLE IF NOT EXISTS `client_response_types` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `response_type` VARCHAR(32) NOT NULL COMMENT 'The response type that a client can use.',
  `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
  PRIMARY KEY (`id`))
ENGINE = InnoDB;"""

    def initialize(self):
        self.connection = mysql.connector.connect(host="127.0.0.1",
                                                  user="root", passwd="",
                                                  db="testdb")

    def create_access_token_store(self):
        return oauth2.store.dbapi.mysql.\
            MysqlAccessTokenStore(connection=self.connection)

    def create_auth_code_store(self):
        return oauth2.store.dbapi.mysql.\
            MysqlAuthCodeStore(connection=self.connection)

    def create_client_store(self):
        return oauth2.store.dbapi.mysql.\
            MysqlClientStore(connection=self.connection)

    def before_create(self):
        # Execute each query on its own instead of one big query.
        # The one big query caused errors where some tables were not created
        # in every run of the tests.
        for stmt in self.create_tables.split(';'):
            cursor = self.connection.cursor()

            try:
                cursor.execute(stmt)

                self.connection.commit()
            finally:
                cursor.close()

    def after_create(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO clients (identifier, secret) VALUES (%s, %s)",
                ("abc", "xyz"))

            client_row_id = cursor.lastrowid

            self.connection.commit()
        finally:
            cursor.close()

        cursor = self.connection.cursor()

        try:
            cursor.execute(
                """INSERT INTO client_redirect_uris
                    (redirect_uri, client_id)
                VALUES (%s, %s)""",
                ("http://127.0.0.1:15487/callback", client_row_id)
            )

            self.connection.commit()
        finally:
            cursor.close()


class RedisStoreCreator(StoreCreator):
    def initialize(self):
        self.r = redis.StrictRedis(host="localhost", port=6379, db=0)

        self.client_store = oauth2.store.redisdb.ClientStore(rs=self.r)
        self.token_store = oauth2.store.redisdb.TokenStore(rs=self.r)

    def create_access_token_store(self):
        return self.token_store

    def create_auth_code_store(self):
        return self.token_store

    def create_client_store(self):
        return self.client_store

    def after_create(self):
        self.client_store.add_client(client_id=self.client_identifier,
                                     client_secret=self.client_secret,
                                     redirect_uris=self.redirect_uris)
