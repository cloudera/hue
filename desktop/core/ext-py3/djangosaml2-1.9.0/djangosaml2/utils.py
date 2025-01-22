# Copyright (C) 2012 Yaco Sistemas (http://www.yaco.es)
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
import re
import urllib
import zlib
from functools import lru_cache, wraps
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import NoReverseMatch
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.module_loading import import_string

from saml2.config import SPConfig
from saml2.mdstore import MetaDataMDX
from saml2.s_utils import UnknownSystemEntity

logger = logging.getLogger(__name__)


def get_custom_setting(name: str, default=None):
    return getattr(settings, name, default)


def available_idps(config: SPConfig, langpref=None, idp_to_check: str = None) -> dict:
    if langpref is None:
        langpref = "en"

    idps = set()

    for metadata in config.metadata.metadata.values():
        # initiate a fetch to the selected idp when using MDQ, otherwise the MetaDataMDX is an empty database
        if isinstance(metadata, MetaDataMDX) and idp_to_check:
            m = metadata[idp_to_check]
        result = metadata.any("idpsso_descriptor", "single_sign_on_service")
        if result:
            idps.update(result.keys())

    return {idp: config.metadata.name(idp, langpref) for idp in idps}


def get_idp_sso_supported_bindings(
    idp_entity_id: Optional[str] = None, config: Optional[SPConfig] = None
) -> list:
    """Returns the list of bindings supported by an IDP
    This is not clear in the pysaml2 code, so wrapping it in a util"""
    if config is None:
        # avoid circular import
        from .conf import get_config

        config = get_config()
    # load metadata store from config
    meta = getattr(config, "metadata", {})
    # if idp is None, assume only one exists so just use that
    if idp_entity_id is None:
        try:
            idp_entity_id = list(available_idps(config).keys())[0]
        except IndexError:
            raise ImproperlyConfigured("No IdP configured!")
    try:
        return list(
            meta.service(
                idp_entity_id, "idpsso_descriptor", "single_sign_on_service"
            ).keys()
        )
    except UnknownSystemEntity:
        raise UnknownSystemEntity
    except Exception as e:
        logger.exception(f"get_idp_sso_supported_bindings failed with: {e}")


def get_location(http_info):
    """Extract the redirect URL from a pysaml2 http_info object"""
    try:
        headers = dict(http_info["headers"])
        return headers["Location"]
    except KeyError:
        return http_info["url"]


def get_fallback_login_redirect_url():
    login_redirect_url = get_custom_setting("LOGIN_REDIRECT_URL", "/")
    return resolve_url(
        get_custom_setting("ACS_DEFAULT_REDIRECT_URL", login_redirect_url)
    )


def validate_referral_url(request, url):
    # Ensure the url is even a valid URL; sometimes the given url is a
    # RelayState containing PySAML data.
    # Some technically-valid urls will be fail this check, so the
    # SAML_STRICT_URL_VALIDATION setting can be used to turn off this check.
    # This should only happen if there is no slash, host and/or protocol in the
    # given URL. A better fix would be to add those to the RelayState.
    saml_strict_url_validation = getattr(
        settings,
        "SAML_STRICT_URL_VALIDATION",
        True
    )
    try:
        if saml_strict_url_validation:
            # This will also resolve Django URL pattern names
            url = resolve_url(url)
    except NoReverseMatch:
        logger.debug(
            "Could not validate given referral url is a valid URL", exc_info=True
        )
        return None

    # Ensure the user-originating redirection url is safe.
    # By setting SAML_ALLOWED_HOSTS in settings.py the user may provide a list of "allowed"
    # hostnames for post-login redirects, much like one would specify ALLOWED_HOSTS .
    # If this setting is absent, the default is to use the hostname that was used for the current
    # request.
    saml_allowed_hosts = set(
        getattr(settings, "SAML_ALLOWED_HOSTS", [request.get_host()])
    )

    if not url_has_allowed_host_and_scheme(url=url, allowed_hosts=saml_allowed_hosts):
        logger.debug("Referral URL not in SAML_ALLOWED_HOSTS or of the origin "
                     "host.")
        return None

    return url


def saml2_from_httpredirect_request(url):
    urlquery = urllib.parse.urlparse(url).query
    b64_inflated_saml2req = urllib.parse.parse_qs(urlquery)["SAMLRequest"][0]

    inflated_saml2req = base64.b64decode(b64_inflated_saml2req)
    deflated_saml2req = zlib.decompress(inflated_saml2req, -15)
    return deflated_saml2req


def get_session_id_from_saml2(saml2_xml):
    saml2_xml = saml2_xml.decode() if isinstance(saml2_xml, bytes) else saml2_xml
    return re.findall(r'ID="([a-z0-9\-]*)"', saml2_xml, re.I)[0]


def get_subject_id_from_saml2(saml2_xml):
    saml2_xml = saml2_xml if isinstance(saml2_xml, str) else saml2_xml.decode()
    re.findall('">([a-z0-9]+)</saml:NameID>', saml2_xml)[0]


def add_param_in_url(url: str, param_key: str, param_value: str):
    params = list(url.split("?"))
    params.append(f"{param_key}={param_value}")
    new_url = params[0] + "?" + "".join(params[1:])
    return new_url


def add_idp_hinting(request, http_response) -> bool:
    idphin_param = getattr(settings, "SAML2_IDPHINT_PARAM", "idphint")
    urllib.parse.urlencode(request.GET)

    if idphin_param not in request.GET.keys():
        return False

    idphint = request.GET[idphin_param]
    # validation : TODO -> improve!
    if idphint[0:4] != "http":
        logger.warning(
            f'Idp hinting: "{idphint}" doesn\'t contain a valid value.'
            "idphint paramenter ignored."
        )
        return False

    if http_response.status_code in (302, 303):
        # redirect binding
        # urlp = urllib.parse.urlparse(http_response.url)
        new_url = add_param_in_url(http_response.url, idphin_param, idphint)
        return HttpResponseRedirect(new_url)

    elif http_response.status_code == 200:
        # post binding
        res = re.search(
            r'action="(?P<url>[a-z0-9\:\/\_\-\.]*)"',
            http_response.content.decode(),
            re.I,
        )
        if not res:
            return False
        orig_url = res.groupdict()["url"]
        #
        new_url = add_param_in_url(orig_url, idphin_param, idphint)
        content = http_response.content.decode().replace(orig_url, new_url).encode()
        return HttpResponse(content)

    else:
        logger.warning(
            f"Idp hinting: cannot detect request type [{http_response.status_code}]"
        )
    return False


@lru_cache()
def get_csp_handler():
    """Returns a view decorator for CSP."""

    def empty_view_decorator(view):
        return view

    csp_handler_string = get_custom_setting("SAML_CSP_HANDLER", None)

    if csp_handler_string is None:
        # No CSP handler configured, attempt to use django-csp
        return _django_csp_update_decorator() or empty_view_decorator

    if csp_handler_string.strip() != "":
        # Non empty string is configured, attempt to import it
        csp_handler = import_string(csp_handler_string)

        def custom_csp_updater(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return csp_handler(f(*args, **kwargs))

            return wrapper

        return custom_csp_updater

    # Fall back to empty decorator when csp_handler_string is empty
    return empty_view_decorator


def _django_csp_update_decorator():
    """Returns a view CSP decorator if django-csp is available, otherwise None."""
    try:
        from csp.decorators import csp_update
    except ModuleNotFoundError:
        # If csp is not installed, do not update fields as Content-Security-Policy
        # is not used
        logger.warning(
            "django-csp could not be found, not updating Content-Security-Policy. Please "
            "make sure CSP is configured. This can be done by your reverse proxy, "
            "django-csp or a custom CSP handler via SAML_CSP_HANDLER. See "
            "https://djangosaml2.readthedocs.io/contents/security.html#content-security-policy"
            " for more information. "
            "This warning can be disabled by setting `SAML_CSP_HANDLER=''` in your settings."
        )
        return
    else:
        # autosubmit of forms uses nonce per default
        # form-action https: to send data to IdPs
        return csp_update(FORM_ACTION=["https:"])
