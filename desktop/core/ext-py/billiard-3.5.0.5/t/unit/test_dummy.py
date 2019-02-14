from __future__ import absolute_import

import threading
import billiard.dummy


class test_restart_state:
    def test_raises(self):
        class Thread(threading.Thread):
            exception = None

            def run(self):
                try:
                    billiard.dummy.Process().start()
                except BaseException as e:
                    self.exception = e

        thread = Thread()
        thread.start()
        thread.join(0.1)
        assert not thread.is_alive()
        assert thread.exception is None
