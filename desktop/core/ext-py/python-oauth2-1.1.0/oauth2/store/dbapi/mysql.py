# -*- coding: utf-8 -*-
"""
Adapters to use mysql as the storage backend.

This module uses the API defined in :mod:`oauth2.store.dbapi`.
Therefore no logic is defined here. Instead all classes define the queries
required by :mod:`oauth2.store.dbapi`.

The queries have been created for the following SQL tables in mind:

.. code-block:: sql

    CREATE TABLE IF NOT EXISTS `testdb`.`access_tokens` (
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

    CREATE TABLE IF NOT EXISTS `testdb`.`access_token_scopes` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(32) NOT NULL COMMENT 'The name of scope.',
      `access_token_id` INT NOT NULL COMMENT 'The unique identifier of the access token this scope belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`access_token_data` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `key` VARCHAR(32) NOT NULL COMMENT 'The key of an entry converted to the key in a Python dict.',
      `value` VARCHAR(32) NOT NULL COMMENT 'The value of an entry converted to the value in a Python dict.',
      `access_token_id` INT NOT NULL COMMENT 'The unique identifier of the access token a row  belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`auth_codes` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `client_id` VARCHAR(32) NOT NULL COMMENT 'The identifier of a client. Assuming it is an arbitrary text which is a maximum of 32 characters long.',
      `code` CHAR(36) NOT NULL COMMENT 'The authorisation code.',
      `expires_at` TIMESTAMP NOT NULL COMMENT 'The timestamp at which the token expires.',
      `redirect_uri` VARCHAR(128) NULL COMMENT 'The redirect URI send by the client during the request of an authorisation code.',
      `user_id` INT NULL COMMENT 'The identifier of the user this authorisation code belongs to.',
      PRIMARY KEY (`id`),
      INDEX `fetch_code` (`code` ASC))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`auth_code_data` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `key` VARCHAR(32) NOT NULL COMMENT 'The key of an entry converted to the key in a Python dict.',
      `value` VARCHAR(32) NOT NULL COMMENT 'The value of an entry converted to the value in a Python dict.',
      `auth_code_id` INT NOT NULL COMMENT 'The identifier of the authorisation code that this row belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`auth_code_scopes` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(32) NOT NULL,
      `auth_code_id` INT NOT NULL,
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`clients` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `identifier` VARCHAR(32) NOT NULL COMMENT 'The identifier of a client.',
      `secret` VARCHAR(32) NOT NULL COMMENT 'The secret of a client.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`client_grants` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `name` VARCHAR(32) NOT NULL,
      `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`client_redirect_uris` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `redirect_uri` VARCHAR(128) NOT NULL COMMENT 'A URI of a client.',
      `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;

    CREATE TABLE IF NOT EXISTS `testdb`.`client_response_types` (
      `id` INT NOT NULL AUTO_INCREMENT,
      `response_type` VARCHAR(32) NOT NULL COMMENT 'The response type that a client can use.',
      `client_id` INT NOT NULL COMMENT 'The id of the client a row belongs to.',
      PRIMARY KEY (`id`))
    ENGINE = InnoDB;
"""

from oauth2.store.dbapi import DbApiAccessTokenStore, DbApiAuthCodeStore, \
    DbApiClientStore


class MysqlAccessTokenStore(DbApiAccessTokenStore):
    delete_refresh_token_query = """
        DELETE FROM
            `access_tokens`
        WHERE
            `refresh_token` = %s"""

    fetch_by_refresh_token_query = """
        SELECT
           `id`, `client_id`, `grant_type`, `token`,
           UNIX_TIMESTAMP(`expires_at`), `refresh_token`,
           UNIX_TIMESTAMP(`refresh_expires_at`), `user_id`
        FROM
            `access_tokens`
        WHERE
            `refresh_token` = %s
        LIMIT 1"""

    fetch_scopes_by_access_token_query = """
        SELECT
            `name`
        FROM
            `access_token_scopes`
        WHERE
            `access_token_id` = %s"""

    fetch_data_by_access_token_query = """
        SELECT
           `key`, `value`
        FROM
            `access_token_data`
        WHERE
            `access_token_id` = %s"""

    fetch_existing_token_of_user_query = """
        SELECT
           `id`, `client_id`, `grant_type`, `token`,
           UNIX_TIMESTAMP(`expires_at`), `refresh_token`,
           UNIX_TIMESTAMP(`refresh_expires_at`), `user_id`
        FROM
            `access_tokens`
        WHERE
            `client_id` = %s
        AND
            `grant_type` = %s
        AND
            `user_id` = %s
        ORDER BY
            `expires_at` DESC
        LIMIT 1"""

    create_access_token_query = """
        INSERT INTO `access_tokens` (
           `client_id`, `grant_type`, `token`, `expires_at`, `refresh_token`,
           `refresh_expires_at`, `user_id`
        ) VALUES (
            %s, %s, %s, FROM_UNIXTIME(%s), %s, FROM_UNIXTIME(%s), %s
        )"""

    create_data_query = """
        INSERT INTO `access_token_data` (
           `key`,`value`, `access_token_id`
        ) VALUES (
            %s, %s, %s
        )"""

    create_scope_query = """
        INSERT INTO `access_token_scopes` (
           `name`, `access_token_id`
        ) VALUES (
            %s, %s
        )"""


class MysqlAuthCodeStore(DbApiAuthCodeStore):
    create_auth_code_query = """
        INSERT INTO `auth_codes` (
           `client_id`,`code`,`expires_at`,`redirect_uri`, `user_id`
        ) VALUES (
            %s, %s, FROM_UNIXTIME(%s), %s, %s
        )"""

    create_data_query = """
        INSERT INTO `auth_code_data` (
           `key`,`value`, `auth_code_id`
        ) VALUES (
            %s, %s, %s
        )"""

    create_scope_query = """
        INSERT INTO `auth_code_scopes` (
           `name`, `auth_code_id`
        ) VALUES (
            %s, %s
        )"""

    delete_code_query = """
        DELETE FROM `auth_codes` WHERE code = %s"""

    fetch_code_query = """
        SELECT
            `id`, `client_id`, `code`, UNIX_TIMESTAMP(`expires_at`),
            `redirect_uri`, `user_id`
        FROM
            `auth_codes`
        WHERE
            `code` = %s"""

    fetch_data_query = """
        SELECT
            `key`, `value`
        FROM
            `auth_code_data`
        WHERE
            `auth_code_id` = %s"""

    fetch_scopes_query = """
        SELECT
            `name`
        FROM
            `auth_code_scopes`
        WHERE
            `auth_code_id` = %s"""


class MysqlClientStore(DbApiClientStore):
    fetch_client_query = """
        SELECT
           `id`,`identifier`, `secret`
        FROM
            `clients`
        WHERE
            `identifier` = %s"""

    fetch_grants_query = """
        SELECT
            `name`
        FROM
            `client_grants`
        WHERE
            `client_id` = %s"""
    fetch_redirect_uris_query = """
        SELECT
            `redirect_uri`
        FROM
            `client_redirect_uris`
        WHERE
            `client_id` = %s"""

    fetch_response_types_query = """
        SELECT
            `response_type`
        FROM
            `client_response_types`
        WHERE
            `client_id` = %s"""
