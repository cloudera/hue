from urlparse import urljoin
import mock
from nose import tools

from .utils import OIDCTestCase
from django.contrib.auth.models import User
from oidc_auth.models import OpenIDProvider, get_default_provider, OpenIDUser
from oidc_auth.settings import oidc_settings


class TestOpenIDPRovider(OIDCTestCase):
    @mock.patch('requests.get')
    def test_discover_by_url(self, get_mock):
        get_mock.return_value = self.response_mock

        provider = OpenIDProvider.discover(issuer=self.issuer)

        get_mock.assert_called_with(urljoin(self.issuer, '.well-known/openid-configuration'), verify=True)
        self.assert_provider_valid(provider)

    @mock.patch('requests.get')
    def test_discover_by_credentials(self, get_mock):
        credentials = {
            'id_token': 'imagine this is a hash'
        }

        get_mock.return_value = self.response_mock

        with mock.patch.object(OpenIDProvider, '_get_issuer') as _get_issuer:
            _get_issuer.return_value = self.issuer
            provider = OpenIDProvider.discover(credentials=credentials)
            _get_issuer.assert_called_with(credentials['id_token'])

        self.assert_provider_valid(provider)

    @mock.patch('requests.get')
    def test_discover_existing_provider(self, get_mock):
        existing_provider = OpenIDProvider.objects.create(issuer='http://example.it')
        get_mock.return_value = self.response_mock

        found_provider = OpenIDProvider.discover(issuer='http://example.it')

        tools.assert_equal(found_provider.id, existing_provider.id)

    @mock.patch('oidc_auth.models.OpenIDProvider')
    def test_get_default_provider__create(self, ProviderMock):
        provider = self.create_bogus_object(self.configs)
        ProviderMock.objects.get_or_create.return_value = (provider, True)

        with oidc_settings.override(DEFAULT_PROVIDER=self.configs):
            got_provider = get_default_provider()

        self.assertIs(provider, got_provider)
        assert not ProviderMock.save.called, 'Save should not have been called!'

    @mock.patch('oidc_auth.models.OpenIDProvider')
    def test_get_default_provider__no_updates(self, ProviderMock):
        provider = self.create_bogus_object(self.configs)
        ProviderMock.objects.get_or_create.return_value = (provider, False)

        with oidc_settings.override(DEFAULT_PROVIDER=self.configs):
            got_provider = get_default_provider()

        self.assertIs(provider, got_provider)
        assert not ProviderMock.save.called, 'Save should not have been called!'

    @mock.patch('oidc_auth.models.OpenIDProvider')
    def test_get_default_provider__with_updates(self, ProviderMock):
        new_url = 'https://another-url.bogus'
        new_configs = dict(self.configs, authorization_endpoint=new_url)

        old_provider = self.create_bogus_object(self.configs)
        old_provider.save = mock.Mock()

        ProviderMock.objects.get_or_create.return_value = (old_provider, False)

        with oidc_settings.override(DEFAULT_PROVIDER=new_configs):
            got_provider = get_default_provider()

        old_provider.save.assert_called_with()
        self.assertEqual(old_provider.authorization_endpoint, new_url)

    def create_bogus_object(self, update_args=None):
        class Foo(object): pass
        foo = Foo()

        if update_args:
            foo.__dict__.update(update_args)

        return foo


class TestOpenIDUser(OIDCTestCase):
    @mock.patch('requests.get')
    def test_create_new_superuser(self, get_mock):
        get_mock.return_value = self.response_mock
        provider = OpenIDProvider.discover(issuer=self.issuer)

        with mock.patch.object(OpenIDUser, '_get_userinfo') as get_userinfo:
            get_userinfo.return_value = {
                'preferred_username': 'admin',
                'email': 'admin@admin.com',
                'given_name': 'foo',
                'family_name': 'bar',
                'is_superuser': True,
                'is_staff': True
            }

            oidc_user = OpenIDUser.get_or_create(
                id_token={'sub': 'admin'},
                access_token='foo',
                refresh_token='bar',
                provider=provider
            )

        user = User.objects.get(username='admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    @mock.patch('requests.get')
    def test_override_data_existing_user(self, get_mock):
        get_mock.return_value = self.response_mock
        provider = OpenIDProvider.discover(issuer=self.issuer)
        user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin password')

        with mock.patch.object(OpenIDUser, '_get_userinfo') as get_userinfo:
            get_userinfo.return_value = {
                'preferred_username': 'admin',
                'email': 'new_admin@admin.com',
                'given_name': 'foo',
                'family_name': 'bar'
            }

            oidc_user = OpenIDUser.get_or_create(
                id_token={'sub': 'admin'},
                access_token='foo',
                refresh_token='bar',
                provider=provider
            )

        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'new_admin@admin.com')

    @mock.patch('requests.get')
    def test_revoke_permissions_existing_user(self, get_mock):
        get_mock.return_value = self.response_mock
        provider = OpenIDProvider.discover(issuer=self.issuer)
        user = User.objects.create_superuser('admin', 'admin@admin.com', 'admin password')

        with mock.patch.object(OpenIDUser, '_get_userinfo') as get_userinfo:
            get_userinfo.return_value = {
                'preferred_username': 'admin',
                'email': 'admin@admin.com',
                'given_name': 'foo',
                'family_name': 'bar'
            }

            oidc_user = OpenIDUser.get_or_create(
                id_token={'sub': 'admin'},
                access_token='foo',
                refresh_token='bar',
                provider=provider
            )

        user = User.objects.get(username='admin')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
