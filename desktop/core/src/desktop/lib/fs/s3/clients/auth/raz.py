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
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import boto3
from botocore import UNSIGNED
from botocore.awsrequest import AWSRequest
from botocore.httpchecksum import AwsChunkedWrapper

from desktop.lib.fs.s3.clients.base import S3AuthProvider
from desktop.lib.raz.clients import S3RazClient

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class RazEventHandler:
  """
  Handles RAZ (Ranger Authorization Service) integration with boto3's event system.

  This handler intercepts boto3 requests before they are signed and applies
  RAZ-signed headers for authenticated access to S3-compatible storage systems.

  Key features:
  - Handles both streaming and non-streaming uploads
  - Properly extracts and preserves query parameters (including empty ones)
  - Supports both AWS virtual-hosted style URLs and generic S3 path-style URLs
  - Integrates with boto3's UNSIGNED signer to let RAZ handle all signing
  """

  def __init__(self, user: str, connector_config: "ConnectorConfig"):
    """
    Initialize RAZ event handler.

    Args:
      user: Username for RAZ authentication
      connector_config: S3 connector configuration containing provider and endpoint details
    """
    self.user = user
    self.connector_config = connector_config
    self.raz_client = S3RazClient(username=user)

  def _handle_choose_signer(self, **kwargs):
    """
    Handle choose-signer boto3 event.

    Instructs boto3 to use the UNSIGNED signer, allowing RAZ to handle
    all request signing via the before-sign event handler.

    Returns:
      UNSIGNED: boto3 signer constant indicating no signing should be performed
    """
    LOG.debug("Using UNSIGNED signer - RAZ will handle request signing")
    return UNSIGNED

  def _handle_before_sign(self, request: AWSRequest, **kwargs) -> None:
    """
    Handle before-sign boto3 event.

    This is the core RAZ integration method that:
    1. Detects streaming vs non-streaming uploads and handles them appropriately
    2. Extracts query parameters from URLs (preserving empty values)
    3. Calls RAZ to get signed headers for the clean URL and parameters
    4. Applies RAZ headers to the request and synchronizes URLs for AWS

    Args:
      request: The boto3 AWSRequest to be signed by RAZ
      **kwargs: Additional boto3 event arguments (unused)

    Raises:
      Exception: If RAZ returns no headers or other signing failures occur
    """
    try:
      # Get request details
      method = request.method
      headers = dict(request.headers)
      data = request.body

      # Detect streaming uploads by checking for boto3's AwsChunkedWrapper
      if isinstance(data, AwsChunkedWrapper):
        # For streaming uploads, boto3 uses a special SHA256 value that RAZ must sign for
        LOG.debug("Detected streaming upload - using STREAMING-UNSIGNED-PAYLOAD-TRAILER")

        headers["x-amz-content-sha256"] = "STREAMING-UNSIGNED-PAYLOAD-TRAILER"
        data_for_raz = b""  # Empty data for signing purposes
      else:
        # For non-streaming requests, use the actual data
        data_for_raz = data

      # Get provider-appropriate URL format and extract query parameters
      base_url = self._get_request_url(request)
      parsed_url = urlparse(base_url)
      clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))

      # Extract query parameters for separate RAZ handling
      params = {}
      if parsed_url.query:
        # CRITICAL: keep_blank_values=True preserves empty parameters like prefix=
        parsed_params = parse_qs(parsed_url.query, keep_blank_values=True)
        params = {key: values[0] if values else "" for key, values in parsed_params.items()}

      # Get signed headers from RAZ
      raz_headers = self.raz_client.get_url(action=method, path=clean_url, params=params, headers=headers, data=data_for_raz)

      if not raz_headers:
        raise Exception("RAZ returned no signed headers")

      # Apply all RAZ headers to the request
      for header_name, header_value in raz_headers.items():
        request.headers[header_name] = header_value

      # Synchronize request URL with RAZ-signed URL for AWS providers
      if self.connector_config.provider.lower() == "aws":
        original_url = request.url
        parsed_original = urlparse(original_url)
        parsed_clean = urlparse(clean_url)

        # Use RAZ's clean URL but preserve original query parameters
        final_url = urlunparse(
          (
            parsed_clean.scheme,
            parsed_clean.netloc,
            parsed_clean.path,
            parsed_original.params,
            parsed_original.query,
            parsed_original.fragment,
          )
        )

        request.url = final_url
        LOG.debug(f"Synchronized request URL with RAZ signature: {original_url} → {final_url}")

      LOG.info(f"RAZ authentication applied for {method} {clean_url}")

    except Exception as e:
      LOG.error(f"RAZ authentication failed: {e}")
      raise

  def _get_request_url(self, request: AWSRequest) -> str:
    """
    Get request URL in RAZ-compatible format based on provider type.

    AWS providers require virtual-hosted style URLs without explicit port 443,
    while generic S3-compatible providers use their original endpoint format.

    Args:
      request: The boto3 AWSRequest to process

    Returns:
      str: URL formatted appropriately for the provider type
    """
    provider = self.connector_config.provider.lower()

    if provider == "aws":
      return self._get_aws_virtual_hosted_url(request)
    else:
      return self._get_generic_provider_url(request)

  def _get_aws_virtual_hosted_url(self, request: AWSRequest) -> str:
    """
    Convert AWS URLs to virtual-hosted style format.

    AWS S3 virtual-hosted style uses bucket.s3.region.amazonaws.com format
    and must not include explicit :443 port to ensure Host header consistency
    with RAZ expectations.

    Args:
      request: The boto3 AWSRequest to convert

    Returns:
      str: Virtual-hosted style URL for AWS S3
    """
    url_parts = list(urlparse(request.url))

    # Extract bucket and key from path
    path = url_parts[2].lstrip("/")
    path_parts = path.split("/", 1) if path else ["", ""]
    bucket_name = path_parts[0] if path_parts[0] else None
    key_path = path_parts[1] if len(path_parts) > 1 else ""

    # Convert to virtual-hosted style URL for AWS
    if bucket_name:
      region = self.connector_config.region or "us-east-1"

      # Build virtual-hosted hostname without explicit port
      if "s3." in url_parts[1]:
        # Regional endpoint: s3.us-west-2.amazonaws.com
        virtual_host = f"{bucket_name}.{url_parts[1]}"
      else:
        # Standard endpoint: s3.amazonaws.com
        virtual_host = f"{bucket_name}.s3.{region}.amazonaws.com"

      # Set virtual-hosted URL components
      url_parts[1] = virtual_host
      url_parts[2] = f"/{key_path}" if key_path else "/"

    # Add query parameters if present
    if request.params:
      query = urlencode(request.params)
      url_parts[4] = query

    final_url = urlunparse(url_parts)
    return final_url

  def _get_generic_provider_url(self, request: AWSRequest) -> str:
    """
    Get URL for generic S3-compatible providers.

    Preserves the original endpoint format and adds explicit port
    if configured in the connector endpoint. This ensures compatibility
    with various S3-compatible storage systems (MinIO, NetApp, Dell, etc.).

    Args:
      request: The boto3 AWSRequest to process

    Returns:
      str: URL formatted for the generic S3 provider
    """
    url_parts = list(urlparse(request.url))

    # Add port from connector endpoint if specified and not already present
    if self.connector_config.endpoint:
      endpoint_parts = urlparse(self.connector_config.endpoint)
      if endpoint_parts.port and ":" not in url_parts[1]:
        url_parts[1] = f"{url_parts[1]}:{endpoint_parts.port}"

    # Add query parameters if present
    if request.params:
      query = urlencode(request.params)
      url_parts[4] = query

    return urlunparse(url_parts)


class RazAuthProvider(S3AuthProvider):
  """
  Authentication provider that integrates with Ranger Authorization Service (RAZ).

  This provider uses boto3's event system to intercept requests before they are
  signed and applies RAZ-generated authentication headers. It works by:
  1. Registering event handlers with boto3's event system
  2. Using UNSIGNED signer to prevent boto3 from signing requests
  3. Intercepting requests in the before-sign event to apply RAZ headers
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    """
    Initialize RAZ authentication provider.

    Args:
      connector_config: S3 connector configuration
      user: Username for RAZ authentication
    """
    super().__init__(connector_config, user)

    # Create RAZ event handler with connector config for provider-aware URL formatting
    self.raz_event_handler = RazEventHandler(user=user, connector_config=connector_config)

    # Create boto3 session and register RAZ event handlers
    self.session = boto3.Session(region_name=connector_config.region)
    self.session.events.register("choose-signer.*.*", self.raz_event_handler._handle_choose_signer)
    self.session.events.register("before-sign.*.*", self.raz_event_handler._handle_before_sign)

    LOG.info(f"RAZ authentication provider initialized for user: {user}")

  def get_credentials(self) -> Dict[str, Any]:
    """
    Return empty credentials dict.

    RAZ authentication doesn't use traditional AWS credentials.
    Instead, authentication is handled through RAZ event handlers
    using the UNSIGNED signer pattern.

    Returns:
      dict: Empty dict since credentials are handled by RAZ events
    """
    return {}

  def get_session_kwargs(self) -> Dict[str, Any]:
    """
    Get kwargs for creating boto3 session.

    Returns minimal kwargs since RAZ handles authentication
    through event handlers rather than session credentials.

    Returns:
      dict: Session kwargs with region name
    """
    return {"region_name": self.connector_config.region}

  def get_session(self):
    """
    Return the pre-configured session with RAZ event handlers.

    This session has RAZ event handlers registered and should be used
    directly rather than creating a new session, as the event handlers
    are essential for RAZ authentication to work.

    Returns:
      Session: The boto3 session with RAZ event handlers registered
    """
    return self.session

  def refresh(self) -> None:
    """
    Refresh credentials (no-op for RAZ).

    RAZ authentication is performed per-request through event handlers,
    so no credential refresh is needed.
    """
    pass
