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
from typing import Any, Dict, Optional, TYPE_CHECKING

import boto3
from boto3.session import Session
from botocore.credentials import Credentials

from desktop.conf import RAZ
from desktop.lib.fs.s3.clients.auth.key import KeyAuthProvider
from desktop.lib.fs.s3.clients.auth.raz import RazAuthProvider
from desktop.lib.fs.s3.clients.base import S3AuthProvider, S3ClientInterface
from desktop.lib.fs.s3.constants import DEFAULT_REGION

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class GenericS3Client(S3ClientInterface):
  """
  Generic S3 client for S3-compatible storage systems.
  Supports any storage that implements the S3 API (Netapp, Dell, etc).
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    super().__init__(connector_config, user)

    # Override client config for generic providers
    self.client_config.signature_version = self._get_signature_version()
    self.client_config.s3.update(
      {
        "addressing_style": "path",  # Always use path style
        "payload_signing_enabled": True,
      }
    )

    # Apply provider-specific settings
    self._setup_provider_specific_config()

  def _create_auth_provider(self) -> S3AuthProvider:
    """Create appropriate auth provider for generic providers"""
    connector = self.connector_config

    # Support RAZ authentication for generic providers
    if RAZ.IS_ENABLED.get() and connector.auth_type == "raz":
      return RazAuthProvider(connector, self.user)
    else:
      # Default to key auth for generic providers
      return KeyAuthProvider(connector, self.user)

  def _get_signature_version(self) -> str:
    """Get signature version with option to override via configuration"""
    options = self.connector_config.options or {}

    # Allow override via options for legacy systems
    return options.get("signature_version", "s3v4")

  def _setup_provider_specific_config(self) -> None:
    """Setup provider-specific configurations"""
    provider = self.connector_config.provider.lower()
    options = self.connector_config.options or {}

    if provider == "netapp":
      self._setup_netapp_config(options)
    elif provider == "dell":
      self._setup_dell_config(options)
    # Add more providers as needed

  def _setup_netapp_config(self, options: Dict[str, Any]) -> None:
    """Setup Netapp StorageGRID specific config"""
    # SSL verification
    if "ssl_verify" in options:
      self.client_config.verify = options["ssl_verify"]

    # Custom headers
    if "custom_headers" in options:
      self.client_config.s3["custom_headers"] = options["custom_headers"]

  def _setup_dell_config(self, options: Dict[str, Any]) -> None:
    """Setup Dell ECS specific config"""
    # Namespace support
    if "namespace" in options:
      self.client_config.s3["namespace"] = options["namespace"]

    # Multipart settings
    if "multipart_threshold" in options:
      self.transfer_config["multipart_threshold"] = options["multipart_threshold"]
    if "multipart_chunksize" in options:
      self.transfer_config["multipart_chunksize"] = options["multipart_chunksize"]

  def _create_session(self) -> Session:
    """Create boto3 session"""
    session_kwargs = self.auth_provider.get_session_kwargs()
    return boto3.Session(**session_kwargs)

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
    """Get delegation token (not supported for generic providers)"""
    return None

  def get_region(self, bucket: str) -> str:
    """
    Get region for a bucket with smart bucket config support.
    Most S3-compatible systems don't use regions,
    so return configured region or default.
    """
    # Check bucket-specific region from bucket_configs first
    if bucket and self.connector_config.bucket_configs:
      bucket_config = self.connector_config.bucket_configs.get(bucket)
      if bucket_config and bucket_config.region:
        return bucket_config.region

    # Fall back to connector default region
    return self.connector_config.region or DEFAULT_REGION
