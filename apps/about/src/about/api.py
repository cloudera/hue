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

from rest_framework import status
from rest_framework.response import Response

from desktop.auth.backend import is_admin
from desktop.lib.conf import coerce_bool
from desktop.models import Settings

LOG = logging.getLogger()


def get_usage_analytics(request) -> Response:
  """
  Retrieve the user preference for analytics settings.

  Args:
    request (Request): The HTTP request object.

  Returns:
    Response: JSON response containing the analytics_enabled preference or an error message.

  Raises:
    403: If the user is not a Hue admin.
    500: If there is an error retrieving preference.
  """
  if not is_admin(request.user):
    return Response({'message': "You must be a Hue admin to access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

  try:
    settings = Settings.get_settings()
    return Response({'analytics_enabled': settings.collect_usage}, status=status.HTTP_200_OK)

  except Exception as e:
    message = f"Error retrieving usage analytics: {e}"
    LOG.error(message)
    return Response({'message': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def update_usage_analytics(request) -> Response:
  """
  Update the user preference for analytics settings.

  Args:
    request (Request): The HTTP request object containing 'analytics_enabled' parameter.

  Returns:
    Response: JSON response with the updated analytics_enabled preference or an error message.

  Raises:
    403: If the user is not a Hue admin.
    400: If 'analytics_enabled' parameter is missing or invalid.
    500: If there is an error updating preference.
  """
  if not is_admin(request.user):
    return Response({'message': "You must be a Hue admin to access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

  try:
    analytics_enabled = request.POST.get('analytics_enabled')

    if analytics_enabled is None:
      return Response({'message': 'Missing parameter: analytics_enabled is required.'}, status=status.HTTP_400_BAD_REQUEST)

    settings = Settings.get_settings()
    settings.collect_usage = coerce_bool(analytics_enabled)
    settings.save()

    return Response({'analytics_enabled': settings.collect_usage}, status=status.HTTP_200_OK)

  except Exception as e:
    message = f"Error updating usage analytics: {e}"
    LOG.error(message)
    return Response({'message': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
