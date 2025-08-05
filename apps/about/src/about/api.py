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
from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from about.serializer import UsageAnalyticsSerializer
from desktop.auth.api_permissions import IsAdminUser
from desktop.models import Settings

LOG = logging.getLogger()


class UsageAnalyticsAPI(APIView):
  """
  Provides GET and PUT handlers for the usage analytics setting.

  This view allows authorized admin users to retrieve the current state of
  the `collect_usage` setting and update it.
  """

  permission_classes = [IsAdminUser]

  def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    """Handles GET requests to retrieve the current analytics setting."""
    try:
      settings = Settings.get_settings()
      data = {"collect_usage": settings.collect_usage}

      return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
      LOG.error("Error retrieving usage analytics: %s", e)
      return Response(
        {"error": "A server error occurred while retrieving usage analytics settings."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
    """Handles PUT requests to update the analytics setting."""
    try:
      serializer = UsageAnalyticsSerializer(data=request.data)
      if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      is_enabled = serializer.validated_data["collect_usage"]

      settings = Settings.get_settings()
      settings.collect_usage = is_enabled
      settings.save()

      return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
      LOG.error("Error updating usage analytics: %s", e)
      return Response(
        {"error": "A server error occurred while saving the usage analytics settings."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )
