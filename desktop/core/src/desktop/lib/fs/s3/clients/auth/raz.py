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
from botocore import UNSIGNED
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

  def __init__(self, user: str, connector_config: "ConnectorConfig"):
    self.user = user
    self.connector_config = connector_config
    # Use existing S3RazClient which has the correct get_url() interface
    self.raz_client = S3RazClient(username=user)

  def _handle_choose_signer(self, **kwargs):
    """
    Handle choose-signer event.
    Tell boto3 to use no signer - RAZ handles all signing.
    """

    LOG.debug("choose-signer: Using UNSIGNED (RAZ will handle signing)")
    return UNSIGNED

  def _handle_before_sign(self, request: AWSRequest, **kwargs) -> None:
    """
    Handle before-sign event.
    Since we use UNSIGNED, this adds RAZ headers to the unsigned request.
    """
    try:
      # ORIGINAL REQUEST DEBUG
      LOG.debug("=== ORIGINAL REQUEST DEBUG ===")
      LOG.debug(f"Original Method: {request.method}")
      LOG.debug(f"Original URL: {request.url}")
      LOG.debug(f"Original Host: {request.headers.get('Host', 'MISSING')}")
      LOG.debug(f"Original User-Agent: {request.headers.get('User-Agent', 'MISSING')[:100]}...")
      LOG.debug("===============================")

      # Get request details
      method = request.method
      headers = dict(request.headers)
      data = request.body

      # CRITICAL FIX: Send clean URL and extract query params separately for RAZ
      # RAZ expects params in protobuf format, not embedded in URL
      base_url = self._get_request_url(request)

      # Extract query parameters from URL for separate RAZ handling
      parsed_url = urlparse(base_url)
      clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))

      # Parse query parameters to send separately to RAZ
      params = {}
      if parsed_url.query:
        from urllib.parse import parse_qs

        parsed_params = parse_qs(parsed_url.query)
        # Convert to flat dict (RAZ expects single values, not lists)
        params = {key: values[0] if values else "" for key, values in parsed_params.items()}

      LOG.debug(f"Original URL with params: {base_url}")
      LOG.debug(f"Clean URL for RAZ: {clean_url}")
      LOG.debug(f"Extracted params for RAZ: {params}")

      # Get RAZ signed headers with clean URL and separate params
      LOG.debug(f"RAZ Call: action={method}, path={clean_url}, params={params}, headers={headers}, data={data}")
      raz_headers = self.raz_client.get_url(action=method, path=clean_url, params=params, headers=headers, data=data)

      if not raz_headers:
        raise Exception("RAZ returned no signed headers")

      # Apply ALL headers from RAZ - they're all required for signature verification
      LOG.debug(f"RAZ returned headers: {list(raz_headers.keys())}")
      LOG.debug("Applying ALL RAZ headers (all are required for signature)")

      for header_name, header_value in raz_headers.items():
        request.headers[header_name] = header_value
        LOG.debug(f"Applied RAZ header: {header_name} = {header_value[:50]}...")

      # CRITICAL: Update request URL to match what RAZ signed for
      if self.connector_config.provider.lower() == "aws":
        # For AWS, boto3 request URL must match the virtual-hosted URL that RAZ signed
        original_url = request.url

        # Build the clean URL but preserve query parameters from original request
        parsed_original = urlparse(original_url)
        parsed_clean = urlparse(clean_url)

        # Use RAZ's virtual-hosted URL but keep original query parameters
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
        LOG.debug(f"Updated request URL to match RAZ signature: {original_url} → {final_url}")

      # CRITICAL DEBUG: Log exact signature components
      LOG.debug("=== SIGNATURE DEBUG ===")
      LOG.debug(f"Method: {request.method}")
      LOG.debug(f"Final URL: {request.url}")
      LOG.debug(f"Host header: {request.headers.get('Host', 'MISSING')}")
      LOG.debug(f"Authorization header: {request.headers.get('Authorization', 'MISSING')[:100]}...")
      LOG.debug(f"User-Agent header: {request.headers.get('User-Agent', 'MISSING')[:100]}...")
      LOG.debug(f"X-Amz-Date: {request.headers.get('X-Amz-Date', 'MISSING')}")
      LOG.debug(f"X-Amz-Content-Sha256: {request.headers.get('x-amz-content-sha256', 'MISSING')}")
      LOG.debug("========================")

      LOG.debug("RAZ headers applied and URL synchronized - ready for S3")

    except Exception as e:
      LOG.error(f"Failed to add RAZ headers to unsigned request: {e}")
      raise

  def _handle_before_send(self, request: AWSRequest, **kwargs) -> None:
    """
    Handle before-send event.
    This is called after signing but before sending.
    Verify RAZ headers are still present and log final request state.
    """
    LOG.debug("Before-send: Verifying RAZ headers are present")

    # Check for key RAZ headers
    raz_headers = ["Authorization", "X-Amz-Date", "X-Amz-Security-Token", "Host"]
    missing_headers = []

    for header in raz_headers:
      if header in request.headers:
        header_value = request.headers[header]
        LOG.debug(f"RAZ header present: {header} = {header_value[:50]}...")
      else:
        missing_headers.append(header)
        LOG.error(f"RAZ header MISSING: {header}")

    if missing_headers:
      LOG.error(f"CRITICAL: Missing RAZ headers: {missing_headers}")
      LOG.error("This explains the 403 error - request not properly signed")
    else:
      LOG.debug("All RAZ headers present in final request")

    # Log final request URL for debugging
    LOG.debug(f"Final request URL: {request.url}")
    LOG.debug(f"Final request method: {request.method}")

    # BEFORE-SEND DEBUG: Compare with what we signed
    LOG.debug("=== BEFORE-SEND SIGNATURE DEBUG ===")
    LOG.debug(f"Method: {request.method}")
    LOG.debug(f"Final URL: {request.url}")
    LOG.debug(f"Host header: {request.headers.get('Host', 'MISSING')}")
    LOG.debug(f"Authorization: {request.headers.get('Authorization', 'MISSING')[:100]}...")
    LOG.debug(f"User-Agent: {request.headers.get('User-Agent', 'MISSING')[:100]}...")
    LOG.debug(f"X-Amz-Date: {request.headers.get('X-Amz-Date', 'MISSING')}")
    LOG.debug(f"X-Amz-Content-Sha256: {request.headers.get('x-amz-content-sha256', 'MISSING')}")
    LOG.debug("===================================")

    # Don't remove headers - they're needed for RAZ authentication

  def _get_request_url(self, request: AWSRequest) -> str:
    """
    Get request URL in RAZ-compatible format based on provider type.
    AWS uses virtual-hosted style (NO :443 port), generic providers use original format.
    """
    provider = self.connector_config.provider.lower()

    if provider == "aws":
      return self._get_aws_virtual_hosted_url(request)
    else:
      return self._get_generic_provider_url(request)

  def _get_aws_virtual_hosted_url(self, request: AWSRequest) -> str:
    """Convert AWS URLs to virtual-hosted style WITHOUT :443 port (for Host header consistency)"""
    url_parts = list(urlparse(request.url))

    # Extract bucket and key from path
    path = url_parts[2].lstrip("/")
    path_parts = path.split("/", 1) if path else ["", ""]
    bucket_name = path_parts[0] if path_parts[0] else None
    key_path = path_parts[1] if len(path_parts) > 1 else ""

    # Convert to virtual-hosted style URL for AWS
    if bucket_name:
      # Get region from connector config (not hardcoded)
      region = self.connector_config.region or "us-east-1"

      # Build virtual-hosted hostname WITHOUT :443 port (for Host header consistency)
      if "s3." in url_parts[1]:
        # Regional endpoint: s3.us-west-2.amazonaws.com
        virtual_host = f"{bucket_name}.{url_parts[1]}"
      else:
        # Standard endpoint: s3.amazonaws.com
        virtual_host = f"{bucket_name}.s3.{region}.amazonaws.com"

      # Set virtual-hosted URL components
      url_parts[1] = virtual_host
      url_parts[2] = f"/{key_path}" if key_path else "/"
    else:
      # Root or bucket listing - keep original host (NO :443 port for consistency)
      # AWS HTTPS is implied, explicit port causes Host header mismatch
      pass

    # Add query parameters
    if request.params:
      query = urlencode(request.params)
      url_parts[4] = query

    final_url = urlunparse(url_parts)
    LOG.debug(f"AWS URL conversion for RAZ: {request.url} → {final_url}")
    return final_url

  def _get_generic_provider_url(self, request: AWSRequest) -> str:
    """Get URL for generic S3 providers - preserve original format with correct port"""
    url_parts = list(urlparse(request.url))

    # For generic providers, use the configured endpoint format
    # Extract port from connector endpoint if available
    if self.connector_config.endpoint:
      endpoint_parts = urlparse(self.connector_config.endpoint)

      # Use the port from connector endpoint if specified
      if endpoint_parts.port:
        if ":" not in url_parts[1]:
          url_parts[1] = f"{url_parts[1]}:{endpoint_parts.port}"
        LOG.debug(f"Added port {endpoint_parts.port} for generic provider")

    # Add query parameters
    if request.params:
      query = urlencode(request.params)
      url_parts[4] = query

    final_url = urlunparse(url_parts)
    LOG.debug(f"Generic provider URL for RAZ: {request.url} → {final_url}")
    return final_url


class RazAuthProvider(S3AuthProvider):
  """
  Authentication provider using RAZ for request signing.
  Uses boto3's event system to intercept and sign requests.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    super().__init__(connector_config, user)

    # Create RAZ event handler with connector config for provider-aware URL formatting
    self.raz_event_handler = RazEventHandler(user=user, connector_config=connector_config)

    # Create boto3 session with RAZ event handlers (clean approach with UNSIGNED signer)
    self.session = boto3.Session(region_name=connector_config.region)

    # Register RAZ handlers with the session's event system
    self.session.events.register("choose-signer.*.*", self.raz_event_handler._handle_choose_signer)
    self.session.events.register("before-sign.*.*", self.raz_event_handler._handle_before_sign)
    self.session.events.register("before-send.*.*", self.raz_event_handler._handle_before_send)

    LOG.debug("Created RAZ session with choose-signer=UNSIGNED and before-sign=RAZ headers")

  def get_credentials(self) -> Dict[str, Any]:
    """
    Return no credentials - UNSIGNED signer handles authentication.
    Real signing is done via RAZ event handlers.
    """
    return {}

  def get_session_kwargs(self) -> Dict[str, Any]:
    """
    Get kwargs for creating boto3 session.
    Returns minimal kwargs since we use UNSIGNED signer.
    """
    return {"region_name": self.connector_config.region}

  def get_session(self):
    """
    Return the pre-configured session with RAZ event handlers.
    This session should be used directly, not recreated.
    """
    LOG.debug(f"RazAuthProvider.get_session() called - returning session ID: {id(self.session)}")
    return self.session

  def refresh(self) -> None:
    """No refresh needed as we sign per-request"""
    pass
