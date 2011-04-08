import sys
import warnings
from tests import LimitedTestCase, main, skip_on_windows

warnings.simplefilter('ignore', DeprecationWarning)
from eventlet import processes, api
warnings.simplefilter('default', DeprecationWarning)

class TestEchoPool(LimitedTestCase):
    def setUp(self):
        super(TestEchoPool, self).setUp()
        self.pool = processes.ProcessPool('echo', ["hello"])

    @skip_on_windows
    def test_echo(self):
        result = None

        proc = self.pool.get()
        try:
            result = proc.read()
        finally:
            self.pool.put(proc)
        self.assertEquals(result, 'hello\n')

    @skip_on_windows
    def test_read_eof(self):
        proc = self.pool.get()
        try:
            proc.read()
            self.assertRaises(processes.DeadProcess, proc.read)
        finally:
            self.pool.put(proc)

    @skip_on_windows    
    def test_empty_echo(self):
        p = processes.Process('echo', ['-n'])
        self.assertEquals('', p.read())
        self.assertRaises(processes.DeadProcess, p.read)
            

class TestCatPool(LimitedTestCase):
    def setUp(self):
        super(TestCatPool, self).setUp()
        api.sleep(0)
        self.pool = processes.ProcessPool('cat')

    @skip_on_windows
    def test_cat(self):
        result = None

        proc = self.pool.get()
        try:
            proc.write('goodbye')
            proc.close_stdin()
            result = proc.read()
        finally:
            self.pool.put(proc)

        self.assertEquals(result, 'goodbye')

    @skip_on_windows
    def test_write_to_dead(self):
        result = None

        proc = self.pool.get()
        try:
            proc.write('goodbye')
            proc.close_stdin()
            result = proc.read()
            self.assertRaises(processes.DeadProcess, proc.write, 'foo')
        finally:
            self.pool.put(proc)

    @skip_on_windows
    def test_close(self):
        result = None

        proc = self.pool.get()
        try:
            proc.write('hello')
            proc.close()
            self.assertRaises(processes.DeadProcess, proc.write, 'goodbye')
        finally:
            self.pool.put(proc)


class TestDyingProcessesLeavePool(LimitedTestCase):
    def setUp(self):
        super(TestDyingProcessesLeavePool, self).setUp()
        self.pool = processes.ProcessPool('echo', ['hello'], max_size=1)

    @skip_on_windows
    def test_dead_process_not_inserted_into_pool(self):
        proc = self.pool.get()
        try:
            try:
                result = proc.read()
                self.assertEquals(result, 'hello\n')
                result = proc.read()
            except processes.DeadProcess:
                pass
        finally:
            self.pool.put(proc)
        proc2 = self.pool.get()
        self.assert_(proc is not proc2)


if __name__ == '__main__':
    main()
