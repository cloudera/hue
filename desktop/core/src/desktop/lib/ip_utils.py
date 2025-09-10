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

import ipaddress
import logging
import socket


def fetch_ipv6_bind_address(http_host, http_port):
  """
  Formats the bind address for IPv6, handling common input scenarios:
  - Already bracketed IPv6: [2001:db8::1] -> [2001:db8::1]:8888
  - Raw IPv6 literal: 2001:db8::1 -> [2001:db8::1]:8888
  - IPv4 or hostname: 0.0.0.0 or hostname.com -> resolve to IPv6 and bracket
  - Special addresses: ::1, :: -> [::1]:8888, [::]:8888
  """
  try:
    # Case 1: Already-bracketed IPv6; validate the inner literal before using.
    if http_host.startswith('[') and http_host.endswith(']'):
      ipv6_part = http_host[1:-1]
      ipaddress.IPv6Address(ipv6_part)  # Validate it's a proper IPv6
      bind_addr = f"{http_host}:{http_port}"
      logging.info(f"Using pre-bracketed IPv6 address: {http_host}")
      return bind_addr

    # Case 2: Try to parse as raw IPv6 address literal
    try:
      ipaddress.IPv6Address(http_host)
      bind_addr = f"[{http_host}]:{http_port}"
      logging.info(f"Formatted IPv6 literal {http_host} as {bind_addr}")
      return bind_addr
    except ipaddress.AddressValueError:
      # Not an IPv6 literal, continue to hostname resolution
      pass

    # Case 3: Not an IPv6 literal, treat as hostname/IPv4 and resolve to IPv6
    try:
      addr_info = socket.getaddrinfo(http_host, None, socket.AF_INET6, socket.SOCK_STREAM)
      if addr_info:
        # Get the first IPv6 address from resolution
        ipv6_addr = str(addr_info[0][4][0])
        # Remove any zone identifier (like %eth0) for binding
        if '%' in ipv6_addr:
          ipv6_addr = ipv6_addr.split('%')[0]
        bind_addr = f"[{ipv6_addr}]:{http_port}"
        logging.info(f"Resolved hostname {http_host} to IPv6 address {ipv6_addr}")
        return bind_addr
      else:
        # No IPv6 resolution available, fallback
        bind_addr = f"{http_host}:{http_port}"
        logging.warning(f"No IPv6 address found for {http_host}, using as-is: {bind_addr}")
        return bind_addr
    except socket.gaierror as e:
      # DNS resolution failed
      bind_addr = f"{http_host}:{http_port}"
      logging.warning(f"IPv6 DNS resolution failed for {http_host}: {e}, using as-is: {bind_addr}")
      return bind_addr

  except Exception as e:
    # Catch-all to avoid breaking bind path on unexpected inputs.
    bind_addr = f"{http_host}:{http_port}"
    logging.warning(f"IPv6 address formatting failed for {http_host}: {e}, using as-is: {bind_addr}")
    return bind_addr
