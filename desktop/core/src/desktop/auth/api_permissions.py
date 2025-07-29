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
import logging
from typing import TYPE_CHECKING

from rest_framework import permissions
from rest_framework.request import Request

from desktop.auth.backend import is_admin

# TYPE_CHECKING is True only during static type checking, avoids circular imports.
if TYPE_CHECKING:
  from rest_framework.views import APIView

LOG = logging.getLogger()


class IsAdminUser(permissions.BasePermission):
  """A DRF permission class that only allows access to admin users."""

  message = "You must be a Hue admin to perform this action."

  def has_permission(self, request: Request, view: "APIView") -> bool:
    """Checks if the request's user is authenticated and is an admin."""

    if not request.user or not request.user.is_authenticated:
      return False

    try:
      return is_admin(request.user)
    except Exception:
      LOG.exception("Permission check failed: Could not validate user %s.", request.user)
      return False
