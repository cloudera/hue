# Copyright (c) 2016 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
import unittest

from jaeger_client.TUDPTransport import TUDPTransport


class TUDPTransportTests(unittest.TestCase):
    def setUp(self):
        self.t = TUDPTransport('127.0.0.1', 12345)

    def test_constructor_blocking(self):
        t = TUDPTransport('127.0.0.1', 12345, blocking=True)
        assert t.transport_sock.gettimeout() is None

    def test_constructor_nonblocking(self):
        t = TUDPTransport('127.0.0.1', 12345, blocking=False)
        assert t.transport_sock.gettimeout() == 0

    def test_write(self):
        self.t.write(b'hello')

    def test_isopen_when_open(self):
        assert self.t.isOpen() is True

    def test_isopen_when_closed(self):
        self.t.close()
        assert self.t.isOpen() is False

    def test_close(self):
        self.t.close()
        with self.assertRaises(Exception):
            # Something bad should happen if we send on a closed socket..
            self.t.write(b'hello')
