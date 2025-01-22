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
from functools import wraps
from typing import Optional
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.shortcuts import render, resolve_url
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django.contrib import auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site

import saml2
from saml2.client_base import LogoutError
from saml2.config import SPConfig
from saml2.ident import code, decode
from saml2.mdstore import SourceNotFound
from saml2.metadata import entity_descriptor
from saml2.response import (
    RequestVersionTooLow,
    SignatureError,
    StatusAuthnFailed,
    StatusError,
    StatusNoAuthnContext,
    StatusRequestDenied,
    UnsolicitedResponse,
)
from saml2.s_utils import UnsupportedBinding
from saml2.saml import SCM_BEARER
from saml2.samlp import AuthnRequest, IDPEntry, IDPList, Scoping
from saml2.sigver import MissingKey
from saml2.validate import ResponseLifetimeExceed, ToEarly

from .cache import IdentityCache, OutstandingQueriesCache, StateCache
from .conf import get_config
from .exceptions import IdPConfigurationMissing
from .overrides import Saml2Client
from .utils import (
    add_idp_hinting,
    available_idps,
    get_csp_handler,
    get_custom_setting,
    get_fallback_login_redirect_url,
    get_idp_sso_supported_bindings,
    get_location,
    validate_referral_url,
)

logger = logging.getLogger("djangosaml2")


def saml2_csp_update(view):
    csp_handler = get_csp_handler()

    @wraps(view)
    def wrapper(*args, **kwargs):
        return csp_handler(view)(*args, **kwargs)

    return wrapper


def _set_subject_id(session, subject_id):
    session["_saml2_subject_id"] = code(subject_id)


def _get_subject_id(session):
    try:
        return decode(session["_saml2_subject_id"])
    except KeyError:
        return None


def _get_next_path(request: HttpRequest) -> Optional[str]:
    if "next" in request.GET:
        next_path = request.GET["next"]
    elif "RelayState" in request.GET:
        next_path = request.GET["RelayState"]
    else:
        return None

    next_path = validate_referral_url(request, next_path)

    return next_path


class SPConfigMixin:
    """Mixin for some of the SAML views with re-usable methods."""

    config_loader_path = None

    def get_config_loader_path(self, request: HttpRequest):
        return self.config_loader_path

    def get_sp_config(self, request: HttpRequest) -> SPConfig:
        return get_config(self.get_config_loader_path(request), request)

    def get_state_client(self, request: HttpRequest):
        conf = self.get_sp_config(request)
        state = StateCache(request.saml_session)
        client = Saml2Client(
            conf, state_cache=state, identity_cache=IdentityCache(request.saml_session)
        )
        return state, client


@method_decorator(saml2_csp_update, name='dispatch')
class LoginView(SPConfigMixin, View):
    """SAML Authorization Request initiator.

    This view initiates the SAML2 Authorization handshake
    using the pysaml2 library to create the AuthnRequest.

    post_binding_form_template is a path to a template containing HTML form with
    hidden input elements, used to send the SAML message data when HTTP POST
    binding is being used. You can customize this template to include custom
    branding and/or text explaining the automatic redirection process. Please
    see the example template in templates/djangosaml2/example_post_binding_form.html
    If set to None or nonexistent template, default form from the saml2 library
    will be rendered.
    """

    wayf_template = getattr(
        settings, "SAML2_CUSTOM_WAYF_TEMPLATE", "djangosaml2/wayf.html"
    )
    authorization_error_template = getattr(
        settings,
        "SAML2_CUSTOM_AUTHORIZATION_ERROR_TEMPLATE",
        "djangosaml2/auth_error.html",
    )
    post_binding_form_template = getattr(
        settings,
        "SAML2_CUSTOM_POST_BINDING_FORM_TEMPLATE",
        "djangosaml2/post_binding_form.html",
    )

    def unknown_idp(self, request, idp):
        msg = f"Error: IdP EntityID {escape(idp)} was not found in metadata"
        logger.exception(msg)
        return HttpResponse(msg, status=403)

    def load_sso_kwargs_scoping(self, sso_kwargs):
        """Performs IdP Scoping if scoping param is present."""
        idp_scoping_param = self.request.GET.get("scoping", None)
        if idp_scoping_param:
            idp_scoping = Scoping()
            idp_scoping.idp_list = IDPList()
            idp_scoping.idp_list.idp_entry.append(
                IDPEntry(provider_id=idp_scoping_param)
            )
            sso_kwargs["scoping"] = idp_scoping

    def load_sso_kwargs(self, sso_kwargs):
        """Inherit me if you want to put your desidered things in sso_kwargs"""

    def add_idp_hinting(self, http_response):
        return add_idp_hinting(self.request, http_response) or http_response

    def should_prevent_auth(self, request) -> bool:
        # If the user is already authenticated that maybe because of two reasons:
        # A) He has this URL in two browser windows and in the other one he
        #    has already initiated the authenticated session.
        # B) He comes from a view that (incorrectly) send him here because
        #    he does not have enough permissions. That view should have shown
        #    an authorization error in the first place.
        return request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        logger.debug("Login process started")
        next_path = _get_next_path(request)
        if next_path is None:
            next_path = get_fallback_login_redirect_url()

        if self.should_prevent_auth(request):
            # If the SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN setting is True
            # (default value), redirect to the next_path. Otherwise, show a
            # configurable authorization error.
            if get_custom_setting("SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN", True):
                return HttpResponseRedirect(next_path)
            logger.debug("User is already logged in")
            return render(
                request,
                self.authorization_error_template,
                {
                    "came_from": next_path,
                },
            )

        try:
            conf = self.get_sp_config(request)
        except SourceNotFound:  # pragma: no cover
            # this is deprecated and it's here only for the doubts that something
            # would happen the day after I'll remove it! :)
            return self.unknown_idp(request, idp="unknown")

        # is a embedded wayf or DiscoveryService needed?
        configured_idps = available_idps(conf)
        selected_idp = request.GET.get("idp", None)

        self.conf = conf
        sso_kwargs = {}

        # Do we have a Discovery Service?
        if not selected_idp:
            discovery_service = getattr(settings, "SAML2_DISCO_URL", None)
            if discovery_service:
                # We have to build the URL to redirect to with all the information
                # for the Discovery Service to know how to send the flow back to us
                logger.debug(
                    (
                        "A discovery process is needed trough a" "Discovery Service: {}"
                    ).format(discovery_service)
                )
                login_url = "{}?next={}".format(
                    request.build_absolute_uri(reverse("saml2_login")),
                    quote(next_path, safe=""),
                )
                ds_url = "{}?entityID={}&return={}&returnIDParam=idp".format(
                    discovery_service,
                    quote(conf.entityid, safe=""),
                    quote(login_url, safe=""),
                )
                return HttpResponseRedirect(ds_url)

            elif len(configured_idps) > 1:
                logger.debug("A discovery process trough WAYF page is needed")
                return render(
                    request,
                    self.wayf_template,
                    {
                        "available_idps": configured_idps.items(),
                        "came_from": next_path,
                    },
                )

        # when using MDQ and DS we need to initiate a check on the selected idp,
        # otherwise the available idps will be empty
        configured_idps = available_idps(conf, idp_to_check=selected_idp)

        # is the first one, otherwise next logger message will print None
        if not configured_idps:  # pragma: no cover
            raise IdPConfigurationMissing("IdP is missing or its metadata is expired.")
        if selected_idp is None:
            selected_idp = list(configured_idps.keys())[0]

        # choose a binding to try first
        binding = getattr(settings, "SAML_DEFAULT_BINDING", saml2.BINDING_HTTP_POST)
        logger.debug(f"Trying binding {binding} for IDP {selected_idp}")

        # ensure our selected binding is supported by the IDP
        try:
            supported_bindings = get_idp_sso_supported_bindings(
                selected_idp, config=conf
            )
        except saml2.s_utils.UnknownSystemEntity:
            return self.unknown_idp(request, selected_idp)

        if binding not in supported_bindings:
            logger.debug(
                f"Binding {binding} not in IDP {selected_idp} "
                f"supported bindings: {supported_bindings}. Trying to switch ...",
            )
            if binding == saml2.BINDING_HTTP_POST:
                logger.warning(
                    f"IDP {selected_idp} does not support {binding} "
                    f"trying {saml2.BINDING_HTTP_REDIRECT}",
                )
                binding = saml2.BINDING_HTTP_REDIRECT
            else:  # pragma: no cover
                logger.warning(
                    f"IDP {selected_idp} does not support {binding} "
                    f"trying {saml2.BINDING_HTTP_POST}",
                )
                binding = saml2.BINDING_HTTP_POST
            # if switched binding still not supported, give up
            if binding not in supported_bindings:  # pragma: no cover
                raise UnsupportedBinding(
                    f"IDP {selected_idp} does not support "
                    f"{saml2.BINDING_HTTP_POST} or {saml2.BINDING_HTTP_REDIRECT}"
                )

        client = Saml2Client(conf)

        # SSO options
        sign_requests = getattr(conf, "_sp_authn_requests_signed", False)
        if sign_requests:
            sso_kwargs["sigalg"] = getattr(
                conf, "_sp_signing_algorithm", saml2.xmldsig.SIG_RSA_SHA256
            )
            sso_kwargs["digest_alg"] = getattr(
                conf, "_sp_digest_algorithm", saml2.xmldsig.DIGEST_SHA256
            )
        # pysaml needs a string otherwise: "cannot serialize True (type bool)"
        if getattr(conf, "_sp_force_authn", False):
            sso_kwargs["force_authn"] = "true"
        if getattr(conf, "_sp_allow_create", False):
            sso_kwargs["allow_create"] = "true"

        # custom nsprefixes
        sso_kwargs["nsprefix"] = get_namespace_prefixes()

        # Enrich sso_kwargs ...
        # idp scoping
        self.load_sso_kwargs_scoping(sso_kwargs)
        # other customization to be inherited
        self.load_sso_kwargs(sso_kwargs)

        logger.debug(f"Redirecting user to the IdP via {binding} binding.")
        _msg = "Unable to know which IdP to use"
        http_response = None

        if binding == saml2.BINDING_HTTP_REDIRECT:
            try:
                session_id, result = client.prepare_for_authenticate(
                    entityid=selected_idp,
                    relay_state=next_path,
                    binding=binding,
                    sign=sign_requests,
                    **sso_kwargs,
                )
            except TypeError as e:
                logger.exception(f"{_msg}: {e}")
                return HttpResponse(_msg)
            else:
                http_response = HttpResponseRedirect(get_location(result))

        elif binding == saml2.BINDING_HTTP_POST:
            if self.post_binding_form_template:
                # get request XML to build our own html based on the template
                try:
                    location = client.sso_location(selected_idp, binding)
                except TypeError as e:
                    logger.exception(f"{_msg}: {e}")
                    return HttpResponse(_msg)

                session_id, request_xml = client.create_authn_request(
                    location, binding=binding, **sso_kwargs
                )
                try:
                    if isinstance(request_xml, AuthnRequest):
                        # request_xml will be an instance of AuthnRequest if the message is not signed
                        request_xml = str(request_xml)
                    saml_request = base64.b64encode(bytes(request_xml, "UTF-8")).decode(
                        "utf-8"
                    )

                    http_response = render(
                        request,
                        self.post_binding_form_template,
                        {
                            "target_url": location,
                            "params": {
                                "SAMLRequest": saml_request,
                                "RelayState": next_path,
                            },
                        },
                    )
                except TemplateDoesNotExist as e:
                    logger.debug(
                        f"TemplateDoesNotExist: [{self.post_binding_form_template}] - {e}",
                        exc_info=True
                    )

            if not http_response:
                # use the html provided by pysaml2 if no template was specified or it doesn't exist
                try:
                    session_id, result = client.prepare_for_authenticate(
                        entityid=selected_idp,
                        relay_state=next_path,
                        binding=binding,
                        **sso_kwargs,
                    )
                except TypeError as e:
                    _msg = f"Can't prepare the authentication for {selected_idp}"
                    logger.exception(f"{_msg}: {e}")
                    return HttpResponse(_msg)
                else:
                    http_response = HttpResponse(result["data"])
        else:
            raise UnsupportedBinding(f"Unsupported binding: {binding}")

        # success, so save the session ID and return our response
        oq_cache = OutstandingQueriesCache(request.saml_session)
        oq_cache.set(session_id, next_path)
        logger.debug(
            f'Saving the session_id "{oq_cache.__dict__}" '
            "in the OutstandingQueries cache",
        )

        # idp hinting support, add idphint url parameter if present in this request
        response = self.add_idp_hinting(http_response) or http_response
        return response


@method_decorator(csrf_exempt, name="dispatch")
class AssertionConsumerServiceView(SPConfigMixin, View):
    """The IdP will send its response to this view, which will process it using pysaml2 and
    log the user in using whatever SAML authentication backend has been enabled in
    settings.py. The `djangosaml2.backends.Saml2Backend` can be used for this purpose,
    though some implementations may instead register their own subclasses of Saml2Backend.
    """

    def custom_validation(self, response):
        pass

    def handle_acs_failure(self, request, exception=None, status=403, **kwargs):
        """Error handler if the login attempt fails. Override this to customize the error response."""

        # Backwards compatibility: if a custom setting was defined, use that one
        custom_failure_function = get_custom_setting(
            "SAML_ACS_FAILURE_RESPONSE_FUNCTION"
        )
        if custom_failure_function:
            failure_function = (
                custom_failure_function
                if callable(custom_failure_function)
                else import_string(custom_failure_function)
            )
            return failure_function(request, exception, status, **kwargs)

        return render(
            request,
            "djangosaml2/login_error.html",
            {"exception": exception},
            status=status,
        )

    def post(self, request, attribute_mapping=None, create_unknown_user=None):
        """SAML Authorization Response endpoint"""

        if "SAMLResponse" not in request.POST:
            logger.warning('Missing "SAMLResponse" parameter in POST data.')
            return HttpResponseBadRequest(
                'Missing "SAMLResponse" parameter in POST data.'
            )

        attribute_mapping = attribute_mapping or get_custom_setting(
            "SAML_ATTRIBUTE_MAPPING", {"uid": ("username",)}
        )
        create_unknown_user = create_unknown_user or get_custom_setting(
            "SAML_CREATE_UNKNOWN_USER", True
        )
        conf = self.get_sp_config(request)

        identity_cache = IdentityCache(request.saml_session)
        client = Saml2Client(conf, identity_cache=identity_cache)
        oq_cache = OutstandingQueriesCache(request.saml_session)
        oq_cache.sync()
        outstanding_queries = oq_cache.outstanding_queries()

        _exception = None
        try:
            response = client.parse_authn_request_response(
                request.POST["SAMLResponse"],
                saml2.BINDING_HTTP_POST,
                outstanding_queries,
            )
        except (StatusError, ToEarly) as e:
            _exception = e
            logger.exception("Error processing SAML Assertion.")
        except ResponseLifetimeExceed as e:
            _exception = e
            logger.info(
                (
                    "SAML Assertion is no longer valid. Possibly caused "
                    "by network delay or replay attack."
                ),
                exc_info=True,
            )
        except SignatureError as e:
            _exception = e
            logger.info("Invalid or malformed SAML Assertion.", exc_info=True)
        except StatusAuthnFailed as e:
            _exception = e
            logger.info("Authentication denied for user by IdP.", exc_info=True)
        except StatusRequestDenied as e:
            _exception = e
            logger.warning("Authentication interrupted at IdP.", exc_info=True)
        except StatusNoAuthnContext as e:
            _exception = e
            logger.warning("Missing Authentication Context from IdP.", exc_info=True)
        except MissingKey as e:
            _exception = e
            logger.exception(
                "SAML Identity Provider is not configured correctly: certificate key is missing!"
            )
        except UnsolicitedResponse as e:
            _exception = e
            logger.exception("Received SAMLResponse when no request has been made.")
        except RequestVersionTooLow as e:
            _exception = e
            logger.exception("Received SAMLResponse have a deprecated SAML2 VERSION.")
        except Exception as e:
            _exception = e
            logger.exception("SAMLResponse Error")

        if _exception:
            return self.handle_acs_failure(request, exception=_exception)
        elif response is None:
            logger.warning("Invalid SAML Assertion received (unknown error).")
            return self.handle_acs_failure(
                request,
                status=400,
                exception=SuspiciousOperation("Unknown SAML2 error"),
            )

        try:
            self.custom_validation(response)
        except Exception as e:
            logger.warning(f"SAML Response validation error: {e}", exc_info=True)
            return self.handle_acs_failure(
                request,
                status=400,
                exception=SuspiciousOperation("SAML2 validation error"),
            )

        session_id = response.session_id()
        oq_cache.delete(session_id)

        # authenticate the remote user
        session_info = response.session_info()

        # assertion_info
        assertion = response.assertion
        assertion_info = {}
        for sc in assertion.subject.subject_confirmation:
            if sc.method == SCM_BEARER:
                assertion_not_on_or_after = sc.subject_confirmation_data.not_on_or_after
                assertion_info = {
                    "assertion_id": assertion.id,
                    "not_on_or_after": assertion_not_on_or_after,
                }
                break

        if callable(attribute_mapping):
            attribute_mapping = attribute_mapping()
        if callable(create_unknown_user):
            create_unknown_user = create_unknown_user()

        try:
            user = self.authenticate_user(
                request,
                session_info,
                attribute_mapping,
                create_unknown_user,
                assertion_info
            )
        except PermissionDenied as e:
            return self.handle_acs_failure(
                request,
                exception=e,
                session_info=session_info,
            )

        relay_state = self.build_relay_state()
        custom_redirect_url = self.custom_redirect(user, relay_state, session_info)
        if custom_redirect_url:
            return HttpResponseRedirect(custom_redirect_url)

        relay_state = validate_referral_url(request, relay_state)
        if not relay_state:
            logger.debug(
                "RelayState is not a valid URL, redirecting to fallback: %s",
                relay_state
            )
            return HttpResponseRedirect(get_fallback_login_redirect_url())

        logger.debug("Redirecting to the RelayState: %s", relay_state)
        return HttpResponseRedirect(relay_state)

    def authenticate_user(
            self,
            request,
            session_info,
            attribute_mapping,
            create_unknown_user,
            assertion_info
        ):
        """Calls Django's authenticate method after the SAML response is verified"""
        logger.debug("Trying to authenticate the user. Session info: %s", session_info)

        user = auth.authenticate(
            request=request,
            session_info=session_info,
            attribute_mapping=attribute_mapping,
            create_unknown_user=create_unknown_user,
            assertion_info=assertion_info,
        )
        if user is None:
            logger.warning(
                "Could not authenticate user received in SAML Assertion. Session info: %s",
                session_info,
            )
            raise PermissionDenied("No user could be authenticated.")

        auth.login(self.request, user)
        _set_subject_id(request.saml_session, session_info["name_id"])
        logger.debug("User %s authenticated via SSO.", user)

        self.post_login_hook(request, user, session_info)
        self.customize_session(user, session_info)

        return user

    def post_login_hook(
        self, request: HttpRequest, user: settings.AUTH_USER_MODEL, session_info: dict
    ) -> None:
        """If desired, a hook to add logic after a user has succesfully logged in."""

    def build_relay_state(self) -> str:
        """The relay state is a URL used to redirect the user to the view where they came from."""
        default_relay_state = get_fallback_login_redirect_url()
        relay_state = self.request.POST.get("RelayState", default_relay_state)
        relay_state = self.customize_relay_state(relay_state)
        if not relay_state:
            logger.warning("The RelayState parameter exists but is empty")
            relay_state = default_relay_state
        return relay_state

    def customize_session(self, user, session_info: dict):
        """Subclasses can use this for customized functionality around user sessions."""

    def customize_relay_state(self, relay_state: str) -> str:
        """Subclasses may override this method to implement custom logic for relay state."""
        return relay_state

    def custom_redirect(self, user, relay_state: str, session_info) -> str:
        """Subclasses may override this method to implement custom logic for redirect.

        For example, some sites may require user registration if the user has not
        yet been provisioned.
        """
        return None


class EchoAttributesView(LoginRequiredMixin, SPConfigMixin, View):
    """Example view that echo the SAML attributes of an user"""

    def get(self, request, *args, **kwargs):
        state, client = self.get_state_client(request)

        subject_id = _get_subject_id(request.saml_session)
        try:
            identity = client.users.get_identity(
                subject_id, check_not_on_or_after=False
            )
        except AttributeError:
            return HttpResponse(
                "No active SAML identity found. Are you sure you have logged in via SAML?"
            )

        return render(
            request, "djangosaml2/echo_attributes.html", {"attributes": identity[0]}
        )


@method_decorator(saml2_csp_update, name='dispatch')
class LogoutInitView(LoginRequiredMixin, SPConfigMixin, View):
    """SAML Logout Request initiator

    This view initiates the SAML2 Logout request
    using the pysaml2 library to create the LogoutRequest.
    """

    def get(self, request, *args, **kwargs):
        state, client = self.get_state_client(request)

        subject_id = _get_subject_id(request.saml_session)
        if subject_id is None:
            logger.warning(
                "The session does not contain the subject id for user %s", request.user
            )

        _error = None
        try:
            result = client.global_logout(subject_id)
        except LogoutError as exp:
            logger.exception(f"Error Handled - SLO not supported by IDP: {exp}")
            _error = exp
        except UnsupportedBinding as exp:
            logger.exception(f"Error Handled - SLO - unsupported binding by IDP: {exp}")
            _error = exp

        auth.logout(request)
        state.sync()

        if _error:
            return self.handle_unsupported_slo_exception(request, _error)

        if not result:
            logger.error(
                "Looks like the user %s is not logged in any IdP/AA", subject_id
            )
            return HttpResponseBadRequest("You are not logged in any IdP/AA")

        if len(result) > 1:
            logger.error(
                "Sorry, I do not know how to logout from several sources. I will logout just from the first one"
            )

        for logout_info in result.values():
            if isinstance(logout_info, tuple):
                binding, http_info = logout_info
                if binding == saml2.BINDING_HTTP_POST:
                    logger.debug(
                        "Returning form to the IdP to continue the logout process"
                    )
                    body = "".join(http_info["data"])
                    return HttpResponse(body)
                elif binding == saml2.BINDING_HTTP_REDIRECT:
                    logger.debug(
                        "Redirecting to the IdP to continue the logout process"
                    )
                    return HttpResponseRedirect(get_location(http_info))
                else:
                    logger.error("Unknown binding: %s", binding)
                    return HttpResponseServerError("Failed to log out")
            # We must have had a soap logout
            return finish_logout(request, logout_info)

        logger.error(
            "Could not logout because there only the HTTP_REDIRECT is supported"
        )
        return HttpResponseServerError("Logout Binding not supported")

    def handle_unsupported_slo_exception(self, request, exception, *args, **kwargs):
        """Subclasses may override this method to implement custom logic for
        handling logout errors. Redirects to LOGOUT_REDIRECT_URL by default.

        For example, a site may want to perform additional logic and redirect
        users somewhere other than the LOGOUT_REDIRECT_URL.
        """
        return HttpResponseRedirect(getattr(settings, "LOGOUT_REDIRECT_URL", "/"))


@method_decorator([saml2_csp_update, csrf_exempt], name="dispatch")
class LogoutView(SPConfigMixin, View):
    """SAML Logout Response endpoint

    The IdP will send the logout response to this view,
    which will process it with pysaml2 help and log the user
    out.
    Note that the IdP can request a logout even when
    we didn't initiate the process as a single logout
    request started by another SP.
    """

    logout_error_template = "djangosaml2/logout_error.html"

    def get(self, request, *args, **kwargs):
        return self.do_logout_service(
            request, request.GET, saml2.BINDING_HTTP_REDIRECT, *args, **kwargs
        )

    def post(self, request, *args, **kwargs):
        return self.do_logout_service(
            request, request.POST, saml2.BINDING_HTTP_POST, *args, **kwargs
        )

    def do_logout_service(self, request, data, binding, *args, **kwargs):
        logger.debug("Logout service started")

        state, client = self.get_state_client(request)

        if "SAMLResponse" in data:  # we started the logout
            logger.debug("Receiving a logout response from the IdP")
            try:
                response = client.parse_logout_request_response(
                    data["SAMLResponse"], binding
                )
            except StatusError as e:
                response = None
                logger.warning(f"Error logging out from remote provider: {e}", exc_info=True)
            state.sync()
            return finish_logout(request, response)

        elif "SAMLRequest" in data:  # logout started by the IdP
            logger.debug("Receiving a logout request from the IdP")
            subject_id = _get_subject_id(request.saml_session)

            if subject_id is None:
                logger.warning(
                    "The session does not contain the subject id for user %s. Performing local logout",
                    request.user,
                )
                auth.logout(request)
                return render(request, self.logout_error_template, status=403)

            http_info = client.handle_logout_request(
                data["SAMLRequest"],
                subject_id,
                binding,
                relay_state=data.get("RelayState", ""),
            )
            state.sync()
            auth.logout(request)
            if (
                http_info.get("method", "GET") == "POST"
                and "data" in http_info
                and ("Content-type", "text/html") in http_info.get("headers", [])
            ):
                # need to send back to the IDP a signed POST response with user session
                # return HTML form content to browser with auto form validation
                # to finally send request to the IDP
                return HttpResponse(http_info["data"])
            return HttpResponseRedirect(get_location(http_info))
        logger.error("No SAMLResponse or SAMLRequest parameter found")
        return HttpResponseBadRequest("No SAMLResponse or SAMLRequest parameter found")


def finish_logout(request, response):
    if getattr(settings, "SAML_IGNORE_LOGOUT_ERRORS", False) or (
        response and response.status_ok()
    ):
        logger.debug("Performing django logout.")

        auth.logout(request)

        next_path = _get_next_path(request)
        if next_path is not None:
            logger.debug("Redirecting to the RelayState: %s", next_path)
            return HttpResponseRedirect(next_path)
        elif settings.LOGOUT_REDIRECT_URL is not None:
            fallback_url = resolve_url(settings.LOGOUT_REDIRECT_URL)
            logger.debug("No valid RelayState found; Redirecting to "
                         "LOGOUT_REDIRECT_URL")
            return HttpResponseRedirect(fallback_url)
        else:
            current_site = get_current_site(request)
            logger.debug("No valid RelayState or LOGOUT_REDIRECT_URL found, "
                         "rendering fallback template.")
            return render(
                request,
                "registration/logged_out.html",
                {
                    "site": current_site,
                    "site_name": current_site.name,
                    "title": _("Logged out"),
                    "subtitle": None,
                },
            )

    logger.error("Unknown error during the logout")
    return render(request, "djangosaml2/logout_error.html", {})


class MetadataView(SPConfigMixin, View):
    """Returns an XML with the SAML 2.0 metadata for this SP as configured in the settings.py file."""

    def get(self, request, *args, **kwargs):
        conf = self.get_sp_config(request)
        metadata = entity_descriptor(conf)
        return HttpResponse(
            content=str(metadata).encode("utf-8"),
            content_type="text/xml; charset=utf-8",
        )


def get_namespace_prefixes():
    from saml2 import md, saml, samlp, xmldsig, xmlenc

    return {
        "saml": saml.NAMESPACE,
        "samlp": samlp.NAMESPACE,
        "md": md.NAMESPACE,
        "ds": xmldsig.NAMESPACE,
        "xenc": xmlenc.NAMESPACE,
    }
