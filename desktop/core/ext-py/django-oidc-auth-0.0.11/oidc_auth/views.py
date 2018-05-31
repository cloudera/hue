from urllib import urlencode
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login as django_login
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
import requests

from . import errors
from . import utils
from .utils import log
from .settings import oidc_settings
from .forms import OpenIDConnectForm
from .models import OpenIDProvider, get_default_provider, Nonce


def login_begin(request, template_name='oidc/login.html',
        form_class=OpenIDConnectForm,
        login_complete_view='oidc-complete',
        redirect_field_name=REDIRECT_FIELD_NAME):

    if _redirect_to_provider(request):
        return _redirect(request, login_complete_view, form_class, redirect_field_name)

    log.debug('Rendering login template at %s' % template_name)
    return render(request, template_name)


def _redirect(request, login_complete_view, form_class, redirect_field_name):
    provider = get_default_provider()

    if not provider:
        form = form_class(request.POST)

        if not form.is_valid():
            raise errors.MissingRedirectURL()

        provider = OpenIDProvider.discover(issuer=form.cleaned_data['issuer'])

    redirect_url = request.GET.get(redirect_field_name, settings.LOGIN_REDIRECT_URL)
    nonce = Nonce.generate(redirect_url, provider.issuer)
    request.session['oidc_state'] = nonce.state

    params = urlencode({
        'response_type': 'code',
        'scope': utils.scopes(),
        # 'redirect_uri': request.build_absolute_uri(reverse(login_complete_view)),
        'client_id': provider.client_id,
        'state': nonce.state
    })
    redirect_url = '%s?%s' % (provider.authorization_endpoint, params)

    log.debug('Redirecting to %s' % redirect_url)
    return redirect(redirect_url)


def login_complete(request, login_complete_view='oidc-complete',
        error_template_name='oidc/error.html'):

    if 'error' in request.GET:
        return render(request, error_template_name, {
            'error': request.GET['error']
        })

    if 'oidc_state' not in request.session:
        return redirect(settings.LOGIN_URL)

    if 'code' not in request.GET and 'state' not in request.GET:
        return HttpResponseBadRequest('Invalid request')

    if request.GET['state'] != request.session['oidc_state']:
        raise errors.ForbiddenAuthRequest()

    nonce = Nonce.objects.get(state=request.GET['state'])
    provider = nonce.provider
    log.debug('Login started from provider %s' % provider)

    params = {
        'grant_type': 'authorization_code',
        'code': request.GET['code'],
        'redirect_uri': request.build_absolute_uri(reverse(login_complete_view))
    }

    response = requests.post(provider.token_endpoint,
                             auth=provider.client_credentials,
                             params=params, verify=oidc_settings.VERIFY_SSL)

    if response.status_code != 200:
        raise errors.RequestError(provider.token_endpoint, response.status_code)

    log.debug('Token exchange done, proceeding authentication')
    credentials = response.json()
    credentials['provider'] = provider
    user = authenticate(credentials=credentials)
    django_login(request, user)

    return redirect(nonce.redirect_url)


def _redirect_to_provider(request):
    """Just a syntax sugar for login_begin. Returns True or False
    whether a request should be redirected to the provider or not.
    """

    has_default_provider = oidc_settings.DEFAULT_PROVIDER

    return (not oidc_settings.DISABLE_OIDC
            and (has_default_provider or request.method == 'POST'))
