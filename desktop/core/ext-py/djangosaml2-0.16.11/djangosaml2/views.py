# Copyright (C) 2010-2013 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import logging

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
try:
    from django.contrib.auth.views import LogoutView
    django_logout = LogoutView.as_view()
except ImportError:
    from django.contrib.auth.views import logout as django_logout
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect  # 30x
from django.http import HttpResponseBadRequest  # 40x
from django.http import HttpResponseServerError  # 50x
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.utils.six import text_type, binary_type, PY3
from django.views.decorators.csrf import csrf_exempt

from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.metadata import entity_descriptor
from saml2.ident import code, decode
from saml2.sigver import MissingKey
from saml2.s_utils import UnsupportedBinding
from saml2.response import StatusError, StatusAuthnFailed, SignatureError, StatusRequestDenied
from saml2.validate import ResponseLifetimeExceed, ToEarly
from saml2.xmldsig import SIG_RSA_SHA1, SIG_RSA_SHA256  # support for SHA1 is required by spec

from djangosaml2.cache import IdentityCache, OutstandingQueriesCache
from djangosaml2.cache import StateCache
from djangosaml2.conf import get_config
from djangosaml2.overrides import Saml2Client
from djangosaml2.signals import post_authenticated
from djangosaml2.utils import (
    available_idps, fail_acs_response, get_custom_setting,
    get_idp_sso_supported_bindings, get_location, is_safe_url_compat,
)


logger = logging.getLogger('djangosaml2')


def _set_subject_id(session, subject_id):
    session['_saml2_subject_id'] = code(subject_id)


def _get_subject_id(session):
    try:
        return decode(session['_saml2_subject_id'])
    except KeyError:
        return None


def callable_bool(value):
    """ A compatibility wrapper for pre Django 1.10 User model API that used
    is_authenticated() and is_anonymous() methods instead of attributes
    """
    if callable(value):
        return value()
    else:
        return value


def login(request,
          config_loader_path=None,
          wayf_template='djangosaml2/wayf.html',
          authorization_error_template='djangosaml2/auth_error.html',
          post_binding_form_template='djangosaml2/post_binding_form.html'):
    """SAML Authorization Request initiator

    This view initiates the SAML2 Authorization handshake
    using the pysaml2 library to create the AuthnRequest.
    It uses the SAML 2.0 Http Redirect protocol binding.

    * post_binding_form_template - path to a template containing HTML form with
    hidden input elements, used to send the SAML message data when HTTP POST
    binding is being used. You can customize this template to include custom
    branding and/or text explaining the automatic redirection process. Please
    see the example template in
    templates/djangosaml2/example_post_binding_form.html
    If set to None or nonexistent template, default form from the saml2 library
    will be rendered.
    """
    logger.debug('Login process started')

    came_from = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    if not came_from:
        logger.warning('The next parameter exists but is empty')
        came_from = settings.LOGIN_REDIRECT_URL

    # Ensure the user-originating redirection url is safe.
    if not is_safe_url_compat(url=came_from, allowed_hosts={request.get_host()}):
        came_from = settings.LOGIN_REDIRECT_URL

    # if the user is already authenticated that maybe because of two reasons:
    # A) He has this URL in two browser windows and in the other one he
    #    has already initiated the authenticated session.
    # B) He comes from a view that (incorrectly) send him here because
    #    he does not have enough permissions. That view should have shown
    #    an authorization error in the first place.
    # We can only make one thing here and that is configurable with the
    # SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN setting. If that setting
    # is True (default value) we will redirect him to the came_from view.
    # Otherwise, we will show an (configurable) authorization error.
    if callable_bool(request.user.is_authenticated):
        redirect_authenticated_user = getattr(settings, 'SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN', True)
        if redirect_authenticated_user:
            return HttpResponseRedirect(came_from)
        else:
            logger.debug('User is already logged in')
            return render(request, authorization_error_template, {
                    'came_from': came_from,
                    }, using='django')

    selected_idp = request.GET.get('idp', None)
    conf = get_config(config_loader_path, request)

    # is a embedded wayf needed?
    idps = available_idps(conf)
    if selected_idp is None and len(idps) > 1:
        logger.debug('A discovery process is needed')
        return render(request, wayf_template, {
                'available_idps': idps.items(),
                'came_from': came_from,
                }, using='django')

    # choose a binding to try first
    sign_requests = getattr(conf, '_sp_authn_requests_signed', False)
    binding = BINDING_HTTP_POST if sign_requests else BINDING_HTTP_REDIRECT
    logger.debug('Trying binding %s for IDP %s', binding, selected_idp)

    # ensure our selected binding is supported by the IDP
    supported_bindings = get_idp_sso_supported_bindings(selected_idp, config=conf)
    if binding not in supported_bindings:
        logger.debug('Binding %s not in IDP %s supported bindings: %s',
                     binding, selected_idp, supported_bindings)
        if binding == BINDING_HTTP_POST:
            logger.warning('IDP %s does not support %s,  trying %s',
                           selected_idp, binding, BINDING_HTTP_REDIRECT)
            binding = BINDING_HTTP_REDIRECT
        else:
            logger.warning('IDP %s does not support %s,  trying %s',
                           selected_idp, binding, BINDING_HTTP_POST)
            binding = BINDING_HTTP_POST
        # if switched binding still not supported, give up
        if binding not in supported_bindings:
            raise UnsupportedBinding('IDP %s does not support %s or %s',
                                     selected_idp, BINDING_HTTP_POST, BINDING_HTTP_REDIRECT)

    client = Saml2Client(conf)
    http_response = None

    logger.debug('Redirecting user to the IdP via %s binding.', binding)
    if binding == BINDING_HTTP_REDIRECT:
        try:
            # do not sign the xml itself, instead use the sigalg to
            # generate the signature as a URL param
            sig_alg_option_map = {'sha1': SIG_RSA_SHA1,
                                  'sha256': SIG_RSA_SHA256}
            sig_alg_option = getattr(conf, '_sp_authn_requests_signed_alg', 'sha1')
            sigalg = sig_alg_option_map[sig_alg_option] if sign_requests else None
            session_id, result = client.prepare_for_authenticate(
                entityid=selected_idp, relay_state=came_from,
                binding=binding, sign=False, sigalg=sigalg)
        except TypeError as e:
            logger.error('Unable to know which IdP to use')
            return HttpResponse(text_type(e))
        else:
            http_response = HttpResponseRedirect(get_location(result))
    elif binding == BINDING_HTTP_POST:
        if post_binding_form_template:
            # get request XML to build our own html based on the template
            try:
                location = client.sso_location(selected_idp, binding)
            except TypeError as e:
                logger.error('Unable to know which IdP to use')
                return HttpResponse(text_type(e))
            session_id, request_xml = client.create_authn_request(
                location,
                binding=binding)
            try:
                if PY3:
                    saml_request = base64.b64encode(binary_type(request_xml, 'UTF-8'))
                else:
                    saml_request = base64.b64encode(binary_type(request_xml))

                http_response = render(request, post_binding_form_template, {
                    'target_url': location,
                    'params': {
                        'SAMLRequest': saml_request,
                        'RelayState': came_from,
                        },
                    }, using='django')
            except TemplateDoesNotExist:
                pass

        if not http_response:
            # use the html provided by pysaml2 if no template was specified or it didn't exist
            try:
                session_id, result = client.prepare_for_authenticate(
                    entityid=selected_idp, relay_state=came_from,
                    binding=binding)
            except TypeError as e:
                logger.error('Unable to know which IdP to use')
                return HttpResponse(text_type(e))
            else:
                http_response = HttpResponse(result['data'])
    else:
        raise UnsupportedBinding('Unsupported binding: %s', binding)

    # success, so save the session ID and return our response
    logger.debug('Saving the session_id in the OutstandingQueries cache')
    oq_cache = OutstandingQueriesCache(request.session)
    oq_cache.set(session_id, came_from)
    return http_response


@require_POST
@csrf_exempt
def assertion_consumer_service(request,
                               config_loader_path=None,
                               attribute_mapping=None,
                               create_unknown_user=None):
    """SAML Authorization Response endpoint

    The IdP will send its response to this view, which
    will process it with pysaml2 help and log the user
    in using the custom Authorization backend
    djangosaml2.backends.Saml2Backend that should be
    enabled in the settings.py
    """
    attribute_mapping = attribute_mapping or get_custom_setting('SAML_ATTRIBUTE_MAPPING', {'uid': ('username', )})
    create_unknown_user = create_unknown_user if create_unknown_user is not None else \
                          get_custom_setting('SAML_CREATE_UNKNOWN_USER', True)
    conf = get_config(config_loader_path, request)
    try:
        xmlstr = request.POST['SAMLResponse']
    except KeyError:
        logger.warning('Missing "SAMLResponse" parameter in POST data.')
        raise SuspiciousOperation

    client = Saml2Client(conf, identity_cache=IdentityCache(request.session))

    oq_cache = OutstandingQueriesCache(request.session)
    outstanding_queries = oq_cache.outstanding_queries()

    try:
        response = client.parse_authn_request_response(xmlstr, BINDING_HTTP_POST, outstanding_queries)
    except (StatusError, ToEarly):
        logger.exception("Error processing SAML Assertion.")
        return fail_acs_response(request)
    except ResponseLifetimeExceed:
        logger.info("SAML Assertion is no longer valid. Possibly caused by network delay or replay attack.", exc_info=True)
        return fail_acs_response(request)
    except SignatureError:
        logger.info("Invalid or malformed SAML Assertion.", exc_info=True)
        return fail_acs_response(request)
    except StatusAuthnFailed:
        logger.info("Authentication denied for user by IdP.", exc_info=True)
        return fail_acs_response(request)
    except StatusRequestDenied:
        logger.warning("Authentication interrupted at IdP.", exc_info=True)
        return fail_acs_response(request)
    except MissingKey:
        logger.exception("SAML Identity Provider is not configured correctly: certificate key is missing!")
        return fail_acs_response(request)

    if response is None:
        logger.warning("Invalid SAML Assertion received (unknown error).")
        return fail_acs_response(request, status=400, exc_class=SuspiciousOperation)

    session_id = response.session_id()
    oq_cache.delete(session_id)

    # authenticate the remote user
    session_info = response.session_info()

    if callable(attribute_mapping):
        attribute_mapping = attribute_mapping()
    if callable(create_unknown_user):
        create_unknown_user = create_unknown_user()

    logger.debug('Trying to authenticate the user. Session info: %s', session_info)
    user = auth.authenticate(request=request,
                             session_info=session_info,
                             attribute_mapping=attribute_mapping,
                             create_unknown_user=create_unknown_user)
    if user is None:
        logger.warning("Could not authenticate user received in SAML Assertion. Session info: %s", session_info)
        raise PermissionDenied

    auth.login(request, user)
    _set_subject_id(request.session, session_info['name_id'])
    logger.debug("User %s authenticated via SSO.", user)

    logger.debug('Sending the post_authenticated signal')
    post_authenticated.send_robust(sender=user, session_info=session_info)

    # redirect the user to the view where he came from
    default_relay_state = get_custom_setting('ACS_DEFAULT_REDIRECT_URL',
                                             settings.LOGIN_REDIRECT_URL)
    relay_state = request.POST.get('RelayState', default_relay_state)
    if not relay_state:
        logger.warning('The RelayState parameter exists but is empty')
        relay_state = default_relay_state
    if not is_safe_url_compat(url=relay_state, allowed_hosts={request.get_host()}):
        relay_state = settings.LOGIN_REDIRECT_URL
    logger.debug('Redirecting to the RelayState: %s', relay_state)
    return HttpResponseRedirect(relay_state)


@login_required
def echo_attributes(request,
                    config_loader_path=None,
                    template='djangosaml2/echo_attributes.html'):
    """Example view that echo the SAML attributes of an user"""
    state = StateCache(request.session)
    conf = get_config(config_loader_path, request)

    client = Saml2Client(conf, state_cache=state,
                         identity_cache=IdentityCache(request.session))
    subject_id = _get_subject_id(request.session)
    try:
        identity = client.users.get_identity(subject_id,
                                             check_not_on_or_after=False)
    except AttributeError:
        return HttpResponse("No active SAML identity found. Are you sure you have logged in via SAML?")

    return render(request, template, {'attributes': identity[0]}, using='django')


@login_required
def logout(request, config_loader_path=None):
    """SAML Logout Request initiator

    This view initiates the SAML2 Logout request
    using the pysaml2 library to create the LogoutRequest.
    """
    state = StateCache(request.session)
    conf = get_config(config_loader_path, request)

    client = Saml2Client(conf, state_cache=state,
                         identity_cache=IdentityCache(request.session))
    subject_id = _get_subject_id(request.session)
    if subject_id is None:
        logger.warning(
            'The session does not contain the subject id for user %s',
            request.user)

    result = client.global_logout(subject_id)

    state.sync()

    if not result:
        logger.error("Looks like the user %s is not logged in any IdP/AA", subject_id)
        return HttpResponseBadRequest("You are not logged in any IdP/AA")

    if len(result) > 1:
        logger.error('Sorry, I do not know how to logout from several sources. I will logout just from the first one')

    for entityid, logout_info in result.items():
        if isinstance(logout_info, tuple):
            binding, http_info = logout_info
            if binding == BINDING_HTTP_POST:
                logger.debug('Returning form to the IdP to continue the logout process')
                body = ''.join(http_info['data'])
                return HttpResponse(body)
            elif binding == BINDING_HTTP_REDIRECT:
                logger.debug('Redirecting to the IdP to continue the logout process')
                return HttpResponseRedirect(get_location(http_info))
            else:
                logger.error('Unknown binding: %s', binding)
                return HttpResponseServerError('Failed to log out')
        else:
            # We must have had a soap logout
            return finish_logout(request, logout_info)

    logger.error('Could not logout because there only the HTTP_REDIRECT is supported')
    return HttpResponseServerError('Logout Binding not supported')


def logout_service(request, *args, **kwargs):
    return do_logout_service(request, request.GET, BINDING_HTTP_REDIRECT, *args, **kwargs)


@csrf_exempt
def logout_service_post(request, *args, **kwargs):
    return do_logout_service(request, request.POST, BINDING_HTTP_POST, *args, **kwargs)


def do_logout_service(request, data, binding, config_loader_path=None, next_page=None,
                   logout_error_template='djangosaml2/logout_error.html'):
    """SAML Logout Response endpoint

    The IdP will send the logout response to this view,
    which will process it with pysaml2 help and log the user
    out.
    Note that the IdP can request a logout even when
    we didn't initiate the process as a single logout
    request started by another SP.
    """
    logger.debug('Logout service started')
    conf = get_config(config_loader_path, request)

    state = StateCache(request.session)
    client = Saml2Client(conf, state_cache=state,
                         identity_cache=IdentityCache(request.session))

    if 'SAMLResponse' in data:  # we started the logout
        logger.debug('Receiving a logout response from the IdP')
        response = client.parse_logout_request_response(data['SAMLResponse'], binding)
        state.sync()
        return finish_logout(request, response, next_page=next_page)

    elif 'SAMLRequest' in data:  # logout started by the IdP
        logger.debug('Receiving a logout request from the IdP')
        subject_id = _get_subject_id(request.session)
        if subject_id is None:
            logger.warning(
                'The session does not contain the subject id for user %s. Performing local logout',
                request.user)
            auth.logout(request)
            return render(request, logout_error_template, status=403, using='django')
        else:
            http_info = client.handle_logout_request(
                data['SAMLRequest'],
                subject_id,
                binding,
                relay_state=data.get('RelayState', ''))
            state.sync()
            auth.logout(request)
            return HttpResponseRedirect(get_location(http_info))
    else:
        logger.error('No SAMLResponse or SAMLRequest parameter found')
        raise Http404('No SAMLResponse or SAMLRequest parameter found')


def finish_logout(request, response, next_page=None):
    if response and response.status_ok():
        if next_page is None and hasattr(settings, 'LOGOUT_REDIRECT_URL'):
            next_page = settings.LOGOUT_REDIRECT_URL
        logger.debug('Performing django logout with a next_page of %s',
                     next_page)
        return django_logout(request, next_page=next_page)
    else:
        logger.error('Unknown error during the logout')
        return render(request, "djangosaml2/logout_error.html", {}, using='django')


def metadata(request, config_loader_path=None, valid_for=None):
    """Returns an XML with the SAML 2.0 metadata for this
    SP as configured in the settings.py file.
    """
    conf = get_config(config_loader_path, request)
    metadata = entity_descriptor(conf)
    return HttpResponse(content=text_type(metadata).encode('utf-8'),
                        content_type="text/xml; charset=utf8")


def register_namespace_prefixes():
    from saml2 import md, saml, samlp
    try:
        from saml2 import xmlenc
        from saml2 import xmldsig
    except ImportError:
        import xmlenc
        import xmldsig
    prefixes = (('saml', saml.NAMESPACE),
                ('samlp', samlp.NAMESPACE),
                ('md', md.NAMESPACE),
                ('ds', xmldsig.NAMESPACE),
                ('xenc', xmlenc.NAMESPACE))
    if hasattr(ElementTree, 'register_namespace'):
        for prefix, namespace in prefixes:
            ElementTree.register_namespace(prefix, namespace)
    else:
        for prefix, namespace in prefixes:
            ElementTree._namespace_map[namespace] = prefix

register_namespace_prefixes()
