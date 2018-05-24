from django.conf import settings
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, 'OIDC_AUTH', None)

DEFAULTS = {
    'OIDC_ENDPOINT': None,
    'OIDC_ENDPOINTS': {},
    'OIDC_AUDIENCES': None,

    # Number of seconds in the past valid tokens can be issued
    'OIDC_LEEWAY': 600,

    # Time before JWKS will be refreshed
    'OIDC_JWKS_EXPIRATION_TIME': 24 * 60 * 60,

    # Function to resolve user from request and token or userinfo
    'OIDC_RESOLVE_USER_FUNCTION': 'oidc_auth.authentication.get_user_by_id',

    # Time before bearer token validity is verified again
    'OIDC_BEARER_TOKEN_EXPIRATION_TIME': 600,

    'JWT_AUTH_HEADER_PREFIX': 'JWT',
    'BEARER_AUTH_HEADER_PREFIX': 'Bearer',
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'OIDC_RESOLVE_USER_FUNCTION',
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
