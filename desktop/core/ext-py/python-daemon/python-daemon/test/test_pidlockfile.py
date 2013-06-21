# -*- coding: utf-8 -*-
#
# test/test_pidlockfile.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2009 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Unit test for pidlockfile module.
    """

import __builtin__
import os
from StringIO import StringIO
import itertools
import tempfile
import errno

import lockfile

import scaffold
from daemon import pidlockfile


class FakeFileDescriptorStringIO(StringIO, object):
    """ A StringIO class that fakes a file descriptor. """

    _fileno_generator = itertools.count()

    def __init__(self, *args, **kwargs):
        self._fileno = self._fileno_generator.next()
        super_instance = super(FakeFileDescriptorStringIO, self)
        super_instance.__init__(*args, **kwargs)

    def fileno(self):
        return self._fileno


class Exception_TestCase(scaffold.Exception_TestCase):
    """ Test cases for module exception classes. """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance. """
        super(Exception_TestCase, self).__init__(*args, **kwargs)

        self.valid_exceptions = {
            pidlockfile.PIDFileError: dict(
                min_args = 1,
                types = (Exception,),
                ),
            pidlockfile.PIDFileParseError: dict(
                min_args = 2,
                types = (pidlockfile.PIDFileError, ValueError),
                ),
            }


def make_pidlockfile_scenarios():
    """ Make a collection of scenarios for testing PIDLockFile instances. """

    mock_current_pid = 235
    mock_other_pid = 8642
    mock_pidfile_path = tempfile.mktemp()

    mock_pidfile_empty = FakeFileDescriptorStringIO()
    mock_pidfile_current_pid = FakeFileDescriptorStringIO(
        "%(mock_current_pid)d\n" % vars())
    mock_pidfile_other_pid = FakeFileDescriptorStringIO(
        "%(mock_other_pid)d\n" % vars())
    mock_pidfile_bogus = FakeFileDescriptorStringIO(
        "b0gUs")

    scenarios = {
        'simple': {},
        'not-exist': {
            'open_func_name': 'mock_open_nonexist',
            'os_open_func_name': 'mock_os_open_nonexist',
            },
        'not-exist-write-denied': {
            'open_func_name': 'mock_open_nonexist',
            'os_open_func_name': 'mock_os_open_nonexist',
            },
        'not-exist-write-busy': {
            'open_func_name': 'mock_open_nonexist',
            'os_open_func_name': 'mock_os_open_nonexist',
            },
        'exist-read-denied': {
            'open_func_name': 'mock_open_read_denied',
            'os_open_func_name': 'mock_os_open_read_denied',
            },
        'exist-locked-read-denied': {
            'locking_pid': mock_other_pid,
            'open_func_name': 'mock_open_read_denied',
            'os_open_func_name': 'mock_os_open_read_denied',
            },
        'exist-empty': {},
        'exist-invalid': {
            'pidfile': mock_pidfile_bogus,
            },
        'exist-current-pid': {
            'pidfile': mock_pidfile_current_pid,
            'pidfile_pid': mock_current_pid,
            },
        'exist-current-pid-locked': {
            'pidfile': mock_pidfile_current_pid,
            'pidfile_pid': mock_current_pid,
            'locking_pid': mock_current_pid,
            },
        'exist-other-pid': {
            'pidfile': mock_pidfile_other_pid,
            'pidfile_pid': mock_other_pid,
            },
        'exist-other-pid-locked': {
            'pidfile': mock_pidfile_other_pid,
            'pidfile_pid': mock_other_pid,
            'locking_pid': mock_other_pid,
            },
        }

    for scenario in scenarios.values():
        scenario['pid'] = mock_current_pid
        scenario['path'] = mock_pidfile_path
        if 'pidfile' not in scenario:
            scenario['pidfile'] = mock_pidfile_empty
        if 'pidfile_pid' not in scenario:
            scenario['pidfile_pid'] = None
        if 'locking_pid' not in scenario:
            scenario['locking_pid'] = None
        if 'open_func_name' not in scenario:
            scenario['open_func_name'] = 'mock_open_okay'
        if 'os_open_func_name' not in scenario:
            scenario['os_open_func_name'] = 'mock_os_open_okay'

    return scenarios


def setup_pidfile_fixtures(testcase):
    """ Set up common fixtures for PID file test cases. """
    testcase.mock_tracker = scaffold.MockTracker()

    scenarios = make_pidlockfile_scenarios()
    testcase.pidlockfile_scenarios = scenarios

    def get_scenario_option(testcase, key, default=None):
        value = default
        try:
            value = testcase.scenario[key]
        except (NameError, TypeError, AttributeError, KeyError):
            pass
        return value

    scaffold.mock(
        "os.getpid",
        returns=scenarios['simple']['pid'],
        tracker=testcase.mock_tracker)

    def make_mock_open_funcs(testcase):

        def mock_open_nonexist(filename, mode, buffering):
            if 'r' in mode:
                raise IOError(
                    errno.ENOENT, "No such file %(filename)r" % vars())
            else:
                result = testcase.scenario['pidfile']
            return result

        def mock_open_read_denied(filename, mode, buffering):
            if 'r' in mode:
                raise IOError(
                    errno.EPERM, "Read denied on %(filename)r" % vars())
            else:
                result = testcase.scenario['pidfile']
            return result

        def mock_open_okay(filename, mode, buffering):
            result = testcase.scenario['pidfile']
            return result

        def mock_os_open_nonexist(filename, flags, mode):
            if (flags & os.O_CREAT):
                result = testcase.scenario['pidfile'].fileno()
            else:
                raise OSError(
                    errno.ENOENT, "No such file %(filename)r" % vars())
            return result

        def mock_os_open_read_denied(filename, flags, mode):
            if (flags & os.O_CREAT):
                result = testcase.scenario['pidfile'].fileno()
            else:
                raise OSError(
                    errno.EPERM, "Read denied on %(filename)r" % vars())
            return result

        def mock_os_open_okay(filename, flags, mode):
            result = testcase.scenario['pidfile'].fileno()
            return result

        funcs = dict(
            (name, obj) for (name, obj) in vars().items()
            if hasattr(obj, '__call__'))

        return funcs

    testcase.mock_pidfile_open_funcs = make_mock_open_funcs(testcase)

    def mock_open(filename, mode='r', buffering=None):
        scenario_path = get_scenario_option(testcase, 'path')
        if filename == scenario_path:
            func_name = testcase.scenario['open_func_name']
            mock_open_func = testcase.mock_pidfile_open_funcs[func_name]
            result = mock_open_func(filename, mode, buffering)
        else:
            result = FakeFileDescriptorStringIO()
        return result

    scaffold.mock(
        "__builtin__.open",
        returns_func=mock_open,
        tracker=testcase.mock_tracker)

    def mock_os_open(filename, flags, mode=None):
        scenario_path = get_scenario_option(testcase, 'path')
        if filename == scenario_path:
            func_name = testcase.scenario['os_open_func_name']
            mock_os_open_func = testcase.mock_pidfile_open_funcs[func_name]
            result = mock_os_open_func(filename, flags, mode)
        else:
            result = FakeFileDescriptorStringIO().fileno()
        return result

    scaffold.mock(
        "os.open",
        returns_func=mock_os_open,
        tracker=testcase.mock_tracker)

    def mock_os_fdopen(fd, mode='r', buffering=None):
        scenario_pidfile = get_scenario_option(
            testcase, 'pidfile', FakeFileDescriptorStringIO())
        if fd == testcase.scenario['pidfile'].fileno():
            result = testcase.scenario['pidfile']
        else:
            raise OSError(errno.EBADF, "Bad file descriptor")
        return result

    scaffold.mock(
        "os.fdopen",
        returns_func=mock_os_fdopen,
        tracker=testcase.mock_tracker)

    testcase.scenario = NotImplemented


def setup_lockfile_method_mocks(testcase, scenario, class_name):
    """ Set up common mock methods for lockfile class. """

    def mock_read_pid():
        return scenario['pidfile_pid']
    def mock_is_locked():
        return (scenario['locking_pid'] is not None)
    def mock_i_am_locking():
        return (
            scenario['locking_pid'] == scenario['pid'])
    def mock_acquire(timeout=None):
        if scenario['locking_pid'] is not None:
            raise lockfile.AlreadyLocked()
        scenario['locking_pid'] = scenario['pid']
    def mock_release():
        if scenario['locking_pid'] is None:
            raise lockfile.NotLocked()
        if scenario['locking_pid'] != scenario['pid']:
            raise lockfile.NotMyLock()
        scenario['locking_pid'] = None
    def mock_break_lock():
        scenario['locking_pid'] = None

    for func_name in [
        'read_pid',
        'is_locked', 'i_am_locking',
        'acquire', 'release', 'break_lock',
        ]:
        mock_func = vars()["mock_%(func_name)s" % vars()]
        lockfile_func_name = "%(class_name)s.%(func_name)s" % vars()
        mock_lockfile_func = scaffold.Mock(
            lockfile_func_name,
            returns_func=mock_func,
            tracker=testcase.mock_tracker)
        try:
            scaffold.mock(
                lockfile_func_name,
                mock_obj=mock_lockfile_func,
                tracker=testcase.mock_tracker)
        except NameError:
            pass


def setup_pidlockfile_fixtures(testcase, scenario_name=None):
    """ Set up common fixtures for PIDLockFile test cases. """

    setup_pidfile_fixtures(testcase)

    scaffold.mock(
        "pidlockfile.write_pid_to_pidfile",
        tracker=testcase.mock_tracker)
    scaffold.mock(
        "pidlockfile.remove_existing_pidfile",
        tracker=testcase.mock_tracker)

    if scenario_name is not None:
        set_pidlockfile_scenario(testcase, scenario_name, clear_tracker=False)


def set_pidlockfile_scenario(testcase, scenario_name, clear_tracker=True):
    """ Set up the test case to the specified scenario. """
    testcase.scenario = testcase.pidlockfile_scenarios[scenario_name]
    setup_lockfile_method_mocks(
        testcase, testcase.scenario, "lockfile.LinkFileLock")
    testcase.pidlockfile_args = dict(
        path=testcase.scenario['path'],
        )
    testcase.test_instance = pidlockfile.PIDLockFile(
        **testcase.pidlockfile_args)
    if clear_tracker:
        testcase.mock_tracker.clear()


class PIDLockFile_TestCase(scaffold.TestCase):
    """ Test cases for PIDLockFile class. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidlockfile_fixtures(self, 'exist-other-pid')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_instantiate(self):
        """ New instance of PIDLockFile should be created. """
        instance = self.test_instance
        self.failUnlessIsInstance(instance, pidlockfile.PIDLockFile)

    def test_inherits_from_linkfilelock(self):
        """ Should inherit from LinkFileLock. """
        instance = self.test_instance
        self.failUnlessIsInstance(instance, lockfile.LinkFileLock)

    def test_has_specified_path(self):
        """ Should have specified path. """
        instance = self.test_instance
        expect_path = self.scenario['path']
        self.failUnlessEqual(expect_path, instance.path)


class PIDLockFile_read_pid_TestCase(scaffold.TestCase):
    """ Test cases for PIDLockFile.read_pid method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidlockfile_fixtures(self, 'exist-other-pid')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_gets_pid_via_read_pid_from_pidfile(self):
        """ Should get PID via read_pid_from_pidfile. """
        instance = self.test_instance
        test_pid = self.scenario['pidfile_pid']
        expect_pid = test_pid
        result = instance.read_pid()
        self.failUnlessEqual(expect_pid, result)


class PIDLockFile_acquire_TestCase(scaffold.TestCase):
    """ Test cases for PIDLockFile.acquire function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidlockfile_fixtures(self)
        set_pidlockfile_scenario(self, 'not-exist')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_calls_linkfilelock_acquire(self):
        """ Should first call LinkFileLock.acquire method. """
        instance = self.test_instance
        expect_mock_output = """\
            Called lockfile.LinkFileLock.acquire()
            ...
            """
        instance.acquire()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_calls_linkfilelock_acquire_with_timeout(self):
        """ Should call LinkFileLock.acquire method with specified timeout. """
        instance = self.test_instance
        test_timeout = object()
        expect_mock_output = """\
            Called lockfile.LinkFileLock.acquire(timeout=%(test_timeout)r)
            ...
            """ % vars()
        instance.acquire(timeout=test_timeout)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_writes_pid_to_specified_file(self):
        """ Should request writing current PID to specified file. """
        instance = self.test_instance
        pidfile_path = self.scenario['path']
        expect_mock_output = """\
            ...
            Called pidlockfile.write_pid_to_pidfile(%(pidfile_path)r)
            """ % vars()
        instance.acquire()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_lock_failed_on_write_error(self):
        """ Should raise LockFailed error if write fails. """
        set_pidlockfile_scenario(self, 'not-exist-write-busy')
        instance = self.test_instance
        pidfile_path = self.scenario['path']
        mock_error = OSError(errno.EBUSY, "Bad stuff", pidfile_path)
        pidlockfile.write_pid_to_pidfile.mock_raises = mock_error
        expect_error = pidlockfile.LockFailed
        self.failUnlessRaises(
            expect_error,
            instance.acquire)


class PIDLockFile_release_TestCase(scaffold.TestCase):
    """ Test cases for PIDLockFile.release function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidlockfile_fixtures(self)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_does_not_remove_existing_pidfile_if_not_locking(self):
        """ Should not request removal of PID file if not locking. """
        set_pidlockfile_scenario(self, 'exist-empty')
        instance = self.test_instance
        expect_error = lockfile.NotLocked
        unwanted_mock_output = (
            "..."
            "Called pidlockfile.remove_existing_pidfile"
            "...")
        self.failUnlessRaises(
            expect_error,
            instance.release)
        self.failIfMockCheckerMatch(unwanted_mock_output)

    def test_does_not_remove_existing_pidfile_if_not_my_lock(self):
        """ Should not request removal of PID file if we are not locking. """
        set_pidlockfile_scenario(self, 'exist-other-pid-locked')
        instance = self.test_instance
        expect_error = lockfile.NotMyLock
        unwanted_mock_output = (
            "..."
            "Called pidlockfile.remove_existing_pidfile"
            "...")
        self.failUnlessRaises(
            expect_error,
            instance.release)
        self.failIfMockCheckerMatch(unwanted_mock_output)

    def test_removes_existing_pidfile_if_i_am_locking(self):
        """ Should request removal of specified PID file if lock is ours. """
        set_pidlockfile_scenario(self, 'exist-current-pid-locked')
        instance = self.test_instance
        pidfile_path = self.scenario['path']
        expect_mock_output = """\
            ...
            Called pidlockfile.remove_existing_pidfile(%(pidfile_path)r)
            ...
            """ % vars()
        instance.release()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_calls_linkfilelock_release(self):
        """ Should finally call LinkFileLock.release method. """
        set_pidlockfile_scenario(self, 'exist-current-pid-locked')
        instance = self.test_instance
        expect_mock_output = """\
            ...
            Called lockfile.LinkFileLock.release()
            """
        instance.release()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class PIDLockFile_break_lock_TestCase(scaffold.TestCase):
    """ Test cases for PIDLockFile.break_lock function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidlockfile_fixtures(self)
        set_pidlockfile_scenario(self, 'exist-other-pid-locked')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_calls_linkfilelock_break_lock(self):
        """ Should first call LinkFileLock.break_lock method. """
        instance = self.test_instance
        expect_mock_output = """\
            Called lockfile.LinkFileLock.break_lock()
            ...
            """
        instance.break_lock()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_removes_existing_pidfile(self):
        """ Should request removal of specified PID file. """
        instance = self.test_instance
        pidfile_path = self.scenario['path']
        expect_mock_output = """\
            ...
            Called pidlockfile.remove_existing_pidfile(%(pidfile_path)r)
            """ % vars()
        instance.break_lock()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class read_pid_from_pidfile_TestCase(scaffold.TestCase):
    """ Test cases for read_pid_from_pidfile function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidfile_fixtures(self)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_opens_specified_filename(self):
        """ Should attempt to open specified pidfile filename. """
        set_pidlockfile_scenario(self, 'exist-other-pid')
        pidfile_path = self.scenario['path']
        expect_mock_output = """\
            Called __builtin__.open(%(pidfile_path)r, 'r')
            """ % vars()
        dummy = pidlockfile.read_pid_from_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_reads_pid_from_file(self):
        """ Should read the PID from the specified file. """
        set_pidlockfile_scenario(self, 'exist-other-pid')
        pidfile_path = self.scenario['path']
        expect_pid = self.scenario['pidfile_pid']
        pid = pidlockfile.read_pid_from_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessEqual(expect_pid, pid)

    def test_returns_none_when_file_nonexist(self):
        """ Should return None when the PID file does not exist. """
        set_pidlockfile_scenario(self, 'not-exist')
        pidfile_path = self.scenario['path']
        pid = pidlockfile.read_pid_from_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessIs(None, pid)

    def test_raises_error_when_file_read_fails(self):
        """ Should raise error when the PID file read fails. """
        set_pidlockfile_scenario(self, 'exist-read-denied')
        pidfile_path = self.scenario['path']
        expect_error = EnvironmentError
        self.failUnlessRaises(
            expect_error,
            pidlockfile.read_pid_from_pidfile, pidfile_path)

    def test_raises_error_when_file_empty(self):
        """ Should raise error when the PID file is empty. """
        set_pidlockfile_scenario(self, 'exist-empty')
        pidfile_path = self.scenario['path']
        expect_error = pidlockfile.PIDFileParseError
        self.failUnlessRaises(
            expect_error,
            pidlockfile.read_pid_from_pidfile, pidfile_path)

    def test_raises_error_when_file_contents_invalid(self):
        """ Should raise error when the PID file contents are invalid. """
        set_pidlockfile_scenario(self, 'exist-invalid')
        pidfile_path = self.scenario['path']
        expect_error = pidlockfile.PIDFileParseError
        self.failUnlessRaises(
            expect_error,
            pidlockfile.read_pid_from_pidfile, pidfile_path)


class remove_existing_pidfile_TestCase(scaffold.TestCase):
    """ Test cases for remove_existing_pidfile function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidfile_fixtures(self)

        scaffold.mock(
            "os.remove",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_removes_specified_filename(self):
        """ Should attempt to remove specified PID file filename. """
        set_pidlockfile_scenario(self, 'exist-current-pid')
        pidfile_path = self.scenario['path']
        expect_mock_output = """\
            Called os.remove(%(pidfile_path)r)
            """ % vars()
        pidlockfile.remove_existing_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_ignores_file_not_exist_error(self):
        """ Should ignore error if file does not exist. """
        set_pidlockfile_scenario(self, 'not-exist')
        pidfile_path = self.scenario['path']
        mock_error = OSError(errno.ENOENT, "Not there", pidfile_path)
        os.remove.mock_raises = mock_error
        expect_mock_output = """\
            Called os.remove(%(pidfile_path)r)
            """ % vars()
        pidlockfile.remove_existing_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_propagates_arbitrary_oserror(self):
        """ Should propagate any OSError other than ENOENT. """
        set_pidlockfile_scenario(self, 'exist-current-pid')
        pidfile_path = self.scenario['path']
        mock_error = OSError(errno.EACCES, "Denied", pidfile_path)
        os.remove.mock_raises = mock_error
        self.failUnlessRaises(
            type(mock_error),
            pidlockfile.remove_existing_pidfile,
            pidfile_path)


class write_pid_to_pidfile_TestCase(scaffold.TestCase):
    """ Test cases for write_pid_to_pidfile function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_pidfile_fixtures(self)
        set_pidlockfile_scenario(self, 'not-exist')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_opens_specified_filename(self):
        """ Should attempt to open specified PID file filename. """
        pidfile_path = self.scenario['path']
        expect_flags = (os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        expect_mode = 0644
        expect_mock_output = """\
            Called os.open(%(pidfile_path)r, %(expect_flags)r, %(expect_mode)r)
            ...
            """ % vars()
        pidlockfile.write_pid_to_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_writes_pid_to_file(self):
        """ Should write the current PID to the specified file. """
        pidfile_path = self.scenario['path']
        self.scenario['pidfile'].close = scaffold.Mock(
            "PIDLockFile.close",
            tracker=self.mock_tracker)
        expect_line = "%(pid)d\n" % self.scenario
        pidlockfile.write_pid_to_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessEqual(expect_line, self.scenario['pidfile'].getvalue())

    def test_closes_file_after_write(self):
        """ Should close the specified file after writing. """
        pidfile_path = self.scenario['path']
        self.scenario['pidfile'].write = scaffold.Mock(
            "PIDLockFile.write",
            tracker=self.mock_tracker)
        self.scenario['pidfile'].close = scaffold.Mock(
            "PIDLockFile.close",
            tracker=self.mock_tracker)
        expect_mock_output = """\
            ...
            Called PIDLockFile.write(...)
            Called PIDLockFile.close()
            """ % vars()
        pidlockfile.write_pid_to_pidfile(pidfile_path)
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class TimeoutPIDLockFile_TestCase(scaffold.TestCase):
    """ Test cases for ‘TimeoutPIDLockFile’ class. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        pidlockfile_scenarios = make_pidlockfile_scenarios()
        self.pidlockfile_scenario = pidlockfile_scenarios['simple']
        pidfile_path = self.pidlockfile_scenario['path']

        scaffold.mock(
            "pidlockfile.PIDLockFile.__init__",
            tracker=self.mock_tracker)
        scaffold.mock(
            "pidlockfile.PIDLockFile.acquire",
            tracker=self.mock_tracker)

        self.scenario = {
            'pidfile_path': self.pidlockfile_scenario['path'],
            'acquire_timeout': object(),
            }

        self.test_kwargs = dict(
            path=self.scenario['pidfile_path'],
            acquire_timeout=self.scenario['acquire_timeout'],
            )
        self.test_instance = pidlockfile.TimeoutPIDLockFile(**self.test_kwargs)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_inherits_from_pidlockfile(self):
        """ Should inherit from PIDLockFile. """
        instance = self.test_instance
        self.failUnlessIsInstance(instance, pidlockfile.PIDLockFile)

    def test_init_has_expected_signature(self):
        """ Should have expected signature for ‘__init__’. """
        def test_func(self, path, acquire_timeout=None, *args, **kwargs): pass
        test_func.__name__ = '__init__'
        self.failUnlessFunctionSignatureMatch(
            test_func, 
            pidlockfile.TimeoutPIDLockFile.__init__)

    def test_has_specified_acquire_timeout(self):
        """ Should have specified ‘acquire_timeout’ value. """
        instance = self.test_instance
        expect_timeout = self.test_kwargs['acquire_timeout']
        self.failUnlessEqual(expect_timeout, instance.acquire_timeout)

    def test_calls_superclass_init(self):
        """ Should call the superclass ‘__init__’. """
        expect_path = self.test_kwargs['path']
        expect_mock_output = """\
            Called pidlockfile.PIDLockFile.__init__(
                %(expect_path)r)
            """ % vars()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_acquire_uses_specified_timeout(self):
        """ Should call the superclass ‘acquire’ with specified timeout. """
        instance = self.test_instance
        test_timeout = object()
        expect_timeout = test_timeout
        self.mock_tracker.clear()
        expect_mock_output = """\
            Called pidlockfile.PIDLockFile.acquire(%(expect_timeout)r)
            """ % vars()
        instance.acquire(test_timeout)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_acquire_uses_stored_timeout_by_default(self):
        """ Should call superclass ‘acquire’ with stored timeout by default. """
        instance = self.test_instance
        test_timeout = self.test_kwargs['acquire_timeout']
        expect_timeout = test_timeout
        self.mock_tracker.clear()
        expect_mock_output = """\
            Called pidlockfile.PIDLockFile.acquire(%(expect_timeout)r)
            """ % vars()
        instance.acquire()
        self.failUnlessMockCheckerMatch(expect_mock_output)
