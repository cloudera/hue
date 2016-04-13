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
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from djangosaml2.signals import pre_user_save

try:
    from django.contrib.auth.models import SiteProfileNotAvailable
except ImportError:
    class SiteProfileNotAvailable(Exception):
        pass


logger = logging.getLogger('djangosaml2')

# Django 1.5 Custom user model
try:
    User = auth.get_user_model()
except AttributeError:
    User = auth.models.User

class Saml2Backend(ModelBackend):

    def authenticate(self, session_info=None, attribute_mapping=None,
                     create_unknown_user=True):
        if session_info is None or attribute_mapping is None:
            logger.error('Session info or attribute mapping are None')
            return None

        if not 'ava' in session_info:
            logger.error('"ava" key not found in session_info')
            return None

        attributes = session_info['ava']
        if not attributes:
            logger.error('The attributes dictionary is empty')

        use_name_id_as_username = getattr(
            settings, 'SAML_USE_NAME_ID_AS_USERNAME', False)

        django_user_main_attribute = getattr(
            settings, 'SAML_DJANGO_USER_MAIN_ATTRIBUTE', 'username')

        logger.debug('attributes: %s' % attributes)
        saml_user = None
        if use_name_id_as_username:
            if 'name_id' in session_info:
                logger.debug('name_id: %s' % session_info['name_id'])
                saml_user = session_info['name_id'].text
            else:
                logger.error('The nameid is not available. Cannot find user without a nameid.')
        else:
            logger.debug('attribute_mapping: %s' % attribute_mapping)
            for saml_attr, django_fields in attribute_mapping.items():
                if (django_user_main_attribute in django_fields
                    and saml_attr in attributes):
                    saml_user = attributes[saml_attr][0]

        if saml_user is None:
            logger.error('Could not find saml_user value')
            return None

        if not self.is_authorized(attributes, attribute_mapping):
            return None

        user = None

        main_attribute = self.clean_user_main_attribute(saml_user)

        user_query_args = {django_user_main_attribute: main_attribute}

        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating unknown users since it has
        # built-in safeguards for multiple threads.
        if create_unknown_user:
            logger.debug('Check if the user "%s" exists or create otherwise'
                         % main_attribute)
            try:
                user, created = User.objects.get_or_create(**user_query_args)
            except MultipleObjectsReturned:
                logger.error("There are more than one user with %s = %s" %
                             (django_user_main_attribute, main_attribute))
                return None

            if created:
                logger.debug('New user created')
                user = self.configure_user(user, attributes, attribute_mapping)
            else:
                logger.debug('User updated')
                user = self.update_user(user, attributes, attribute_mapping)
        else:
            logger.debug('Retrieving existing user "%s"' % main_attribute)
            try:
                user = User.objects.get(**user_query_args)
                user = self.update_user(user, attributes, attribute_mapping)
            except User.DoesNotExist:
                logger.error('The user "%s" does not exist' % main_attribute)
                return None
            except MultipleObjectsReturned:
                logger.error("There are more than one user with %s = %s" %
                             (django_user_main_attribute, main_attribute))
                return None

        return user

    def is_authorized(self, attributes, attribute_mapping):
        """Hook to allow custom authorization policies based on
        SAML attributes.
        """
        return True

    def clean_user_main_attribute(self, main_attribute):
        """Performs any cleaning on the user main attribute (which
        usually is "username") prior to using it to get or
        create the user object.  Returns the cleaned attribute.

        By default, returns the attribute unchanged.
        """
        return main_attribute

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
        that field defined it will be set, otherwise it will try to set
        it in the profile object.
        """
        if not attribute_mapping:
            return user

        try:
            profile = user.get_profile()
        except ObjectDoesNotExist:
            profile = None
        except SiteProfileNotAvailable:
            profile = None
        # Django 1.5 custom model assumed
        except AttributeError:
            profile = user

        user_modified = False
        profile_modified = False
        for saml_attr, django_attrs in attribute_mapping.items():
            try:
                for attr in django_attrs:
                    if hasattr(user, attr):
                        modified = self._set_attribute(
                            user, attr, attributes[saml_attr][0])
                        user_modified = user_modified or modified

                    elif profile is not None and hasattr(profile, attr):
                        modified = self._set_attribute(
                            profile, attr, attributes[saml_attr][0])
                        profile_modified = profile_modified or modified

            except KeyError:
                # the saml attribute is missing
                pass

        logger.debug('Sending the pre_save signal')
        signal_modified = any(
            [response for receiver, response
             in pre_user_save.send_robust(sender=user,
                                          attributes=attributes,
                                          user_modified=user_modified)]
            )

        if user_modified or signal_modified or force_save:
            user.save()

        if (profile is not None
            and (profile_modified or signal_modified or force_save)):
            profile.save()

        return user

    def _set_attribute(self, obj, attr, value):
        """Set an attribute of an object to a specific value.

        Return True if the attribute was changed and False otherwise.
        """
        field = obj._meta.get_field_by_name(attr)
        if len(value) > field[0].max_length:
            cleaned_value = value[:field[0].max_length]
            logger.warn('The attribute "%s" was trimmed from "%s" to "%s"' %
                        (attr, value, cleaned_value))
        else:
            cleaned_value = value

        old_value = getattr(obj, attr)
        if cleaned_value != old_value:
            setattr(obj, attr, cleaned_value)
            return True

        return False
