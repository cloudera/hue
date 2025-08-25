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
Centralized TLS utilities for Hue components.

This module provides optimized, cached, and consistent TLS functionality
across HTTP clients, Thrift clients, and Gunicorn server.
"""

import ssl
import logging
import threading
from functools import lru_cache
from typing import Optional, Tuple, Dict, Any
from enum import Enum

LOG = logging.getLogger(__name__)

# Thread-safe cache for TLS support detection
_tls_support_cache = {}
_tls_cache_lock = threading.RLock()

class TLSVersion(Enum):
    """Supported TLS versions in order of preference."""
    TLS_1_3 = "1.3"
    TLS_1_2 = "1.2"
    TLS_1_1 = "1.1"
    TLS_1_0 = "1.0"

class TLSCipherSuite:
    """Standard TLS cipher suites organized by version."""
    # TLS 1.3 cipher suites (RFC 8446)
    TLS13_CIPHERS = [
        'TLS_AES_128_GCM_SHA256',
        'TLS_AES_256_GCM_SHA384', 
        'TLS_CHACHA20_POLY1305_SHA256'
    ]
    # TLS 1.3 compatible algorithms in TLS 1.2 format
    TLS13_COMPATIBLE_ALGORITHMS = [
        'AES128-GCM',
        'AES256-GCM', 
        'CHACHA20-POLY1305'
    ]
    # Recommended TLS 1.2 cipher suites (Mozilla Intermediate)
    TLS12_CIPHERS = [
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-ECDSA-AES128-GCM-SHA256',
        'ECDHE-ECDSA-AES256-GCM-SHA384',
        'ECDHE-RSA-CHACHA20-POLY1305',
        'ECDHE-ECDSA-CHACHA20-POLY1305'
    ]

@lru_cache(maxsize=1)
def get_system_tls_capabilities() -> Dict[str, Any]:
    """
    Get system TLS capabilities with caching.
    
    Returns:
        Dict containing system TLS support information
    """
    try:
        capabilities = {
            'has_ssl_module': True,
            'has_tls13': hasattr(ssl, 'HAS_TLSv1_3') and ssl.HAS_TLSv1_3,
            'has_protocol_tls': hasattr(ssl, 'PROTOCOL_TLS'),
            'has_tlsversion_enum': hasattr(ssl, 'TLSVersion'),
            'has_create_default_context': hasattr(ssl, 'create_default_context'),
            'has_sslcontext': hasattr(ssl, 'SSLContext'),
            'openssl_version': ssl.OPENSSL_VERSION if hasattr(ssl, 'OPENSSL_VERSION') else 'Unknown',
            'ssl_version': ssl.OPENSSL_VERSION_INFO if hasattr(ssl, 'OPENSSL_VERSION_INFO') else None
        }
        
        # Check for TLS version constants
        if capabilities['has_tlsversion_enum']:
            capabilities['available_tls_versions'] = []
            for version in ['TLSv1', 'TLSv1_1', 'TLSv1_2']:
                if hasattr(ssl.TLSVersion, version):
                    capabilities['available_tls_versions'].append(version)
            if hasattr(ssl.TLSVersion, 'TLSv1_3'):
                capabilities['available_tls_versions'].append('TLSv1_3')
        LOG.debug(f"TLS system capabilities: {capabilities}")
        return capabilities
    except ImportError:
        LOG.warning("SSL module not available")
        return {'has_ssl_module': False}

def check_cipher_compatibility(cipher_list: str, tls_version: TLSVersion = TLSVersion.TLS_1_3) -> bool:
    """
    Check if cipher list contains compatible ciphers for specified TLS version.
    
    Args:
        cipher_list: Colon-separated cipher list
        tls_version: TLS version to check compatibility for
        
    Returns:
        True if compatible ciphers are found
    """
    if not cipher_list:
        return False
        
    cipher_list_upper = cipher_list.upper()
    
    if tls_version == TLSVersion.TLS_1_3:
        # Check for TLS 1.3 cipher suites
        if any(cipher in cipher_list_upper for cipher in TLSCipherSuite.TLS13_CIPHERS):
            return True
        # Fallback: Check for TLS 1.3 compatible algorithms
        return any(alg in cipher_list_upper for alg in TLSCipherSuite.TLS13_COMPATIBLE_ALGORITHMS)
    
    elif tls_version == TLSVersion.TLS_1_2:
        return any(cipher.replace('-', '_').upper() in cipher_list_upper.replace('-', '_') 
                  for cipher in TLSCipherSuite.TLS12_CIPHERS)
    return False

def get_optimal_ssl_protocol() -> int:
    """
    Get the optimal SSL protocol constant based on system capabilities and configuration.
    
    Returns:
        ssl.PROTOCOL_* constant for the best available TLS version
    """
    from desktop import conf
    
    capabilities = get_system_tls_capabilities()
    
    if not capabilities.get('has_ssl_module'):
        LOG.error("SSL module not available")
        return getattr(ssl, 'PROTOCOL_SSLv23', 2)  # Fallback
    
    # Check if TLS 1.3 is enabled and supported
    if (conf.SSL_TLS13_ENABLED.get() and 
        capabilities.get('has_tls13') and 
        capabilities.get('has_protocol_tls')):
        LOG.debug("Using ssl.PROTOCOL_TLS with TLS 1.3 support")
        return ssl.PROTOCOL_TLS
    # Fallback to TLS 1.2
    if hasattr(ssl, 'PROTOCOL_TLSv1_2'):
        LOG.debug("Using ssl.PROTOCOL_TLSv1_2")
        return ssl.PROTOCOL_TLSv1_2
    # Final fallback
    LOG.warning("Using fallback SSL protocol")
    return getattr(ssl, 'PROTOCOL_SSLv23', 2)

def create_ssl_context(
    purpose: str = 'client',
    validate_certs: bool = True,
    ca_certs: Optional[str] = None,
    keyfile: Optional[str] = None,
    certfile: Optional[str] = None,
    check_hostname: bool = True
) -> Optional[ssl.SSLContext]:
    """
    Create an optimized SSL context with TLS 1.3 support.
    
    Args:
        purpose: 'client' or 'server' context
        validate_certs: Whether to validate certificates
        ca_certs: Path to CA certificates
        keyfile: Path to private key
        certfile: Path to certificate
        check_hostname: Whether to check hostname
        
    Returns:
        Configured SSLContext or None if creation fails
    """
    from desktop import conf
    
    try:
        capabilities = get_system_tls_capabilities()
        
        if not capabilities.get('has_ssl_module'):
            LOG.error("SSL module not available for context creation")
            return None
        
        # Create context with best available method
        if capabilities.get('has_create_default_context'):
            if purpose == 'server':
                context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            else:
                context = ssl.create_default_context()
        elif capabilities.get('has_sslcontext'):
            protocol = get_optimal_ssl_protocol()
            context = ssl.SSLContext(protocol)
        else:
            LOG.warning("SSLContext not available")
            return None
        
        # Configure TLS 1.2 ciphers
        try:
            cipher_list = conf.SSL_CIPHER_LIST.get()
            context.set_ciphers(cipher_list)
            LOG.debug(f"Set TLS 1.2 cipher list: {cipher_list[:50]}...")
        except Exception as e:
            LOG.warning(f"Could not set TLS 1.2 ciphers: {e}")
        # Configure TLS 1.3 ciphersuites if supported
        if (conf.SSL_TLS13_ENABLED.get() and 
            capabilities.get('has_tls13') and 
            hasattr(context, 'set_ciphersuites')):
            try:
                tls13_ciphersuites = conf.SSL_TLS13_CIPHER_SUITES.get()
                context.set_ciphersuites(tls13_ciphersuites)
                LOG.debug(f"Set TLS 1.3 ciphersuites: {tls13_ciphersuites}")
            except Exception as e:
                LOG.debug(f"Could not set TLS 1.3 ciphersuites: {e}")
        # Configure protocol version limits
        if (capabilities.get('has_tlsversion_enum') and 
            hasattr(context, 'minimum_version')):
            try:
                # Set minimum to TLS 1.2
                context.minimum_version = ssl.TLSVersion.TLSv1_2
                # Set maximum based on configuration
                if (conf.SSL_TLS13_ENABLED.get() and 
                    capabilities.get('has_tls13') and
                    hasattr(ssl.TLSVersion, 'TLSv1_3')):
                    context.maximum_version = ssl.TLSVersion.TLSv1_3
                    LOG.debug("Set TLS version range: 1.2 to 1.3")
                else:
                    context.maximum_version = ssl.TLSVersion.TLSv1_2
                    LOG.debug("Set TLS version range: 1.2 to 1.2")
            except Exception as e:
                LOG.debug(f"Could not set TLS version limits: {e}")
        
        # Configure certificate validation
        if validate_certs:
            context.check_hostname = check_hostname
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
                LOG.debug("Loaded client certificate")
            except Exception as e:
                LOG.warning(f"Could not load client certificate: {e}")
        # Log final configuration
        tls13_enabled = conf.SSL_TLS13_ENABLED.get() and capabilities.get('has_tls13')
        LOG.info(f"SSL context created for {purpose} with TLS 1.3: {tls13_enabled}")
        return context
    except Exception as e:
        LOG.error(f"Failed to create SSL context: {e}")
        return None

def get_tls_configuration_summary() -> Dict[str, Any]:
    """
    Get a comprehensive summary of TLS configuration.
    
    Returns:
        Dict containing TLS configuration details
    """
    from desktop import conf
    
    capabilities = get_system_tls_capabilities()
    
    summary = {
        'system': capabilities,
        'configuration': {
            'tls13_enabled': conf.SSL_TLS13_ENABLED.get(),
            'tls13_cipher_suites': conf.SSL_TLS13_CIPHER_SUITES.get(),
            'tls12_cipher_list': conf.SSL_CIPHER_LIST.get(),
            'ssl_validate': conf.SSL_VALIDATE.get(),
        },
        'compatibility': {
            'can_use_tls13': (
                capabilities.get('has_tls13', False) and
                conf.SSL_TLS13_ENABLED.get() and
                check_cipher_compatibility(conf.SSL_TLS13_CIPHER_SUITES.get(), TLSVersion.TLS_1_3)
            ),
            'optimal_protocol': 'TLS 1.3' if (
                capabilities.get('has_tls13') and conf.SSL_TLS13_ENABLED.get()
            ) else 'TLS 1.2'
        }
    }
    return summary

# Cached version of TLS support check
@lru_cache(maxsize=1)
def has_tls13_support_cached() -> bool:
    """
    Cached version of TLS 1.3 support check for performance.
    
    Returns:
        True if TLS 1.3 is fully supported and configured
    """
    from desktop import conf
    
    try:
        capabilities = get_system_tls_capabilities()
        
        # System support check
        if not capabilities.get('has_tls13'):
            return False
        
        # Configuration check
        if not conf.SSL_TLS13_ENABLED.get():
            return False
        # Cipher compatibility check
        try:
            tls13_ciphersuites = conf.SSL_TLS13_CIPHER_SUITES.get()
            if check_cipher_compatibility(tls13_ciphersuites, TLSVersion.TLS_1_3):
                return True
            # Fallback: Check TLS 1.2 cipher compatibility
            tls12_ciphers = conf.SSL_CIPHER_LIST.get()
            return check_cipher_compatibility(tls12_ciphers, TLSVersion.TLS_1_3)
        except (NameError, AttributeError):
            # Configuration not yet available
            return True
    except Exception as e:
        LOG.debug(f"TLS 1.3 support check failed: {e}")
        return False

def clear_tls_cache():
    """Clear all TLS-related caches."""
    global _tls_support_cache
    with _tls_cache_lock:
        _tls_support_cache.clear()
    # Clear function caches
    get_system_tls_capabilities.cache_clear()
    has_tls13_support_cached.cache_clear()
    LOG.debug("TLS caches cleared")
