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

import logging

try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout as django_logout
from django.http import Http404, HttpResponse
from django.http import HttpResponseRedirect  # 30x
from django.http import  HttpResponseBadRequest, HttpResponseForbidden  # 40x
from django.http import HttpResponseServerError  # 50x
from django.views.decorators.http import require_POST
from django.shortcuts import render_to_response
from django.template import RequestContext
try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    # Django 1.0 compatibility
    def csrf_exempt(view_func):
        return view_func

from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.metadata import entity_descriptor
from saml2.ident import code, decode

from djangosaml2.cache import IdentityCache, OutstandingQueriesCache
from djangosaml2.cache import StateCache
from djangosaml2.conf import get_config
from djangosaml2.signals import post_authenticated
from djangosaml2.utils import get_custom_setting, available_idps, get_location


logger = logging.getLogger('djangosaml2')


def _set_subject_id(session, subject_id):
    session['_saml2_subject_id'] = code(subject_id)


def _get_subject_id(session):
    try:
        return decode(session['_saml2_subject_id'])
    except KeyError:
        return None


def login(request,
          config_loader_path=None,
          wayf_template='djangosaml2/wayf.html',
          authorization_error_template='djangosaml2/auth_error.html'):
    """SAML Authorization Request initiator

    This view initiates the SAML2 Authorization handshake
    using the pysaml2 library to create the AuthnRequest.
    It uses the SAML 2.0 Http Redirect protocol binding.
    """
    logger.debug('Login process started')

    came_from = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    if not came_from:
        logger.warning('The next parameter exists but is empty')
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
    if not request.user.is_anonymous():
        try:
            redirect_authenticated_user = settings.SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN
        except AttributeError:
            redirect_authenticated_user = True

        if redirect_authenticated_user:
            return HttpResponseRedirect(came_from)
        else:
            logger.debug('User is already logged in')
            return render_to_response(authorization_error_template, {
                    'came_from': came_from,
                    }, context_instance=RequestContext(request))

    selected_idp = request.GET.get('idp', None)
    conf = get_config(config_loader_path, request)

    # is a embedded wayf needed?
    idps = available_idps(conf)
    if selected_idp is None and len(idps) > 1:
        logger.debug('A discovery process is needed')
        return render_to_response(wayf_template, {
                'available_idps': idps.items(),
                'came_from': came_from,
                }, context_instance=RequestContext(request))

    client = Saml2Client(conf)
    try:
        (session_id, result) = client.prepare_for_authenticate(
            entityid=selected_idp, relay_state=came_from,
            binding=BINDING_HTTP_REDIRECT,
            )
    except TypeError, e:
        logger.error('Unable to know which IdP to use')
        return HttpResponse(unicode(e))

    logger.debug('Saving the session_id in the OutstandingQueries cache')
    oq_cache = OutstandingQueriesCache(request.session)
    oq_cache.set(session_id, came_from)

    logger.debug('Redirecting the user to the IdP')
    return HttpResponseRedirect(get_location(result))


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
    attribute_mapping = attribute_mapping or get_custom_setting(
            'SAML_ATTRIBUTE_MAPPING', {'uid': ('username', )})
    create_unknown_user = create_unknown_user or get_custom_setting(
            'SAML_CREATE_UNKNOWN_USER', True)
    logger.debug('Assertion Consumer Service started')

    conf = get_config(config_loader_path, request)
    if 'SAMLResponse' not in request.POST:
        return HttpResponseBadRequest(
            'Couldn\'t find "SAMLResponse" in POST data.')
    xmlstr = request.POST['SAMLResponse']
    client = Saml2Client(conf, identity_cache=IdentityCache(request.session))

    oq_cache = OutstandingQueriesCache(request.session)
    outstanding_queries = oq_cache.outstanding_queries()

    # process the authentication response
    response = client.parse_authn_request_response(xmlstr, BINDING_HTTP_POST,
                                                   outstanding_queries)
    if response is None:
        logger.error('SAML response is None')
        return HttpResponseBadRequest(
            "SAML response has errors. Please check the logs")

    session_id = response.session_id()
    oq_cache.delete(session_id)

    # authenticate the remote user
    session_info = response.session_info()

    if callable(attribute_mapping):
        attribute_mapping = attribute_mapping()
    if callable(create_unknown_user):
        create_unknown_user = create_unknown_user()

    logger.debug('Trying to authenticate the user')
    user = auth.authenticate(session_info=session_info,
                             attribute_mapping=attribute_mapping,
                             create_unknown_user=create_unknown_user)
    if user is None:
        logger.error('The user is None')
        return HttpResponseForbidden("Permission denied")

    auth.login(request, user)
    _set_subject_id(request.session, session_info['name_id'])

    logger.debug('Sending the post_authenticated signal')
    post_authenticated.send_robust(sender=user, session_info=session_info)

    # redirect the user to the view where he came from
    relay_state = request.POST.get('RelayState', '/')
    if not relay_state:
        logger.warning('The RelayState parameter exists but is empty')
        relay_state = settings.LOGIN_REDIRECT_URL
    logger.debug('Redirecting to the RelayState: ' + relay_state)
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
    identity = client.users.get_identity(subject_id,
                                         check_not_on_or_after=False)
    return render_to_response(template, {'attributes': identity[0]},
                              context_instance=RequestContext(request))


@login_required
def logout(request, config_loader_path=None):
    """SAML Logout Request initiator

    This view initiates the SAML2 Logout request
    using the pysaml2 library to create the LogoutRequest.
    """
    logger.debug('Logout process started')
    state = StateCache(request.session)
    conf = get_config(config_loader_path, request)

    client = Saml2Client(conf, state_cache=state,
                         identity_cache=IdentityCache(request.session))
    subject_id = _get_subject_id(request.session)
    if subject_id is None:
        logger.warning(
            'The session does not contains the subject id for user %s'
            % request.user)

    result = client.global_logout(subject_id)

    state.sync()

    if not result:
        logger.error("Looks like the user %s is not logged in any IdP/AA" % subject_id)
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
                'The session does not contain the subject id for user %s. Performing local logout'
                % request.user)
            auth.logout(request)
            return render_to_response(logout_error_template, {},
                                      context_instance=RequestContext(request))
        else:
            http_info = client.handle_logout_request(
                data['SAMLRequest'],
                subject_id,
                binding)
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
        logger.debug('Performing django_logout with a next_page of %s'
                     % next_page)
        return django_logout(request, next_page=next_page)
    else:
        logger.error('Unknown error during the logout')
        return HttpResponse('Error during logout')


def metadata(request, config_loader_path=None, valid_for=None):
    """Returns an XML with the SAML 2.0 metadata for this
    SP as configured in the settings.py file.
    """
    conf = get_config(config_loader_path, request)
    metadata = entity_descriptor(conf)
    return HttpResponse(content=str(metadata),
                        content_type="text/xml; charset=utf8")


def register_namespace_prefixes():
    from saml2 import md, saml, samlp
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
