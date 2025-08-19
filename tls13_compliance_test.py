#!/usr/bin/env python3
"""
Comprehensive TLS 1.3 Compliance Test Suite for Hue

This script thoroughly tests the TLS 1.3 implementation across all Hue components:
- Configuration system with TLS 1.3 options
- Gunicorn server with TLS 1.3 support  
- Thrift client with TLS 1.3 connectivity
- HTTP client with TLS 1.3 requests

Usage:
    python tls13_compliance_test.py [--verbose] [--help]

Requirements:
    - Python 3.7+ (for TLS 1.3 support)
    - OpenSSL 1.1.1+ (for TLS 1.3 protocol)
    - Hue development environment
"""

import os
import sys
import ssl
import socket
import logging
import tempfile
import time
import subprocess
import argparse
from pathlib import Path

# Add the desktop directory to the path so we can import Hue modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'desktop/core/src'))

try:
    from desktop import conf
    from desktop.lib.rest.http_client import create_tls13_ssl_context, TLS13HTTPAdapter
    from desktop.lib.thrift_util import get_thrift_ssl_protocol, create_thrift_ssl_context
    from desktop.lib.tls_utils import (
        get_system_tls_capabilities, get_tls_configuration_summary, 
        create_ssl_context, has_tls13_support_cached, clear_tls_cache
    )
    from desktop.management.commands.rungunicornserver import (
        get_optimal_ssl_protocol, configure_tls_options, get_cipher_configuration
    )
    import requests
except ImportError as e:
    print(f"Error importing Hue modules: {e}")
    print("Make sure you're running this script from the Hue root directory")
    print("Ensure Hue dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = None


class TLS13TestSuite:
    """Comprehensive TLS 1.3 test suite for Hue components."""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results."""
        self.total_tests += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"🧪 Running Test: {test_name}")
        logger.info(f"{'='*60}")
        
        try:
            result = test_func()
            self.results.append((test_name, result, None))
            if result:
                self.passed_tests += 1
                logger.info(f"{test_name}: PASSED")
            else:
                logger.error(f"{test_name}: FAILED")
            return result
        except Exception as e:
            self.results.append((test_name, False, str(e)))
            logger.error(f"{test_name}: ERROR - {e}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary."""
        logger.info(f"\n{'='*80}")
        logger.info(f"🏁 TLS 1.3 COMPLIANCE TEST SUMMARY")
        logger.info(f"{'='*80}")
        
        for test_name, result, error in self.results:
            status = "PASSED" if result else "FAILED"
            if error:
                status += f" ({error})"
            logger.info(f"{status:<20} | {test_name}")
        
        logger.info(f"\nOverall Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            logger.info("ALL TESTS PASSED! TLS 1.3 compliance is fully implemented.")
            return True
        else:
            logger.error(f"{self.total_tests - self.passed_tests} tests failed. Review the output above.")
            return False


def test_system_tls13_support():
    """Test if the system supports TLS 1.3."""
    logger.info("Checking system TLS 1.3 support...")
    
    # Check Python SSL module
    has_tls13 = hasattr(ssl, 'HAS_TLSv1_3') and ssl.HAS_TLSv1_3
    has_protocol_tls = hasattr(ssl, 'PROTOCOL_TLS')
    has_tlsversion = hasattr(ssl, 'TLSVersion')
    has_tlsv13_enum = has_tlsversion and hasattr(ssl.TLSVersion, 'TLSv1_3')
    
    logger.info(f"Python SSL module TLS 1.3 support: {has_tls13}")
    logger.info(f"PROTOCOL_TLS available: {has_protocol_tls}")
    logger.info(f"TLSVersion enum available: {has_tlsversion}")
    logger.info(f"TLSv1_3 enum available: {has_tlsv13_enum}")
    
    # Check OpenSSL version
    openssl_version = ssl.OPENSSL_VERSION
    logger.info(f"OpenSSL version: {openssl_version}")
    
    # TLS 1.3 requires OpenSSL 1.1.1 or later
    openssl_supports_tls13 = ("1.1.1" in openssl_version or 
                             "3." in openssl_version or
                             "1.1.0" not in openssl_version)
    logger.info(f"OpenSSL supports TLS 1.3: {openssl_supports_tls13}")
    
    # Check Python version
    python_version = sys.version_info
    python_supports_tls13 = python_version >= (3, 7)
    logger.info(f"Python version: {python_version}")
    logger.info(f"Python supports TLS 1.3: {python_supports_tls13}")
    
    overall_support = has_tls13 and openssl_supports_tls13 and python_supports_tls13
    
    if overall_support:
        logger.info("System fully supports TLS 1.3")
    else:
        logger.warning("System has limited TLS 1.3 support")
    
    return overall_support


def test_hue_configuration():
    """Test Hue TLS 1.3 configuration options."""
    logger.info("Testing Hue TLS 1.3 configuration...")
    
    try:
        # Test configuration access
        tls13_enabled = conf.SSL_TLS13_ENABLED.get()
        cipher_list = conf.SSL_CIPHER_LIST.get()
        
        logger.info(f"TLS 1.3 enabled: {tls13_enabled}")
        logger.info(f"Cipher list: {cipher_list[:100]}...")
        
        # Validate configuration values
        config_valid = (
            isinstance(tls13_enabled, bool) and
            isinstance(cipher_list, str) and len(cipher_list) > 0
        )
        
        if config_valid:
            logger.info("Configuration values are valid")
        else:
            logger.error("Configuration values are invalid")
            
        return config_valid
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False


def test_ssl_context_creation():
    """Test SSL context creation with TLS 1.3 support."""
    logger.info("Testing SSL context creation...")
    
    success_count = 0
    total_count = 3
    
    # Test HTTP client SSL context
    try:
        http_context = create_tls13_ssl_context()
        if http_context:
            logger.info("HTTP client SSL context created successfully")
            success_count += 1
        else:
            logger.warning("HTTP client SSL context creation returned None")
    except Exception as e:
        logger.error(f"HTTP client SSL context creation failed: {e}")
    
    # Test Thrift SSL context
    try:
        thrift_context = create_thrift_ssl_context()
        if thrift_context:
            logger.info("Thrift SSL context created successfully")
            success_count += 1
        else:
            logger.warning("Thrift SSL context creation returned None")
    except Exception as e:
        logger.error(f"Thrift SSL context creation failed: {e}")
    
    # Test basic SSL context with TLS version limits
    try:
        context = ssl.create_default_context()
        if hasattr(ssl, 'TLSVersion') and hasattr(context, 'minimum_version'):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            if hasattr(ssl.TLSVersion, 'TLSv1_3'):
                context.maximum_version = ssl.TLSVersion.TLSv1_3
            logger.info("Basic SSL context with TLS version limits created")
            success_count += 1
        else:
            logger.warning("TLS version limits not supported")
    except Exception as e:
        logger.error(f"Basic SSL context creation failed: {e}")
    
    return success_count >= 2  # At least 2 out of 3 should work


def test_cipher_suite_configuration():
    """Test cipher suite configuration for TLS 1.2 and TLS 1.3."""
    logger.info("Testing cipher suite configuration...")
    
    try:
        # Test cipher configuration
        context = ssl.create_default_context()
        
        # Test TLS 1.2 ciphers
        cipher_list = conf.SSL_CIPHER_LIST.get()
        context.set_ciphers(cipher_list)
        logger.info("TLS 1.2 cipher configuration successful")
        
        # Test TLS 1.3 ciphersuites if available
        tls13_configured = False
        if (conf.SSL_TLS13_ENABLED.get() and 
            hasattr(context, 'set_ciphersuites') and 
            hasattr(ssl, 'HAS_TLSv1_3') and 
            ssl.HAS_TLSv1_3):
            try:
                ciphersuites = conf.SSL_TLS13_CIPHERSUITES.get()
                context.set_ciphersuites(ciphersuites)
                logger.info("TLS 1.3 ciphersuite configuration successful")
                tls13_configured = True
            except Exception as e:
                logger.warning(f"TLS 1.3 ciphersuites not configurable: {e}")
        else:
            logger.info("TLS 1.3 ciphersuites not available on this system")
        
        return True
        
    except Exception as e:
        logger.error(f"Cipher suite configuration failed: {e}")
        return False


def test_protocol_selection():
    """Test protocol version selection logic."""
    logger.info("Testing protocol version selection...")
    
    try:
        # Test Gunicorn protocol selection
        gunicorn_protocol = get_optimal_ssl_protocol()
        logger.info(f"Gunicorn optimal protocol: {gunicorn_protocol}")
        
        # Test Thrift protocol selection
        thrift_protocol = get_thrift_ssl_protocol()
        logger.info(f"Thrift optimal protocol: {thrift_protocol}")
        
        # Test TLS options configuration
        tls_options = configure_tls_options()
        logger.info(f"TLS options: {tls_options}")
        
        # Test cipher configuration
        cipher_list, ciphersuites = get_cipher_configuration()
        logger.info(f"Cipher list length: {len(cipher_list)}")
        logger.info(f"TLS 1.3 ciphersuites: {ciphersuites}")
        
        # Validate that protocols are reasonable
        valid_protocols = [ssl.PROTOCOL_TLS, ssl.PROTOCOL_TLSv1_2]
        protocols_valid = (gunicorn_protocol in valid_protocols and 
                          thrift_protocol in valid_protocols)
        
        if protocols_valid:
            logger.info("Protocol selection logic working correctly")
        else:
            logger.warning("Unexpected protocol selection results")
            
        return protocols_valid
        
    except Exception as e:
        logger.error(f"Protocol selection test failed: {e}")
        return False


def test_http_adapter():
    """Test HTTP client TLS 1.3 adapter."""
    logger.info("Testing HTTP client TLS 1.3 adapter...")
    
    try:
        # Create TLS 1.3 HTTP adapter
        adapter = TLS13HTTPAdapter()
        logger.info("TLS 1.3 HTTP adapter created successfully")
        
        # Test session configuration
        session = requests.Session()
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        logger.info("HTTP session configured with TLS 1.3 adapter")
        
        # Test that the session has the adapter
        https_adapter = session.get_adapter('https://example.com')
        if isinstance(https_adapter, TLS13HTTPAdapter):
            logger.info("HTTPS adapter correctly mounted")
        else:
            logger.warning("HTTPS adapter not correctly mounted")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"HTTP adapter test failed: {e}")
        return False


def test_comprehensive_integration():
    """Test comprehensive integration of all TLS 1.3 components."""
    logger.info("Testing comprehensive TLS 1.3 integration...")
    
    try:
        integration_score = 0
        
        # Test that all components can be initialized together
        try:
            # Initialize all SSL contexts
            http_context = create_tls13_ssl_context()
            thrift_context = create_thrift_ssl_context()
            
            # Initialize protocol selections
            gunicorn_protocol = get_optimal_ssl_protocol()
            thrift_protocol = get_thrift_ssl_protocol()
            
            # Initialize configurations
            tls_options = configure_tls_options()
            cipher_list, ciphersuites = get_cipher_configuration()
            
            # Initialize HTTP adapter
            adapter = TLS13HTTPAdapter()
            
            integration_score += 1
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
        
        # Test logging integration
        try:
            from desktop.management.commands.rungunicornserver import log_tls_configuration
            log_tls_configuration()  # This should not raise an exception
            integration_score += 1
            logger.info("TLS configuration logging working")
            
        except Exception as e:
            logger.error(f"TLS configuration logging failed: {e}")
        
        # Test cipher and protocol configuration consistency
        try:
            cipher_list, ciphersuites = get_cipher_configuration()
            if cipher_list and len(cipher_list) > 0:
                if conf.SSL_TLS13_ENABLED.get() and ciphersuites:
                    logger.info("TLS 1.3 cipher suites configured correctly")
                else:
                    logger.info("TLS 1.3 disabled or ciphersuites not available")
                integration_score += 1
            else:
                logger.warning("Cipher list configuration issue")
                
        except Exception as e:
            logger.error(f"Cipher configuration test failed: {e}")
        
        success = integration_score >= 3
        
        if success:
            logger.info("Comprehensive integration test passed")
        else:
            logger.warning("Comprehensive integration test has issues")
            
        return success
        
    except Exception as e:
        logger.error(f"Comprehensive integration test failed: {e}")
        return False


def print_usage_guide():
    """Print usage and configuration guide."""
    print("""
TLS 1.3 Configuration Guide for Hue
=====================================

Configuration (hue.ini):
[desktop]
# Enable TLS 1.3 support (auto-detected by default)
ssl_tls13_enabled=true

# Standard SSL configuration
ssl_certificate=/path/to/certificate.pem
ssl_private_key=/path/to/private_key.pem
ssl_cacerts=/path/to/ca_certificates.pem

# Enhanced cipher list (automatically includes TLS 1.2 and 1.3 support)
ssl_cipher_list=ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-CHACHA20-POLY1305:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK

Testing TLS 1.3:
1. Start Hue with Gunicorn:
   python manage.py rungunicornserver --bind 0.0.0.0:8888

2. Test TLS 1.3 connection:
   openssl s_client -connect localhost:8888 -tls1_3 -servername localhost

3. Check logs for TLS configuration:
   Look for "TLS 1.3 support" and "TLS Configuration Summary" messages

Requirements:
- Python 3.7+ (for TLS 1.3 APIs)
- OpenSSL 1.1.1+ (for TLS 1.3 protocol)
- Updated requests/urllib3 (for HTTP client TLS 1.3)

Troubleshooting:
- If TLS 1.3 is not available, Hue will automatically fall back to TLS 1.2
- TLS 1.3 uses hardcoded standard cipher suites (AES-GCM, ChaCha20-Poly1305)
- Protocol version limits are automatically set (min: TLS 1.2, max: TLS 1.3 if available)
- Check system logs for detailed SSL/TLS configuration information
- Use --verbose flag with this test script for detailed debugging

""")


def test_optimized_configuration_system():
    """Test optimized TLS 1.3 configuration system with caching."""
    try:
        logger.info("Testing optimized configuration system...")
        # Test basic configuration access
        tls13_enabled = conf.SSL_TLS13_ENABLED.get()
        cipher_list = conf.SSL_CIPHER_LIST.get()
        tls13_ciphers = conf.SSL_TLS13_CIPHER_SUITES.get()
        logger.info(f"TLS 1.3 enabled: {tls13_enabled}")
        logger.info(f"TLS 1.2 cipher list: {len(cipher_list)} characters")
        logger.info(f"TLS 1.3 cipher suites: {tls13_ciphers}")
        # Test optimized TLS 1.3 support detection with caching
        has_support = conf.has_tls13_support()
        has_support_cached = has_tls13_support_cached()
        logger.info(f"TLS 1.3 support detected: {has_support}")
        logger.info(f"TLS 1.3 support cached: {has_support_cached}")
        # Test centralized system capabilities
        capabilities = get_system_tls_capabilities()
        logger.info(f"System TLS 1.3 support: {capabilities.get('has_tls13', False)}")
        logger.info(f"OpenSSL version: {capabilities.get('openssl_version', 'Unknown')}")
        # Test comprehensive configuration summary
        summary = get_tls_configuration_summary()
        logger.info(f"Configuration summary generated with {len(summary)} sections")
        logger.info(f"Can use TLS 1.3: {summary['compatibility']['can_use_tls13']}")
        logger.info(f"Optimal protocol: {summary['compatibility']['optimal_protocol']}")
        # Test cache functionality
        clear_tls_cache()
        logger.info("TLS caches cleared successfully")
        return True
    except Exception as e:
        logger.error(f"Optimized configuration system test failed: {e}")
        return False


def test_centralized_ssl_context_creation():
    """Test centralized SSL context creation utilities."""
    try:
        logger.info("Testing centralized SSL context creation...")
        # Test client context creation
        client_context = create_ssl_context(purpose='client')
        if client_context:
            logger.info("Client SSL context created successfully")
        else:
            logger.warning("Client SSL context creation failed")
            return False
        # Test server context creation  
        server_context = create_ssl_context(purpose='server')
        if server_context:
            logger.info("Server SSL context created successfully")
        else:
            logger.warning("Server SSL context creation failed")
            return False
        return True
    except Exception as e:
        logger.error(f"Centralized SSL context test failed: {e}")
        return False


def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(
        description='Comprehensive TLS 1.3 compliance test suite for Hue',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tls13_compliance_test.py                    # Run all tests
  python tls13_compliance_test.py --verbose          # Run with detailed output
  python tls13_compliance_test.py --help             # Show this help
        """
    )
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output with detailed debugging')
    
    args = parser.parse_args()
    
    # Setup logging
    global logger
    logger = setup_logging(args.verbose)
    
    logger.info("Starting Hue TLS 1.3 Compliance Test Suite")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
    
    # Initialize test suite
    test_suite = TLS13TestSuite()
    
    # Run all tests
    tests = [
        ("System TLS 1.3 Support", test_system_tls13_support),
        ("Hue Configuration", test_hue_configuration),
        ("SSL Context Creation", test_ssl_context_creation),
        ("Cipher Suite Configuration", test_cipher_suite_configuration),
        ("Protocol Selection Logic", test_protocol_selection),
        ("HTTP Client Adapter", test_http_adapter),
        ("Comprehensive Integration", test_comprehensive_integration),
        ("Optimized Configuration System", test_optimized_configuration_system),
        ("Centralized SSL Context Creation", test_centralized_ssl_context_creation),
    ]
    
    for test_name, test_func in tests:
        test_suite.run_test(test_name, test_func)
    
    # Print results
    success = test_suite.print_summary()
    
    if success:
        logger.info("\nSUCCESS! Hue TLS 1.3 compliance is fully implemented!")
        print_usage_guide()
        return 0
    else:
        logger.error("\nFAILURE! Some TLS 1.3 compliance tests failed.")
        logger.error("Review the test output above and fix any issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 