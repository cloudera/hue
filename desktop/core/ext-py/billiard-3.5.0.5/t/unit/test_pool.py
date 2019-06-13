from __future__ import absolute_import

import billiard.pool

class test_pool:
    def test_raises(self):
        pool = billiard.pool.Pool()
        assert pool.did_start_ok() is True
        pool.close()
        pool.terminate()
