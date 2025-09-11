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

from desktop.conf import RAZ
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
    super().__init__(connector_config, user)

    # AWS specific config
    self.client_config.signature_version = "s3v4"

    options = connector_config.options or {}
    self.client_config.s3.update(
      {
        "payload_signing_enabled": True,
        "use_accelerate_endpoint": options.get("use_accelerate", False),
        "use_dualstack_endpoint": options.get("use_dualstack", False),
      }
    )

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

  def _create_session(self) -> Session:
    """Create boto3 session with credentials from auth provider"""
    session_kwargs = self.auth_provider.get_session_kwargs()
    return boto3.Session(**session_kwargs)

  def _create_client(self) -> Any:
    """Create boto3 S3 client"""
    return self.session.client("s3", config=self.client_config, endpoint_url=self.connector_config.endpoint)

  def _create_resource(self) -> Any:
    """Create boto3 S3 resource"""
    return self.session.resource("s3", config=self.client_config, endpoint_url=self.connector_config.endpoint)

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
