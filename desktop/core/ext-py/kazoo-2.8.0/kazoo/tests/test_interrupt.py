import os
from sys import platform

import pytest

from kazoo.testing import KazooTestCase


class KazooInterruptTests(KazooTestCase):
    def test_interrupted_systemcall(self):
        '''
        Make sure interrupted system calls don't break the world, since we
        can't control what all signals our connection thread will get
        '''
        if 'linux' not in platform:
            pytest.skip(
                'Unable to reproduce error case on non-linux platforms'
            )

        path = 'interrupt_test'
        value = b"1"
        self.client.create(path, value)

        # set the euid to the current process' euid.
        # glibc sends SIGRT to all children, which will interrupt the
        # system call
        os.seteuid(os.geteuid())

        # basic sanity test that it worked alright
        assert self.client.get(path)[0] == value
