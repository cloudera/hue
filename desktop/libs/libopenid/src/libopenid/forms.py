from django_openid_auth.forms import OpenIDLoginForm
from django.conf import settings

class OpenIDLoginFormExt(OpenIDLoginForm):

  def clean_openid_identifier(self):
    openid_identifier = super(OpenIDLoginFormExt, self).clean_openid_identifier()
    identity_url_prefix = getattr(settings, 'OPENID_IDENTITY_URL_PREFIX', None)

    #Case of non centralized endpoint POST request with identity prefix
    if identity_url_prefix is not None and not (openid_identifier.startswith('http') or openid_identifier.startswith('https')):
      openid_identifier = identity_url_prefix + openid_identifier

    return openid_identifier
