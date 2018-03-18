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

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import (
    MultipleObjectsReturned, ImproperlyConfigured,
)

from djangosaml2.signals import pre_user_save


logger = logging.getLogger('djangosaml2')


def get_model(model_path):
    try:
        from django.apps import apps
        return apps.get_model(model_path)
    except ImportError:
        # Django < 1.7 (cannot use the new app loader)
        from django.db.models import get_model as django_get_model
        try:
            app_label, model_name = model_path.split('.')
        except ValueError:
            raise ImproperlyConfigured("SAML_USER_MODEL must be of the form "
                "'app_label.model_name'")
        user_model = django_get_model(app_label, model_name)
        if user_model is None:
            raise ImproperlyConfigured("SAML_USER_MODEL refers to model '%s' "
                "that has not been installed" % model_path)
        return user_model


def get_saml_user_model():
    try:
        # djangosaml2 custom user model
        return get_model(settings.SAML_USER_MODEL)
    except AttributeError:
        try:
            # Django 1.5 Custom user model
            return auth.get_user_model()
        except AttributeError:
            return auth.models.User


class Saml2Backend(ModelBackend):

    def authenticate(self, request, session_info=None, attribute_mapping=None,
                     create_unknown_user=True, **kwargs):
        if session_info is None or attribute_mapping is None:
            logger.info('Session info or attribute mapping are None')
            return None

        if 'ava' not in session_info:
            logger.error('"ava" key not found in session_info')
            return None

        attributes = self.clean_attributes(session_info['ava'])
        if not attributes:
            logger.error('The attributes dictionary is empty')

        use_name_id_as_username = getattr(
            settings, 'SAML_USE_NAME_ID_AS_USERNAME', False)

        django_user_main_attribute = self.get_django_user_main_attribute()

        logger.debug('attributes: %s', attributes)
        saml_user = None
        if use_name_id_as_username:
            if 'name_id' in session_info:
                logger.debug('name_id: %s', session_info['name_id'])
                saml_user = session_info['name_id'].text
            else:
                logger.error('The nameid is not available. Cannot find user without a nameid.')
        else:
            saml_user = self.get_attribute_value(django_user_main_attribute, attributes, attribute_mapping)

        if saml_user is None:
            logger.error('Could not find saml_user value')
            return None

        if not self.is_authorized(attributes, attribute_mapping):
            return None

        main_attribute = self.clean_user_main_attribute(saml_user)

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        return self.get_saml2_user(
            create_unknown_user, main_attribute, attributes, attribute_mapping)

    def get_attribute_value(self, django_field, attributes, attribute_mapping):
        saml_user = None
        logger.debug('attribute_mapping: %s', attribute_mapping)
        for saml_attr, django_fields in attribute_mapping.items():
            if django_field in django_fields and saml_attr in attributes:
                saml_user = attributes[saml_attr][0]
        return saml_user

    def is_authorized(self, attributes, attribute_mapping):
        """Hook to allow custom authorization policies based on
        SAML attributes.
        """
        return True

    def clean_attributes(self, attributes):
        """Hook to clean attributes from the SAML response."""
        return attributes

    def clean_user_main_attribute(self, main_attribute):
        """Performs any cleaning on the user main attribute (which
        usually is "username") prior to using it to get or
        create the user object.  Returns the cleaned attribute.

        By default, returns the attribute unchanged.
        """
        return main_attribute

    def get_django_user_main_attribute(self):
        return getattr(
            settings,
            'SAML_DJANGO_USER_MAIN_ATTRIBUTE',
            getattr(get_saml_user_model(), 'USERNAME_FIELD', 'username'))

    def get_django_user_main_attribute_lookup(self):
        return getattr(settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP', '')

    def get_user_query_args(self, main_attribute):
        lookup = (self.get_django_user_main_attribute() +
                  self.get_django_user_main_attribute_lookup())
        return {lookup: main_attribute}

    def get_saml2_user(self, create, main_attribute, attributes, attribute_mapping):
        if create:
            return self._get_or_create_saml2_user(main_attribute, attributes, attribute_mapping)

        return self._get_saml2_user(main_attribute, attributes, attribute_mapping)

    def _get_or_create_saml2_user(self, main_attribute, attributes, attribute_mapping):
        logger.debug('Check if the user "%s" exists or create otherwise',
                     main_attribute)
        django_user_main_attribute = self.get_django_user_main_attribute()
        user_query_args = self.get_user_query_args(main_attribute)
        user_create_defaults = {django_user_main_attribute: main_attribute}

        User = get_saml_user_model()
        try:
            user, created = User.objects.get_or_create(
                defaults=user_create_defaults, **user_query_args)
        except MultipleObjectsReturned:
            logger.error("There are more than one user with %s = %s",
                         django_user_main_attribute, main_attribute)
            return None

        if created:
            logger.debug('New user created')
            user = self.configure_user(user, attributes, attribute_mapping)
        else:
            logger.debug('User updated')
            user = self.update_user(user, attributes, attribute_mapping)
        return user

    def _get_saml2_user(self, main_attribute, attributes, attribute_mapping):
        User = get_saml_user_model()
        django_user_main_attribute = self.get_django_user_main_attribute()
        user_query_args = self.get_user_query_args(main_attribute)

        logger.debug('Retrieving existing user "%s"', main_attribute)
        try:
            user = User.objects.get(**user_query_args)
            user = self.update_user(user, attributes, attribute_mapping)
        except User.DoesNotExist:
            logger.error('The user "%s" does not exist, searched %s', main_attribute, django_user_main_attribute)
            return None
        except MultipleObjectsReturned:
            logger.error("There are more than one user with %s = %s",
                         django_user_main_attribute, main_attribute)
            return None
        return user

    def configure_user(self, user, attributes, attribute_mapping):
        """Configures a user after creation and returns the updated user.

        By default, returns the user with his attributes updated.
        """
        user.set_unusable_password()
        return self.update_user(user, attributes, attribute_mapping,
                                force_save=True)

    def update_user(self, user, attributes, attribute_mapping,
                    force_save=False):
        """Update a user with a set of attributes and returns the updated user.

        By default it uses a mapping defined in the settings constant
        SAML_ATTRIBUTE_MAPPING. For each attribute, if the user object has
        that field defined it will be set.
        """
        if not attribute_mapping:
            return user

        user_modified = False
        for saml_attr, django_attrs in attribute_mapping.items():
            attr_value_list = attributes.get(saml_attr)
            if not attr_value_list:
                logger.debug(
                    'Could not find value for "%s", not updating fields "%s"',
                    saml_attr, django_attrs)
                continue

            for attr in django_attrs:
                if hasattr(user, attr):
                    user_attr = getattr(user, attr)
                    if callable(user_attr):
                        modified = user_attr(attr_value_list)
                    else:
                        modified = self._set_attribute(user, attr, attr_value_list[0])

                    user_modified = user_modified or modified
                else:
                    logger.debug(
                        'Could not find attribute "%s" on user "%s"', attr, user)

        logger.debug('Sending the pre_save signal')
        signal_modified = any(
            [response for receiver, response
             in pre_user_save.send_robust(sender=user.__class__,
                                          instance=user,
                                          attributes=attributes,
                                          user_modified=user_modified)]
            )

        if user_modified or signal_modified or force_save:
            user.save()

        return user

    def _set_attribute(self, obj, attr, value):
        """Set an attribute of an object to a specific value.

        Return True if the attribute was changed and False otherwise.
        """
        field = obj._meta.get_field(attr)
        if field.max_length is not None and len(value) > field.max_length:
            cleaned_value = value[:field.max_length]
            logger.warn('The attribute "%s" was trimmed from "%s" to "%s"',
                        attr, value, cleaned_value)
        else:
            cleaned_value = value

        old_value = getattr(obj, attr)
        if cleaned_value != old_value:
            setattr(obj, attr, cleaned_value)
            return True

        return False
