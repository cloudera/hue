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
from typing import Any, Optional, TYPE_CHECKING

import boto3
from boto3.session import Session
from botocore.credentials import Credentials
from botocore.exceptions import ClientError

from desktop.conf import default_ssl_cacerts, default_ssl_validate, RAZ
from desktop.lib.fs.s3.clients.auth.iam import IAMAuthProvider
from desktop.lib.fs.s3.clients.auth.idbroker import IDBrokerAuthProvider
from desktop.lib.fs.s3.clients.auth.key import KeyAuthProvider
from desktop.lib.fs.s3.clients.auth.raz import RazAuthProvider
from desktop.lib.fs.s3.clients.base import S3AuthProvider, S3ClientInterface
from desktop.lib.fs.s3.constants import DEFAULT_REGION
from desktop.lib.idbroker import conf as conf_idbroker

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class AWSS3Client(S3ClientInterface):
  """
  AWS S3 client implementation.
  Handles AWS-specific features and optimizations.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    # Store options for pre-configuration
    self._options = connector_config.options or {}

    # Initialize with proper configuration applied BEFORE client creation
    super().__init__(connector_config, user)

  def _create_auth_provider(self) -> S3AuthProvider:
    """Create appropriate auth provider based on connector config"""
    connector = self.connector_config

    # Priority-based auth provider selection
    if RAZ.IS_ENABLED.get() and connector.auth_type == "raz":
      return RazAuthProvider(connector, self.user)
    elif conf_idbroker.is_idbroker_enabled("s3a") and connector.auth_type == "idbroker":
      return IDBrokerAuthProvider(connector, self.user)
    elif connector.auth_type == "iam" and connector.iam_role:
      return IAMAuthProvider(connector, self.user)
    else:
      return KeyAuthProvider(connector, self.user)

  def _configure_client_settings(self) -> None:
    """Configure AWS-specific client settings before client creation"""
    # AWS specific config
    self.client_config.signature_version = "s3v4"
    self.client_config.s3.update(
      {
        "payload_signing_enabled": True,
        "use_accelerate_endpoint": self._options.get("use_accelerate", False),
        "use_dualstack_endpoint": self._options.get("use_dualstack", False),
      }
    )

    # Apply SSL configuration (using global Hue SSL settings)
    self._setup_ssl_config()

  def _setup_ssl_config(self) -> None:
    """Setup SSL verification configuration using global SSL settings with connector overrides"""
    # Start with global Hue SSL settings
    ssl_validate = default_ssl_validate()
    ssl_cacerts = default_ssl_cacerts()

    # Allow connector-specific overrides via options
    if "ssl_cert_ca_verify" in self._options:
      ssl_validate = self._options["ssl_cert_ca_verify"]
      LOG.debug(f"Connector overrides SSL verification: {ssl_validate}")

    if "ca_bundle" in self._options:
      ssl_cacerts = self._options["ca_bundle"]
      LOG.debug(f"Connector overrides CA bundle: {ssl_cacerts}")

    # Apply SSL configuration
    if ssl_validate:
      if ssl_cacerts:
        # Use custom CA bundle if specified
        self.client_config.verify = ssl_cacerts
        LOG.debug(f"Using CA bundle for SSL verification: {ssl_cacerts}")
      else:
        # Use default system CA certificates
        self.client_config.verify = True
        LOG.debug("Using system CA certificates for SSL verification")
    else:
      # Disable SSL verification
      self.client_config.verify = False
      LOG.warning("SSL certificate verification is DISABLED - use only for testing!")

    # Client-side certificates (if needed)
    if "client_cert" in self._options:
      self.client_config.client_cert = self._options["client_cert"]

  def _create_session(self) -> Session:
    """Create boto3 session with credentials from auth provider"""
    # For RAZ auth, use the pre-configured session with event handlers
    if hasattr(self.auth_provider, "get_session"):
      raz_session = self.auth_provider.get_session()
      if raz_session is not None:
        LOG.debug(f"Using pre-configured RAZ session with event handlers - ID: {id(raz_session)}")
        return raz_session

    # For other auth types, create new session
    LOG.debug("Creating new session from auth provider kwargs")
    session_kwargs = self.auth_provider.get_session_kwargs()
    new_session = boto3.Session(**session_kwargs)
    LOG.debug(f"Created new session - ID: {id(new_session)}")
    return new_session

  def _create_client(self) -> Any:
    """Create boto3 S3 client"""
    return self.session.client(
      "s3", config=self.client_config, endpoint_url=self.connector_config.endpoint, verify=getattr(self.client_config, "verify", None)
    )

  def _create_resource(self) -> Any:
    """Create boto3 S3 resource"""
    return self.session.resource(
      "s3", config=self.client_config, endpoint_url=self.connector_config.endpoint, verify=getattr(self.client_config, "verify", None)
    )

  def get_credentials(self) -> Optional[Credentials]:
    """Get current credentials"""
    return self.session.get_credentials()

  def get_delegation_token(self) -> Optional[str]:
    """Get delegation token (not supported for AWS)"""
    return None

  def get_region(self, bucket: str) -> str:
    """
    Get region for a bucket with smart bucket config support.
    Checks:
    1. Bucket-specific region from bucket_configs
    2. Bucket location constraint (AWS API)
    3. Connector default region
    4. System default region
    """
    # Check bucket-specific region from bucket_configs first
    if bucket and self.connector_config.bucket_configs:
      bucket_config = self.connector_config.bucket_configs.get(bucket)
      if bucket_config and bucket_config.region:
        LOG.debug(f"Using bucket-specific region '{bucket_config.region}' for bucket '{bucket}'")
        return bucket_config.region

    try:
      # Try to get region from AWS API bucket location
      response = self.s3_client.get_bucket_location(Bucket=bucket)
      region = response.get("LocationConstraint")

      # Handle special cases
      if region is None:
        # US East 1 returns None
        return "us-east-1"
      elif region == "EU":
        # Legacy EU region
        return "eu-west-1"

      LOG.debug(f"Detected bucket '{bucket}' in region '{region}' via AWS API")
      return region
    except ClientError as e:
      LOG.debug(f"Could not detect region for bucket {bucket} via AWS API: {e}")
      # Fall back to connector default or system default
      return self.connector_config.region or DEFAULT_REGION
