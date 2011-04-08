from __future__ import with_statement

import os

from tests import LimitedTestCase

from eventlet import greenio

class TestGreenPipeWithStatement(LimitedTestCase):
    def test_pipe_context(self):
        # ensure using a pipe as a context actually closes it.
        r, w = os.pipe()

        r = greenio.GreenPipe(r)
        w = greenio.GreenPipe(w, 'w')

        with r:
            pass

        assert r.closed and not w.closed

        with w as f:
            assert f == w

        assert r.closed and w.closed
