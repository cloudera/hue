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
from dataclasses import dataclass
from typing import List, Optional

from desktop.lib.fs.s3.clients.aws import AWSS3Client
from desktop.lib.fs.s3.clients.base import S3ClientInterface
from desktop.lib.fs.s3.clients.generic import GenericS3Client
from desktop.lib.fs.s3.config_utils import ConnectorConfig, get_all_connectors, get_connector

LOG = logging.getLogger()


@dataclass
class ConnectorInfo:
  """Information about an available connector for API consumers"""

  id: str
  provider: str
  auth_type: str
  endpoint: Optional[str]
  region: Optional[str]
  bucket_names: List[str]  # Buckets configured for this connector


class S3ClientFactory:
  """Simplified factory for creating S3 clients using connector architecture"""

  @classmethod
  def get_available_connectors(cls, user: str) -> List[ConnectorInfo]:
    """Get list of all available connectors with their bucket information"""
    connector_infos = []

    try:
      connectors = get_all_connectors()

      for connector_id, connector in connectors.items():
        bucket_names = list(connector.bucket_configs.keys()) if connector.bucket_configs else []

        connector_infos.append(
          ConnectorInfo(
            id=connector_id,
            provider=connector.provider,
            auth_type=connector.auth_type,
            endpoint=connector.endpoint,
            region=connector.region,
            bucket_names=bucket_names,
          )
        )
    except Exception as e:
      LOG.error(f"Failed to get available connectors: {e}")

    return connector_infos

  @classmethod
  def get_client_for_connector(cls, connector_id: str, user: str) -> S3ClientInterface:
    """
    Get S3 client instance for a specific connector.

    Args:
      connector_id: ID of the connector
      user: Username for the client

    Returns:
      S3ClientInterface instance configured for the connector

    Raises:
      ValueError: If connector not found
    """
    try:
      connector = get_connector(connector_id)

      if not connector:
        available = list(get_all_connectors().keys())
        raise ValueError(f"Unknown connector ID: {connector_id}. Available connectors: {available}")

      return cls._create_client_for_connector(connector, user)

    except Exception as e:
      LOG.error(f"Failed to create S3 client for connector '{connector_id}': {e}")
      raise

  @classmethod
  def _create_client_for_connector(cls, connector: ConnectorConfig, user: str) -> S3ClientInterface:
    """Create appropriate client based on connector provider type"""
    provider_type = connector.provider.lower()

    try:
      if provider_type == "aws":
        return AWSS3Client(connector, user)
      elif provider_type in ("generic", "netapp", "dell"):
        return GenericS3Client(connector, user)
      else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    except Exception as e:
      LOG.error(f"Failed to create {provider_type} client: {e}")
      raise

  @classmethod
  def get_client(cls, connector_id: str, user: str) -> S3ClientInterface:
    """
    Get S3 client instance for a connector.
    This is the main public method for getting clients.

    Args:
      connector_id: ID of the connector
      user: Username for the client

    Returns:
      S3ClientInterface instance
    """
    return cls.get_client_for_connector(connector_id, user)
