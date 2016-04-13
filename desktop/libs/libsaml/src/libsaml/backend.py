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
from desktop.auth.backend import rewrite_user
from libsaml import conf
from libsaml import metrics
from useradmin.models import get_profile, get_default_user_group, UserProfile

LOG = logging.getLogger(__name__)


class SAML2Backend(_Saml2Backend):
  """
  Wrapper around djangosaml2 backend.
  """

  @metrics.saml2_authentication_time
  def authenticate(self, *args, **kwargs):
    return super(SAML2Backend, self).authenticate(*args, **kwargs)


  def update_user(self, user, attributes, attribute_mapping, force_save=False):
    # Do this check up here, because the auth call creates a django user upon first login per user
    is_super = False
    if not UserProfile.objects.filter(creation_method=str(UserProfile.CreationMethod.EXTERNAL)).exists():
      # If there are no LDAP users already in the system, the first one will
      # become a superuser
      is_super = True
    elif User.objects.filter(username=user.username).exists():
      # If the user already exists, we shouldn't change its superuser
      # privileges. However, if there's a naming conflict with a non-external
      # user, we should do the safe thing and turn off superuser privs.
      user = User.objects.get(username=user.username)
      existing_profile = get_profile(user)
      if existing_profile.creation_method == str(UserProfile.CreationMethod.EXTERNAL):
        is_super = user.is_superuser

    user = super(SAML2Backend, self).update_user(user, attributes, attribute_mapping, force_save)

    if user is not None and user.is_active:
      profile = get_profile(user)
      profile.creation_method = UserProfile.CreationMethod.EXTERNAL
      profile.save()
      user.is_superuser = is_super
      user = rewrite_user(user)

      default_group = get_default_user_group()
      if default_group is not None:
        user.groups.add(default_group)
        user.save()

      return user

    return None

  def get_user(self, user_id):
    user = super(SAML2Backend, self).get_user(user_id)
    user = rewrite_user(user)
    return user

  @classmethod
  def manages_passwords_externally(cls):
    return True

  def logout(self, request, next_page=None):
    if conf.LOGOUT_ENABLED.get():
      response = saml_logout(request)
      auth_logout(request)
      return response
    else:
      return None
