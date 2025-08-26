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

from desktop.conf import S3_OBJECT_STORES
from desktop.lib.fs.s3.clients.aws import AWSS3Client
from desktop.lib.fs.s3.clients.base import S3ClientInterface
from desktop.lib.fs.s3.clients.generic import GenericS3Client

LOG = logging.getLogger()


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

    try:
      if provider_type == "aws":
        return AWSS3Client(provider_id, user)
      elif provider_type == "generic":
        return GenericS3Client(provider_id, user)
      else:
        raise ValueError(f"Unknown provider type: {provider_type}")
    except Exception as e:
      LOG.error(f"Failed to create S3 client: {e}")
      raise
