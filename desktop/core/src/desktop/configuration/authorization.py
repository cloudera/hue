#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Authorization for DefaultConfiguration REST endpoints.

Non-admin users may only read and write their own user-specific configuration rows.
Default and group-wide configuration management requires a Hue admin (``is_admin``).
"""

from django.contrib.auth.models import User
from django.utils.translation import gettext as _

from desktop.auth.backend import is_admin
from desktop.lib.exceptions_renderable import PopupException


def require_configuration_admin(user):
  """
  :raises PopupException: When ``user`` is not a Hue admin.
  """
  if not is_admin(user):
    raise PopupException(_("You must be an admin."), error_code=401)


def resolve_target_user(request, user_id):
  """
  Resolve the User record that the caller is allowed to access for per-user configuration.

  Admins may specify any valid user id. Non-admins may only use their own id.

  :param request: Django request with authenticated ``request.user``.
  :param user_id: Raw ``user_id`` from GET/POST (string or int).
  :return: ``User`` instance.
  :raises PopupException: Invalid id, unknown user, or cross-user access without admin rights.
  """
  if user_id is None or str(user_id).strip() == '':
    raise PopupException(_('app_configuration_for_user requires app and user_id'))

  try:
    requested_id = int(user_id)
  except (TypeError, ValueError):
    raise PopupException(_('Invalid user_id.'))

  if is_admin(request.user):
    try:
      return User.objects.get(id=requested_id)
    except User.DoesNotExist:
      raise PopupException(_('Could not find user with User ID: %s') % requested_id)

  if requested_id != request.user.id:
    raise PopupException(
      _('You do not have permission to access configuration for this user.'),
      error_code=403,
    )

  return request.user


def assert_can_delete_configuration(request, config):
  """
  Ensure the caller may delete a ``DefaultConfiguration`` row.

  Default and group configurations require admin. User-specific rows may be deleted by the
  owner or an admin.

  :raises PopupException: When the caller lacks permission.
  """
  if config.is_default or config.groups.exists():
    require_configuration_admin(request.user)
    return

  if config.user_id is not None:
    if config.user_id != request.user.id and not is_admin(request.user):
      raise PopupException(
        _('You do not have permission to delete this configuration.'),
        error_code=403,
      )
    return

  require_configuration_admin(request.user)
