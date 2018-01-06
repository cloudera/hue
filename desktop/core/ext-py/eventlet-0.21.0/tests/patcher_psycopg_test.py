import os

from eventlet.support import six

from tests import patcher_test, skip_unless
from tests import get_database_auth
from tests.db_pool_test import postgres_requirement

psycopg_test_file = """
import os
import sys
import eventlet
eventlet.monkey_patch()
from eventlet import patcher
if not patcher.is_monkey_patched('psycopg'):
    print("Psycopg not monkeypatched")
    sys.exit(0)

count = [0]
def tick(totalseconds, persecond):
    for i in range(totalseconds*persecond):
        count[0] += 1
        eventlet.sleep(1.0/persecond)

dsn = os.environ['PSYCOPG_TEST_DSN']
import psycopg2
def fetch(num, secs):
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    for i in range(num):
        cur.execute("select pg_sleep(%s)", (secs,))

f = eventlet.spawn(fetch, 2, 1)
t = eventlet.spawn(tick, 2, 100)
f.wait()
assert count[0] > 100, count[0]
print("done")
"""


class PatchingPsycopg(patcher_test.ProcessBase):
    @skip_unless(postgres_requirement)
    def test_psycopg_patched(self):
        if 'PSYCOPG_TEST_DSN' not in os.environ:
            # construct a non-json dsn for the subprocess
            psycopg_auth = get_database_auth()['psycopg2']
            if isinstance(psycopg_auth, str):
                dsn = psycopg_auth
            else:
                dsn = " ".join(["%s=%s" % (k, v) for k, v in six.iteritems(psycopg_auth)])
            os.environ['PSYCOPG_TEST_DSN'] = dsn
        self.write_to_tempfile("psycopg_patcher", psycopg_test_file)
        output, lines = self.launch_subprocess('psycopg_patcher.py')
        if lines[0].startswith('Psycopg not monkeypatched'):
            print("Can't test psycopg2 patching; it's not installed.")
            return
        # if there's anything wrong with the test program it'll have a stack trace
        assert lines[0].startswith('done'), output
