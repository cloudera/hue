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
import logging

from thrift.transport.TTransport import TTransportBase
import socket

logger = logging.getLogger('jaeger_tracing')


class TUDPTransport(TTransportBase, object):
    """
    TUDPTransport implements just enough of the tornado transport interface
    to work for blindly sending UDP packets.
    """
    def __init__(self, host, port, blocking=False):
        self.transport_host = host
        self.transport_port = port
        self.transport_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if blocking:
            blocking = 1
        else:
            blocking = 0
        self.transport_sock.setblocking(blocking)

    def write(self, buf):
        """Raw write to the UDP socket."""
        return self.transport_sock.sendto(
            buf,
            (self.transport_host, self.transport_port)
        )

    def isOpen(self):
        """
        isOpen for UDP is always true (there is no connection) as long
        as we have a sock
        """
        return self.transport_sock is not None

    def close(self):
        self.transport_sock.close()
        self.transport_sock = None
