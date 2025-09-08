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
from typing import Any, Dict, TYPE_CHECKING
from urllib.parse import urlencode, urlparse, urlunparse

import boto3
from botocore.awsrequest import AWSRequest

from desktop.lib.fs.s3.clients.base import S3AuthProvider
from desktop.lib.raz.clients import S3RazClient

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class RazEventHandler:
  """
  Handles RAZ integration with boto3's event system.
  Intercepts requests before they're signed and sent to S3.
  """

  def __init__(self, user: str):
    self.user = user
    # Use existing S3RazClient which has the correct get_url() interface
    self.raz_client = S3RazClient(username=user)

  def _handle_before_sign(self, request: AWSRequest, **kwargs) -> None:
    """
    Handle before-sign event.
    This is called before boto3 would normally sign the request.
    We intercept here to get RAZ to sign instead.
    """
    try:
      # Get request details
      url = self._get_request_url(request)
      method = request.method
      headers = dict(request.headers)
      data = request.body

      # Get RAZ signed headers
      raz_headers = self.raz_client.get_url(action=method, url=url, headers=headers, data=data)

      if not raz_headers:
        raise Exception("RAZ returned no signed headers")

      # Update request headers with RAZ signed headers
      request.headers.update(raz_headers)

      # Mark request as pre-signed to skip boto3 signing
      request.context["pre_signed"] = True

    except Exception as e:
      LOG.error(f"Failed to sign request with RAZ: {e}")
      raise

  def _handle_before_send(self, request: AWSRequest, **kwargs) -> None:
    """
    Handle before-send event.
    This is called after signing but before sending.
    We clean up any leftover AWS headers here.
    """
    # TODO: Is this needed?
    # Remove any AWS specific headers that RAZ doesn't need
    aws_headers = ["X-Amz-Security-Token", "X-Amz-Date", "X-Amz-Content-SHA256", "Authorization"]

    for header in aws_headers:
      request.headers.pop(header, None)

  def _get_request_url(self, request: AWSRequest) -> str:
    """
    Get full request URL including query parameters.
    Handles virtual hosted and path style URLs.
    """
    url_parts = list(urlparse(request.url))

    # Add query parameters
    if request.params:
      query = urlencode(request.params)
      url_parts[4] = query

    # Handle virtual hosted style URLs
    if "s3." in url_parts[1] and request.context.get("bucket_name"):
      bucket = request.context["bucket_name"]
      url_parts[1] = f"{bucket}.{url_parts[1]}"
      # Remove bucket from path
      url_parts[2] = url_parts[2].replace(f"/{bucket}", "", 1)

    return urlunparse(url_parts)


class RazAuthProvider(S3AuthProvider):
  """
  Authentication provider using RAZ for request signing.
  Uses boto3's event system to intercept and sign requests.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    super().__init__(connector_config, user)

    # Create RAZ event handler (uses global RAZ configuration internally)
    self.raz_event_handler = RazEventHandler(user=user)

    # Store boto3 session with RAZ event handlers
    self.session = boto3.Session(aws_access_key_id="dummy", aws_secret_access_key="dummy", region_name=connector_config.region)

    # Register RAZ handlers with the session's event system
    self.session.events.register("before-sign.*.*", self.raz_event_handler._handle_before_sign)

  def get_credentials(self) -> Dict[str, Any]:
    """
    Return dummy credentials.
    Real signing is done via event handlers.
    """
    return {"access_key_id": "dummy", "secret_access_key": "dummy"}

  def get_session_kwargs(self) -> Dict[str, Any]:
    """
    Get kwargs for creating boto3 session.
    Returns pre-configured session with RAZ event handlers.
    """
    return {"aws_access_key_id": "dummy", "aws_secret_access_key": "dummy", "region_name": self.connector_config.region}

  def refresh(self) -> None:
    """No refresh needed as we sign per-request"""
    pass
