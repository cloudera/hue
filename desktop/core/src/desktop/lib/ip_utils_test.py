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

import socket

from desktop.lib.ip_utils import fetch_ipv6_bind_address


def test_fetch_ipv6_with_hostname_aaaa(monkeypatch):
  addrinfo = [
    (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('2001:db8::1', 0, 0, 0))
  ]
  monkeypatch.setattr(socket, 'getaddrinfo', lambda *args, **kwargs: addrinfo)

  bind = fetch_ipv6_bind_address('hue.local', '8888')
  assert bind == '[2001:db8::1]:8888'


def test_fetch_ipv6_zone_id_stripped(monkeypatch):
  addrinfo = [
    (socket.AF_INET6, socket.SOCK_STREAM, 6, '', ('fe80::1%en0', 0, 0, 0))
  ]
  monkeypatch.setattr(socket, 'getaddrinfo', lambda *args, **kwargs: addrinfo)

  bind = fetch_ipv6_bind_address('hue.local', '7777')
  assert bind == '[fe80::1]:7777'


def test_fetch_ipv6_no_aaaa_fallback(monkeypatch):
  monkeypatch.setattr(socket, 'getaddrinfo', lambda *args, **kwargs: [])

  bind = fetch_ipv6_bind_address('hue-no-aaaa.local', '8000')
  assert bind == 'hue-no-aaaa.local:8000'
