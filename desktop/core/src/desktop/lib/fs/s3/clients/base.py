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

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TYPE_CHECKING

from boto3.session import Session
from botocore.client import Config
from botocore.credentials import Credentials

from desktop.lib.fs.s3.constants import CLIENT_CONFIG, TRANSFER_CONFIG

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig


class S3AuthProvider(ABC):
  """
  Base interface for S3 authentication providers.
  Each auth method (key, IAM, RAZ) must implement this interface.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    self.connector_config = connector_config
    self.user = user

  @abstractmethod
  def get_credentials(self) -> Dict[str, Any]:
    """
    Get credentials for S3 access.
    Returns dict with keys:
    - access_key_id
    - secret_access_key
    - session_token (optional)
    - expiration (optional)
    """
    pass

  @abstractmethod
  def get_session_kwargs(self) -> Dict[str, Any]:
    """Get kwargs for creating boto3 session"""
    pass

  @abstractmethod
  def refresh(self) -> None:
    """Refresh credentials if needed"""
    pass


class S3ClientInterface(ABC):
  """
  Base interface for S3 clients. All provider-specific clients must implement this interface.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    self.connector_config = connector_config
    self.user = user

    # Initialize auth provider
    self.auth_provider = self._create_auth_provider()

    # Initialize boto3 client config
    self.client_config = Config(
      **{
        **CLIENT_CONFIG,
        "region_name": connector_config.region,
        "s3": {
          "addressing_style": "path"  # Use path style for compatibility
        },
      }
    )

    # Initialize transfer config
    self.transfer_config = TRANSFER_CONFIG.copy()

    # Initialize session and clients
    self.session = self._create_session()
    self.s3_client = self._create_client()
    self.s3_resource = self._create_resource()

  @abstractmethod
  def _create_auth_provider(self) -> S3AuthProvider:
    """Create and return appropriate auth provider"""
    pass

  @abstractmethod
  def _create_session(self) -> Session:
    """Create and return a boto3 session with appropriate credentials"""
    pass

  @abstractmethod
  def _create_client(self) -> Any:
    """Create and return a boto3 S3 client"""
    pass

  @abstractmethod
  def _create_resource(self) -> Any:
    """Create and return a boto3 S3 resource"""
    pass

  @abstractmethod
  def get_credentials(self) -> Optional[Credentials]:
    """Get credentials for the client"""
    pass

  @abstractmethod
  def get_delegation_token(self) -> Optional[str]:
    """Get delegation token if supported"""
    pass

  @abstractmethod
  def get_region(self, bucket: str) -> str:
    """Get region for a bucket"""
    pass
