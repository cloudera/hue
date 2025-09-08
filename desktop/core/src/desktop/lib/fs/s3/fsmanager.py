#!/usr/bin/env python

import logging
from typing import Optional

from desktop.lib.fs.s3.conf_utils import get_s3_home_directory as get_home_dir
from desktop.lib.fs.s3.core.s3fs import S3FileSystem

LOG = logging.getLogger()


def make_s3_client(connector_id: str, user: str) -> S3FileSystem:
  """
  Create a new S3FileSystem instance.

  Args:
    connector_id: ID of the S3 connector to use
    user: Username for operations

  Returns:
    S3FileSystem instance

  Raises:
    ValueError: If connector configuration is invalid
  """
  return S3FileSystem(connector_id, user)


def get_s3_home_directory(user: Optional[str] = None, connector_id: str = None, bucket_name: str = None) -> str:
  """
  Get the S3 home directory for a user with smart defaults.

  Args:
    user: Optional username
    connector_id: Optional connector ID (uses smart default if not provided)
    bucket_name: Optional bucket name (uses smart bucket selection if not provided)

  Returns:
    S3 home directory path with intelligent fallbacks
  """
  return get_home_dir(connector_id, bucket_name, user)
