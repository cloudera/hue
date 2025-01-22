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

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as DjangoUserModel

from djangosaml2.backends import Saml2Backend, get_saml_user_model, set_attribute
from djangosaml2.utils import get_csp_handler
from testprofiles.models import TestUser


class BackendUtilMethodsTests(TestCase):
    def test_set_attribute(self):
        u = TestUser()
        self.assertFalse(hasattr(u, "custom_attribute"))

        # Set attribute initially
        changed = set_attribute(u, "custom_attribute", "value")
        self.assertTrue(changed)
        self.assertEqual(u.custom_attribute, "value")

        # 'Update' to the same value again
        changed_same = set_attribute(u, "custom_attribute", "value")
        self.assertFalse(changed_same)
        self.assertEqual(u.custom_attribute, "value")

        # Update to a different value
        changed_different = set_attribute(u, "custom_attribute", "new_value")
        self.assertTrue(changed_different)
        self.assertEqual(u.custom_attribute, "new_value")


class dummyNameId:
    text = "dummyNameId"


class Saml2BackendTests(TestCase):
    """UnitTests on backend classes"""

    backend_cls = Saml2Backend

    def setUp(self):
        self.backend = self.backend_cls()
        self.user = TestUser.objects.create(username="john")

    def test_get_model_ok(self):
        self.assertEqual(self.backend._user_model, TestUser)

    def test_get_model_nonexisting(self):
        with override_settings(SAML_USER_MODEL="testprofiles.NonExisting"):
            with self.assertRaisesMessage(
                ImproperlyConfigured,
                "Model 'testprofiles.NonExisting' could not be loaded",
            ):
                self.assertEqual(self.backend._user_model, None)

    def test_get_model_invalid_specifier(self):
        with override_settings(
            SAML_USER_MODEL="random_package.specifier.testprofiles.NonExisting"
        ):
            with self.assertRaisesMessage(
                ImproperlyConfigured,
                "Model was specified as 'random_package.specifier.testprofiles.NonExisting', but it must be of the form 'app_label.model_name'",
            ):
                self.assertEqual(self.backend._user_model, None)

    def test_user_model_specified(self):
        with override_settings(AUTH_USER_MODEL="auth.User"):
            with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
                self.assertEqual(self.backend._user_model, TestUser)

    def test_user_model_default(self):
        with override_settings(AUTH_USER_MODEL="auth.User"):
            self.assertEqual(self.backend._user_model, DjangoUserModel)

    def test_user_lookup_attribute_specified(self):
        with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
            with override_settings(SAML_DJANGO_USER_MAIN_ATTRIBUTE="age"):
                self.assertEqual(self.backend._user_lookup_attribute, "age")

    def test_user_lookup_attribute_default(self):
        with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
            self.assertEqual(self.backend._user_lookup_attribute, "username")

    def test_extract_user_identifier_params_use_nameid_present(self):
        with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
            with override_settings(SAML_USE_NAME_ID_AS_USERNAME=True):
                _, lookup_value = self.backend._extract_user_identifier_params(
                    {"name_id": dummyNameId()}, {}, {}
                )
                self.assertEqual(lookup_value, "dummyNameId")

    def test_extract_user_identifier_params_use_nameid_missing(self):
        with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
            with override_settings(SAML_USE_NAME_ID_AS_USERNAME=True):
                _, lookup_value = self.backend._extract_user_identifier_params(
                    {}, {}, {}
                )
                self.assertEqual(lookup_value, None)

    def test_is_authorized(self):
        self.assertTrue(self.backend.is_authorized({}, {}, "", {}))

    def test_clean_attributes(self):
        attributes = {"random": "dummy", "value": 123}
        self.assertEqual(self.backend.clean_attributes(attributes, ""), attributes)

    def test_clean_user_main_attribute(self):
        self.assertEqual(self.backend.clean_user_main_attribute("value"), "value")

    def test_update_user_simple(self):
        u = TestUser(username="johny")
        self.assertIsNone(u.pk)
        u = self.backend._update_user(u, {}, {})
        self.assertIsNotNone(u.pk)

    def test_update_user(self):
        attribute_mapping = {
            "uid": ("username",),
            "mail": ("email",),
            "cn": ("first_name",),
            "sn": ("last_name",),
        }
        attributes = {
            "uid": ("john",),
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": ("Doe",),
        }
        self.backend._update_user(self.user, attributes, attribute_mapping)
        self.assertEqual(self.user.email, "john@example.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")

        attribute_mapping["saml_age"] = ("age",)
        attributes["saml_age"] = ("22",)
        self.backend._update_user(self.user, attributes, attribute_mapping)
        self.assertEqual(self.user.age, "22")

    def test_update_user_callable_attributes(self):
        attribute_mapping = {
            "uid": ("username",),
            "mail": ("email",),
            "cn": ("process_first_name",),
            "sn": ("last_name",),
        }
        attributes = {
            "uid": ("john",),
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": ("Doe",),
        }
        self.backend._update_user(self.user, attributes, attribute_mapping)
        self.assertEqual(self.user.email, "john@example.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")

    def test_update_user_empty_attribute(self):
        self.user.last_name = "Smith"
        self.user.save()

        attribute_mapping = {
            "uid": ("username",),
            "mail": ("email",),
            "cn": ("first_name",),
            "sn": ("last_name",),
        }
        attributes = {
            "uid": ("john",),
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": (),
        }
        with self.assertLogs("djangosaml2", level="DEBUG") as logs:
            self.backend._update_user(self.user, attributes, attribute_mapping)
        self.assertEqual(self.user.email, "john@example.com")
        self.assertEqual(self.user.first_name, "John")
        # empty attribute list: no update
        self.assertEqual(self.user.last_name, "Smith")
        self.assertIn(
            'DEBUG:djangosaml2:Could not find value for "sn", not updating fields "(\'last_name\',)"',
            logs.output,
        )

    def test_invalid_model_attribute_log(self):
        attribute_mapping = {
            "uid": ["username"],
            "cn": ["nonexistent"],
        }
        attributes = {
            "uid": ["john"],
            "cn": ["John"],
        }

        with self.assertLogs("djangosaml2", level="DEBUG") as logs:
            user, _ = self.backend.get_or_create_user(
                self.backend._user_lookup_attribute,
                "john",
                True,
                None,
                None,
                None,
                None,
            )
            self.backend._update_user(user, attributes, attribute_mapping)

        self.assertIn(
            'DEBUG:djangosaml2:Could not find attribute "nonexistent" on user "john"',
            logs.output,
        )

    @override_settings(SAML_USER_MODEL="testprofiles.RequiredFieldUser")
    def test_create_user_with_required_fields(self):
        attribute_mapping = {"mail": ["email"], "mail_verified": ["email_verified"]}
        attributes = {
            "mail": ["john@example.org"],
            "mail_verified": [True],
        }
        # User creation does not fail if several fields are required.
        user, created = self.backend.get_or_create_user(
            self.backend._user_lookup_attribute,
            "john@example.org",
            True,
            None,
            None,
            None,
            None,
        )

        self.assertEqual(user.email, "john@example.org")
        self.assertIs(user.email_verified, None)

        user = self.backend._update_user(user, attributes, attribute_mapping, created)
        self.assertIs(user.email_verified, True)

    def test_django_user_main_attribute(self):
        old_username_field = get_user_model().USERNAME_FIELD
        get_user_model().USERNAME_FIELD = "slug"
        self.assertEqual(self.backend._user_lookup_attribute, "slug")
        get_user_model().USERNAME_FIELD = old_username_field

        with override_settings(AUTH_USER_MODEL="auth.User"):
            self.assertEqual(
                DjangoUserModel.USERNAME_FIELD, self.backend._user_lookup_attribute
            )

        with override_settings(AUTH_USER_MODEL="testprofiles.StandaloneUserModel"):
            self.assertEqual(self.backend._user_lookup_attribute, "username")

        with override_settings(SAML_DJANGO_USER_MAIN_ATTRIBUTE="foo"):
            self.assertEqual(self.backend._user_lookup_attribute, "foo")

    def test_get_or_create_user_existing(self):
        with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
            user, created = self.backend.get_or_create_user(
                self.backend._user_lookup_attribute,
                "john",
                False,
                None,
                None,
                None,
                None,
            )

        self.assertTrue(isinstance(user, TestUser))
        self.assertFalse(created)

    def test_get_or_create_user_duplicates(self):
        TestUser.objects.create(username="paul")

        with self.assertLogs("djangosaml2", level="DEBUG") as logs:
            with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
                user, created = self.backend.get_or_create_user(
                    "age", "", False, None, None, None, None
                )

        self.assertTrue(user is None)
        self.assertFalse(created)
        self.assertIn(
            "ERROR:djangosaml2:Multiple users match, model: testprofiles.testuser, lookup: {'age': ''}",
            logs.output[0],
        )

    def test_get_or_create_user_no_create(self):
        with self.assertLogs("djangosaml2", level="DEBUG") as logs:
            with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
                user, created = self.backend.get_or_create_user(
                    self.backend._user_lookup_attribute,
                    "paul",
                    False,
                    None,
                    None,
                    None,
                    None,
                )

        self.assertTrue(user is None)
        self.assertFalse(created)
        self.assertIn(
            "ERROR:djangosaml2:The user does not exist, model: testprofiles.testuser, lookup: {'username': 'paul'}",
            logs.output[0],
        )

    def test_get_or_create_user_create(self):
        with self.assertLogs("djangosaml2", level="DEBUG") as logs:
            with override_settings(SAML_USER_MODEL="testprofiles.TestUser"):
                user, created = self.backend.get_or_create_user(
                    self.backend._user_lookup_attribute,
                    "paul",
                    True,
                    None,
                    None,
                    None,
                    None,
                )

        self.assertTrue(isinstance(user, TestUser))
        self.assertTrue(created)
        self.assertIn(
            f"DEBUG:djangosaml2:New user created: {user}",
            logs.output[0],
        )

    def test_deprecations(self):
        attribute_mapping = {"mail": ["email"], "mail_verified": ["email_verified"]}
        attributes = {
            "mail": ["john@example.org"],
            "mail_verified": [True],
        }

        old = self.backend.get_attribute_value(
            "email_verified", attributes, attribute_mapping
        )
        self.assertEqual(old, True)

        self.assertEqual(
            self.backend.get_django_user_main_attribute(),
            self.backend._user_lookup_attribute,
        )

        with override_settings(SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP="user_name"):
            self.assertEqual(
                self.backend.get_django_user_main_attribute_lookup(),
                settings.SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP,
            )

        self.assertEqual(self.backend.get_user_query_args(""), {"username"})

        u = TestUser(username="mathieu")
        self.assertEqual(u.email, "")
        new_u = self.backend.configure_user(u, attributes, attribute_mapping)
        self.assertIsNotNone(new_u.pk)
        self.assertEqual(new_u.email, "john@example.org")

        u = TestUser(username="mathieu_2")
        self.assertEqual(u.email, "")
        new_u = self.backend.update_user(u, attributes, attribute_mapping)
        self.assertIsNotNone(new_u.pk)
        self.assertEqual(new_u.email, "john@example.org")

        u = TestUser()
        self.assertTrue(self.backend._set_attribute(u, "new_attribute", True))
        self.assertFalse(self.backend._set_attribute(u, "new_attribute", True))
        self.assertTrue(self.backend._set_attribute(u, "new_attribute", False))

        self.assertEqual(get_saml_user_model(), TestUser)


class CustomizedBackend(Saml2Backend):
    """Override the available methods with some customized implementation to test customization"""

    def is_authorized(
        self, attributes, attribute_mapping, idp_entityid: str, assertion_info, **kwargs
    ):
        """Allow only staff users from the IDP"""
        return (
            attributes.get("is_staff", (None,))[0] == True
            and assertion_info.get("assertion_id", None) != None
        )

    def clean_attributes(self, attributes: dict, idp_entityid: str, **kwargs) -> dict:
        """Keep only certain attribute"""
        return {
            "age": attributes.get("age", (None,)),
            "mail": attributes.get("mail", (None,)),
            "is_staff": attributes.get("is_staff", (None,)),
            "uid": attributes.get("uid", (None,)),
        }

    def clean_user_main_attribute(self, main_attribute):
        """Partition string on @ and return the first part"""
        if main_attribute:
            return main_attribute.partition("@")[0]
        return main_attribute


class CustomizedSaml2BackendTests(Saml2BackendTests):
    backend_cls = CustomizedBackend

    def test_is_authorized(self):
        attribute_mapping = {
            "uid": ("username",),
            "mail": ("email",),
            "cn": ("first_name",),
            "sn": ("last_name",),
        }
        attributes = {
            "uid": ("john",),
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": ("Doe",),
        }
        assertion_info = {
            "assertion_id": None,
            "not_on_or_after": None,
        }
        self.assertFalse(
            self.backend.is_authorized(
                attributes, attribute_mapping, "", assertion_info
            )
        )
        attributes["is_staff"] = (True,)
        self.assertFalse(
            self.backend.is_authorized(
                attributes, attribute_mapping, "", assertion_info
            )
        )
        assertion_info["assertion_id"] = "abcdefg12345"
        self.assertTrue(
            self.backend.is_authorized(
                attributes, attribute_mapping, "", assertion_info
            )
        )

    def test_clean_attributes(self):
        attributes = {"random": "dummy", "value": 123, "age": "28"}
        self.assertEqual(
            self.backend.clean_attributes(attributes, ""),
            {"age": "28", "mail": (None,), "is_staff": (None,), "uid": (None,)},
        )

    def test_clean_user_main_attribute(self):
        self.assertEqual(
            self.backend.clean_user_main_attribute("john@example.com"), "john"
        )

    def test_authenticate(self):
        attribute_mapping = {
            "uid": ("username",),
            "mail": ("email",),
            "cn": ("first_name",),
            "sn": ("last_name",),
            "age": ("age",),
            "is_staff": ("is_staff",),
        }
        attributes = {
            "uid": ("john",),
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": ("Doe",),
            "age": ("28",),
            "is_staff": (True,),
        }
        assertion_info = {
            "assertion_id": "abcdefg12345",
            "not_on_or_after": "",
        }

        self.assertEqual(self.user.age, "")
        self.assertEqual(self.user.is_staff, False)

        user = self.backend.authenticate(None)
        self.assertIsNone(user)

        user = self.backend.authenticate(
            None,
            session_info={"random": "content"},
            attribute_mapping=attribute_mapping,
            assertion_info=assertion_info,
        )
        self.assertIsNone(user)

        with override_settings(SAML_USE_NAME_ID_AS_USERNAME=True):
            user = self.backend.authenticate(
                None,
                session_info={"ava": attributes, "issuer": "dummy_entity_id"},
                attribute_mapping=attribute_mapping,
                assertion_info=assertion_info,
            )
            self.assertIsNone(user)

        attributes["is_staff"] = (False,)
        user = self.backend.authenticate(
            None,
            session_info={"ava": attributes, "issuer": "dummy_entity_id"},
            attribute_mapping=attribute_mapping,
            assertion_info=assertion_info,
        )
        self.assertIsNone(user)

        attributes["is_staff"] = (True,)
        user = self.backend.authenticate(
            None,
            session_info={"ava": attributes, "issuer": "dummy_entity_id"},
            attribute_mapping=attribute_mapping,
            assertion_info=assertion_info,
        )

        self.assertEqual(user, self.user)

        self.user.refresh_from_db()
        self.assertEqual(self.user.age, "28")
        self.assertEqual(self.user.is_staff, True)

    def test_user_cleaned_main_attribute(self):
        """
        In this test the username is taken from the `mail` attribute,
        but cleaned to remove the @domain part. After fetching and
        updating the user, the username remains the same.
        """
        attribute_mapping = {
            "mail": ("username",),
            "cn": ("first_name",),
            "sn": ("last_name",),
            "is_staff": ("is_staff",),
        }
        attributes = {
            "mail": ("john@example.com",),
            "cn": ("John",),
            "sn": ("Doe",),
            "is_staff": (True,),
        }
        assertion_info = {
            "assertion_id": "abcdefg12345",
        }
        user = self.backend.authenticate(
            None,
            session_info={"ava": attributes, "issuer": "dummy_entity_id"},
            attribute_mapping=attribute_mapping,
            assertion_info=assertion_info,
        )
        self.assertEqual(user, self.user)

        self.user.refresh_from_db()
        self.assertEqual(user.username, "john")


class CSPHandlerTests(TestCase):
    def test_get_csp_handler_none(self):
        get_csp_handler.cache_clear()
        with override_settings(SAML_CSP_HANDLER=None):
            csp_handler = get_csp_handler()
            self.assertIn(
                csp_handler.__module__, ["csp.decorators", "djangosaml2.utils"]
            )
            self.assertIn(csp_handler.__name__, ["decorator", "empty_view_decorator"])

    def test_get_csp_handler_empty(self):
        get_csp_handler.cache_clear()
        with override_settings(SAML_CSP_HANDLER=""):
            csp_handler = get_csp_handler()
            self.assertEqual(csp_handler.__name__, "empty_view_decorator")

    def test_get_csp_handler_specified(self):
        get_csp_handler.cache_clear()
        with override_settings(SAML_CSP_HANDLER="testprofiles.utils.csp_handler"):
            client = Client()
            response = client.get(reverse("saml2_login"))
            self.assertIn("Content-Security-Policy", response.headers)
            self.assertEqual(
                response.headers["Content-Security-Policy"], "testing CSP value"
            )

    def test_get_csp_handler_specified_missing(self):
        get_csp_handler.cache_clear()
        with override_settings(SAML_CSP_HANDLER="does.not.exist"):
            with self.assertRaises(ImportError):
                get_csp_handler()
