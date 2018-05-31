import json
from base64 import b64decode as python_b64decode
import logging
from django.contrib import auth

from .settings import oidc_settings


def scopes():
    _scopes = set(oidc_settings.SCOPES)
    _scopes.update({'openid', 'email', 'preferred_username'})

    return ' '.join(_scopes)


def b64decode(token):
    token += ('=' * (len(token) % 4))
    decoded = python_b64decode(token)
    return json.loads(decoded)


def get_user_model():
    if hasattr(auth, 'get_user_model'):
        return auth.get_user_model()
    else:
        return auth.models.User


log = logging.getLogger('oidc_auth')
log.addHandler(logging.NullHandler())
