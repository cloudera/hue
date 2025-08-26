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
from typing import Any, Optional

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

LOG = logging.getLogger(__name__)


class AWSS3Client(S3ClientInterface):
  """
  AWS S3 client implementation.
  Handles AWS-specific features and optimizations.
  """

  def __init__(self, provider_id: str, user: str):
    super().__init__(provider_id, user)

    # AWS specific config
    self.client_config.signature_version = "s3v4"
    self.client_config.s3.update(
      {
        "use_accelerate_endpoint": self.config.OPTIONS.get().get("use_accelerate", False),
        "payload_signing_enabled": True,
        "use_dualstack_endpoint": self.config.OPTIONS.get().get("use_dualstack", False),
      }
    )

  def _create_auth_provider(self) -> S3AuthProvider:
    """Create appropriate auth provider based on config"""
    if RAZ.IS_ENABLED.get():
      return RazAuthProvider(self.provider_id, self.user)
    elif conf_idbroker.is_idbroker_enabled("s3a"):
      return IDBrokerAuthProvider(self.provider_id, self.user)
    elif self.config.IAM_ROLE.get():
      return IAMAuthProvider(self.provider_id, self.user)
    else:
      return KeyAuthProvider(self.provider_id, self.user)

  def _create_session(self) -> Session:
    """Create boto3 session with credentials from auth provider"""
    session_kwargs = self.auth_provider.get_session_kwargs()
    return boto3.Session(**session_kwargs)

  def _create_client(self) -> Any:
    """Create boto3 S3 client"""
    return self.session.client("s3", config=self.client_config, endpoint_url=self.config.ENDPOINT.get())

  def _create_resource(self) -> Any:
    """Create boto3 S3 resource"""
    return self.session.resource("s3", config=self.client_config, endpoint_url=self.config.ENDPOINT.get())

  def get_credentials(self) -> Optional[Credentials]:
    """Get current credentials"""
    return self.session.get_credentials()

  def get_delegation_token(self) -> Optional[str]:
    """Get delegation token (not supported for AWS)"""
    return None

  def get_region(self, bucket: str) -> str:
    """
    Get region for a bucket.
    Checks:
    1. Bucket region map from config
    2. Bucket location constraint
    3. Default region
    """
    # Check bucket region map first
    region_map = self.config.BUCKET_REGION_MAP.get()
    if bucket in region_map:
      return region_map[bucket]

    try:
      # Try to get region from bucket location
      response = self.s3_client.get_bucket_location(Bucket=bucket)
      region = response.get("LocationConstraint")

      # Handle special cases
      if region is None:
        # US East 1 returns None
        return "us-east-1"
      elif region == "EU":
        # Legacy EU region
        return "eu-west-1"

      return region
    except ClientError as e:
      LOG.warning(f"Failed to get region for bucket {bucket}: {e}")
      # Fall back to default region
      return self.config.REGION.get() or DEFAULT_REGION

  def validate_region(self, bucket: str) -> bool:
    """
    Validate that we're using the correct region for a bucket.
    Important for signature v4 compatibility.
    """
    actual_region = self.get_region(bucket)
    current_region = self.config.REGION.get() or DEFAULT_REGION

    if actual_region != current_region:
      LOG.warning(f"Bucket {bucket} is in region {actual_region} but client is configured for {current_region}")
      return False
    return True
