from urlparse import urljoin
import mock
from nose import tools
from django.test import TransactionTestCase

from oidc_auth.models import OpenIDProvider
from oidc_auth.settings import DEFAULTS


class OIDCTestCase(TransactionTestCase):
    def setUp(self):
        self.issuer = 'http://example.it'
        self.configs = {
            'issuer': self.issuer,
            'authorization_endpoint': urljoin(self.issuer, 'authorize'),
            'token_endpoint': urljoin(self.issuer, 'token'),
            'userinfo_endpoint': urljoin(self.issuer, 'userinfo_endpoint'),
            'jwks_uri': urljoin(self.issuer, 'jwks_uri'),
            'client_id': 'this is a client id',
            'client_secret': 'this is a client secret'
        }

        # to be used with requests lib
        self.response_mock = mock.MagicMock()
        self.response_mock.status_code = 200
        self.response_mock.json.return_value = self.configs
    
    def tearDown(self):
        OpenIDProvider.objects.all().delete()
    
    def assert_provider_valid(self, provider, credentials=None):
        if not credentials:
            credentials = self.configs

        tools.assert_is_instance(provider, OpenIDProvider)
        tools.assert_equal(provider.issuer, credentials['issuer'])
        tools.assert_equal(provider.authorization_endpoint, credentials['authorization_endpoint'])
        tools.assert_equal(provider.token_endpoint, credentials['token_endpoint'])
        tools.assert_equal(provider.userinfo_endpoint, credentials['userinfo_endpoint'])
        tools.assert_equal(provider.jwks_uri, credentials['jwks_uri'])
