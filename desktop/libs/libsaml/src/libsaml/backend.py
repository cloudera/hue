#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
See desktop/auth/backend.py
"""

from __future__ import absolute_import

import logging

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from djangosaml2.backends import Saml2Backend as _Saml2Backend
from djangosaml2.views import logout as saml_logout

from desktop.auth.backend import force_username_case, rewrite_user
from desktop.conf import AUTH

from libsaml import conf
from libsaml import metrics

from useradmin.models import get_profile, get_default_user_group, UserProfile

LOG = logging.getLogger(__name__)


class SAML2Backend(_Saml2Backend):
  """
  Wrapper around djangosaml2 backend.
  """

  @classmethod
  def manages_passwords_externally(cls):
    return True


  @metrics.saml2_authentication_time
  def authenticate(self, *args, **kwargs):
    return super(SAML2Backend, self).authenticate(*args, **kwargs)


  def clean_user_main_attribute(self, main_attribute):
    """
    Overrides the clean_user_main_attribute method to force case if needed
    """
    return force_username_case(main_attribute)


  def get_user(self, user_id):
    if isinstance(user_id, str):
      user_id = force_username_case(user_id)
    user = super(SAML2Backend, self).get_user(user_id)
    user = rewrite_user(user)
    return user


  def update_user(self, user, attributes, attribute_mapping, force_save=False):
    # Do this check up here, because the auth call creates a django user upon first login per user
    is_super = False
    if not UserProfile.objects.filter(creation_method=UserProfile.CreationMethod.EXTERNAL.name).exists():
      # If there are no LDAP users already in the system, the first one will
      # become a superuser
      is_super = True
    else:
      user = self._get_user_by_username(user.username)
      if user is not None:
        # If the user already exists, we shouldn't change its superuser
        # privileges. However, if there's a naming conflict with a non-external
        # user, we should do the safe thing and turn off superuser privs.
        existing_profile = get_profile(user)
        if existing_profile.creation_method == UserProfile.CreationMethod.EXTERNAL.name:
          is_super = user.is_superuser

    user = super(SAML2Backend, self).update_user(user, attributes, attribute_mapping, force_save)

    if user is not None and user.is_active:
      user.username = force_username_case(user.username)
      profile = get_profile(user)
      profile.creation_method = UserProfile.CreationMethod.EXTERNAL.name
      profile.save()
      user.is_superuser = is_super
      user = rewrite_user(user)

      default_group = get_default_user_group()
      if default_group is not None:
        user.groups.add(default_group)
        user.save()

      return user

    return None


  def logout(self, request, next_page=None):
    if conf.LOGOUT_ENABLED.get():
      response = saml_logout(request)
      auth_logout(request)
      return response
    else:
      return None


  def _get_user_by_username(self, username):
    try:
      if AUTH.IGNORE_USERNAME_CASE.get():
        user = User.objects.get(username__iexact=username)
      else:
        user = User.objects.get(username=username)
    except User.DoesNotExist, e:
      user = None
    return user
