#!/usr/bin/env python

from eventlet import patcher
from eventlet.green import socket

# enable network resource
import test.test_support
i_r_e = test.test_support.is_resource_enabled


def is_resource_enabled(resource):
    if resource == 'network':
        return True
    else:
        return i_r_e(resource)
test.test_support.is_resource_enabled = is_resource_enabled

try:
    socket.ssl
    socket.sslerror
except AttributeError:
    raise ImportError("Socket module doesn't support ssl")

patcher.inject('test.test_socket_ssl', globals())

test_basic = patcher.patch_function(test_basic)
test_rude_shutdown = patcher.patch_function(test_rude_shutdown)


def test_main():
    if not hasattr(socket, "ssl"):
        raise test_support.TestSkipped("socket module has no ssl support")
    test_rude_shutdown()
    test_basic()
    test_timeout()


if __name__ == "__main__":
    test_main()
