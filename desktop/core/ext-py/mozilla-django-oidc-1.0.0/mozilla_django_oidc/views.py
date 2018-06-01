import time
try:
    from urllib.parse import urlencode
except ImportError:
    # Python < 3
    from urllib import urlencode

import django
from django.core.exceptions import SuspiciousOperation
try:
    from django.urls import reverse
except ImportError:
    # Django < 2.0.0
    from django.core.urlresolvers import reverse
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string
from django.utils.http import is_safe_url
from django.utils.module_loading import import_string
from django.views.generic import View

from mozilla_django_oidc.utils import (
    absolutify,
    import_from_settings,
    is_authenticated
)


class OIDCAuthenticationCallbackView(View):
    """OIDC client authentication callback HTTP endpoint"""

    http_method_names = ['get']

    @property
    def failure_url(self):
        return import_from_settings('LOGIN_REDIRECT_URL_FAILURE', '/')

    @property
    def success_url(self):
        # Pull the next url from the session or settings--we don't need to
        # sanitize here because it should already have been sanitized.
        next_url = self.request.session.get('oidc_login_next', None)
        return next_url or import_from_settings('LOGIN_REDIRECT_URL', '/')

    def login_failure(self):
        return HttpResponseRedirect(self.failure_url)

    def login_success(self):
        auth.login(self.request, self.user)

        # Figure out when this id_token will expire. This is ignored unless you're
        # using the RenewIDToken middleware.
        expiration_interval = import_from_settings('OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS', 60 * 15)
        self.request.session['oidc_id_token_expiration'] = time.time() + expiration_interval

        return HttpResponseRedirect(self.success_url)

    def get(self, request):
        """Callback handler for OIDC authorization code flow"""

        nonce = request.session.get('oidc_nonce')
        if nonce:
            # Make sure that nonce is not used twice
            del request.session['oidc_nonce']

        if request.GET.get('error'):
            # Ouch! Something important failed.
            # Make sure the user doesn't get to continue to be logged in
            # otherwise the refresh middleware will force the user to
            # redirect to authorize again if the session refresh has
            # expired.
            if is_authenticated(request.user):
                auth.logout(request)
            assert not is_authenticated(request.user)
        elif 'code' in request.GET and 'state' in request.GET:
            kwargs = {
                'request': request,
                'nonce': nonce,
            }

            if 'oidc_state' not in request.session:
                return self.login_failure()

            if request.GET['state'] != request.session['oidc_state']:
                msg = 'Session `oidc_state` does not match the OIDC callback state'
                raise SuspiciousOperation(msg)

            self.user = auth.authenticate(**kwargs)

            if self.user and self.user.is_active:
                return self.login_success()
        return self.login_failure()


def get_next_url(request, redirect_field_name):
    """Retrieves next url from request

    Note: This verifies that the url is safe before returning it. If the url
    is not safe, this returns None.

    :arg HttpRequest request: the http request
    :arg str redirect_field_name: the name of the field holding the next url

    :returns: safe url or None

    """
    next_url = request.GET.get(redirect_field_name)
    if next_url:
        kwargs = {
            'url': next_url,
            'host': request.get_host()
        }
        # NOTE(willkg): Django 1.11+ allows us to require https, too.
        if django.VERSION >= (1, 11):
            kwargs['require_https'] = request.is_secure()
        is_safe = is_safe_url(**kwargs)
        if is_safe:
            return next_url
    return None


class OIDCAuthenticationRequestView(View):
    """OIDC client authentication HTTP endpoint"""

    http_method_names = ['get']

    def __init__(self, *args, **kwargs):
        super(OIDCAuthenticationRequestView, self).__init__(*args, **kwargs)

        self.OIDC_OP_AUTH_ENDPOINT = import_from_settings('OIDC_OP_AUTHORIZATION_ENDPOINT')
        self.OIDC_RP_CLIENT_ID = import_from_settings('OIDC_RP_CLIENT_ID')

    def get(self, request):
        """OIDC client authentication initialization HTTP endpoint"""
        state = get_random_string(import_from_settings('OIDC_STATE_SIZE', 32))
        redirect_field_name = import_from_settings('OIDC_REDIRECT_FIELD_NAME', 'next')
        reverse_url = import_from_settings('OIDC_AUTHENTICATION_CALLBACK_URL',
                                           'oidc_authentication_callback')

        params = {
            'response_type': 'code',
            'scope': import_from_settings('OIDC_RP_SCOPES', 'openid email'),
            'client_id': self.OIDC_RP_CLIENT_ID,
            'redirect_uri': absolutify(
                request,
                reverse(reverse_url)
            ),
            'state': state,
        }

        params.update(self.get_extra_params(request))

        if import_from_settings('OIDC_USE_NONCE', True):
            nonce = get_random_string(import_from_settings('OIDC_NONCE_SIZE', 32))
            params.update({
                'nonce': nonce
            })
            request.session['oidc_nonce'] = nonce

        request.session['oidc_state'] = state
        request.session['oidc_login_next'] = get_next_url(request, redirect_field_name)

        query = urlencode(params)
        redirect_url = '{url}?{query}'.format(url=self.OIDC_OP_AUTH_ENDPOINT, query=query)
        return HttpResponseRedirect(redirect_url)

    def get_extra_params(self, request):
        return import_from_settings('OIDC_AUTH_REQUEST_EXTRA_PARAMS', {})


class OIDCLogoutView(View):
    """Logout helper view"""

    http_method_names = ['get', 'post']

    @property
    def redirect_url(self):
        """Return the logout url defined in settings."""
        return import_from_settings('LOGOUT_REDIRECT_URL', '/')

    def post(self, request):
        """Log out the user."""
        logout_url = self.redirect_url

        if is_authenticated(request.user):
            # Check if a method exists to build the URL to log out the user
            # from the OP.
            logout_from_op = import_from_settings('OIDC_OP_LOGOUT_URL_METHOD', '')
            if logout_from_op:
                logout_url = import_string(logout_from_op)(request)

            # Log out the Django user if they were logged in.
            auth.logout(request)

        return HttpResponseRedirect(logout_url)
