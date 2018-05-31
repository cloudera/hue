from contextlib import contextmanager
from django.conf import settings


DEFAULTS = {
    'DISABLE_OIDC': False,
    'DEFAULT_PROVIDER': {},
    'SCOPES': ('openid', 'given_name', 'family_name', 'preferred_username', 'email'),
    'CLIENT_ID': None,
    'CLIENT_SECRET': None,
    'NONCE_LENGTH': 8,
    'VERIFY_SSL': True
}

USER_SETTINGS = getattr(settings, 'OIDC_AUTH', {})


class OIDCSettings(object):
    """Shamelessly copied from django-oauth-toolkit"""

    def __init__(self, user_settings, defaults):
        self.user_settings = user_settings
        self.defaults = defaults
        self.patched_settings = {}

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid oidc_auth setting: %s' % attr)

        if attr in self.patched_settings:
            val = self.patched_settings[attr]
        elif attr in self.user_settings:
            val = self.user_settings[attr]
        else:
            val = self.defaults[attr]

        return val

    @contextmanager
    def override(self, **kwargs):
        self.patched_settings = kwargs
        yield
        self.patched_settings = {}


oidc_settings = OIDCSettings(USER_SETTINGS, DEFAULTS)
