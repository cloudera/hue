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
from datetime import datetime
from typing import Any, Dict, TYPE_CHECKING

import boto3

from desktop.lib.fs.s3.clients.base import S3AuthProvider

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class IAMAuthProvider(S3AuthProvider):
  """
  Authentication provider using AWS IAM roles.
  Supports:
  1. EC2 instance profiles
  2. ECS task roles
  3. Explicit IAM role assumption
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    super().__init__(connector_config, user)
    self._credentials = None
    self._sts_client = None
    self._role_arn = connector_config.iam_role
    self._session_name = f"hue-{user}-session"
    self._init_sts()

  def _init_sts(self) -> None:
    """Initialize STS client for role assumption if needed"""
    try:
      # Create STS client using instance/task credentials
      self._sts_client = boto3.client("sts")

      if self._role_arn:
        # Assume the specified role
        response = self._sts_client.assume_role(RoleArn=self._role_arn, RoleSessionName=self._session_name)
        self._credentials = {
          "access_key_id": response["Credentials"]["AccessKeyId"],
          "secret_access_key": response["Credentials"]["SecretAccessKey"],
          "session_token": response["Credentials"]["SessionToken"],
          "expiration": response["Credentials"]["Expiration"],
        }
      else:
        # Use instance/task credentials directly
        instance_creds = boto3.Session().get_credentials()
        if instance_creds:
          self._credentials = {
            "access_key_id": instance_creds.access_key,
            "secret_access_key": instance_creds.secret_key,
            "session_token": instance_creds.token,
            "expiration": getattr(instance_creds, "_expiry_time", None),
          }
        else:
          raise Exception("No instance credentials found")
    except Exception as e:
      LOG.error(f"Failed to initialize IAM credentials: {e}")
      raise

  def get_credentials(self) -> Dict[str, Any]:
    """Get current IAM credentials"""
    if self._should_refresh():
      self.refresh()
    return self._credentials

  def get_session_kwargs(self) -> Dict[str, Any]:
    """Get kwargs for creating boto3 session"""
    creds = self.get_credentials()
    return {
      "aws_access_key_id": creds["access_key_id"],
      "aws_secret_access_key": creds["secret_access_key"],
      "aws_session_token": creds.get("session_token"),
      "region_name": self.connector_config.region,
    }

  def _should_refresh(self) -> bool:
    """Check if credentials need refresh"""
    if not self._credentials:
      return True
    if "expiration" not in self._credentials:
      return False

    # Refresh if less than 5 minutes remaining
    now = datetime.utcnow()
    expiry = self._credentials["expiration"]
    return (expiry - now).total_seconds() < 300

  def refresh(self) -> None:
    """Refresh IAM credentials"""
    self._init_sts()
