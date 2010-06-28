# -*- coding: utf-8 -*-
#
# test/test_runner.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2009 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Unit test for runner module.
    """

import __builtin__
import os
import sys
import tempfile
import errno
import signal

import scaffold
from test_pidlockfile import (
    FakeFileDescriptorStringIO,
    setup_pidfile_fixtures,
    make_pidlockfile_scenarios,
    setup_lockfile_method_mocks,
    )
from test_daemon import (
    setup_streams_fixtures,
    )
import daemon.daemon

from daemon import pidlockfile
from daemon import runner


class Exception_TestCase(scaffold.Exception_TestCase):
    """ Test cases for module exception classes. """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance. """
        super(Exception_TestCase, self).__init__(*args, **kwargs)

        self.valid_exceptions = {
            runner.DaemonRunnerError: dict(
                min_args = 1,
                types = (Exception,),
                ),
            runner.DaemonRunnerInvalidActionError: dict(
                min_args = 1,
                types = (runner.DaemonRunnerError, ValueError),
                ),
            runner.DaemonRunnerStartFailureError: dict(
                min_args = 1,
                types = (runner.DaemonRunnerError, RuntimeError),
                ),
            runner.DaemonRunnerStopFailureError: dict(
                min_args = 1,
                types = (runner.DaemonRunnerError, RuntimeError),
                ),
            }


def make_runner_scenarios():
    """ Make a collection of scenarios for testing DaemonRunner instances. """

    pidlockfile_scenarios = make_pidlockfile_scenarios()

    scenarios = {
        'simple': {
            'pidlockfile_scenario_name': 'simple',
            },
        'pidfile-locked': {
            'pidlockfile_scenario_name': 'exist-other-pid-locked',
            },
        }

    for scenario in scenarios.values():
        if 'pidlockfile_scenario_name' in scenario:
            pidlockfile_scenario = pidlockfile_scenarios.pop(
                scenario['pidlockfile_scenario_name'])
        scenario['pid'] = pidlockfile_scenario['pid']
        scenario['pidfile_path'] = pidlockfile_scenario['path']
        scenario['pidfile_timeout'] = 23
        scenario['pidlockfile_scenario'] = pidlockfile_scenario

    return scenarios


def set_runner_scenario(testcase, scenario_name, clear_tracker=True):
    """ Set the DaemonRunner test scenario for the test case. """
    scenarios = testcase.runner_scenarios
    testcase.scenario = scenarios[scenario_name]
    set_pidlockfile_scenario(
        testcase, testcase.scenario['pidlockfile_scenario_name'])
    if clear_tracker:
        testcase.mock_tracker.clear()


def set_pidlockfile_scenario(testcase, scenario_name):
    """ Set the PIDLockFile test scenario for the test case. """
    scenarios = testcase.pidlockfile_scenarios
    testcase.pidlockfile_scenario = scenarios[scenario_name]
    setup_lockfile_method_mocks(
        testcase, testcase.pidlockfile_scenario,
        testcase.lockfile_class_name)


def setup_runner_fixtures(testcase):
    """ Set up common test fixtures for DaemonRunner test case. """
    testcase.mock_tracker = scaffold.MockTracker()

    setup_pidfile_fixtures(testcase)
    setup_streams_fixtures(testcase)

    testcase.runner_scenarios = make_runner_scenarios()

    testcase.mock_stderr = FakeFileDescriptorStringIO()
    scaffold.mock(
        "sys.stderr",
        mock_obj=testcase.mock_stderr,
        tracker=testcase.mock_tracker)

    simple_scenario = testcase.runner_scenarios['simple']

    testcase.lockfile_class_name = "pidlockfile.TimeoutPIDLockFile"

    testcase.mock_runner_lock = scaffold.Mock(
        testcase.lockfile_class_name,
        tracker=testcase.mock_tracker)
    testcase.mock_runner_lock.path = simple_scenario['pidfile_path']

    scaffold.mock(
        testcase.lockfile_class_name,
        returns=testcase.mock_runner_lock,
        tracker=testcase.mock_tracker)

    class TestApp(object):

        def __init__(self):
            self.stdin_path = testcase.stream_file_paths['stdin']
            self.stdout_path = testcase.stream_file_paths['stdout']
            self.stderr_path = testcase.stream_file_paths['stderr']
            self.pidfile_path = simple_scenario['pidfile_path']
            self.pidfile_timeout = simple_scenario['pidfile_timeout']

        run = scaffold.Mock(
            "TestApp.run",
            tracker=testcase.mock_tracker)

    testcase.TestApp = TestApp

    scaffold.mock(
        "daemon.runner.DaemonContext",
        returns=scaffold.Mock(
            "DaemonContext",
            tracker=testcase.mock_tracker),
        tracker=testcase.mock_tracker)

    testcase.test_app = testcase.TestApp()

    testcase.test_program_name = "bazprog"
    testcase.test_program_path = (
        "/foo/bar/%(test_program_name)s" % vars(testcase))
    testcase.valid_argv_params = {
        'start': [testcase.test_program_path, 'start'],
        'stop': [testcase.test_program_path, 'stop'],
        'restart': [testcase.test_program_path, 'restart'],
        }

    def mock_open(filename, mode=None, buffering=None):
        if filename in testcase.stream_files_by_path:
            result = testcase.stream_files_by_path[filename]
        else:
            result = FakeFileDescriptorStringIO()
        result.mode = mode
        result.buffering = buffering
        return result

    scaffold.mock(
        "__builtin__.open",
        returns_func=mock_open,
        tracker=testcase.mock_tracker)

    scaffold.mock(
        "os.kill",
        tracker=testcase.mock_tracker)

    scaffold.mock(
        "sys.argv",
        mock_obj=testcase.valid_argv_params['start'],
        tracker=testcase.mock_tracker)

    testcase.test_instance = runner.DaemonRunner(testcase.test_app)

    testcase.scenario = NotImplemented


class DaemonRunner_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner class. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'simple')

        scaffold.mock(
            "runner.DaemonRunner.parse_args",
            tracker=self.mock_tracker)

        self.test_instance = runner.DaemonRunner(self.test_app)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_instantiate(self):
        """ New instance of DaemonRunner should be created. """
        self.failUnlessIsInstance(self.test_instance, runner.DaemonRunner)

    def test_parses_commandline_args(self):
        """ Should parse commandline arguments. """
        expect_mock_output = """\
            Called runner.DaemonRunner.parse_args()
            ...
            """
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_has_specified_app(self):
        """ Should have specified application object. """
        self.failUnlessIs(self.test_app, self.test_instance.app)

    def test_sets_pidfile_none_when_pidfile_path_is_none(self):
        """ Should set ‘pidfile’ to ‘None’ when ‘pidfile_path’ is ‘None’. """
        pidfile_path = None
        self.test_app.pidfile_path = pidfile_path
        expect_pidfile = None
        instance = runner.DaemonRunner(self.test_app)
        self.failUnlessIs(expect_pidfile, instance.pidfile)

    def test_error_when_pidfile_path_not_string(self):
        """ Should raise ValueError when PID file path not a string. """
        pidfile_path = object()
        self.test_app.pidfile_path = pidfile_path
        expect_error = ValueError
        self.failUnlessRaises(
            expect_error,
            runner.DaemonRunner, self.test_app)

    def test_error_when_pidfile_path_not_absolute(self):
        """ Should raise ValueError when PID file path not absolute. """
        pidfile_path = "foo/bar.pid"
        self.test_app.pidfile_path = pidfile_path
        expect_error = ValueError
        self.failUnlessRaises(
            expect_error,
            runner.DaemonRunner, self.test_app)

    def test_creates_lock_with_specified_parameters(self):
        """ Should create a TimeoutPIDLockFile with specified params. """
        pidfile_path = self.scenario['pidfile_path']
        pidfile_timeout = self.scenario['pidfile_timeout']
        lockfile_class_name = self.lockfile_class_name
        expect_mock_output = """\
            ...
            Called %(lockfile_class_name)s(
                %(pidfile_path)r,
                %(pidfile_timeout)r)
            """ % vars()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)
 
    def test_has_created_pidfile(self):
        """ Should have new PID lock file as `pidfile` attribute. """
        expect_pidfile = self.mock_runner_lock
        instance = self.test_instance
        self.failUnlessIs(
            expect_pidfile, instance.pidfile)
 
    def test_daemon_context_has_created_pidfile(self):
        """ DaemonContext component should have new PID lock file. """
        expect_pidfile = self.mock_runner_lock
        daemon_context = self.test_instance.daemon_context
        self.failUnlessIs(
            expect_pidfile, daemon_context.pidfile)

    def test_daemon_context_has_specified_stdin_stream(self):
        """ DaemonContext component should have specified stdin file. """
        test_app = self.test_app
        expect_file = self.stream_files_by_name['stdin']
        daemon_context = self.test_instance.daemon_context
        self.failUnlessEqual(expect_file, daemon_context.stdin)

    def test_daemon_context_has_stdin_in_read_mode(self):
        """ DaemonContext component should open stdin file for read. """
        expect_mode = 'r'
        daemon_context = self.test_instance.daemon_context
        self.failUnlessIn(daemon_context.stdin.mode, expect_mode)

    def test_daemon_context_has_specified_stdout_stream(self):
        """ DaemonContext component should have specified stdout file. """
        test_app = self.test_app
        expect_file = self.stream_files_by_name['stdout']
        daemon_context = self.test_instance.daemon_context
        self.failUnlessEqual(expect_file, daemon_context.stdout)

    def test_daemon_context_has_stdout_in_append_mode(self):
        """ DaemonContext component should open stdout file for append. """
        expect_mode = 'w+'
        daemon_context = self.test_instance.daemon_context
        self.failUnlessIn(daemon_context.stdout.mode, expect_mode)

    def test_daemon_context_has_specified_stderr_stream(self):
        """ DaemonContext component should have specified stderr file. """
        test_app = self.test_app
        expect_file = self.stream_files_by_name['stderr']
        daemon_context = self.test_instance.daemon_context
        self.failUnlessEqual(expect_file, daemon_context.stderr)

    def test_daemon_context_has_stderr_in_append_mode(self):
        """ DaemonContext component should open stderr file for append. """
        expect_mode = 'w+'
        daemon_context = self.test_instance.daemon_context
        self.failUnlessIn(daemon_context.stderr.mode, expect_mode)

    def test_daemon_context_has_stderr_with_no_buffering(self):
        """ DaemonContext component should open stderr file unbuffered. """
        expect_buffering = 0
        daemon_context = self.test_instance.daemon_context
        self.failUnlessEqual(
            expect_buffering, daemon_context.stderr.buffering)


class DaemonRunner_usage_exit_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.usage_exit method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'simple')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_raises_system_exit(self):
        """ Should raise SystemExit exception. """
        instance = self.test_instance
        argv = [self.test_program_path]
        self.failUnlessRaises(
            SystemExit,
            instance._usage_exit, argv)

    def test_message_follows_conventional_format(self):
        """ Should emit a conventional usage message. """
        instance = self.test_instance
        progname = self.test_program_name
        argv = [self.test_program_path]
        expect_stderr_output = """\
            usage: %(progname)s ...
            """ % vars()
        self.failUnlessRaises(
            SystemExit,
            instance._usage_exit, argv)
        self.failUnlessOutputCheckerMatch(
            expect_stderr_output, self.mock_stderr.getvalue())


class DaemonRunner_parse_args_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.parse_args method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'simple')

        scaffold.mock(
            "daemon.runner.DaemonRunner._usage_exit",
            raises=NotImplementedError,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_emits_usage_message_if_insufficient_args(self):
        """ Should emit a usage message and exit if too few arguments. """
        instance = self.test_instance
        argv = [self.test_program_path]
        expect_mock_output = """\
            Called daemon.runner.DaemonRunner._usage_exit(%(argv)r)
            """ % vars()
        try:
            instance.parse_args(argv)
        except NotImplementedError:
            pass
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_emits_usage_message_if_unknown_action_arg(self):
        """ Should emit a usage message and exit if unknown action. """
        instance = self.test_instance
        progname = self.test_program_name
        argv = [self.test_program_path, 'bogus']
        expect_mock_output = """\
            Called daemon.runner.DaemonRunner._usage_exit(%(argv)r)
            """ % vars()
        try:
            instance.parse_args(argv)
        except NotImplementedError:
            pass
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_should_parse_system_argv_by_default(self):
        """ Should parse sys.argv by default. """
        instance = self.test_instance
        expect_action = 'start'
        argv = self.valid_argv_params['start']
        scaffold.mock(
            "sys.argv",
            mock_obj=argv,
            tracker=self.mock_tracker)
        instance.parse_args()
        self.failUnlessEqual(expect_action, instance.action)

    def test_sets_action_from_first_argument(self):
        """ Should set action from first commandline argument. """
        instance = self.test_instance
        for name, argv in self.valid_argv_params.items():
            expect_action = name
            instance.parse_args(argv)
            self.failUnlessEqual(expect_action, instance.action)


class DaemonRunner_do_action_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.do_action method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'simple')

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_raises_error_if_unknown_action(self):
        """ Should emit a usage message and exit if action is unknown. """
        instance = self.test_instance
        instance.action = 'bogus'
        expect_error = runner.DaemonRunnerInvalidActionError
        self.failUnlessRaises(
            expect_error,
            instance.do_action)


class DaemonRunner_do_action_start_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.do_action method, action 'start'. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'simple')

        self.test_instance.action = 'start'

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_raises_error_if_pidfile_locked(self):
        """ Should raise error if PID file is locked. """
        set_pidlockfile_scenario(self, 'exist-other-pid-locked')
        instance = self.test_instance
        instance.daemon_context.open.mock_raises = (
            pidlockfile.AlreadyLocked)
        pidfile_path = self.scenario['pidfile_path']
        expect_error = runner.DaemonRunnerStartFailureError
        expect_message_content = pidfile_path
        try:
            instance.do_action()
        except expect_error, exc:
            pass
        else:
            raise self.failureException(
                "Failed to raise " + expect_error.__name__)
        self.failUnlessIn(exc.message, expect_message_content)

    def test_breaks_lock_if_no_such_process(self):
        """ Should request breaking lock if PID file process is not running. """
        set_runner_scenario(self, 'pidfile-locked')
        instance = self.test_instance
        self.mock_runner_lock.read_pid.mock_returns = (
            self.scenario['pidlockfile_scenario']['pidfile_pid'])
        pidfile_path = self.scenario['pidfile_path']
        test_pid = self.scenario['pidlockfile_scenario']['pidfile_pid']
        expect_signal = signal.SIG_DFL
        error = OSError(errno.ESRCH, "Not running")
        os.kill.mock_raises = error
        lockfile_class_name = self.lockfile_class_name
        expect_mock_output = """\
            ...
            Called os.kill(%(test_pid)r, %(expect_signal)r)
            Called %(lockfile_class_name)s.break_lock()
            ...
            """ % vars()
        instance.do_action()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_requests_daemon_context_open(self):
        """ Should request the daemon context to open. """
        instance = self.test_instance
        expect_mock_output = """\
            ...
            Called DaemonContext.open()
            ...
            """
        instance.do_action()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_emits_start_message_to_stderr(self):
        """ Should emit start message to stderr. """
        instance = self.test_instance
        current_pid = self.scenario['pid']
        expect_stderr = """\
            started with pid %(current_pid)d
            """ % vars()
        instance.do_action()
        self.failUnlessOutputCheckerMatch(
            expect_stderr, self.mock_stderr.getvalue())

    def test_requests_app_run(self):
        """ Should request the application to run. """
        instance = self.test_instance
        expect_mock_output = """\
            ...
            Called TestApp.run()
            """
        instance.do_action()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class DaemonRunner_do_action_stop_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.do_action method, action 'stop'. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'pidfile-locked')

        self.test_instance.action = 'stop'

        self.mock_runner_lock.is_locked.mock_returns = True
        self.mock_runner_lock.i_am_locking.mock_returns = False
        self.mock_runner_lock.read_pid.mock_returns = (
            self.scenario['pidlockfile_scenario']['pidfile_pid'])

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_raises_error_if_pidfile_not_locked(self):
        """ Should raise error if PID file is not locked. """
        set_runner_scenario(self, 'simple')
        instance = self.test_instance
        self.mock_runner_lock.is_locked.mock_returns = False
        self.mock_runner_lock.i_am_locking.mock_returns = False
        self.mock_runner_lock.read_pid.mock_returns = (
            self.scenario['pidlockfile_scenario']['pidfile_pid'])
        pidfile_path = self.scenario['pidfile_path']
        expect_error = runner.DaemonRunnerStopFailureError
        expect_message_content = pidfile_path
        try:
            instance.do_action()
        except expect_error, exc:
            pass
        else:
            raise self.failureException(
                "Failed to raise " + expect_error.__name__)
        scaffold.mock_restore()
        self.failUnlessIn(exc.message, expect_message_content)

    def test_breaks_lock_if_pidfile_stale(self):
        """ Should break lock if PID file is stale. """
        instance = self.test_instance
        pidfile_path = self.scenario['pidfile_path']
        test_pid = self.scenario['pidlockfile_scenario']['pidfile_pid']
        expect_signal = signal.SIG_DFL
        error = OSError(errno.ESRCH, "Not running")
        os.kill.mock_raises = error
        lockfile_class_name = self.lockfile_class_name
        expect_mock_output = """\
            ...
            Called %(lockfile_class_name)s.break_lock()
            """ % vars()
        instance.do_action()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_sends_terminate_signal_to_process_from_pidfile(self):
        """ Should send SIGTERM to the daemon process. """
        instance = self.test_instance
        test_pid = self.scenario['pidlockfile_scenario']['pidfile_pid']
        expect_signal = signal.SIGTERM
        expect_mock_output = """\
            ...
            Called os.kill(%(test_pid)r, %(expect_signal)r)
            """ % vars()
        instance.do_action()
        scaffold.mock_restore()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_error_if_cannot_send_signal_to_process(self):
        """ Should raise error if cannot send signal to daemon process. """
        instance = self.test_instance
        test_pid = self.scenario['pidlockfile_scenario']['pidfile_pid']
        pidfile_path = self.scenario['pidfile_path']
        error = OSError(errno.EPERM, "Nice try")
        os.kill.mock_raises = error
        expect_error = runner.DaemonRunnerStopFailureError
        expect_message_content = str(test_pid)
        try:
            instance.do_action()
        except expect_error, exc:
            pass
        else:
            raise self.failureException(
                "Failed to raise " + expect_error.__name__)
        scaffold.mock_restore()
        self.failUnlessIn(exc.message, expect_message_content)


class DaemonRunner_do_action_restart_TestCase(scaffold.TestCase):
    """ Test cases for DaemonRunner.do_action method, action 'restart'. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_runner_fixtures(self)
        set_runner_scenario(self, 'pidfile-locked')

        self.test_instance.action = 'restart'

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_requests_stop_then_start(self):
        """ Should request stop, then start. """
        instance = self.test_instance
        scaffold.mock(
            "daemon.runner.DaemonRunner._start",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.runner.DaemonRunner._stop",
            tracker=self.mock_tracker)
        expect_mock_output = """\
            Called daemon.runner.DaemonRunner._stop()
            Called daemon.runner.DaemonRunner._start()
            """
        instance.do_action()
        self.failUnlessMockCheckerMatch(expect_mock_output)
