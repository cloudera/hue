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

"""
Configuration utilities for the simplified S3 connector system.
Uses bucket-embedded configuration for clean, simple setup.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlparse

from aws.conf import AWS_ACCOUNTS, is_raz_s3 as legacy_is_raz_s3
from desktop.conf import RAZ, STORAGE_CONNECTORS, USE_STORAGE_CONNECTORS
from desktop.lib.idbroker import conf as conf_idbroker
from filebrowser.conf import REMOTE_STORAGE_HOME

LOG = logging.getLogger()


class ConfigurationError(Exception):
  """Raised when configuration validation fails"""

  pass


def _load_legacy_aws_accounts_as_connectors() -> Dict[str, "ConnectorConfig"]:
  """
  Convert legacy AWS_ACCOUNTS configurations to ConnectorConfig format.
  This provides backward compatibility for existing AWS configurations.

  Returns:
    Dict mapping connector IDs to ConnectorConfig objects
  """
  try:
    connectors = {}

    for account_id in AWS_ACCOUNTS.keys():
      aws_config = AWS_ACCOUNTS[account_id]

      # Skip accounts without basic configuration
      if not aws_config.get_raw():
        continue

      try:
        connector = ConnectorConfig(
          id=account_id,
          provider=_detect_provider_from_aws_config(aws_config),
          auth_type=_detect_auth_type_from_aws_config(aws_config),
          region=aws_config.REGION.get(),
          endpoint=_convert_aws_endpoint_to_new_format(aws_config),
          access_key_id=aws_config.ACCESS_KEY_ID.get(),
          secret_key=aws_config.SECRET_ACCESS_KEY.get(),
          bucket_configs=_extract_bucket_configs_from_aws(aws_config),
          options=_convert_aws_options_to_new_format(aws_config),
        )

        connectors[account_id] = connector
        LOG.debug(
          f"Converted legacy AWS account '{account_id}' to storage connector: provider={connector.provider}, auth={connector.auth_type}"
        )

      except Exception as e:
        LOG.warning(f"Failed to convert legacy AWS account '{account_id}': {e}")
        continue

    if connectors:
      LOG.info(f"Auto-converted {len(connectors)} legacy AWS accounts to storage connectors")

    return connectors
  except Exception as e:
    LOG.error(f"Failed to load legacy AWS accounts: {e}")
    return {}


def _detect_provider_from_aws_config(aws_config) -> str:
  """Detect provider type from AWS config"""
  # Check if it's a standard AWS endpoint
  host = aws_config.HOST.get()
  if not host or "amazonaws.com" in host:
    return "aws"

  # Custom endpoint means generic S3-compatible provider
  return "generic"


def _detect_auth_type_from_aws_config(aws_config) -> str:
  """
  Detect authentication type from AWS config using priority order:
  1. RAZ (highest priority - global setting)
  2. IDBroker (global setting)
  3. IAM (if environment credentials allowed)
  4. Key (static keys - default)
  """
  try:
    # Priority 1: RAZ authentication
    if legacy_is_raz_s3():
      return "raz"

    # Priority 2: IDBroker authentication
    if conf_idbroker.is_idbroker_enabled("s3a"):
      return "idbroker"

    # Priority 3: IAM roles (if environment credentials are allowed)
    if aws_config.ALLOW_ENVIRONMENT_CREDENTIALS.get():
      return "iam"

    # Priority 4: Static key authentication (default)
    return "key"

  except Exception as e:
    LOG.warning(f"Failed to detect auth type, defaulting to 'key': {e}")
    return "key"


def _convert_aws_endpoint_to_new_format(aws_config) -> Optional[str]:
  """Convert AWS HOST config to new endpoint format"""
  host = aws_config.HOST.get()
  if not host:
    return None

  # Ensure proper URL format
  if not host.startswith(("http://", "https://")):
    # Default to HTTPS for security, but respect IS_SECURE setting
    is_secure = aws_config.IS_SECURE.get() if hasattr(aws_config, "IS_SECURE") else True
    protocol = "https" if is_secure else "http"
    host = f"{protocol}://{host}"

  return host


def _extract_bucket_configs_from_aws(aws_config) -> Dict[str, "BucketConfig"]:
  """
  Extract bucket configurations from AWS config following old priority logic:
  1. REMOTE_STORAGE_HOME (global, highest priority)
  2. DEFAULT_HOME_PATH (per AWS account)
  """
  # Priority 1: Check REMOTE_STORAGE_HOME (global override, same logic as old get_s3_home_directory)
  home_path = None
  try:
    if hasattr(REMOTE_STORAGE_HOME, "get") and REMOTE_STORAGE_HOME.get():
      remote_home = REMOTE_STORAGE_HOME.get()
      if remote_home.startswith("s3a://"):
        home_path = remote_home
        LOG.debug(f"Using REMOTE_STORAGE_HOME for bucket config: {home_path}")
  except Exception as e:
    LOG.warning(f"Failed to check REMOTE_STORAGE_HOME: {e}")

  # Priority 2: Fall back to DEFAULT_HOME_PATH (per AWS account)
  if not home_path:
    default_home = aws_config.DEFAULT_HOME_PATH.get()
    if default_home and default_home.startswith("s3a://"):
      home_path = default_home
      LOG.debug(f"Using DEFAULT_HOME_PATH for bucket config: {home_path}")

  # If still no home path configured, return empty dict
  if not home_path:
    return {}

  try:
    # Parse s3a://bucket-name/path/to/home/
    bucket_name = extract_bucket_from_path(home_path)
    if not bucket_name:
      return {}

    # Extract the path part and make it relative
    if home_path.startswith(("s3a://", "s3://")):
      # Remove s3a://bucket-name/ prefix to get relative path
      scheme_and_bucket = f"s3a://{bucket_name}/"
      if home_path.startswith(scheme_and_bucket):
        relative_path = home_path[len(scheme_and_bucket) :]
      else:
        relative_path = None
    else:
      relative_path = home_path

    return {
      bucket_name: BucketConfig(
        name=bucket_name,
        default_home_path=relative_path if relative_path else None,
        region=None,  # Will be inherited from connector
        options=None,
      )
    }

  except Exception as e:
    LOG.warning(f"Failed to extract bucket config from home path '{home_path}': {e}")
    return {}


def _convert_aws_options_to_new_format(aws_config) -> Dict[str, any]:
  """Convert AWS-specific options to new options format"""
  options = {}

  try:
    # Proxy settings
    if aws_config.PROXY_ADDRESS.get():
      options["proxy_address"] = aws_config.PROXY_ADDRESS.get()
    if aws_config.PROXY_PORT.get():
      options["proxy_port"] = aws_config.PROXY_PORT.get()
    if aws_config.PROXY_USER.get():
      options["proxy_user"] = aws_config.PROXY_USER.get()
    if aws_config.PROXY_PASS.get():
      options["proxy_pass"] = aws_config.PROXY_PASS.get()

    # SSL/Security settings
    if hasattr(aws_config, "IS_SECURE"):
      options["is_secure"] = aws_config.IS_SECURE.get()

    # Calling format (for compatibility)
    if hasattr(aws_config, "CALLING_FORMAT"):
      calling_format = aws_config.CALLING_FORMAT.get()
      if calling_format and calling_format != "boto.s3.connection.OrdinaryCallingFormat":
        options["calling_format"] = calling_format

    # Session token (if available)
    if aws_config.SECURITY_TOKEN.get():
      options["security_token"] = aws_config.SECURITY_TOKEN.get()

    # Environment credentials setting
    if aws_config.ALLOW_ENVIRONMENT_CREDENTIALS.get() is not None:
      options["allow_environment_credentials"] = aws_config.ALLOW_ENVIRONMENT_CREDENTIALS.get()

  except Exception as e:
    LOG.warning(f"Failed to convert some AWS options: {e}")

  return options if options else {}


@dataclass
class BucketConfig:
  """Configuration for a specific bucket within a connector"""

  name: str
  default_home_path: Optional[str] = None
  region: Optional[str] = None
  options: Optional[Dict[str, any]] = None

  def get_effective_home_path(self, user: str = None) -> str:
    """
    Get effective home path for this bucket, handling relative paths and user context.

    Args:
      user: Username for RAZ user directory handling

    Returns:
      Absolute S3 path
    """
    if not self.default_home_path:
      # Default to bucket root
      path = f"s3a://{self.name}/"
    elif self.default_home_path.startswith("s3a://"):
      # Already absolute
      path = self.default_home_path
    else:
      # Relative path - make it absolute
      path = f"s3a://{self.name}/{self.default_home_path.lstrip('/')}"
      if not path.endswith("/"):
        path += "/"

    # Handle RAZ user directory logic
    if user and RAZ.IS_ENABLED.get():
      from desktop.models import _handle_user_dir_raz

      path = _handle_user_dir_raz(user, path)

    return path


@dataclass
class ConnectorConfig:
  """Simplified S3 connector configuration"""

  id: str
  provider: str
  auth_type: str
  region: Optional[str] = None
  endpoint: Optional[str] = None
  access_key_id: Optional[str] = None
  secret_key: Optional[str] = None
  iam_role: Optional[str] = None
  bucket_configs: Optional[Dict[str, BucketConfig]] = None
  options: Optional[Dict[str, any]] = None

  def get_bucket_config(self, bucket_name: str) -> BucketConfig:
    """Get configuration for a specific bucket, creating default if not found"""
    if self.bucket_configs and bucket_name in self.bucket_configs:
      return self.bucket_configs[bucket_name]

    # Return default bucket config
    return BucketConfig(name=bucket_name)


class S3ConfigManager:
  """
  Simplified S3 connector configuration manager.
  No more sources, just connectors with embedded bucket configs.
  """

  def __init__(self):
    self._connectors: Dict[str, ConnectorConfig] = {}
    self._loaded = False

  def load_configurations(self) -> None:
    """Load and validate connector configurations"""
    if self._loaded:
      return

    try:
      self._load_connectors()
      self._validate_configurations()

      self._loaded = True
      LOG.info(f"Successfully loaded {len(self._connectors)} S3 connectors")

    except Exception as e:
      LOG.error(f"Failed to load S3 configurations: {e}")
      raise ConfigurationError(f"Configuration loading failed: {e}")

  def _load_connectors(self) -> None:
    """Load connector configurations from STORAGE_CONNECTORS and legacy AWS_ACCOUNTS"""

    # First, load new STORAGE_CONNECTORS (if any)
    if STORAGE_CONNECTORS.keys():
      for connector_id in STORAGE_CONNECTORS.keys():
        connector_conf = STORAGE_CONNECTORS[connector_id]
        try:
          # Parse bucket configurations
          bucket_configs = {}
          bucket_configs_raw = connector_conf.BUCKET_CONFIGS.get()

          for bucket_name, bucket_conf_dict in bucket_configs_raw.items():
            bucket_configs[bucket_name] = BucketConfig(
              name=bucket_name,
              default_home_path=bucket_conf_dict.get("default_home_path"),
              region=bucket_conf_dict.get("region"),
              options=bucket_conf_dict.get("options"),
            )

          connector = ConnectorConfig(
            id=connector_id,
            provider=connector_conf.PROVIDER.get(),
            auth_type=connector_conf.AUTH_TYPE.get(),
            region=connector_conf.REGION.get(),
            endpoint=connector_conf.ENDPOINT.get(),
            access_key_id=connector_conf.ACCESS_KEY_ID.get(),
            secret_key=connector_conf.SECRET_KEY.get(),
            iam_role=connector_conf.IAM_ROLE.get(),
            bucket_configs=bucket_configs,
            options=connector_conf.OPTIONS.get(),
          )

          self._connectors[connector_id] = connector

          bucket_info = f"with {len(bucket_configs)} buckets" if bucket_configs else "no bucket configs"
          LOG.debug(f"Loaded connector: {connector_id} ({connector.provider}, {connector.auth_type}) {bucket_info}")

        except Exception as e:
          raise ConfigurationError(f"Failed to load connector '{connector_id}': {e}")
    else:
      LOG.debug("No STORAGE_CONNECTORS configuration found")

    # Second, auto-convert legacy AWS_ACCOUNTS (only when storage connectors feature is enabled)
    if USE_STORAGE_CONNECTORS.get():
      legacy_connectors = _load_legacy_aws_accounts_as_connectors()

      for connector_id, connector in legacy_connectors.items():
        # Don't override new STORAGE_CONNECTORS configs
        if connector_id not in self._connectors:
          self._connectors[connector_id] = connector
        else:
          LOG.debug(f"Skipping legacy AWS account '{connector_id}' - already configured in STORAGE_CONNECTORS")

  def _validate_configurations(self) -> None:
    """Validate connector configurations"""
    errors = []

    for connector_id, connector in self._connectors.items():
      try:
        self._validate_connector(connector)
      except ConfigurationError as e:
        errors.append(f"Connector '{connector_id}': {e}")

    if errors:
      raise ConfigurationError("Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors))

  def _validate_connector(self, connector: ConnectorConfig) -> None:
    """Validate a single connector configuration"""
    # Rule: AWS provider requires region
    if connector.provider == "aws" and not connector.region:
      raise ConfigurationError("AWS provider requires 'region' to be specified")

    # Rule: Non-AWS providers require endpoint
    if connector.provider != "aws" and not connector.endpoint:
      raise ConfigurationError(f"Provider '{connector.provider}' requires 'endpoint' to be specified")

    # Rule: Key auth requires access_key_id and secret_key
    if connector.auth_type == "key":
      if not connector.access_key_id:
        raise ConfigurationError("Key authentication requires 'access_key_id'")
      if not connector.secret_key:
        raise ConfigurationError("Key authentication requires 'secret_key'")

    # Rule: RAZ auth requires global RAZ configuration
    if connector.auth_type == "raz":
      if not RAZ.IS_ENABLED.get():
        raise ConfigurationError("RAZ authentication requires global [desktop] [[raz]] configuration to be enabled")

    # Rule: IDBroker auth requires global IDBroker configuration
    if connector.auth_type == "idbroker":
      if not conf_idbroker.is_idbroker_enabled("s3a"):
        raise ConfigurationError("IDBroker authentication requires global IDBroker configuration in core-site.xml")

  def get_connector(self, connector_id: str) -> Optional[ConnectorConfig]:
    """Get connector by ID"""
    self.load_configurations()
    return self._connectors.get(connector_id)

  def get_all_connectors(self) -> Dict[str, ConnectorConfig]:
    """Get all connectors"""
    self.load_configurations()
    return self._connectors.copy()


def get_all_connectors() -> Dict[str, ConnectorConfig]:
  """Get all configured S3 connectors"""
  return S3ConfigManager().get_all_connectors()


def get_connector(connector_id: str) -> Optional[ConnectorConfig]:
  """Get specific connector by ID"""
  return S3ConfigManager().get_connector(connector_id)


def validate_s3_configuration() -> List[str]:
  """
  Validate S3 configuration and return list of validation errors.
  Used by Hue's configuration validation system.
  """
  try:
    S3ConfigManager().load_configurations()
    return []
  except ConfigurationError as e:
    return [str(e)]
  except Exception as e:
    return [f"Unexpected error validating S3 configuration: {e}"]


def get_s3_home_directory(user: Optional[str] = None, connector_id: str = None, bucket_name: str = None) -> str:
  """
  Get S3 home directory with smart defaulting logic.
  Priority is already handled during config loading (REMOTE_STORAGE_HOME vs DEFAULT_HOME_PATH).

  Args:
    user: Optional username for RAZ handling
    connector_id: Optional connector ID (defaults to 'default' or first available)
    bucket_name: Optional bucket name (uses smart bucket selection if not provided)

  Returns:
    S3 home directory path
  """
  try:
    # Smart connector defaulting
    if not connector_id:
      connector_id = get_default_connector()

    connector = get_connector(connector_id)
    if not connector:
      LOG.error(f"Connector '{connector_id}' not found, defaulting to s3a://")
      return "s3a://"

    # Smart bucket defaulting
    if not bucket_name:
      bucket_name = _get_default_bucket_for_connector(connector)

    if bucket_name:
      bucket_config = connector.get_bucket_config(bucket_name)
      return bucket_config.get_effective_home_path(user)

    # No bucket available, return generic path
    return "s3a://"

  except Exception as e:
    LOG.error(f"Failed to get S3 home directory, defaulting to s3a://: {e}")
    return "s3a://"


def get_default_connector() -> str:
  """
  Get the default connector ID using smart selection logic.

  Logic:
  1. Prefer 'default' if it exists
  2. Otherwise return first available
  3. Fall back to 'default' string if no connectors (for error handling)
  """
  try:
    connectors = get_all_connectors()

    # Prefer 'default' if it exists
    if "default" in connectors:
      LOG.debug("Using 'default' connector")
      return "default"

    # Otherwise return first available
    if connectors:
      first_id = next(iter(connectors.keys()))
      LOG.debug(f"No 'default' connector found, using first available: '{first_id}'")
      return first_id

    # No connectors configured - return 'default' for error handling
    LOG.warning("No connectors configured, returning 'default' (will likely fail)")
    return "default"

  except Exception as e:
    LOG.warning(f"Failed to get default connector: {e}")
    return "default"


def _get_default_bucket_for_connector(connector: ConnectorConfig) -> Optional[str]:
  """
  Get default bucket for a connector using smart selection logic.

  Logic:
  - Multiple buckets: Return None (let caller handle bucket-specific logic)
  - Single bucket: Return that bucket name
  - No buckets: Return None
  """
  if not connector.bucket_configs:
    LOG.debug(f"Connector '{connector.id}' has no bucket configs")
    return None

  bucket_names = list(connector.bucket_configs.keys())

  if len(bucket_names) == 1:
    # Single bucket - return it as default
    default_bucket = bucket_names[0]
    LOG.debug(f"Connector '{connector.id}' has single bucket '{default_bucket}', using as default")
    return default_bucket
  elif len(bucket_names) > 1:
    # Multiple buckets - no clear default
    LOG.debug(f"Connector '{connector.id}' has {len(bucket_names)} buckets, no clear default")
    return None

  return None


def extract_bucket_from_path(path: str) -> Optional[str]:
  """Extract bucket name from S3 path"""
  try:
    if not path or not path.startswith(("s3a://", "s3://")):
      return None

    # Parse s3a://bucket-name/path/to/file
    parsed = urlparse(path)
    if parsed.netloc:
      return parsed.netloc
    elif parsed.path:
      # Handle s3a:///bucket-name/path format
      path_parts = parsed.path.strip("/").split("/", 1)
      return path_parts[0] if path_parts[0] else None

    return None
  except Exception as e:
    LOG.error(f"Failed to extract bucket from path: {e}")
    return None


def get_default_bucket_home_path(connector_id: str = None, user: str = None) -> str:
  """
  Get default home path when no specific bucket is provided.

  Smart Logic:
  - Single bucket configured: Use that bucket's home path
  - Multiple buckets: Return s3a:// (generic)
  - No buckets: Return s3a:// (generic)
  """
  try:
    if not connector_id:
      connector_id = get_default_connector()

    connector = get_connector(connector_id)
    if not connector:
      return "s3a://"

    # Check if connector has buckets configured
    if not connector.bucket_configs:
      LOG.debug(f"Connector '{connector_id}' has no bucket configs, using s3a://")
      return "s3a://"

    bucket_names = list(connector.bucket_configs.keys())

    if len(bucket_names) == 1:
      # Single bucket - use its home path as default
      bucket_name = bucket_names[0]
      bucket_config = connector.get_bucket_config(bucket_name)
      home_path = bucket_config.get_effective_home_path(user)
      LOG.debug(f"Using single bucket '{bucket_name}' home path: {home_path}")
      return home_path

    elif len(bucket_names) > 1:
      # Multiple buckets - no clear default, use generic
      LOG.debug(f"Connector '{connector_id}' has {len(bucket_names)} buckets, using generic s3a://")
      return "s3a://"

    return "s3a://"

  except Exception as e:
    LOG.error(f"Failed to get default bucket home path: {e}")
    return "s3a://"


def is_enabled() -> bool:
  """
  Check if Storage Connector S3 system is enabled.
  Equivalent to aws.conf.is_enabled() for the new system.

  Returns:
    True if Storage Connectors are available via:
    - STORAGE_CONNECTORS configuration
    - Legacy AWS_ACCOUNTS (when feature flag enabled)
    - Global RAZ/IDBroker systems
  """
  try:
    # Check if Storage Connectors are directly configured
    if STORAGE_CONNECTORS.keys():
      return True

    # Check if legacy AWS accounts can be auto-converted
    if USE_STORAGE_CONNECTORS.get():
      legacy_connectors = _load_legacy_aws_accounts_as_connectors()
      if legacy_connectors:
        return True

    # Check if global RAZ or IDBroker provide S3 access (same pattern as legacy)
    if is_raz_s3():
      return True

    if conf_idbroker.is_idbroker_enabled("s3a"):
      return True

    return False

  except Exception as e:
    LOG.warning(f"Failed to check Storage Connector S3 availability: {e}")
    return False


def has_s3_access(user) -> bool:
  """
  Check if user has access to Storage Connector S3 system.
  Equivalent to aws.conf.has_s3_access() for the new system.

  Args:
    user: User object to check permissions for

  Returns:
    True if user has S3 access via Storage Connectors
  """
  try:
    # Same user validation logic as legacy
    if not (user.is_authenticated and user.is_active):
      return False

    from desktop.auth.backend import is_admin

    # Admin always has access
    if is_admin(user):
      return True

    # Check if user has S3 permission
    if user.has_hue_permission(action="s3_access", app="filebrowser"):
      return True

    # RAZ users get access if system is enabled
    if is_raz_s3():
      return True

    return False

  except Exception as e:
    LOG.warning(f"Failed to check Storage Connector S3 access for user {user}: {e}")
    return False


def is_raz_s3() -> bool:
  """
  Check if RAZ S3 is enabled for Storage Connector system.
  Equivalent to aws.conf.is_raz_s3() for the new system.

  Returns:
    True if RAZ is enabled AND at least one storage connector exists
  """
  try:
    # Must have RAZ enabled globally
    if not RAZ.IS_ENABLED.get():
      return False

    # Must have at least one storage connector (like legacy AWS_ACCOUNTS check)
    connectors = get_all_connectors()
    if not connectors:
      return False

    # RAZ can work with any connector, so any connector + RAZ = RAZ S3 enabled for now
    return True

  except Exception as e:
    LOG.warning(f"Failed to check Storage Connector RAZ S3 status: {e}")
    return False
