# Copyright (C) 2010-2012 Yaco Sistemas (http://www.yaco.es)
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
import warnings
from typing import Any, Optional, Tuple

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, MultipleObjectsReturned

from django.contrib import auth
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger("djangosaml2")


def set_attribute(obj: Any, attr: str, new_value: Any) -> bool:
    """Set an attribute of an object to a specific value, if it wasn't that already.
    Return True if the attribute was changed and False otherwise.
    """
    if not hasattr(obj, attr):
        setattr(obj, attr, new_value)
        return True
    if new_value != getattr(obj, attr):
        setattr(obj, attr, new_value)
        return True
    return False


class Saml2Backend(ModelBackend):

    # ############################################
    # Internal logic, not meant to be overwritten
    # ############################################

    @property
    def _user_model(self):
        """Returns the user model specified in the settings, or the default one from this Django installation"""
        if hasattr(settings, "SAML_USER_MODEL"):
            try:
                return apps.get_model(settings.SAML_USER_MODEL)
            except LookupError:
                raise ImproperlyConfigured(
                    f"Model '{settings.SAML_USER_MODEL}' could not be loaded"
                )
            except ValueError:
                raise ImproperlyConfigured(
                    f"Model was specified as '{settings.SAML_USER_MODEL}', but it must be of the form 'app_label.model_name'"
                )

        return auth.get_user_model()

    @property
    def _user_lookup_attribute(self) -> str:
        """Returns the attribute on which to match the identifier with when performing a user lookup"""
        if hasattr(settings, "SAML_DJANGO_USER_MAIN_ATTRIBUTE"):
            return settings.SAML_DJANGO_USER_MAIN_ATTRIBUTE
        return getattr(self._user_model, "USERNAME_FIELD", "username")

    def _extract_user_identifier_params(
        self, session_info: dict, attributes: dict, attribute_mapping: dict
    ) -> Tuple[str, Optional[Any]]:
        """Returns the attribute to perform a user lookup on, and the value to use for it.
        The value could be the name_id, or any other saml attribute from the request.
        """
        # Lookup key
        user_lookup_key = self._user_lookup_attribute

        # Lookup value
        if getattr(settings, "SAML_USE_NAME_ID_AS_USERNAME", False):
            if session_info.get("name_id"):
                logger.debug(f"name_id: {session_info['name_id']}")
                user_lookup_value = session_info["name_id"].text
            else:
                logger.error(
                    "The nameid is not available. Cannot find user without a nameid."
                )
                user_lookup_value = None
        else:
            # Obtain the value of the custom attribute to use
            user_lookup_value = self._get_attribute_value(
                user_lookup_key, attributes, attribute_mapping
            )

        return user_lookup_key, self.clean_user_main_attribute(user_lookup_value)

    def _get_attribute_value(
        self, django_field: str, attributes: dict, attribute_mapping: dict
    ):
        saml_attribute = None
        logger.debug("attribute_mapping: %s", attribute_mapping)
        for saml_attr, django_fields in attribute_mapping.items():
            if django_field in django_fields and saml_attr in attributes:
                saml_attribute = attributes.get(saml_attr, [None])

        if saml_attribute:
            return saml_attribute[0]
        else:
            logger.error(
                "attributes[saml_attr] attribute value is missing. "
                f"Either the user session is expired or your mapping is invalid.\n"
                f"django_field: {django_field}\n"
                f"attributes: {attributes}\n"
                f"attribute_mapping: {attribute_mapping}"
            )

    def authenticate(
        self,
        request,
        session_info=None,
        attribute_mapping=None,
        create_unknown_user=True,
        assertion_info=None,
        **kwargs,
    ):
        if session_info is None or attribute_mapping is None:
            logger.info("Session info or attribute mapping are None")
            return None

        if "ava" not in session_info:
            logger.error('"ava" key not found in session_info')
            return None

        idp_entityid = session_info["issuer"]

        attributes = self.clean_attributes(session_info["ava"], idp_entityid)

        logger.debug(f"attributes: {attributes}")

        if not self.is_authorized(
            attributes, attribute_mapping, idp_entityid, assertion_info
        ):
            logger.error("Request not authorized")
            return None

        user_lookup_key, user_lookup_value = self._extract_user_identifier_params(
            session_info, attributes, attribute_mapping
        )
        if not user_lookup_value:
            logger.error("Could not determine user identifier")
            return None

        user, created = self.get_or_create_user(
            user_lookup_key,
            user_lookup_value,
            create_unknown_user,
            idp_entityid=idp_entityid,
            attributes=attributes,
            attribute_mapping=attribute_mapping,
            request=request,
        )

        # Update user with new attributes from incoming request
        if user is not None:
            user = self._update_user(
                user, attributes, attribute_mapping, force_save=created
            )

        if self.user_can_authenticate(user):
            return user

    def _update_user(
        self, user, attributes: dict, attribute_mapping: dict, force_save: bool = False
    ):
        """Update a user with a set of attributes and returns the updated user.

        By default it uses a mapping defined in the settings constant
        SAML_ATTRIBUTE_MAPPING. For each attribute, if the user object has
        that field defined it will be set.
        """

        # No attributes to set on the user instance, nothing to update
        if not attribute_mapping:
            # Always save a brand new user instance
            if user.pk is None:
                user = self.save_user(user)
            return user

        # Lookup key
        user_lookup_key = self._user_lookup_attribute
        has_updated_fields = False
        for saml_attr, django_attrs in attribute_mapping.items():
            attr_value_list = attributes.get(saml_attr)
            if not attr_value_list:
                logger.debug(
                    f'Could not find value for "{saml_attr}", not updating fields "{django_attrs}"'
                )
                continue

            for attr in django_attrs:
                if attr == user_lookup_key:
                    # Don't update user_lookup_key (e.g. username) (issue #245)
                    # It was just used to find/create this user and might have
                    # been changed by `clean_user_main_attribute`
                    continue
                elif hasattr(user, attr):
                    user_attr = getattr(user, attr)
                    if callable(user_attr):
                        modified = user_attr(attr_value_list)
                    else:
                        modified = set_attribute(user, attr, attr_value_list[0])

                    has_updated_fields = has_updated_fields or modified
                else:
                    logger.debug(f'Could not find attribute "{attr}" on user "{user}"')

        if has_updated_fields or force_save:
            user = self.save_user(user)

        return user

    # ############################################
    # Hooks to override by end-users in subclasses
    # ############################################

    def clean_attributes(self, attributes: dict, idp_entityid: str, **kwargs) -> dict:
        """Hook to clean or filter attributes from the SAML response. No-op by default."""
        return attributes

    def is_authorized(
        self,
        attributes: dict,
        attribute_mapping: dict,
        idp_entityid: str,
        assertion_info: dict,
        **kwargs,
    ) -> bool:
        """Hook to allow custom authorization policies based on SAML attributes. True by default."""
        return True

    def user_can_authenticate(self, user) -> bool:
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, "is_active", None)
        return is_active or is_active is None

    def clean_user_main_attribute(self, main_attribute: Any) -> Any:
        """Hook to clean the extracted user-identifying value. No-op by default."""
        return main_attribute

    def get_or_create_user(
        self,
        user_lookup_key: str,
        user_lookup_value: Any,
        create_unknown_user: bool,
        idp_entityid: str,
        attributes: dict,
        attribute_mapping: dict,
        request,
    ) -> Tuple[Optional[settings.AUTH_USER_MODEL], bool]:
        """Look up the user to authenticate. If he doesn't exist, this method creates him (if so desired).
        The default implementation looks only at the user_identifier. Override this method in order to do more complex behaviour,
        e.g. customize this per IdP.
        """
        UserModel = self._user_model

        # Construct query parameters to query the userModel with. An additional lookup modifier could be specified in the settings.
        user_query_args = {
            user_lookup_key
            + getattr(
                settings, "SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP", ""
            ): user_lookup_value
        }

        # Lookup existing user
        # Lookup existing user
        user, created = None, False
        try:
            user = UserModel.objects.get(**user_query_args)
        except MultipleObjectsReturned:
            logger.exception(
                f"Multiple users match, model: {UserModel._meta}, lookup: {user_query_args}",
            )
        except UserModel.DoesNotExist:
            # Create new one if desired by settings
            if create_unknown_user:
                user = UserModel(**{user_lookup_key: user_lookup_value})
                user.set_unusable_password()
                created = True
                logger.debug(f"New user created: {user}", exc_info=True)
            else:
                logger.exception(
                    f"The user does not exist, model: {UserModel._meta}, lookup: {user_query_args}"
                )

        return user, created

    def save_user(
        self, user: settings.AUTH_USER_MODEL, *args, **kwargs
    ) -> settings.AUTH_USER_MODEL:
        """Hook to add custom logic around saving a user. Return the saved user instance."""
        is_new_instance = user.pk is None
        user.save()

        if is_new_instance:
            logger.debug("New user created")
        else:
            logger.debug(f"User {user} updated with incoming attributes")

        return user

    # ############################################
    # Backwards-compatibility stubs
    # ############################################

    def get_attribute_value(self, django_field, attributes, attribute_mapping):
        warnings.warn(
            "get_attribute_value() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return self._get_attribute_value(django_field, attributes, attribute_mapping)

    def get_django_user_main_attribute(self):
        warnings.warn(
            "get_django_user_main_attribute() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return self._user_lookup_attribute

    def get_django_user_main_attribute_lookup(self):
        warnings.warn(
            "get_django_user_main_attribute_lookup() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return getattr(settings, "SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP", "")

    def get_user_query_args(self, main_attribute):
        warnings.warn(
            "get_user_query_args() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return {
            self.get_django_user_main_attribute()
            + self.get_django_user_main_attribute_lookup()
        }

    def configure_user(self, user, attributes, attribute_mapping):
        warnings.warn(
            "configure_user() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return self._update_user(user, attributes, attribute_mapping)

    def update_user(self, user, attributes, attribute_mapping, force_save=False):
        warnings.warn(
            "update_user() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return self._update_user(user, attributes, attribute_mapping)

    def _set_attribute(self, obj, attr, value):
        warnings.warn(
            "_set_attribute() is deprecated, look at the Saml2Backend on how to subclass it",
            DeprecationWarning,
        )
        return set_attribute(obj, attr, value)


def get_saml_user_model():
    warnings.warn(
        "_set_attribute() is deprecated, look at the Saml2Backend on how to subclass it",
        DeprecationWarning,
    )
    return Saml2Backend()._user_model
