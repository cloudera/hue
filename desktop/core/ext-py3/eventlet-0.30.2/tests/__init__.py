# package is named tests, not test, so it won't be confused with test in stdlib
from __future__ import print_function

import contextlib
import errno
import functools
import gc
import json
import os
try:
    import resource
except ImportError:
    resource = None
import signal
try:
    import subprocess32 as subprocess  # py2
except ImportError:
    import subprocess  # py3
import sys
import unittest
import warnings

from nose.plugins.skip import SkipTest

import eventlet
from eventlet import tpool
import six
import socket
from threading import Thread
import struct


# convenience for importers
main = unittest.main


@contextlib.contextmanager
def assert_raises(exc_type):
    try:
        yield
    except exc_type:
        pass
    else:
        name = str(exc_type)
        try:
            name = exc_type.__name__
        except AttributeError:
            pass
        assert False, 'Expected exception {0}'.format(name)


def skipped(func, *decorator_args):
    """Decorator that marks a function as skipped.
    """
    @functools.wraps(func)
    def wrapped(*a, **k):
        raise SkipTest(*decorator_args)

    return wrapped


def skip_if(condition):
    """ Decorator that skips a test if the *condition* evaluates True.
    *condition* can be a boolean or a callable that accepts one argument.
    The callable will be called with the function to be decorated, and
    should return True to skip the test.
    """
    def skipped_wrapper(func):
        @functools.wraps(func)
        def wrapped(*a, **kw):
            if isinstance(condition, bool):
                result = condition
            else:
                result = condition(func)
            if result:
                raise SkipTest()
            else:
                return func(*a, **kw)
        return wrapped
    return skipped_wrapper


def skip_unless(condition):
    """ Decorator that skips a test if the *condition* does not return True.
    *condition* can be a boolean or a callable that accepts one argument.
    The callable will be called with the  function to be decorated, and
    should return True if the condition is satisfied.
    """
    def skipped_wrapper(func):
        @functools.wraps(func)
        def wrapped(*a, **kw):
            if isinstance(condition, bool):
                result = condition
            else:
                result = condition(func)
            if not result:
                raise SkipTest()
            else:
                return func(*a, **kw)
        return wrapped
    return skipped_wrapper


def using_pyevent(_f):
    from eventlet.hubs import get_hub
    return 'pyevent' in type(get_hub()).__module__


def skip_with_pyevent(func):
    """ Decorator that skips a test if we're using the pyevent hub."""
    return skip_if(using_pyevent)(func)


def skip_on_windows(func):
    """ Decorator that skips a test on Windows."""
    return skip_if(sys.platform.startswith('win'))(func)


def skip_if_no_itimer(func):
    """ Decorator that skips a test if the `itimer` module isn't found """
    has_itimer = False
    try:
        import itimer
        has_itimer = True
    except ImportError:
        pass
    return skip_unless(has_itimer)(func)


def skip_if_CRLock_exist(func):
    """ Decorator that skips a test if the `_thread.RLock` class exists """
    try:
        from _thread import RLock
        return skipped(func)
    except ImportError:
        return func


def skip_if_no_ssl(func):
    """ Decorator that skips a test if SSL is not available."""
    try:
        import eventlet.green.ssl
        return func
    except ImportError:
        try:
            import eventlet.green.OpenSSL
            return func
        except ImportError:
            return skipped(func)


def skip_if_no_ipv6(func):
    if os.environ.get('eventlet_test_ipv6') != '1':
        return skipped(func)
    return func


class TestIsTakingTooLong(Exception):
    """ Custom exception class to be raised when a test's runtime exceeds a limit. """
    pass


class LimitedTestCase(unittest.TestCase):
    """ Unittest subclass that adds a timeout to all tests.  Subclasses must
    be sure to call the LimitedTestCase setUp and tearDown methods.  The default
    timeout is 1 second, change it by setting TEST_TIMEOUT to the desired
    quantity."""

    TEST_TIMEOUT = 1

    def setUp(self):
        self.previous_alarm = None
        self.timer = eventlet.Timeout(self.TEST_TIMEOUT,
                                      TestIsTakingTooLong(self.TEST_TIMEOUT))

    def reset_timeout(self, new_timeout):
        """Changes the timeout duration; only has effect during one test.
        `new_timeout` can be int or float.
        """
        self.timer.cancel()
        self.timer = eventlet.Timeout(new_timeout,
                                      TestIsTakingTooLong(new_timeout))

    def set_alarm(self, new_timeout):
        """Call this in the beginning of your test if you expect busy loops.
        Only has effect during one test.
        `new_timeout` must be int.
        """
        def sig_alarm_handler(sig, frame):
            # Could arm previous alarm but test is failed anyway
            # seems to be no point in restoring previous state.
            raise TestIsTakingTooLong(new_timeout)

        self.previous_alarm = (
            signal.signal(signal.SIGALRM, sig_alarm_handler),
            signal.alarm(new_timeout),
        )

    def tearDown(self):
        self.timer.cancel()
        if self.previous_alarm:
            signal.signal(signal.SIGALRM, self.previous_alarm[0])
            signal.alarm(self.previous_alarm[1])

        tpool.killall()
        gc.collect()
        eventlet.sleep(0)
        verify_hub_empty()

    def assert_less_than(self, a, b, msg=None):
        msg = msg or "%s not less than %s" % (a, b)
        assert a < b, msg

    assertLessThan = assert_less_than

    def assert_less_than_equal(self, a, b, msg=None):
        msg = msg or "%s not less than or equal to %s" % (a, b)
        assert a <= b, msg

    assertLessThanEqual = assert_less_than_equal


def check_idle_cpu_usage(duration, allowed_part):
    if resource is None:
        # TODO: use https://code.google.com/p/psutil/
        from nose.plugins.skip import SkipTest
        raise SkipTest('CPU usage testing not supported (`import resource` failed)')

    r1 = resource.getrusage(resource.RUSAGE_SELF)
    eventlet.sleep(duration)
    r2 = resource.getrusage(resource.RUSAGE_SELF)
    utime = r2.ru_utime - r1.ru_utime
    stime = r2.ru_stime - r1.ru_stime

    # This check is reliably unreliable on Travis, presumably because of CPU
    # resources being quite restricted by the build environment. The workaround
    # is to apply an arbitrary factor that should be enough to make it work nicely.
    if os.environ.get('TRAVIS') == 'true':
        allowed_part *= 5

    assert utime + stime < duration * allowed_part, \
        "CPU usage over limit: user %.0f%% sys %.0f%% allowed %.0f%%" % (
            utime / duration * 100, stime / duration * 100,
            allowed_part * 100)


def verify_hub_empty():

    def format_listener(listener):
        return 'Listener %r for greenlet %r with run callback %r' % (
            listener, listener.greenlet, getattr(listener.greenlet, 'run', None))

    from eventlet import hubs
    hub = hubs.get_hub()
    readers = hub.get_readers()
    writers = hub.get_writers()
    num_readers = len(readers)
    num_writers = len(writers)
    num_timers = hub.get_timers_count()
    assert num_readers == 0 and num_writers == 0, \
        "Readers: %s (%d) Writers: %s (%d)" % (
            ', '.join(map(format_listener, readers)), num_readers,
            ', '.join(map(format_listener, writers)), num_writers,
        )


def find_command(command):
    for dir in os.getenv('PATH', '/usr/bin:/usr/sbin').split(os.pathsep):
        p = os.path.join(dir, command)
        if os.access(p, os.X_OK):
            return p
    raise IOError(errno.ENOENT, 'Command not found: %r' % command)


def silence_warnings(func):
    def wrapper(*args, **kw):
        warnings.simplefilter('ignore', DeprecationWarning)
        try:
            return func(*args, **kw)
        finally:
            warnings.simplefilter('default', DeprecationWarning)
    wrapper.__name__ = func.__name__
    return wrapper


def get_database_auth():
    """Retrieves a dict of connection parameters for connecting to test databases.

    Authentication parameters are highly-machine specific, so
    get_database_auth gets its information from either environment
    variables or a config file.  The environment variable is
    "EVENTLET_DB_TEST_AUTH" and it should contain a json object.  If
    this environment variable is present, it's used and config files
    are ignored.  If it's not present, it looks in the local directory
    (tests) and in the user's home directory for a file named
    ".test_dbauth", which contains a json map of parameters to the
    connect function.
    """
    retval = {
        'MySQLdb': {'host': 'localhost', 'user': 'root', 'passwd': ''},
        'psycopg2': {'user': 'test'},
    }

    if 'EVENTLET_DB_TEST_AUTH' in os.environ:
        return json.loads(os.environ.get('EVENTLET_DB_TEST_AUTH'))

    files = [os.path.join(os.path.dirname(__file__), '.test_dbauth'),
             os.path.join(os.path.expanduser('~'), '.test_dbauth')]
    for f in files:
        try:
            auth_utf8 = json.load(open(f))
            # Have to convert unicode objects to str objects because
            # mysqldb is dumb. Using a doubly-nested list comprehension
            # because we know that the structure is a two-level dict.
            return dict(
                [(str(modname), dict(
                    [(str(k), str(v)) for k, v in connectargs.items()]))
                 for modname, connectargs in auth_utf8.items()])
        except IOError:
            pass
    return retval


def run_python(path, env=None, args=None, timeout=None, pythonpath_extend=None, expect_pass=False):
    new_argv = [sys.executable]
    if sys.version_info[:2] <= (2, 7):
        new_argv += ['-W', 'ignore:Python 2 is no longer supported']
    new_env = os.environ.copy()
    new_env.setdefault('eventlet_test_in_progress', 'yes')
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path:
        path = os.path.abspath(path)
        new_argv.append(path)
        new_env['PYTHONPATH'] = os.pathsep.join(sys.path + [src_dir])
    if env:
        new_env.update(env)
    if pythonpath_extend:
        new_path = [p for p in new_env.get('PYTHONPATH', '').split(os.pathsep) if p]
        new_path.extend(
            p if os.path.isabs(p) else os.path.join(src_dir, p) for p in pythonpath_extend
        )
        new_env['PYTHONPATH'] = os.pathsep.join(new_path)
    if args:
        new_argv.extend(args)
    p = subprocess.Popen(
        new_argv,
        env=new_env,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    if timeout is None:
        timeout = 10
    try:
        output, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        output, _ = p.communicate(timeout=timeout)
        if expect_pass:
            sys.stderr.write('Program {0} output:\n---\n{1}\n---\n'.format(path, output.decode()))
            assert False, 'timed out'
        return '{0}\nFAIL - timed out'.format(output).encode()

    if expect_pass:
        if output.startswith(b'skip'):
            parts = output.rstrip().split(b':', 1)
            skip_args = []
            if len(parts) > 1:
                skip_args.append(parts[1])
            raise SkipTest(*skip_args)
        ok = output.rstrip() == b'pass'
        if not ok:
            sys.stderr.write('Program {0} output:\n---\n{1}\n---\n'.format(path, output.decode()))
        assert ok, 'Expected single line "pass" in stdout'

    return output


def run_isolated(path, prefix='tests/isolated/', **kwargs):
    kwargs.setdefault('expect_pass', True)
    run_python(prefix + path, **kwargs)


def check_is_timeout(obj):
    value_text = getattr(obj, 'is_timeout', '(missing)')
    assert obj.is_timeout, 'type={0} str={1} .is_timeout={2}'.format(type(obj), str(obj), value_text)


@contextlib.contextmanager
def capture_stderr():
    stream = six.StringIO()
    original = sys.stderr
    try:
        sys.stderr = stream
        yield stream
    finally:
        sys.stderr = original
        stream.seek(0)


certificate_file = os.path.join(os.path.dirname(__file__), 'test_server.crt')
private_key_file = os.path.join(os.path.dirname(__file__), 'test_server.key')


def test_run_python_timeout():
    output = run_python('', args=('-c', 'import time; time.sleep(0.5)'), timeout=0.1)
    assert output.endswith(b'FAIL - timed out')


def test_run_python_pythonpath_extend():
    code = '''import os, sys ; print('\\n'.join(sys.path))'''
    output = run_python('', args=('-c', code), pythonpath_extend=('dira', 'dirb'))
    assert b'/dira\n' in output
    assert b'/dirb\n' in output


@contextlib.contextmanager
def dns_tcp_server(ip_to_give, request_count=1):
    state = [0]  # request count storage writable by thread
    host = "localhost"
    death_pill = b"DEATH_PILL"

    def extract_domain(data):
        domain = b''
        kind = (data[4] >> 3) & 15  # Opcode bits
        if kind == 0:  # Standard query
            ini = 14
            length = data[ini]
            while length != 0:
                domain += data[ini + 1:ini + length + 1] + b'.'
                ini += length + 1
                length = data[ini]
        return domain

    def answer(data, domain):
        domain_length = len(domain)
        packet = b''
        if domain:
            # If an ip was given we return it in the answer
            if ip_to_give:
                packet += data[2:4] + b'\x81\x80'
                packet += data[6:8] + data[6:8] + b'\x00\x00\x00\x00'  # Questions and answers counts
                packet += data[14: 14 + domain_length + 1]  # Original domain name question
                packet += b'\x00\x01\x00\x01' # Type and class
                packet += b'\xc0\x0c\x00\x01'  # TTL
                packet += b'\x00\x01'
                packet += b'\x00\x00\x00\x08'
                packet += b'\x00\x04' # Resource data length -> 4 bytes
                packet += bytearray(int(x) for x in ip_to_give.split("."))
            else:
                packet += data[2:4] + b'\x85\x80'
                packet += data[6:8] + b'\x00\x00' + b'\x00\x00\x00\x00'  # Questions and answers counts
                packet += data[14: 14 + domain_length + 1]  # Original domain name question
                packet += b'\x00\x01\x00\x01'  # Type and class

        sz = struct.pack('>H', len(packet))
        return sz + packet

    def serve(server_socket):  # thread target
        client_sock, address = server_socket.accept()
        state[0] += 1
        if state[0] <= request_count:
            data = bytearray(client_sock.recv(1024))
            if data == death_pill:
                client_sock.close()
                return

            domain = extract_domain(data)
            client_sock.sendall(answer(data, domain))
        client_sock.close()

    # Server starts
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, 0))
    server_socket.listen(5)
    server_addr = server_socket.getsockname()

    thread = Thread(target=serve, args=(server_socket, ))
    thread.start()

    yield server_addr

    # Stop the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_addr)
    client.send(death_pill)
    client.close()
    thread.join()
    server_socket.close()
