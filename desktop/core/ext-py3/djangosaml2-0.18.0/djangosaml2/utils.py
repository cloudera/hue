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

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.http import is_safe_url
from django.utils.module_loading import import_string
from saml2.s_utils import UnknownSystemEntity
from functools import lru_cache, wraps
from django.utils.module_loading import import_string

def get_custom_setting(name, default=None):
    return getattr(settings, name, default)


def available_idps(config, langpref=None):
    if langpref is None:
        langpref = "en"

    idps = set()

    for metadata_name, metadata in config.metadata.metadata.items():
        result = metadata.any('idpsso_descriptor', 'single_sign_on_service')
        if result:
            idps = idps.union(set(result.keys()))

    return dict([(idp, config.metadata.name(idp, langpref)) for idp in idps])


def get_idp_sso_supported_bindings(idp_entity_id=None, config=None):
    """Returns the list of bindings supported by an IDP
    This is not clear in the pysaml2 code, so wrapping it in a util"""
    if config is None:
        # avoid circular import
        from djangosaml2.conf import get_config
        config = get_config()
    # load metadata store from config
    meta = getattr(config, 'metadata', {})
    # if idp is None, assume only one exists so just use that
    if idp_entity_id is None:
        # .keys() returns dict_keys in python3.5+
        try:
            idp_entity_id = list(available_idps(config).keys())[0]
        except IndexError:
            raise ImproperlyConfigured("No IdP configured!")
    try:
        return meta.service(idp_entity_id, 'idpsso_descriptor', 'single_sign_on_service').keys()
    except UnknownSystemEntity:
        return []


def get_location(http_info):
    """Extract the redirect URL from a pysaml2 http_info object"""
    try:
        headers = dict(http_info['headers'])
        return headers['Location']
    except KeyError:
        return http_info['url']


def fail_acs_response(request, *args, **kwargs):
    """ Serves as a common mechanism for ending ACS in case of any SAML related failure.
    Handling can be configured by setting the SAML_ACS_FAILURE_RESPONSE_FUNCTION as
    suitable for the project.

    The default behavior uses SAML specific template that is rendered on any ACS error,
    but this can be simply changed so that PermissionDenied exception is raised instead.
    """
    failure_function = import_string(get_custom_setting('SAML_ACS_FAILURE_RESPONSE_FUNCTION',
                                                        'djangosaml2.acs_failures.template_failure'))
    return failure_function(request, *args, **kwargs)


def is_safe_url_compat(url, allowed_hosts=None, require_https=False):
    if django.VERSION >= (1, 11):
        return is_safe_url(url, allowed_hosts=allowed_hosts, require_https=require_https)
    assert len(allowed_hosts) == 1
    host = allowed_hosts.pop()
    return is_safe_url(url, host=host)

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