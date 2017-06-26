# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from collections import namedtuple
import logging
import os

from altuscli import ALTUS_ACCESS_KEY_ID_KEY_NAME, ALTUS_PRIVATE_KEY_KEY_NAME
import altuscli.compat
from altuscli.compat import json
from altuscli.configloader import raw_config_parse
from altuscli.exceptions import ConfigNotFound
from altuscli.exceptions import NoCredentialsError
from altuscli.exceptions import PartialCredentialsError
from altuscli.exceptions import UnknownCredentialError

LOG = logging.getLogger('altuscli.credentials')
ReadOnlyCredentials = namedtuple('ReadOnlyCredentials',
                                 ['access_key_id', 'private_key', 'method'])
ACCESS_KEY_ID = 'access_key_id'
PRIVATE_KEY = 'private_key'


def create_credential_resolver(context):
    """Create a default credential resolver.

    This creates a pre-configured credential resolver
    that includes the default lookup chain for
    credentials.
    """
    profile_name = context.effective_profile
    auth_file = context.get_config_variable('auth_config')
    shared_credential_file = context.get_config_variable('credentials_file')

    env_provider = EnvProvider()
    providers = [
        env_provider,
        AuthConfigFile(auth_file),
        SharedCredentialProvider(
            creds_filename=shared_credential_file,
            profile_name=profile_name
        ),
    ]

    explicit_profile = context.get_config_variable('profile',
                                                   methods=('instance',))
    if explicit_profile is not None:
        # An explicitly provided profile will negate an EnvProvider.
        # We will defer to providers that understand the "profile"
        # concept to retrieve credentials.
        # The one edge case is if all three values are provided via
        # env vars:
        # export ALTUS_ACCESS_KEY_ID=foo
        # export ALTUS_PRIVATE_KEY=bar
        # export ALTUS_PROFILE=baz
        # Then, just like our client() calls, the explicit credentials
        # will take precedence.
        #
        # This precedence is enforced by leaving the EnvProvider in the chain.
        # This means that the only way a "profile" would win is if the
        # EnvProvider does not return credentials, which is what we want
        # in this scenario.
        providers.remove(env_provider)
        LOG.debug('Skipping environment variable credential check because '
                  'profile name was explicitly set.')

    resolver = CredentialResolver(providers=providers)
    return resolver


def get_credentials(context):
    resolver = create_credential_resolver(context)
    return resolver.load_credentials()


class Credentials(object):
    """
    Holds the credentials needed to authenticate requests.
    """

    def __init__(self, access_key_id, private_key, method):
        self.access_key_id = access_key_id
        self.private_key = private_key
        self.method = method
        self._normalize()

    def _normalize(self):
        self.access_key_id = altuscli.compat.ensure_unicode(self.access_key_id)
        self.private_key = altuscli.compat.ensure_unicode(self.private_key)

    def get_frozen_credentials(self):
        return ReadOnlyCredentials(self.access_key_id,
                                   self.private_key,
                                   self.method)


class CredentialProvider(object):

    # Implementations must provide a method.
    METHOD = None

    def load(self):
        return True

    def _extract_creds_from_mapping(self, mapping, *key_names):
        found = []
        for key_name in key_names:
            try:
                found.append(mapping[key_name])
            except KeyError:
                raise PartialCredentialsError(provider=self.METHOD,
                                              cred_var=key_name)
        return found


class EnvProvider(CredentialProvider):
    METHOD = 'env'
    ACCESS_KEY_ID_ENV_VAR = 'ALTUS_ACCESS_KEY_ID'
    PRIVATE_KEY_ENV_VAR = 'ALTUS_PRIVATE_KEY'

    def __init__(self, environ=None, mapping=None):
        super(EnvProvider, self).__init__()
        if environ is None:
            environ = os.environ
        self.environ = environ
        self._mapping = self._build_mapping(mapping)

    def _build_mapping(self, mapping):
        # Mapping of variable name to env var name.
        var_mapping = {}
        if mapping is None:
            # Use the class var default.
            var_mapping[ACCESS_KEY_ID] = self.ACCESS_KEY_ID_ENV_VAR
            var_mapping[PRIVATE_KEY] = self.PRIVATE_KEY_ENV_VAR
        else:
            var_mapping[ACCESS_KEY_ID] = mapping.get(
                ACCESS_KEY_ID, self.ACCESS_KEY_ID_ENV_VAR)
            var_mapping[PRIVATE_KEY] = mapping.get(
                PRIVATE_KEY, self.PRIVATE_KEY_ENV_VAR)
        return var_mapping

    def load(self):
        """
        Search for credentials in explicit environment variables.
        """
        if self._mapping[ACCESS_KEY_ID] in self.environ:
            access_key_id, private_key = self._extract_creds_from_mapping(
                self.environ, self._mapping[ACCESS_KEY_ID],
                self._mapping[PRIVATE_KEY])
            LOG.info('Found credentials in environment variables.')
            if not os.path.isfile(private_key):
                LOG.debug("Private key at %s does not exist!" % private_key)
                raise NoCredentialsError()
            pem = open(private_key).read()
            return Credentials(access_key_id, pem, method=self.METHOD)
        else:
            return None


class CredentialResolver(object):

    def __init__(self, providers):
        self.providers = providers

    def insert_before(self, name, credential_provider):
        """
        Inserts a new instance of ``CredentialProvider`` into the chain that will
        be tried before an existing one.
        """
        try:
            offset = [p.METHOD for p in self.providers].index(name)
        except ValueError:
            raise UnknownCredentialError(name=name)
        self.providers.insert(offset, credential_provider)

    def insert_after(self, name, credential_provider):
        """
        Inserts a new type of ``Credentials`` instance into the chain that will
        be tried after an existing one.
        """
        offset = self._get_provider_offset(name)
        self.providers.insert(offset + 1, credential_provider)

    def remove(self, name):
        """
        Removes a given ``Credentials`` instance from the chain.
        """
        available_methods = [p.METHOD for p in self.providers]
        if name not in available_methods:
            # It's not present. Fail silently.
            return

        offset = available_methods.index(name)
        self.providers.pop(offset)

    def get_provider(self, name):
        """
        Return a credential provider by name.
        """
        return self.providers[self._get_provider_offset(name)]

    def _get_provider_offset(self, name):
        try:
            return [p.METHOD for p in self.providers].index(name)
        except ValueError:
            raise UnknownCredentialError(name=name)

    def load_credentials(self):
        """
        Goes through the credentials chain, returning the first ``Credentials``
        that could be loaded.
        """
        # First provider to return a non-None response wins.
        for provider in self.providers:
            LOG.debug("Looking for credentials via: %s", provider.METHOD)
            creds = provider.load()
            if creds is not None:
                return creds

        raise NoCredentialsError()


class AuthConfigFile(CredentialProvider):
    METHOD = 'auth_config_file'

    def __init__(self, conf):
        super(AuthConfigFile, self).__init__()
        self._conf = conf

    def load(self):
        """
        load the credential from the json configuration file.
        """
        if self._conf is None:
            return None

        if not os.path.isfile(self._conf):
            LOG.debug("Conf file at %s does not exist!" % self._conf)
            raise NoCredentialsError()
        try:
            conf = json.loads(open(self._conf).read())
        except Exception:
            LOG.debug("Could not read conf: %s", exc_info=True)
            return None

        if ACCESS_KEY_ID in conf:
            LOG.debug('Found credentials for key: %s in configuration file.',
                      conf[ACCESS_KEY_ID])
            access_key_id, private_key = self._extract_creds_from_mapping(
                conf,
                ACCESS_KEY_ID,
                PRIVATE_KEY)
            return Credentials(access_key_id, private_key, self.METHOD)
        raise NoCredentialsError()


class SharedCredentialProvider(CredentialProvider):
    METHOD = 'shared-credentials-file'

    def __init__(self, creds_filename, profile_name):
        self._creds_filename = creds_filename
        self._profile_name = profile_name

    def load(self):
        try:
            available_creds = raw_config_parse(self._creds_filename)
        except ConfigNotFound:
            LOG.debug("Credentials file at %s does not exist!" % self._creds_filename)
            return None
        if self._profile_name in available_creds:
            config = available_creds[self._profile_name]
            access_key_id, private_key = self._extract_creds_from_mapping(
                config, ALTUS_ACCESS_KEY_ID_KEY_NAME, ALTUS_PRIVATE_KEY_KEY_NAME)
            # We store the private key in the credentials file as a one-line
            # value in which the newlines in the PEM file are replaced with
            # '\n'. We need to replace them back as the RawConfigParser we use
            # does not do it for us. Note that if the value in the configuration
            # IS a PEM formatted value this is a no-op.
            private_key = private_key.replace('\\n', '\n')
            LOG.info("Found credentials in shared credentials file: %s",
                     self._creds_filename)
            return Credentials(access_key_id, private_key, method=self.METHOD)
