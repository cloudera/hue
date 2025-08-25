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

from typing import Any, Dict

from desktop.lib.fs.s3.clients.base import S3AuthProvider


class KeyAuthProvider(S3AuthProvider):
  """
  Authentication provider using access key and secret key.
  Simple static credentials without refresh.
  """

  def __init__(self, provider_id: str, user: str):
    super().__init__(provider_id, user)
    self._credentials = None
    self._load_credentials()

  def _load_credentials(self) -> None:
    """Load credentials from config"""
    self._credentials = {"access_key_id": self.config.ACCESS_KEY_ID.get(), "secret_access_key": self.config.SECRET_KEY.get()}

    if not self._credentials["access_key_id"] or not self._credentials["secret_access_key"]:
      raise ValueError(f"Missing access key or secret key for provider {self.provider_id}")

  def get_credentials(self) -> Dict[str, Any]:
    """Get static credentials"""
    return self._credentials

  def get_session_kwargs(self) -> Dict[str, Any]:
    """Get kwargs for creating boto3 session"""
    return {
      "aws_access_key_id": self._credentials["access_key_id"],
      "aws_secret_access_key": self._credentials["secret_access_key"],
      "region_name": self.config.REGION.get(),
    }

  def refresh(self) -> None:
    """No refresh needed for static credentials"""
    pass
