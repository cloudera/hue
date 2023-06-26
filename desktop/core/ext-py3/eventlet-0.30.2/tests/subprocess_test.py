import sys
import time

import eventlet
from eventlet.green import subprocess
import eventlet.patcher
import tests
original_subprocess = eventlet.patcher.original('subprocess')


def test_subprocess_wait():
    # https://bitbucket.org/eventlet/eventlet/issue/89
    # In Python 3.3 subprocess.Popen.wait() method acquired `timeout`
    # argument.
    # RHEL backported it to their Python 2.6 package.
    cmd = [sys.executable, "-c", "import time; time.sleep(0.5)"]
    p = subprocess.Popen(cmd)
    ok = False
    t1 = time.time()
    try:
        p.wait(timeout=0.1)
    except subprocess.TimeoutExpired as e:
        str(e)  # make sure it doesn't throw
        assert e.cmd == cmd
        assert e.timeout == 0.1
        ok = True
    tdiff = time.time() - t1
    assert ok, 'did not raise subprocess.TimeoutExpired'
    assert 0.1 <= tdiff <= 0.2, 'did not stop within allowed time'


def test_communicate_with_poll():
    # This test was being skipped since git 25812fca8, I don't there's
    # a need to do this. The original comment:
    #
    # https://github.com/eventlet/eventlet/pull/24
    # `eventlet.green.subprocess.Popen.communicate()` was broken
    # in Python 2.7 because the usage of the `select` module was moved from
    # `_communicate` into two other methods `_communicate_with_select`
    # and `_communicate_with_poll`. Link to 2.7's implementation:
    # http://hg.python.org/cpython/file/2145593d108d/Lib/subprocess.py#l1255

    p = subprocess.Popen(
        [sys.executable, '-c', 'import time; time.sleep(0.5)'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    t1 = time.time()
    eventlet.with_timeout(0.1, p.communicate, timeout_value=True)
    tdiff = time.time() - t1
    assert 0.1 <= tdiff <= 0.2, 'did not stop within allowed time'


def test_close_popen_stdin_with_close_fds():
    p = subprocess.Popen(
        ['ls'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        shell=False,
        cwd=None,
        env=None)

    p.communicate(None)

    try:
        p.stdin.close()
    except Exception as e:
        assert False, "Exception should not be raised, got %r instead" % e


def test_universal_lines():
    p = subprocess.Popen(
        [sys.executable, '--version'],
        shell=False,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    p.communicate(None)


def test_patched_communicate_290():
    # https://github.com/eventlet/eventlet/issues/290
    # Certain order of import and monkey_patch breaks subprocess communicate()
    # with AttributeError module `select` has no `poll` on Linux
    # unpatched methods are removed for safety reasons in commit f63165c0e3
    tests.run_isolated('subprocess_patched_communicate.py')


def test_check_call_without_timeout_works():
    # There was a regression that'd result in the following exception:
    # TypeError: check_call() missing 1 required keyword-only argument: 'timeout'
    subprocess.check_call(
        ['ls'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def test_exception_identity():
    # https://github.com/eventlet/eventlet/issues/413
    # green module must keep exceptions classes as stdlib version
    tests.run_isolated('subprocess_exception_identity.py')
