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

from desktop.lib.fs.s3.clients.base import S3AuthProvider
from desktop.lib.idbroker import conf as conf_idbroker
from desktop.lib.idbroker.client import IDBroker

if TYPE_CHECKING:
  from desktop.lib.fs.s3.conf_utils import ConnectorConfig

LOG = logging.getLogger()


class IDBrokerAuthProvider(S3AuthProvider):
  """
  Authentication provider using IDBroker service.
  IDBroker provides temporary credentials for S3 access.
  """

  def __init__(self, connector_config: "ConnectorConfig", user: str):
    super().__init__(connector_config, user)
    self._credentials = None
    self._idbroker = None
    self._init_idbroker()

  def _init_idbroker(self) -> None:
    """Initialize IDBroker client using existing global configuration"""
    try:
      # Use existing IDBroker configuration from core-site
      self._idbroker = IDBroker.from_core_site("s3a", self.user)
      self._load_credentials()
    except Exception as e:
      LOG.error(f"Failed to initialize IDBroker: {e}")
      raise

  def _load_credentials(self) -> None:
    """Load credentials from IDBroker"""
    try:
      cab = self._idbroker.get_cab()
      if not cab or "Credentials" not in cab:
        raise Exception("No credentials in IDBroker response")

      creds = cab["Credentials"]
      self._credentials = {
        "access_key_id": creds.get("AccessKeyId"),
        "secret_access_key": creds.get("SecretAccessKey"),
        "session_token": creds.get("SessionToken"),
        "expiration": creds.get("Expiration"),
      }

      if not self._credentials["access_key_id"] or not self._credentials["secret_access_key"]:
        raise Exception("Missing required credentials from IDBroker")

    except Exception as e:
      LOG.error(f"Failed to load credentials from IDBroker: {e}")
      raise

  def get_credentials(self) -> Dict[str, Any]:
    """Get current credentials"""
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
    """Refresh credentials from IDBroker"""
    self._load_credentials()

  @classmethod
  def is_enabled(cls) -> bool:
    """Check if IDBroker is enabled"""
    return conf_idbroker.is_idbroker_enabled("s3a")
