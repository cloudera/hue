from urlparse import urlparse, parse_qs
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.importlib import import_module
from django.test import Client
from nose import tools
import mock

from .utils import OIDCTestCase
from oidc_auth.models import OpenIDProvider, Nonce
from oidc_auth.settings import oidc_settings

UserModel = get_user_model()


class TestAuthorizationPhase(OIDCTestCase):
    def setUp(self):
        super(TestAuthorizationPhase, self).setUp()
        self.client = Client()

    def tearDown(self):
        OpenIDProvider.objects.all().delete()

    def test_get_login(self):
        with oidc_settings.override(DEFAULT_PROVIDER={}):
            response = self.client.get('/oidc/login/')

        tools.assert_equal(response.status_code, 200)
        tools.assert_true(any(t.name == 'oidc/login.html' for t in response.templates))

    @mock.patch('requests.get')
    def test_post_login(self, get_mock):
        get_mock.return_value = self.response_mock

        with oidc_settings.override(DEFAULT_PROVIDER=self.configs):
            response = self.client.post('/oidc/login/', data={
                'issuer': 'http://example.it'
            })

        tools.assert_equal(response.status_code, 302)

        redirect_url = urlparse(response['Location'])
        tools.assert_equal('http://example.it', '%s://%s' % (redirect_url.scheme, redirect_url.hostname))

        params = parse_qs(redirect_url.query)
        tools.assert_equal(set(params.keys()),
            {'response_type', 'scope', 'client_id', 'state'})

    def test_login_complete_without_oidc_session(self):
        response = self.client.get('/oidc/complete')  # without oidc_state in session *on purpose*
        tools.assert_equal(response.status_code, 301)

    @mock.patch('requests.get')
    def test_login_default_provider(self, get_mock):
        configs = dict(self.configs,
                authorization_endpoint='http://default.example.it/authorize')
        get_mock.return_value.status_code = 200
        get_mock.return_value.json.return_value = configs

        with oidc_settings.override(DEFAULT_PROVIDER=configs):
            response = self.client.get('/oidc/login/')

        tools.assert_equal(response.status_code, 302)
        redirect_url = urlparse(response['Location'])
        tools.assert_equal('default.example.it', redirect_url.hostname)


class TestTokenExchangePhase(OIDCTestCase):
    def setUp(self):
        super(TestTokenExchangePhase, self).setUp()
        self.client = Client()

        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()  
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_invalid_request(self):
        session = self.client.session
        session['oidc_state'] = 'foobar'
        session.save()

        tools.assert_equal(400, self.client.post('/oidc/complete/').status_code)
        tools.assert_equal(400, self.client.post('/oidc/complete/', data={
            'code': '12345'}).status_code)
        tools.assert_equal(400, self.client.post('/oidc/complete/', data={
            'state': '12345'}).status_code)

    @mock.patch('requests.post')
    def test_post_token_endpoint(self, post_mock):
        response = mock.MagicMock()
        response.status_code = 200
        response.json.return_value = {
            'access_token': '12345',
            'refresh_token': '12345',
            'expires_in': 3600,
            'token_type': 'Bearer',
            'id_token': '12345'
        }
        post_mock.return_value = response

        state = 'abcde'
        Nonce.objects.create(issuer_url='http://example.it', state=state, redirect_url='http://back.to.me')
        provider = OpenIDProvider.objects.create(issuer='http://example.it',
                client_id='12345',
                client_secret='abcde',
                token_endpoint='http://example.it/token',
                authorization_endpoint='http://a.b/auth',
                userinfo_endpoint='http://a.b/userinfo',
                jwks_uri='http://a.b/jwks')

        user = UserModel.objects.create(username='foobar')

        session = self.client.session
        session['oidc_state'] = state
        session.save()

        with mock.patch.object(OpenIDProvider, 'verify_id_token') as mock_verify_id_token:
            mock_verify_id_token.return_value = { 'sub': 'foobar' }

            response = self.client.get('/oidc/complete/', data={
                'state': state,
                'code': '12345'
            })

        post_mock.assert_called_with(provider.token_endpoint, params={
            'grant_type': 'authorization_code',
            'code': '12345',
            'redirect_uri': 'http://testserver/oidc/complete/'
        }, auth=provider.client_credentials, verify=True)

    @mock.patch('requests.post')
    def test_post_token_endpoint_with_invalid_ssl(self, post_mock):
        with oidc_settings.override(VERIFY_SSL=False):
            response = mock.MagicMock()
            response.status_code = 200
            response.json.return_value = {
                'access_token': '12345',
                'refresh_token': '12345',
                'expires_in': 3600,
                'token_type': 'Bearer',
                'id_token': (
                    'eyJhbGciOiJSUzI1NiIsImtpZCI6IjFlOWdkazcifQ.ewogImlzc'
                    'yI6ICJodHRwOi8vc2VydmVyLmV4YW1wbGUuY29tIiwKICJzdWIiOiAiMjQ4Mjg5'
                    'NzYxMDAxIiwKICJhdWQiOiAiczZCaGRSa3F0MyIsCiAibm9uY2UiOiAibi0wUzZ'
                    'fV3pBMk1qIiwKICJleHAiOiAxMzExMjgxOTcwLAogImlhdCI6IDEzMTEyODA5Nz'
                    'AKfQ.ggW8hZ1EuVLuxNuuIJKX_V8a_OMXzR0EHR9R6jgdqrOOF4daGU96Sr_P6q'
                    'Jp6IcmD3HP99Obi1PRs-cwh3LO-p146waJ8IhehcwL7F09JdijmBqkvPeB2T9CJ'
                    'NqeGpe-gccMg4vfKjkM8FcGvnzZUN4_KSP0aAp1tOJ1zZwgjxqGByKHiOtX7Tpd'
                    'QyHE5lcMiKPXfEIQILVq0pc_E2DzL7emopWoaoZTF_m0_N0YzFC6g6EJbOEoRoS'
                    'K5hoDalrcvRYLSrQAZZKflyuVCyixEoV9GfNQC3_osjzw2PAithfubEEBLuVVk4'
                    'XUVrWOLrLl0nx7RkKU8NXNHq-rvKMzqg'),
            }
            post_mock.return_value = response

            state = 'abcde'
            Nonce.objects.create(issuer_url='http://example.it', state=state, redirect_url='http://back.to.me')
            provider = OpenIDProvider.objects.create(issuer='http://example.it',
                    client_id='12345',
                    client_secret='abcde',
                    token_endpoint='http://example.it/token',
                    authorization_endpoint='http://a.b/',
                    userinfo_endpoint='http://a.b/',
                    jwks_uri='http://a.b/')

            session = self.client.session
            session['oidc_state'] = state
            session.save()

            user = UserModel.objects.create(username='foobar')

            with mock.patch.object(OpenIDProvider, 'verify_id_token') as mock_verify_id_token:
                mock_verify_id_token.return_value = { 'sub': 'foobar' }

                response = self.client.get('/oidc/complete/', data={
                    'state': state,
                    'code': '12345'
                })

            post_mock.assert_called_with(provider.token_endpoint, params={
                'grant_type': 'authorization_code',
                'code': '12345',
                'redirect_uri': 'http://testserver/oidc/complete/'
            }, auth=provider.client_credentials, verify=False)
