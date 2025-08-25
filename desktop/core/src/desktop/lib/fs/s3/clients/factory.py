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

from dataclasses import dataclass
from typing import Dict, List, Optional, Type

from desktop.conf import S3_OBJECT_STORES
from desktop.lib.fs.s3.clients.base import S3AuthProvider, S3ClientInterface


@dataclass
class ClientConfig:
  """Configuration for a single client instance"""

  provider_id: str
  name: str
  provider_type: str
  auth_type: str
  endpoint: Optional[str]
  region: Optional[str]


class S3ClientFactory:
  """Factory for creating S3 clients"""

  _PROVIDER_MAP = {}  # Will be populated by register_provider
  _AUTH_PROVIDER_MAP = {}  # Will be populated by register_auth_provider

  @classmethod
  def get_available_clients(cls, user: str) -> List[ClientConfig]:
    """Get list of all available client configurations"""
    configs = []

    for provider_id, provider_conf in S3_OBJECT_STORES.items():
      configs.append(
        ClientConfig(
          provider_id=provider_id,
          name=provider_conf.NAME.get(),
          provider_type=provider_conf.PROVIDER.get().lower(),
          auth_type=provider_conf.AUTH_TYPE.get(),
          endpoint=provider_conf.ENDPOINT.get(),
          region=provider_conf.REGION.get(),
        )
      )

    return configs

  @classmethod
  def get_client(cls, provider_id: str, user: str) -> S3ClientInterface:
    """Get S3 client instance for given provider"""
    if provider_id not in S3_OBJECT_STORES:
      raise ValueError(f"Unknown provider ID: {provider_id}")

    provider_conf = S3_OBJECT_STORES[provider_id]
    provider_type = provider_conf.PROVIDER.get().lower()
    auth_type = provider_conf.AUTH_TYPE.get()

    # Validate provider and auth type
    if provider_type not in cls._PROVIDER_MAP:
      raise ValueError(f"Unknown provider type: {provider_type}")
    if auth_type not in cls._AUTH_PROVIDER_MAP:
      raise ValueError(f"Unknown auth type: {auth_type}")

    # Create client with auth provider
    client_class = cls._PROVIDER_MAP[provider_type]
    auth_provider_class = cls._AUTH_PROVIDER_MAP[auth_type]

    client = client_class(provider_id, user)
    client.auth_provider = auth_provider_class(provider_id, user)

    return client

  @classmethod
  def register_provider(cls, provider_type: str, client_class: Type[S3ClientInterface]) -> None:
    """Register a new provider type"""
    cls._PROVIDER_MAP[provider_type.lower()] = client_class

  @classmethod
  def register_auth_provider(cls, auth_type: str, auth_provider_class: Type[S3AuthProvider]) -> None:
    """Register a new auth provider type"""
    cls._AUTH_PROVIDER_MAP[auth_type.lower()] = auth_provider_class
