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
Common TLS utilities for Hue components.

This module provides centralized TLS configuration functionality that can be used
across different Hue components including Gunicorn server, HTTP client, and Thrift client.
"""

import logging

LOG = logging.getLogger(__name__)


def get_tls_settings():
  """
  Get TLS configuration settings based on Hue configuration.

  Returns:
    dict: Dictionary containing TLS configuration settings including:
      - tls_minimum_version: Minimum TLS version (e.g., "TLSv1.2", "TLSv1.3")
      - tls_maximum_version: Maximum TLS version (e.g., "TLSv1.2", "TLSv1.3")
      - ciphers: Cipher list for TLS 1.2 (empty for TLS 1.3)
      - ssl_version: SSL protocol constant name for compatibility
      - error: Error message if SSL module not available
  """
  from desktop import conf

  tls_settings = {}
  try:
    import ssl

    # Check for both TLS 1.3 and TLS 1.2
    tls13_enabled = conf.SSL_TLS13_ENABLED.get()
    tls12_enabled = conf.SSL_TLS12_ENABLED.get()

    # Set default values for minimum and maximum versions
    min_version = "TLSv1.2"
    max_version = "TLSv1.2"
    ciphers = conf.SSL_CIPHER_LIST.get()

    if tls13_enabled:
      max_version = "TLSv1.3"
      ciphers = ""  # Ciphers are not configurable for TLS 1.3
    if tls13_enabled and tls12_enabled:
      min_version = "TLSv1.2"
    elif tls13_enabled and not tls12_enabled:
      min_version = "TLSv1.3"

    tls_settings["tls_maximum_version"] = max_version
    tls_settings["tls_minimum_version"] = min_version
    tls_settings["ciphers"] = ciphers

    # Check for SSL version protocol and assign
    if hasattr(ssl, "PROTOCOL_TLS"):
      tls_settings["ssl_version"] = "PROTOCOL_TLS"
    else:
      tls_settings["ssl_version"] = "PROTOCOL_TLSv1_2"

  except ImportError:
    tls_settings["error"] = "SSL module not available"
    LOG.error("SSL module not available")

  return tls_settings


def create_ssl_context(validate=True, ca_certs=None, keyfile=None, certfile=None):
  """
  Create an SSL context based on Hue TLS configuration.

  Args:
    validate: Whether to validate server certificates
    ca_certs: Path to CA certificates file
    keyfile: Path to client private key file
    certfile: Path to client certificate file

  Returns:
    ssl.SSLContext: Configured SSL context or None if creation failed
  """
  try:
    import ssl

    # Get TLS settings from centralized configuration
    tls_settings = get_tls_settings()

    # Check for errors in TLS settings
    if "error" in tls_settings:
      LOG.error(f"TLS configuration error: {tls_settings['error']}")
      return None

    # Create SSL context with the best available protocol
    if hasattr(ssl, 'create_default_context'):
      context = ssl.create_default_context()
    elif hasattr(ssl, 'SSLContext'):
      # Use the SSL version from TLS settings
      ssl_version = tls_settings.get("ssl_version", "PROTOCOL_TLSv1_2")
      if ssl_version == "PROTOCOL_TLS" and hasattr(ssl, 'PROTOCOL_TLS'):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
      else:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    else:
      LOG.warning("SSLContext not available")
      return None

    # Configure ciphers from TLS settings
    cipher_list = tls_settings.get("ciphers", "")
    if cipher_list:
      try:
        context.set_ciphers(cipher_list)
        LOG.debug(f"SSL context configured with ciphers: {cipher_list}")
      except Exception as e:
        LOG.debug(f"Could not set ciphers: {e}")

    # Configure TLS 1.3 ciphersuites if TLS 1.3 is enabled
    max_version = tls_settings.get("tls_maximum_version")
    if (max_version == "TLSv1.3" and
        hasattr(context, 'set_ciphersuites') and
        hasattr(ssl, 'HAS_TLSv1_3') and
        ssl.HAS_TLSv1_3):
      try:
        # Use standard TLS 1.3 ciphersuites
        ciphersuites = 'TLS_AES_128_GCM_SHA256:TLS_AES_256_GCM_SHA384'
        context.set_ciphersuites(ciphersuites)
        LOG.debug(f"SSL context configured with TLS 1.3 ciphersuites: {ciphersuites}")
      except Exception as e:
        LOG.debug(f"Could not set TLS 1.3 ciphersuites: {e}")

    # Configure protocol version limits from TLS settings
    if hasattr(ssl, 'TLSVersion') and hasattr(context, 'minimum_version'):
      try:
        min_version = tls_settings.get("tls_minimum_version")
        max_version = tls_settings.get("tls_maximum_version")

        # Set minimum version
        if min_version == "TLSv1.3" and hasattr(ssl.TLSVersion, 'TLSv1_3'):
          context.minimum_version = ssl.TLSVersion.TLSv1_3
        else:
          context.minimum_version = ssl.TLSVersion.TLSv1_2

        # Set maximum version
        if max_version == "TLSv1.3" and hasattr(ssl.TLSVersion, 'TLSv1_3'):
          context.maximum_version = ssl.TLSVersion.TLSv1_3
        else:
          context.maximum_version = ssl.TLSVersion.TLSv1_2

      except Exception as e:
        LOG.debug(f"Could not set TLS version limits: {e}")

    # Configure certificate verification
    if validate:
      context.check_hostname = True
      context.verify_mode = ssl.CERT_REQUIRED
      if ca_certs:
        context.load_verify_locations(ca_certs)
    else:
      context.check_hostname = False
      context.verify_mode = ssl.CERT_NONE

    # Load client certificate if provided
    if keyfile and certfile:
      try:
        context.load_cert_chain(certfile, keyfile)
        LOG.debug("Loaded client certificate for SSL context")
      except Exception as e:
        LOG.warning(f"Could not load client certificate: {e}")

    min_ver = tls_settings.get('tls_minimum_version')
    max_ver = tls_settings.get('tls_maximum_version')
    LOG.info(f"SSL context created with TLS version range: {min_ver} to {max_ver}")
    return context

  except Exception as e:
    LOG.error(f"Failed to create SSL context: {e}")
    return None


def get_ssl_protocol():
  """
  Get the optimal SSL protocol for connections based on configuration.

  Returns:
    ssl.PROTOCOL constant for the best available TLS version
  """
  from desktop import conf

  try:
    import ssl

    # Check if TLS 1.3 is enabled and supported
    if conf.SSL_TLS13_ENABLED.get() and hasattr(ssl, 'HAS_TLSv1_3') and ssl.HAS_TLSv1_3:
      if hasattr(ssl, 'PROTOCOL_TLS'):
        LOG.info("Using ssl.PROTOCOL_TLS with TLS 1.3 support")
        return ssl.PROTOCOL_TLS
      else:
        LOG.warning("TLS 1.3 requested but PROTOCOL_TLS not available, using TLS 1.2")
        return ssl.PROTOCOL_TLSv1_2
    else:
      LOG.info("Using TLS 1.2 (TLS 1.3 disabled or not supported)")
      return ssl.PROTOCOL_TLSv1_2

  except ImportError:
    LOG.error("SSL module not available")
    return 2  # Fallback to a basic SSL protocol


def create_thrift_ssl_context(validate=True, ca_certs=None, keyfile=None, certfile=None):
  """
  Create an SSL context specifically configured for Thrift connections.

  This is a specialized version of create_ssl_context that handles Thrift-specific
  requirements like hostname validation.

  Args:
    validate: Whether to validate server certificates
    ca_certs: Path to CA certificates
    keyfile: Path to client private key
    certfile: Path to client certificate

  Returns:
    ssl.SSLContext configured for Thrift connections or None if creation failed
  """
  context = create_ssl_context(validate, ca_certs, keyfile, certfile)

  if context and validate:
    # Thrift handles hostname validation separately
    context.check_hostname = False

  return context


def create_http_ssl_context():
  """
  Create an SSL context specifically configured for HTTP client connections.

  Returns:
    ssl.SSLContext configured for HTTP client connections or None if creation failed
  """
  from desktop import conf

  return create_ssl_context(
    validate=conf.SSL_VALIDATE.get(),
    ca_certs=conf.SSL_CACERTS.get() if conf.SSL_VALIDATE.get() else None
  )
