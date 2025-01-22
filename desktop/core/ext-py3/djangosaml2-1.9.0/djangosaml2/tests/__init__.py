# Copyright (C) 2012 Sam Bull (lsb@pocketuniverse.ca)
# Copyright (C) 2011-2012 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2010 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
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
import datetime
import re
import sys
from importlib import import_module
from unittest import mock
from urllib.parse import parse_qs, urlparse

from django import http
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse, reverse_lazy

from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.auth.models import AnonymousUser

from saml2.config import SPConfig
from saml2.s_utils import (
    UnknownSystemEntity,
    decode_base64_and_inflate,
    deflate_and_base64_encode,
)

from djangosaml2 import views
from djangosaml2.cache import OutstandingQueriesCache
from djangosaml2.conf import get_config
from djangosaml2.middleware import SamlSessionMiddleware
from djangosaml2.tests import conf
from djangosaml2.utils import (
    get_fallback_login_redirect_url,
    get_idp_sso_supported_bindings,
    get_session_id_from_saml2,
    get_subject_id_from_saml2,
    saml2_from_httpredirect_request,
)
from djangosaml2.views import EchoAttributesView, finish_logout

from .auth_response import auth_response
from .utils import SAMLPostFormParser

User = get_user_model()

PY_VERSION = sys.version_info[:2]


def dummy_loader(request):
    return "dummy_loader"


def dummy_get_response(request: http.HttpRequest):
    """
    Return a basic HttpResponse.

    Function needed to instantiate SamlSessionMiddleware.
    """
    return http.HttpResponse("Session test")


non_callable = "just a string"


class UtilsTests(TestCase):
    def test_get_config_valid_path(self):
        self.assertEqual(get_config("djangosaml2.tests.dummy_loader"), "dummy_loader")

    def test_get_config_wrongly_formatted_path(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured, "SAML config loader must be a callable object."
        ):
            get_config("djangosaml2.tests.non_callable")

    def test_get_config_nonsense_path(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "Error importing SAML config loader lalala.nonexisting.blabla: \"No module named 'lalala'\"",
        ):
            get_config("lalala.nonexisting.blabla")

    def test_get_config_missing_function(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            'Module "djangosaml2.tests" does not define a "nonexisting_function" attribute/class',
        ):
            get_config("djangosaml2.tests.nonexisting_function")

    @override_settings(LOGIN_REDIRECT_URL="/accounts/profile/")
    def test_get_fallback_login_redirect_url(self):
        self.assertEqual(get_fallback_login_redirect_url(), "/accounts/profile/")

        with override_settings():
            del settings.LOGIN_REDIRECT_URL
            # Neither LOGIN_REDIRECT_URL nor ACS_DEFAULT_REDIRECT_URL is configured
            self.assertEqual(get_fallback_login_redirect_url(), "/")

        with override_settings(ACS_DEFAULT_REDIRECT_URL="testprofiles:dashboard"):
            # ACS_DEFAULT_REDIRECT_URL is configured, so it is used (and resolved)
            self.assertEqual(get_fallback_login_redirect_url(), "/dashboard/")

        with override_settings(
            ACS_DEFAULT_REDIRECT_URL=reverse_lazy("testprofiles:dashboard")
        ):
            # Lazy urls are resolved
            self.assertEqual(get_fallback_login_redirect_url(), "/dashboard/")


class SAML2Tests(TestCase):

    urls = "djangosaml2.tests.urls"

    def init_cookies(self):
        self.client.cookies[settings.SESSION_COOKIE_NAME] = "testing"

    def add_outstanding_query(self, session_id, came_from):
        settings.SESSION_ENGINE = "django.contrib.sessions.backends.db"
        engine = import_module(settings.SESSION_ENGINE)
        self.saml_session = engine.SessionStore()
        self.saml_session.save()
        self.oq_cache = OutstandingQueriesCache(self.saml_session)

        self.oq_cache.set(
            session_id if isinstance(session_id, str) else session_id.decode(),
            came_from,
        )
        self.saml_session.save()
        self.client.cookies[
            settings.SESSION_COOKIE_NAME
        ] = self.saml_session.session_key

    def b64_for_post(self, xml_text, encoding="utf-8"):
        return base64.b64encode(xml_text.encode(encoding)).decode("ascii")

    def test_get_idp_sso_supported_bindings_noargs(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
        idp_id = "https://idp.example.com/simplesaml/saml2/idp/metadata.php"
        self.assertEqual(
            get_idp_sso_supported_bindings()[0],
            list(
                settings.SAML_CONFIG["service"]["sp"]["idp"][idp_id][
                    "single_sign_on_service"
                ].keys()
            )[0],
        )

    def test_get_idp_sso_supported_bindings_unknown_idp(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        with self.assertRaises(UnknownSystemEntity):
            get_idp_sso_supported_bindings(idp_entity_id="random")

    def test_get_idp_sso_supported_bindings_no_idps(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=[],
            metadata_file="remote_metadata_no_idp.xml",
        )
        with self.assertRaisesMessage(ImproperlyConfigured, "No IdP configured!"):
            get_idp_sso_supported_bindings()

    def test_unsigned_post_authn_request(self):
        """
        Test that unsigned authentication requests via POST binding
        does not error.

        https://github.com/knaperek/djangosaml2/issues/168
        """
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_post_binding.xml",
            authn_requests_signed=False,
        )
        response = self.client.get(reverse("saml2_login"))

        self.assertEqual(response.status_code, 200)

        # Using POST-binding returns a page with form containing the SAMLRequest
        response_parser = SAMLPostFormParser()
        response_parser.feed(response.content.decode("utf-8"))
        saml_request = response_parser.saml_request_value

        self.assertIsNotNone(saml_request)
        self.assertIn(
            "AuthnRequest xmlns", base64.b64decode(saml_request).decode("utf-8")
        )

    def test_login_evil_redirect(self):
        """
        Make sure that if we give an URL other than our own host as the next
        parameter, it is replaced with the fallback login redirect url.
        """

        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        for redirect_url in ["/dashboard/", "testprofiles:dashboard"]:
            with self.subTest(LOGIN_REDIRECT_URL=redirect_url):
                with override_settings(LOGIN_REDIRECT_URL=redirect_url):
                    response = self.client.get(
                        reverse("saml2_login") + "?next=http://evil.com"
                    )
                    url = urlparse(response["Location"])
                    params = parse_qs(url.query)

                    self.assertEqual(params["RelayState"], ["/dashboard/"])

            with self.subTest(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                with override_settings(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                    response = self.client.get(
                        reverse("saml2_login") + "?next=http://evil.com"
                    )
                    url = urlparse(response["Location"])
                    params = parse_qs(url.query)

                    self.assertEqual(params["RelayState"], ["/dashboard/"])

    def test_no_redirect(self):
        """
        Make sure that if we give an empty path as the next parameter,
        it is replaced with the fallback login redirect url.
        """

        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        for redirect_url in ["/dashboard/", "testprofiles:dashboard"]:
            with self.subTest(LOGIN_REDIRECT_URL=redirect_url):
                with override_settings(LOGIN_REDIRECT_URL=redirect_url):
                    response = self.client.get(reverse("saml2_login") + "?next=")
                    url = urlparse(response["Location"])
                    params = parse_qs(url.query)

                    self.assertEqual(params["RelayState"], ["/dashboard/"])

            with self.subTest(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                with override_settings(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                    response = self.client.get(reverse("saml2_login") + "?next=")
                    url = urlparse(response["Location"])
                    params = parse_qs(url.query)

                    self.assertEqual(params["RelayState"], ["/dashboard/"])

    @override_settings(SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN=True)
    def test_login_already_logged(self):
        self.client.force_login(User.objects.create(username="user", password="pass"))

        for redirect_url in ["/dashboard/", "testprofiles:dashboard"]:
            with self.subTest(LOGIN_REDIRECT_URL=redirect_url):
                with override_settings(LOGIN_REDIRECT_URL=redirect_url):
                    with self.subTest("no next url"):
                        response = self.client.get(reverse("saml2_login"))
                        self.assertRedirects(response, "/dashboard/")

                    with self.subTest("evil next url"):
                        response = self.client.get(
                            reverse("saml2_login") + "?next=http://evil.com"
                        )
                        self.assertRedirects(response, "/dashboard/")

            with self.subTest(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                with override_settings(ACS_DEFAULT_REDIRECT_URL=redirect_url):
                    with self.subTest("no next url"):
                        response = self.client.get(reverse("saml2_login"))
                        self.assertRedirects(response, "/dashboard/")

                    with self.subTest("evil next url"):
                        response = self.client.get(
                            reverse("saml2_login") + "?next=http://evil.com"
                        )
                        self.assertRedirects(response, "/dashboard/")

    def test_unknown_idp(self):
        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            metadata_file="remote_metadata_three_idps.xml",
        )

        response = self.client.get(reverse("saml2_login") + "?idp=<b>https://unknown.org</b>")
        self.assertContains(response, "&lt;b&gt;https://unknown.org&lt;/b&gt;", status_code=403)

    def test_login_authn_context(self):
        sp_kwargs = {
            "requested_authn_context": {
                "authn_context_class_ref": [
                    "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
                    "urn:oasis:names:tc:SAML:2.0:ac:classes:TLSClient",
                ],
                "comparison": "minimum",
            }
        }

        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
            sp_kwargs=sp_kwargs,
        )

        response = self.client.get(reverse("saml2_login"))
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SSOService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)

        saml_request = params["SAMLRequest"][0]
        self.assertIn(
            "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport",
            decode_base64_and_inflate(saml_request).decode("utf-8"),
        )

    def test_login_one_idp(self):
        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        response = self.client.get(reverse("saml2_login"))
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SSOService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)
        self.assertIn("RelayState", params)

        saml_request = params["SAMLRequest"][0]
        self.assertIn(
            "AuthnRequest xmlns",
            decode_base64_and_inflate(saml_request).decode("utf-8"),
        )

        # if we set a next arg in the login view, it is preserverd
        # in the RelayState argument
        nexturl = "/another-view/"
        response = self.client.get(reverse("saml2_login"), {"next": nexturl})
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SSOService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)
        self.assertIn("RelayState", params)
        self.assertEqual(params["RelayState"][0], nexturl)

    def test_login_several_idps(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp1.example.com", "idp2.example.com", "idp3.example.com"],
            metadata_file="remote_metadata_three_idps.xml",
        )
        response = self.client.get(reverse("saml2_login"))
        # a WAYF page should be displayed
        self.assertContains(response, "Where are you from?", status_code=200)
        for i in range(1, 4):
            link = "/login/?idp=https://idp%d.example.com/simplesaml/saml2/idp/metadata.php&next=/"
            self.assertContains(response, link % i)

        # click on the second idp
        response = self.client.get(
            reverse("saml2_login"),
            {
                "idp": "https://idp2.example.com/simplesaml/saml2/idp/metadata.php",
                "next": "/",
            },
        )
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp2.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SSOService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)
        self.assertIn("RelayState", params)

        saml_request = params["SAMLRequest"][0]
        self.assertIn(
            "AuthnRequest xmlns",
            decode_base64_and_inflate(saml_request).decode("utf-8"),
        )

    @override_settings(ACS_DEFAULT_REDIRECT_URL="testprofiles:dashboard")
    def test_assertion_consumer_service(self):
        # Get initial number of users
        initial_user_count = User.objects.count()
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
        response = self.client.get(reverse("saml2_login"))
        saml2_req = saml2_from_httpredirect_request(response.url)
        session_id = get_session_id_from_saml2(saml2_req)
        # session_id should start with a letter since it is a NCName
        came_from = "/another-view/"
        self.add_outstanding_query(session_id, came_from)

        # this will create a user
        saml_response = auth_response(session_id, "student")
        _url = reverse("saml2_acs")
        response = self.client.post(
            _url,
            {
                "SAMLResponse": self.b64_for_post(saml_response),
                "RelayState": came_from,
            },
        )
        self.assertEqual(response.status_code, 302)
        location = response["Location"]
        url = urlparse(location)
        self.assertEqual(url.path, came_from)

        self.assertEqual(User.objects.count(), initial_user_count + 1)
        user_id = self.client.session[SESSION_KEY]
        user = User.objects.get(id=user_id)
        self.assertEqual(user.username, "student")
        # Since a new user object is created, the password
        # field is set to have an unusable password.
        self.assertEqual(user.has_usable_password(), False)

        # let's create another user and log in with that one
        new_user = User.objects.create(username="teacher", password="not-used")

        #  session_id = "a1111111111111111111111111111111"
        client = Client()
        response = client.get(reverse("saml2_login"))
        saml2_req = saml2_from_httpredirect_request(response.url)
        session_id = get_session_id_from_saml2(saml2_req)

        came_from = ""  # bad, let's see if we can deal with this
        saml_response = auth_response(session_id, "teacher")
        self.add_outstanding_query(session_id, "/")
        response = client.post(
            reverse("saml2_acs"),
            {
                "SAMLResponse": self.b64_for_post(saml_response),
                "RelayState": came_from,
            },
        )

        # as the RelayState is empty we have redirect to ACS_DEFAULT_REDIRECT_URL
        self.assertRedirects(response, "/dashboard/")
        self.assertEqual(str(new_user.id), client.session[SESSION_KEY])
        new_user.refresh_from_db()
        # Since "new_user" already had a password,
        # the password field will remain unchanged.
        self.assertEqual(new_user.has_usable_password(), True)

    @override_settings(ACS_DEFAULT_REDIRECT_URL="testprofiles:dashboard")
    def test_assertion_consumer_service_default_relay_state(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        new_user = User.objects.create(username="teacher", password="not-used")

        response = self.client.get(reverse("saml2_login"))
        saml2_req = saml2_from_httpredirect_request(response.url)
        session_id = get_session_id_from_saml2(saml2_req)

        saml_response = auth_response(session_id, "teacher")
        self.add_outstanding_query(session_id, "/")
        response = self.client.post(
            reverse("saml2_acs"),
            {
                "SAMLResponse": self.b64_for_post(saml_response),
            },
        )
        self.assertEqual(response.status_code, 302)

        # The RelayState is missing, redirect to ACS_DEFAULT_REDIRECT_URL
        self.assertRedirects(response, "/dashboard/")
        self.assertEqual(str(new_user.id), self.client.session[SESSION_KEY])

    def test_assertion_consumer_service_already_logged_in_allowed(self):
        self.client.force_login(User.objects.create(username="user", password="pass"))

        settings.SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN = True

        came_from = "/dummy-url/"
        response = self.client.get(reverse("saml2_login") + f"?next={came_from}")
        self.assertEqual(response.status_code, 302)
        url = urlparse(response["Location"])
        self.assertEqual(url.path, came_from)

    def test_assertion_consumer_service_already_logged_in_error(self):
        self.client.force_login(User.objects.create(username="user", password="pass"))

        settings.SAML_IGNORE_AUTHENTICATED_USERS_ON_LOGIN = False

        came_from = "/dummy-url/"
        response = self.client.get(reverse("saml2_login") + f"?next={came_from}")
        self.assertEqual(response.status_code, 200)
        self.assertInHTML(
            "<p>You are already logged in and you are trying to go to the login page again.</p>",
            response.content.decode(),
        )

    def test_assertion_consumer_service_no_session(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        response = self.client.get(reverse("saml2_login"))
        saml2_req = saml2_from_httpredirect_request(response.url)
        session_id = get_session_id_from_saml2(saml2_req)
        # session_id should start with a letter since it is a NCName

        came_from = "/another-view/"
        self.add_outstanding_query(session_id, came_from)

        # Authentication is confirmed.
        saml_response = auth_response(session_id, "student")
        response = self.client.post(
            reverse("saml2_acs"),
            {
                "SAMLResponse": self.b64_for_post(saml_response),
                "RelayState": came_from,
            },
        )
        self.assertEqual(response.status_code, 302)
        location = response["Location"]
        url = urlparse(location)
        self.assertEqual(url.path, came_from)

        # Session should no longer be in outstanding queries.
        saml_response = auth_response(session_id, "student")
        response = self.client.post(
            reverse("saml2_acs"),
            {
                "SAMLResponse": self.b64_for_post(saml_response),
                "RelayState": came_from,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_missing_param_to_assertion_consumer_service_request(self):
        # Send request without SAML2Response parameter
        response = self.client.post(reverse("saml2_acs"))
        # Assert that view responded with "Bad Request" error
        self.assertEqual(response.status_code, 400)

    def test_bad_request_method_to_assertion_consumer_service(self):
        # Send request with non-POST method.
        response = self.client.get(reverse("saml2_acs"))
        # Assert that view responded with method not allowed status
        self.assertEqual(response.status_code, 405)

    def do_login(self):
        """Auxiliary method used in several tests (mainly logout tests)"""
        self.init_cookies()

        response = self.client.get(reverse("saml2_login"))
        saml2_req = saml2_from_httpredirect_request(response.url)
        session_id = get_session_id_from_saml2(saml2_req)
        # session_id should start with a letter since it is a NCName
        came_from = "/another-view/"
        self.add_outstanding_query(session_id, came_from)

        saml_response = auth_response(session_id, "student")

        # this will create a user
        response = self.client.post(
            reverse("saml2_acs"),
            {
                "SAMLResponse": self.b64_for_post(saml_response),
                "RelayState": came_from,
            },
        )
        subject_id = get_subject_id_from_saml2(saml_response)
        self.assertEqual(response.status_code, 302)
        return subject_id

    def test_echo_view_no_saml_session(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
        self.do_login()

        request = RequestFactory().get("/bar/foo")
        request.COOKIES = self.client.cookies
        request.user = User.objects.last()

        middleware = SamlSessionMiddleware(dummy_get_response)
        middleware.process_request(request)

        response = EchoAttributesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode(),
            "No active SAML identity found. Are you sure you have logged in via SAML?",
        )

    def test_echo_view_success(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
        self.do_login()

        request = RequestFactory().get("/")
        request.user = User.objects.last()

        middleware = SamlSessionMiddleware(dummy_get_response)
        middleware.process_request(request)

        saml_session_name = getattr(
            settings, "SAML_SESSION_COOKIE_NAME", "saml_session"
        )
        getattr(request, saml_session_name)[
            "_saml2_subject_id"
        ] = "1f87035b4c1325b296a53d92097e6b3fa36d7e30ee82e3fcb0680d60243c1f03"
        getattr(request, saml_session_name).save()

        response = EchoAttributesView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "<h1>SAML attributes</h1>",
            response.content.decode(),
            "Echo page not rendered",
        )

    def test_logout(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
        self.do_login()

        response = self.client.get(reverse("saml2_logout"))
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SingleLogoutService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)

        saml_request = params["SAMLRequest"][0]

        self.assertIn(
            "LogoutRequest xmlns",
            decode_base64_and_inflate(saml_request).decode("utf-8"),
            "Not a valid LogoutRequest",
        )

    def test_logout_service_local(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        self.do_login()

        response = self.client.get(reverse("saml2_logout"))
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SingleLogoutService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLRequest", params)

        saml_request = params["SAMLRequest"][0]

        self.assertIn(
            "LogoutRequest xmlns",
            decode_base64_and_inflate(saml_request).decode("utf-8"),
            "Not a valid LogoutRequest",
        )

        # now simulate a logout response sent by the idp
        expected_request = """<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="XXXXXXXXXXXXXXXXXXXXXX" Version="2.0" Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" Reason=""><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">1f87035b4c1325b296a53d92097e6b3fa36d7e30ee82e3fcb0680d60243c1f03</saml:NameID><samlp:SessionIndex>a0123456789abcdef0123456789abcdef</samlp:SessionIndex></samlp:LogoutRequest>"""

        request_id = re.findall(r' ID="(.*?)" ', expected_request)[0]
        instant = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_response = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutResponse xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="http://sp.example.com/saml2/ls/" ID="a140848e7ce2bce834d7264ecdde0151" InResponseTo="{}" IssueInstant="{}" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></samlp:Status></samlp:LogoutResponse>""".format(
            request_id, instant
        )

        response = self.client.get(
            reverse("saml2_ls"),
            {
                "SAMLResponse": deflate_and_base64_encode(saml_response),
            },
        )
        self.assertContains(response, "Logged out", status_code=200)
        self.assertListEqual(list(self.client.session.keys()), [])

    def test_logout_service_global(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        subject_id = self.do_login()
        # now simulate a global logout process initiated by another SP
        subject_id = views._get_subject_id(self.saml_session)
        instant = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        saml_request = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_9961abbaae6d06d251226cb25e38bf8f468036e57e" Version="2.0" IssueInstant="{}" Destination="http://sp.example.com/saml2/ls/"><saml:Issuer>https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">{}</saml:NameID><samlp:SessionIndex>_1837687b7bc9faad85839dbeb319627889f3021757</samlp:SessionIndex></samlp:LogoutRequest>""".format(
            instant, subject_id
        )

        response = self.client.get(
            reverse("saml2_ls"),
            {
                "SAMLRequest": deflate_and_base64_encode(saml_request),
            },
        )
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SingleLogoutService.php")

        params = parse_qs(url.query)
        self.assertIn("SAMLResponse", params)
        saml_response = params["SAMLResponse"][0]

        self.assertIn(
            "Response xmlns",
            decode_base64_and_inflate(saml_response).decode("utf-8"),
            "Not a valid Response",
        )

    @override_settings(LOGOUT_REDIRECT_URL="/dashboard/")
    def test_post_logout_redirection(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        self.do_login()

        response = self.client.get(reverse("saml2_logout"))
        self.assertEqual(response.status_code, 302)

        # now simulate a logout response sent by the idp
        expected_request = """<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="XXXXXXXXXXXXXXXXXXXXXX" Version="2.0" Destination="https://idp.example.com/simplesaml/saml2/idp/SingleLogoutService.php" Reason=""><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://sp.example.com/saml2/metadata/</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">1f87035b4c1325b296a53d92097e6b3fa36d7e30ee82e3fcb0680d60243c1f03</saml:NameID><samlp:SessionIndex>a0123456789abcdef0123456789abcdef</samlp:SessionIndex></samlp:LogoutRequest>"""

        request_id = re.findall(r' ID="(.*?)" ', expected_request)[0]
        instant = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        saml_response = """<?xml version='1.0' encoding='UTF-8'?>
<samlp:LogoutResponse xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" Destination="http://sp.example.com/saml2/ls/" ID="a140848e7ce2bce834d7264ecdde0151" InResponseTo="{}" IssueInstant="{}" Version="2.0"><saml:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success" /></samlp:Status></samlp:LogoutResponse>""".format(
            request_id, instant
        )

        response = self.client.get(
            reverse("saml2_ls"),
            {
                "SAMLResponse": deflate_and_base64_encode(saml_response),
            },
        )
        self.assertRedirects(response, "/dashboard/")
        self.assertListEqual(list(self.client.session.keys()), [])

    def test_incomplete_logout(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com", idp_hosts=["idp.example.com"]
        )

        # don't do a login

        # now simulate a global logout process initiated by another SP
        instant = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        saml_request = '<samlp:LogoutRequest xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_9961abbaae6d06d251226cb25e38bf8f468036e57e" Version="2.0" IssueInstant="{}" Destination="http://sp.example.com/saml2/ls/"><saml:Issuer>https://idp.example.com/simplesaml/saml2/idp/metadata.php</saml:Issuer><saml:NameID SPNameQualifier="http://sp.example.com/saml2/metadata/" Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">{}</saml:NameID><samlp:SessionIndex>_1837687b7bc9faad85839dbeb319627889f3021757</samlp:SessionIndex></samlp:LogoutRequest>'.format(
            instant, "invalid-subject-id"
        )

        response = self.client.get(
            reverse("saml2_ls"),
            {
                "SAMLRequest": deflate_and_base64_encode(saml_request),
            },
        )
        self.assertContains(response, "Logout error", status_code=403)

    def test_finish_logout_renders_error_template(self):
        request = RequestFactory().get("/bar/foo")
        response = finish_logout(request, None)
        self.assertContains(response, "<h1>Logout error</h1>", status_code=200)

    def test_sigalg_not_passed_when_not_signing_request(self):
        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        with mock.patch(
            "djangosaml2.views.Saml2Client.prepare_for_authenticate",
            return_value=("session_id", {"url": "fake"}),
        ) as prepare_for_auth_mock:
            self.client.get(reverse("saml2_login"))
        prepare_for_auth_mock.assert_called_once()
        _args, kwargs = prepare_for_auth_mock.call_args
        self.assertNotIn("sigalg", kwargs)

    def test_sigalg_passed_when_signing_request(self):
        # monkey patch SAML configuration
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )

        settings.SAML_CONFIG["service"]["sp"]["authn_requests_signed"] = True
        with mock.patch(
            "djangosaml2.views.Saml2Client.prepare_for_authenticate",
            return_value=("session_id", {"url": "fake"}),
        ) as prepare_for_auth_mock:
            self.client.get(reverse("saml2_login"))
        prepare_for_auth_mock.assert_called_once()
        _args, kwargs = prepare_for_auth_mock.call_args
        self.assertIn("sigalg", kwargs)

    @override_settings(SAML2_DISCO_URL="https://that-ds.org/ds")
    def test_discovery_service(self):
        settings.SAML_CONFIG = conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_three_idps.xml",
        )

        response = self.client.get(reverse("saml2_login"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://that-ds.org/ds", response.url)


def test_config_loader(request):
    config = SPConfig()
    config.load({"entityid": "testentity"})
    return config


def test_config_loader_callable(request):
    config = SPConfig()
    config.load({"entityid": "testentity_callable"})
    return config


def test_config_loader_with_real_conf(request):
    config = SPConfig()
    config.load(
        conf.create_conf(
            sp_host="sp.example.com",
            idp_hosts=["idp.example.com"],
            metadata_file="remote_metadata_one_idp.xml",
        )
    )
    return config


class ConfTests(TestCase):
    def test_custom_conf_loader(self):
        config_loader_path = "djangosaml2.tests.test_config_loader"
        request = RequestFactory().get("/bar/foo")
        conf = get_config(config_loader_path, request)

        self.assertEqual(conf.entityid, "testentity")

    def test_custom_conf_loader_callable(self):
        config_loader_path = test_config_loader_callable
        request = RequestFactory().get("/bar/foo")
        conf = get_config(config_loader_path, request)

        self.assertEqual(conf.entityid, "testentity_callable")

    def test_custom_conf_loader_from_view(self):
        config_loader_path = "djangosaml2.tests.test_config_loader_with_real_conf"
        request = RequestFactory().get("/login/")
        request.user = AnonymousUser()
        middleware = SamlSessionMiddleware(dummy_get_response)
        middleware.process_request(request)

        saml_session_name = getattr(
            settings, "SAML_SESSION_COOKIE_NAME", "saml_session"
        )
        getattr(request, saml_session_name).save()

        response = views.LoginView.as_view(config_loader_path=config_loader_path)(
            request
        )
        self.assertEqual(response.status_code, 302)
        location = response["Location"]

        url = urlparse(location)
        self.assertEqual(url.hostname, "idp.example.com")
        self.assertEqual(url.path, "/simplesaml/saml2/idp/SSOService.php")


class SessionEnabledTestCase(TestCase):
    def get_session(self):
        engine = import_module(settings.SESSION_ENGINE)
        session = self.client.session or engine.SessionStore()
        return session

    def set_session_cookies(self, session):
        # Set the cookie to represent the session
        session_cookie = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie] = session.session_key
        cookie_data = {
            "max-age": None,
            "path": "/",
            "domain": settings.SESSION_COOKIE_DOMAIN,
            "secure": settings.SESSION_COOKIE_SECURE or None,
            "expires": None,
        }
        self.client.cookies[session_cookie].update(cookie_data)


class MiddlewareTests(SessionEnabledTestCase):
    def test_middleware_cookie_expireatbrowserclose(self):
        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=True):
            session = self.get_session()
            session.save()
            self.set_session_cookies(session)

            config_loader_path = "djangosaml2.tests.test_config_loader_with_real_conf"
            request = RequestFactory().get("/login/")
            request.user = AnonymousUser()
            request.session = session
            middleware = SamlSessionMiddleware(dummy_get_response)
            middleware.process_request(request)

            saml_session_name = getattr(
                settings, "SAML_SESSION_COOKIE_NAME", "saml_session"
            )
            getattr(request, saml_session_name).save()

            response = views.LoginView.as_view(config_loader_path=config_loader_path)(
                request
            )

            response = middleware.process_response(request, response)

            cookie = response.cookies[saml_session_name]

            self.assertEqual(cookie["expires"], "")
            self.assertEqual(cookie["max-age"], "")

    def test_middleware_cookie_with_expiry(self):
        with override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=False):
            session = self.get_session()
            session.save()
            self.set_session_cookies(session)

            config_loader_path = "djangosaml2.tests.test_config_loader_with_real_conf"
            request = RequestFactory().get("/login/")
            request.user = AnonymousUser()
            request.session = session
            middleware = SamlSessionMiddleware(dummy_get_response)
            middleware.process_request(request)

            saml_session_name = getattr(
                settings, "SAML_SESSION_COOKIE_NAME", "saml_session"
            )
            getattr(request, saml_session_name).save()

            response = views.LoginView.as_view(config_loader_path=config_loader_path)(
                request
            )

            response = middleware.process_response(request, response)

            cookie = response.cookies[saml_session_name]

            self.assertIsNotNone(cookie["expires"])
            self.assertNotEqual(cookie["expires"], "")
            self.assertNotEqual(cookie["max-age"], "")

    def test_middleware_cookie_samesite(self):
        with override_settings(SAML_SESSION_COOKIE_SAMESITE="Lax"):
            session = self.get_session()
            session.save()
            self.set_session_cookies(session)

            config_loader_path = "djangosaml2.tests.test_config_loader_with_real_conf"
            request = RequestFactory().get("/login/")
            request.user = AnonymousUser()
            request.session = session
            middleware = SamlSessionMiddleware(dummy_get_response)
            middleware.process_request(request)

            saml_session_name = getattr(
                settings, "SAML_SESSION_COOKIE_NAME", "saml_session"
            )
            getattr(request, saml_session_name).save()

            response = views.LoginView.as_view(config_loader_path=config_loader_path)(
                request
            )

            response = middleware.process_response(request, response)

            cookie = response.cookies[saml_session_name]

            self.assertEqual(cookie["samesite"], "Lax")
