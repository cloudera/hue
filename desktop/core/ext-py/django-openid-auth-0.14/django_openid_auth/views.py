# django-openid-auth -  OpenID integration for django.contrib.auth
#
# Copyright (C) 2007 Simon Willison
# Copyright (C) 2008-2013 Canonical Ltd.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals

import re
try:
    from urllib.parse import urlencode, urlsplit
except ImportError:
    from urllib import urlencode
    from urlparse import urlsplit

from django.conf import settings
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, authenticate, login as auth_login)
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import QueryDict
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    from django.contrib.csrf.middleware import csrf_exempt

from openid.consumer.consumer import (
    Consumer, SUCCESS, CANCEL, FAILURE)
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg, ax, pape

from django_openid_auth import teams
from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.models import UserOpenID
from django_openid_auth.signals import openid_login_complete
from django_openid_auth.store import DjangoOpenIDStore
from django_openid_auth.exceptions import (
    DjangoOpenIDException,
)


next_url_re = re.compile('^/[-\w/]+$')


def is_valid_next_url(next):
    # When we allow this:
    #   /openid/?next=/welcome/
    # For security reasons we want to restrict the next= bit to being a local
    # path, not a complete URL.
    return bool(next_url_re.match(next))


def sanitise_redirect_url(redirect_to):
    """Sanitise the redirection URL."""
    # Light security check -- make sure redirect_to isn't garbage.
    is_valid = True
    if not redirect_to or ' ' in redirect_to:
        is_valid = False
    elif '//' in redirect_to:
        # Allow the redirect URL to be external if it's a permitted domain
        allowed_domains = getattr(
            settings, "ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS", [])
        s, netloc, p, q, f = urlsplit(redirect_to)
        # allow it if netloc is blank or if the domain is allowed
        if netloc:
            # a domain was specified. Is it an allowed domain?
            if netloc.find(":") != -1:
                netloc, _ = netloc.split(":", 1)
            if netloc not in allowed_domains:
                is_valid = False

    # If the return_to URL is not valid, use the default.
    if not is_valid:
        redirect_to = settings.LOGIN_REDIRECT_URL

    return redirect_to


def make_consumer(request):
    """Create an OpenID Consumer object for the given Django request."""
    # Give the OpenID library its own space in the session object.
    session = request.session.setdefault('OPENID', {})
    store = DjangoOpenIDStore()
    return Consumer(session, store)


def render_openid_request(request, openid_request, return_to, trust_root=None):
    """Render an OpenID authentication request."""
    if trust_root is None:
        trust_root = getattr(settings, 'OPENID_TRUST_ROOT',
                             request.build_absolute_uri('/'))

    if openid_request.shouldSendRedirect():
        redirect_url = openid_request.redirectURL(
            trust_root, return_to)
        response = HttpResponseRedirect(redirect_url)
    else:
        form_html = openid_request.htmlMarkup(
            trust_root, return_to, form_tag_attrs={'id': 'openid_message'})
        response = HttpResponse(
            form_html, content_type='text/html;charset=UTF-8')
    return response


def default_render_failure(request, message, status=403,
                           template_name='openid/failure.html',
                           exception=None):
    """Render an error page to the user."""
    context = RequestContext(request)
    context.update(dict(message=message, exception=exception))
    data = render_to_string(template_name, context)
    return HttpResponse(data, status=status)


def parse_openid_response(request):
    """Parse an OpenID response from a Django request."""
    current_url = request.build_absolute_uri()

    consumer = make_consumer(request)
    data = get_request_data(request)
    return consumer.complete(data, current_url)


def get_request_data(request):
    # simulate old request.REQUEST for backwards compatibility
    data = QueryDict(query_string=None, mutable=True)
    data.update(request.GET)
    data.update(request.POST)
    return data


def login_begin(request, template_name='openid/login.html',
                login_complete_view='openid-complete',
                form_class=OpenIDLoginForm,
                render_failure=default_render_failure,
                redirect_field_name=REDIRECT_FIELD_NAME):
    """Begin an OpenID login request, possibly asking for an identity URL."""
    data = get_request_data(request)
    redirect_to = data.get(redirect_field_name, '')

    # Get the OpenID URL to try.  First see if we've been configured
    # to use a fixed server URL.
    openid_url = getattr(settings, 'OPENID_SSO_SERVER_URL', None)

    if openid_url is None:
        if request.POST:
            login_form = form_class(data=request.POST)
            if login_form.is_valid():
                openid_url = login_form.cleaned_data['openid_identifier']
        else:
            login_form = form_class()

        # Invalid or no form data:
        if openid_url is None:
            context = RequestContext(request)
            context.update({
                'form': login_form,
                redirect_field_name: redirect_to,
            })
            return render_to_response(template_name, context)

    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure as exc:
        return render_failure(
            request, "OpenID discovery error: %s" % (str(exc),), status=500,
            exception=exc)

    # Request some user details.  If the provider advertises support
    # for attribute exchange, use that.
    endpoint = openid_request.endpoint
    if endpoint.supportsType(ax.AXMessage.ns_uri):
        fetch_request = ax.FetchRequest()
        # We mark all the attributes as required, since Google ignores
        # optional attributes.  We request both the full name and
        # first/last components since some providers offer one but not
        # the other.
        for (attr, alias) in [
                ('http://axschema.org/contact/email', 'email'),
                ('http://axschema.org/namePerson', 'fullname'),
                ('http://axschema.org/namePerson/first', 'firstname'),
                ('http://axschema.org/namePerson/last', 'lastname'),
                ('http://axschema.org/namePerson/friendly', 'nickname'),
                # The myOpenID provider advertises AX support, but uses
                # attribute names from an obsolete draft of the
                # specification.  We request them for compatibility.
                ('http://schema.openid.net/contact/email', 'old_email'),
                ('http://schema.openid.net/namePerson', 'old_fullname'),
                ('http://schema.openid.net/namePerson/friendly',
                 'old_nickname')]:
            fetch_request.add(ax.AttrInfo(attr, alias=alias, required=True))

        # conditionally require account_verified attribute
        verification_scheme_map = getattr(
            settings, 'OPENID_VALID_VERIFICATION_SCHEMES', {})
        valid_schemes = verification_scheme_map.get(
            endpoint.server_url, verification_scheme_map.get(None, ()))
        if valid_schemes:
            # there are valid schemes configured for this endpoint, so
            # request account_verified status
            fetch_request.add(ax.AttrInfo(
                'http://ns.login.ubuntu.com/2013/validation/account',
                alias='account_verified', required=True))

        openid_request.addExtension(fetch_request)
    else:
        sreg_required_fields = []
        sreg_required_fields.extend(
            getattr(settings, 'OPENID_SREG_REQUIRED_FIELDS', []))
        sreg_optional_fields = ['email', 'fullname', 'nickname']
        sreg_optional_fields.extend(
            getattr(settings, 'OPENID_SREG_EXTRA_FIELDS', []))
        sreg_optional_fields = [
            field for field in sreg_optional_fields
            if field not in sreg_required_fields]
        openid_request.addExtension(
            sreg.SRegRequest(optional=sreg_optional_fields,
                             required=sreg_required_fields))

    if getattr(settings, 'OPENID_PHYSICAL_MULTIFACTOR_REQUIRED', False):
        preferred_auth = [
            pape.AUTH_MULTI_FACTOR_PHYSICAL,
        ]
        pape_request = pape.Request(preferred_auth_policies=preferred_auth)
        openid_request.addExtension(pape_request)

    # Request team info
    teams_mapping_auto = getattr(
        settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO', False)
    teams_mapping_auto_blacklist = getattr(
        settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST', [])
    launchpad_teams = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
    if teams_mapping_auto:
        # ignore launchpad teams. use all django-groups
        launchpad_teams = dict()
        all_groups = Group.objects.exclude(
            name__in=teams_mapping_auto_blacklist)
        for group in all_groups:
            launchpad_teams[group.name] = group.name

    if launchpad_teams:
        openid_request.addExtension(teams.TeamsRequest(launchpad_teams.keys()))

    # Construct the request completion URL, including the page we
    # should redirect to.
    return_to = request.build_absolute_uri(reverse(login_complete_view))
    if redirect_to:
        if '?' in return_to:
            return_to += '&'
        else:
            return_to += '?'
        # Django gives us Unicode, which is great.  We must encode URI.
        # urllib enforces str. We can't trust anything about the default
        # encoding inside  str(foo) , so we must explicitly make foo a str.
        return_to += urlencode(
            {redirect_field_name: redirect_to.encode("UTF-8")})

    return render_openid_request(request, openid_request, return_to)


@csrf_exempt
def login_complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
                   render_failure=None):
    data = get_request_data(request)
    redirect_to = data.get(redirect_field_name, '')
    render_failure = (
        render_failure or getattr(settings, 'OPENID_RENDER_FAILURE', None) or
        default_render_failure)

    openid_response = parse_openid_response(request)
    if not openid_response:
        return render_failure(
            request, 'This is an OpenID relying party endpoint.')

    if openid_response.status == SUCCESS:
        try:
            user = authenticate(openid_response=openid_response)
        except DjangoOpenIDException as e:
            return render_failure(
                request, getattr(e, 'message', str(e)), exception=e)

        if user is not None:
            if user.is_active:
                auth_login(request, user)
                response = HttpResponseRedirect(
                    sanitise_redirect_url(redirect_to))

                # Notify any listeners that we successfully logged in.
                openid_login_complete.send(
                    sender=UserOpenID, request=request,
                    openid_response=openid_response)

                return response
            else:
                return render_failure(request, 'Disabled account')
        else:
            return render_failure(request, 'Unknown user')
    elif openid_response.status == FAILURE:
        return render_failure(
            request, 'OpenID authentication failed: %s' %
            openid_response.message)
    elif openid_response.status == CANCEL:
        return render_failure(request, 'Authentication cancelled')
    else:
        assert False, (
            "Unknown OpenID response type: %r" % openid_response.status)


def logo(request):
    return HttpResponse(
        OPENID_LOGO_BASE_64.decode('base64'), mimetype='image/gif'
    )


# Logo from http://openid.net/login-bg.gif
# Embedded here for convenience; you should serve this as a static file
OPENID_LOGO_BASE_64 = """
R0lGODlhEAAQAMQAAO3t7eHh4srKyvz8/P5pDP9rENLS0v/28P/17tXV1dHEvPDw8M3Nzfn5+d3d
3f5jA97Syvnv6MfLzcfHx/1mCPx4Kc/S1Pf189C+tP+xgv/k1N3OxfHy9NLV1/39/f///yH5BAAA
AAAALAAAAAAQABAAAAVq4CeOZGme6KhlSDoexdO6H0IUR+otwUYRkMDCUwIYJhLFTyGZJACAwQcg
EAQ4kVuEE2AIGAOPQQAQwXCfS8KQGAwMjIYIUSi03B7iJ+AcnmclHg4TAh0QDzIpCw4WGBUZeikD
Fzk0lpcjIQA7
"""
