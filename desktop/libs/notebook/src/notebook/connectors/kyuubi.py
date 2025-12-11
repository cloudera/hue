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

'''
Kyuubi SQLAlchemy connector

This connector uses SQLAlchemy to connect to Kyuubi via the Hive dialect.
It supports ZooKeeper-based service discovery for high availability.

Example connection strings:
- Direct connection: hive://username:password@host:port/database
- ZooKeeper HA: hive://username:password@zk1:2181,zk2:2181,zk3:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=kyuubi

'''

import json
import logging
import re
import time
import uuid
from urllib.parse import urlparse

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

from desktop.lib.conf import coerce_bool
from notebook.connectors.sql_alchemy import SqlAlchemyApi, ENGINES
from notebook.connectors.base import AuthenticationRequired, QueryError

LOG = logging.getLogger(__name__)

# ZooKeeper configuration
ZOOKEEPER_CONN_TIMEOUT = 10  # seconds


class KyuubiApi(SqlAlchemyApi):
    """Kyuubi API using SQLAlchemy with ZooKeeper service discovery support"""

    def __init__(self, user, interpreter):
        super(KyuubiApi, self).__init__(user, interpreter)
        self.options = interpreter['options'] if interpreter['options'] else {}
        self.zk_client = None

    def _create_engine(self):
        """Create SQLAlchemy engine with Kyuubi-specific handling"""
        # Check if url is in options, if not, try to get it from kyuubi_url or global kyuubi section
        url = self._get_kyuubi_url()
        LOG.info("Initial Kyuubi URL: %s", url)
        
        # Check if this is a ZooKeeper URL that needs resolution
        if self._is_zookeeper_url(url):
            url = self._resolve_zookeeper_url(url)
            LOG.info("Resolved Kyuubi ZooKeeper URL to: %s", url)
        
        # Update the URL in options for the parent class
        self.options['url'] = url
        LOG.info("Final URL for SQLAlchemy: %s", url)
        
        # For Kerberos authentication, we should not pass password in session properties
        # Check if this is a Kerberos-enabled connection
        if self._is_kerberos_url(url):
            # Remove password from session properties if present
            if 'session' in self.options and 'properties' in self.options['session']:
                session_props = self.options['session']['properties']
                # Filter out password property
                self.options['session']['properties'] = [
                    prop for prop in session_props if prop['name'] != 'password'
                ]
                
            # Also handle the case where URL has template variables
            # For Kerberos, we should not use templated URL with PASSWORD
            if '${' in url and '${PASSWORD}' in url:
                # Remove the PASSWORD template variable
                url = url.replace('${PASSWORD}', '')
                self.options['url'] = url
                
            # Make sure we don't pass any auth information through connect_args
            if 'session' in self.options:
                # Remove any auth configuration from session
                if 'auth' in self.options['session']:
                    del self.options['session']['auth']
                    
            # Set connect_args for Kerberos authentication
            # This ensures PyHive knows we're using Kerberos
            # Note: PyHive only accepts specific parameters: auth, kerberos_service_name, password, thrift_transport
            connect_args = {
                'auth': 'KERBEROS',
                'kerberos_service_name': 'hive'
            }
            
            # Convert connect_args to JSON string as expected by SqlAlchemyApi
            self.options['connect_args'] = json.dumps(connect_args)
            
            # Log the connect_args for debugging
            LOG.info("Connect args for SQLAlchemy: %s", connect_args)
            
            # Remove session entirely if it's now empty
            if 'session' in self.options and not self.options['session'].get('properties'):
                LOG.info("Removing empty session properties")
                self.options.pop('session', None)
                
            # For Kerberos authentication, ensure the URL is clean
            # Remove any username from the URL to prevent PyHive from expecting a password
            parsed = urlparse(url)
            if '@' in parsed.netloc:
                # Extract just the host:port part
                host_port = parsed.netloc.split('@')[1]
                clean_netloc = host_port
                # Reconstruct the URL without the username
                clean_url = parsed._replace(netloc=clean_netloc).geturl()
                self.options['url'] = clean_url
                LOG.info("Cleaned URL for Kerberos (removed username): %s", clean_url)
                
            # Also ensure we have the right auth parameters in the URL
            if ';auth=KERBEROS' not in self.options['url']:
                self.options['url'] += ';auth=KERBEROS'
                
            # Explicitly remove any session to prevent password being passed
            if 'session' in self.options:
                LOG.info("Explicitly removing session to prevent password conflicts: %s", self.options['session'])
                del self.options['session']
                
            # Remove any connect_args that may have been set elsewhere to prevent conflicts
            # We'll build our own clean connect_args
            if 'connect_args' in self.options:
                try:
                    parsed_connect_args = json.loads(self.options['connect_args'])
                    # Ensure we only have the necessary parameters for Kerberos
                    clean_connect_args = {
                        'auth': 'KERBEROS',
                        'kerberos_service_name': 'hive'
                    }
                    self.options['connect_args'] = json.dumps(clean_connect_args)
                except (json.JSONDecodeError, TypeError):
                    # If there's an issue parsing connect_args, replace with clean version
                    self.options['connect_args'] = json.dumps({
                        'auth': 'KERBEROS',
                        'kerberos_service_name': 'hive'
                    })

        # Log the final options being passed to SQLAlchemy
        LOG.info("Final options for SQLAlchemy engine: %s", {k: v for k, v in self.options.items() if k not in ['url']})
        LOG.info("Final URL for SQLAlchemy engine: %s", self.options['url'])

        return super(KyuubiApi, self)._create_engine()

    def _get_kyuubi_url(self):
        """Get Kyuubi URL from options or global configuration"""
        LOG.info("Attempting to get Kyuubi URL from options: %s", self.options)
        # First check in options
        if self.options and 'url' in self.options:
            LOG.info("Found URL in options['url']: %s", self.options['url'])
            return self.options['url']
        
        if self.options and 'kyuubi_url' in self.options:
            LOG.info("Found URL in options['kyuubi_url']: %s", self.options['kyuubi_url'])
            return self.options['kyuubi_url']
            
        # Then check in global kyuubi section
        try:
            # Let's try a different approach - directly access the configuration
            from desktop.conf import KU_CONF
            LOG.info("Accessing KU_CONF: %s", KU_CONF)
            if hasattr(KU_CONF, 'KYUUBI_URL'):
                LOG.info("KU_CONF has KYUUBI_URL attribute")
                url = KU_CONF.KYUUBI_URL.get()
                if url:
                    LOG.info("Got URL from KU_CONF.KYUUBI_URL: %s", url)
                    return url
                else:
                    LOG.info("KU_CONF.KYUUBI_URL is empty")
            else:
                # Try to access the configuration differently
                LOG.info("Trying alternative access to KU_CONF.KYUUBI_URL")
                if KU_CONF.KYUUBI_URL:
                    url = KU_CONF.KYUUBI_URL.get()
                    if url:
                        LOG.info("Got URL from alternative KU_CONF.KYUUBI_URL access: %s", url)
                        return url
        except Exception as e:
            LOG.warning("Could not access KU_CONF: %s", e)
            import traceback
            LOG.warning(traceback.format_exc())
            pass
            
        # As a fallback, let's try to get it from the interpreter configuration directly
        try:
            # Access the global configuration directly
            from django.conf import settings
            LOG.info("Accessing Django settings")
            kyuubi_config = getattr(settings, 'KYUUBI', {})
            LOG.info("KYUUBI config from settings: %s", kyuubi_config)
            if 'kyuubi_url' in kyuubi_config:
                LOG.info("Found kyuubi_url in settings.KYUUBI: %s", kyuubi_config['kyuubi_url'])
                return kyuubi_config['kyuubi_url']
        except Exception as e:
            LOG.warning("Could not access settings.KYUUBI: %s", e)
            import traceback
            LOG.warning(traceback.format_exc())
            pass
            
        # Last resort - hard-coded for testing
        LOG.warning("Using hardcoded URL for testing purposes")
        # Hardcoded URL as requested
        hardcoded_url = "hive://192.168.4.4:10009/default;auth=KERBEROS;principal=hive/_HOST@BIGDATA.CHINATELECOM.CN"
        LOG.info("Hardcoded URL: %s", hardcoded_url)
        return hardcoded_url

    def _is_zookeeper_url(self, url):
        """Check if the URL uses ZooKeeper service discovery"""
        return 'serviceDiscoveryMode=zooKeeper' in url

    def _is_kerberos_url(self, url):
        """Check if the URL uses Kerberos authentication"""
        return 'principal=' in url and ('auth=KERBEROS' in url or ';auth=KERBEROS' in url)

    def _clean_kerberos_url(self, url):
        """Clean URL for Kerberos authentication by removing any parameters that might trigger password requirement"""
        LOG.info("Cleaning Kerberos URL: %s", url)
        
        # Parse the URL
        parsed = urlparse(url)
        
        # For Kerberos, we want a clean URL without any extra parameters that might confuse PyHive
        # Keep only the scheme, netloc, and path
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path.split(';')[0]}"
        
        # Add back Kerberos authentication parameters
        clean_url += ";auth=KERBEROS"
        LOG.info("Cleaned Kerberos URL: %s", clean_url)
        
        return clean_url

    def _resolve_zookeeper_url(self, url):
        """
        Resolve ZooKeeper service discovery URL to a direct Thrift server URL.
        
        Example input:
        hive://username:password@zk1:2181,zk2:2181,zk3:2181/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=kyuubi
        
        Example output:
        hive://username:password@kyuubi-host:10009/default
        """
        # Parse the URL
        parsed = urlparse(url)
        LOG.info("Parsed URL: %s", parsed)
        
        # Check if this is a Kerberos URL
        is_kerberos = self._is_kerberos_url(url)
        
        # Extract ZooKeeper hosts and namespace from the URL
        # Handle URLs with and without user authentication
        if '@' in parsed.netloc:
            zk_hosts = parsed.netloc.split('@')[1]
        else:
            # For URLs without authentication (e.g., Kerberos)
            zk_hosts = parsed.netloc
            
        LOG.info("Using ZooKeeper hosts: %s", zk_hosts)
        namespace = 'kyuubi'
        
        # Extract namespace from path/query
        full_path = parsed.path
        if parsed.query:
            full_path += ';' + parsed.query
            
        for part in full_path.split(';'):
            if part.startswith('zooKeeperNamespace='):
                namespace = part.split('=')[1]
            # Add other parameter handling as needed
        
        # Connect to ZooKeeper
        zk_client = None
        try:
            LOG.debug("Connecting to ZooKeeper hosts: %s", zk_hosts)
            zk_client = KazooClient(hosts=zk_hosts, read_only=True)
            zk_client.start(timeout=ZOOKEEPER_CONN_TIMEOUT)
            
            # Look for Kyuubi instances
            znode_path = f"/{namespace}"
            try:
                if zk_client.exists(znode_path):
                    instances = zk_client.get_children(znode_path)
                    LOG.info("Found Kyuubi instances: %s", instances)
                    if instances:
                        # Sort instances by sequence number if present
                        sorted_instances = self._sort_zk_instances(instances)
                        selected_instance = sorted_instances[0]  # Select the first one
                        LOG.info("Selected instance: %s", selected_instance)
                        
                        # Parse the instance info
                        instance_info = self._parse_instance_info(selected_instance)
                        LOG.info("Instance info: %s", instance_info)
                        if instance_info:
                            # For Kerberos authentication, we don't need username/password in URL
                            if is_kerberos:
                                # For Kerberos, construct URL without username/password
                                new_netloc = f"{instance_info['host']}:{instance_info['port']}"
                            elif '@' in parsed.netloc:
                                # Preserve user authentication if it exists and not Kerberos
                                new_netloc = f"{parsed.netloc.split('@')[0]}@{instance_info['host']}:{instance_info['port']}"
                            else:
                                # No user authentication in original URL
                                new_netloc = f"{instance_info['host']}:{instance_info['port']}"
                            
                            # Construct new path - just the base path without any params for Kerberos
                            new_path = parsed.path.split(';')[0]  # Take only the path part before any params
                                
                            new_url = parsed._replace(netloc=new_netloc, path=new_path, query='').geturl()
                            LOG.info("URL with new netloc: %s", new_url)
                            
                            # For Kerberos, clean the URL to remove any params that might trigger password requirement
                            if is_kerberos:
                                new_url = self._clean_kerberos_url(new_url)
                            
                            LOG.info("Resolved URL: %s", new_url)
                            return new_url
                        else:
                            raise QueryError("Could not parse Kyuubi instance information from ZooKeeper")
                    else:
                        raise QueryError(f"No Kyuubi instances found in ZooKeeper at {znode_path}")
                else:
                    raise QueryError(f"ZooKeeper namespace {znode_path} does not exist")
            except NoNodeError:
                raise QueryError(f"ZooKeeper path {znode_path} not found")
        except Exception as e:
            LOG.error("Error resolving ZooKeeper URL: %s", e)
            raise QueryError(f"Failed to resolve ZooKeeper URL: {e}")
        finally:
            if zk_client:
                zk_client.stop()
                zk_client.close()
        
        # If we couldn't resolve, return the original URL
        return url

    def _sort_zk_instances(self, instances):
        """Sort ZooKeeper instances by sequence number if present"""
        # Filter nodes that match the expected pattern before sorting
        sequence_nodes = [x for x in instances if re.search(r'sequence=\d+', x)]
        if sequence_nodes:
            # Sort the filtered list based on the sequence number
            sequence_nodes.sort(key=lambda x: int(re.findall(r'sequence=(\d+)', x)[0]))
            return sequence_nodes
        else:
            # Return original list if no sequence numbers found
            return instances

    def _parse_instance_info(self, instance_string):
        """
        Parse instance information from ZooKeeper node data.
        
        Expected format: serverUri=host:port;version=x.x.x;sequence=xxxxxx
        """
        try:
            # Split the instance string into components
            components = instance_string.split(';')
            server_info = {}
            
            for component in components:
                if '=' in component:
                    key, value = component.split('=', 1)
                    server_info[key] = value
            
            if 'serverUri' in server_info:
                host_port = server_info['serverUri']
                host, port = host_port.split(':')
                return {
                    'host': host,
                    'port': int(port),
                    'version': server_info.get('version', 'unknown'),
                    'sequence': server_info.get('sequence', '0')
                }
        except Exception as e:
            LOG.error("Error parsing instance info '%s': %s", instance_string, e)
        
        return None

    def _remove_zk_query_params(self, url):
        """Remove ZooKeeper-specific query parameters from URL"""
        LOG.info("Removing ZK params from URL: %s", url)
        
        # Remove serviceDiscoveryMode and zooKeeperNamespace parameters
        zk_params = ['serviceDiscoveryMode', 'zooKeeperNamespace']
        
        # Process each ZooKeeper parameter
        for param in zk_params:
            # Remove parameter with its value in semicolon-separated format
            url = re.sub(f';{param}=[^;]*', '', url)
            # Also handle case where it's the first parameter after path
            url = re.sub(f'/([^/]+);{param}=[^;]*', r'/\1', url)
            
        LOG.info("URL after removing ZK query params: %s", url)
        
        # Clean up any leftover separators or malformed parts
        url = re.sub(r'[;]{2,}', ';', url)  # Multiple semicolons to single
        url = re.sub(r';+$', '', url)  # Remove trailing semicolons
        url = re.sub(r'/;', '/', url)  # Remove semicolon right after slash
        
        LOG.info("Final cleaned URL: %s", url)
        return url

    def execute(self, notebook, snippet):
        """Override execute to handle Kerberos authentication properly"""
        # Store original session to restore later if needed
        original_session = self.options.get('session')
        
        # For Kerberos authentication, we should not pass password in session properties
        url = self._get_kyuubi_url()
        if 'session' in self.options and self._is_kerberos_url(url):
            session_props = self.options['session']['properties']
            # Filter out password property
            filtered_props = [prop for prop in session_props if prop['name'] != 'password']
            self.options['session']['properties'] = filtered_props
            
            # If no properties left, remove session entirely
            if not self.options['session']['properties']:
                LOG.info("Removing empty session properties in execute")
                self.options.pop('session', None)
                
        # Explicitly remove session for Kerberos connections to prevent password conflicts
        if self._is_kerberos_url(url) and 'session' in self.options:
            LOG.info("Explicitly removing session for Kerberos connection in execute")
            del self.options['session']
        
        try:
            # Call parent execute method
            result = super(KyuubiApi, self).execute(notebook, snippet)
            return result
        finally:
            # Restore original session
            if original_session is not None:
                self.options['session'] = original_session

    def _get_engine(self):
        """Get or create SQLAlchemy engine with retry logic for HA"""
        engine_key = self._get_engine_key()
        
        # Try to get existing engine first
        if engine_key in ENGINES:
            return ENGINES[engine_key]
        
        # Create new engine with potential ZooKeeper resolution
        try:
            engine = self._create_engine()
            ENGINES[engine_key] = engine
            return engine
        except Exception as e:
            # If it failed and it was a ZooKeeper URL, try to refresh and retry once
            url = self._get_kyuubi_url()
            if self._is_zookeeper_url(url):
                LOG.info("Retrying Kyuubi connection with refreshed ZooKeeper resolution")
                try:
                    # Force re-resolution of the URL
                    resolved_url = self._resolve_zookeeper_url(url)
                    if resolved_url != url:
                        self.options['url'] = resolved_url
                        engine = self._create_engine()
                        ENGINES[engine_key] = engine
                        return engine
                except Exception as retry_e:
                    LOG.error("Retry failed: %s", retry_e)
                    # Raise the original exception
                    raise e
            # If not a ZK URL or retry failed, raise the original exception
            raise e