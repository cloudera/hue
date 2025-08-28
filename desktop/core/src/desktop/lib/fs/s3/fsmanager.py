#!/usr/bin/env python

from typing import Optional

from desktop.conf import S3_OBJECT_STORES
from desktop.lib.fs.s3.core.s3fs import S3FileSystem


def make_s3_client(name: str, user: str) -> S3FileSystem:
  """
  Create a new S3FileSystem instance.

  Args:
      name: Provider ID from S3_OBJECT_STORES config
      user: Username for operations

  Returns:
      S3FileSystem instance

  Raises:
      ValueError: If provider configuration is invalid
  """
  return S3FileSystem(name, user)


def get_s3_home_directory(user: Optional[str] = None) -> str:
  """
  Get the S3 home directory for a user.

  Args:
      user: Optional username, uses current user if None

  Returns:
      S3 home directory path
  """
  # Get first available provider
  for provider_id in S3_OBJECT_STORES:
    provider_conf = S3_OBJECT_STORES[provider_id]
    home_path = provider_conf.DEFAULT_HOME_PATH.get()
    if home_path:
      # If user provided, append username
      if user and home_path.rstrip("/").endswith("/user"):
        return f"{home_path.rstrip('/')}/{user}"
      return home_path

  # Default to S3 root if no home path configured
  return "s3a://"
