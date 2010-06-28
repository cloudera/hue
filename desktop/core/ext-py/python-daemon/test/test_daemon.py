# -*- coding: utf-8 -*-
#
# test/test_daemon.py
# Part of python-daemon, an implementation of PEP 3143.
#
# Copyright © 2008–2009 Ben Finney <ben+python@benfinney.id.au>
#
# This is free software: you may copy, modify, and/or distribute this work
# under the terms of the Python Software Foundation License, version 2 or
# later as published by the Python Software Foundation.
# No warranty expressed or implied. See the file LICENSE.PSF-2 for details.

""" Unit test for daemon module.
    """

import os
import sys
import tempfile
import resource
import errno
import signal
import socket
from types import ModuleType
import atexit
from StringIO import StringIO

import scaffold
from test_pidlockfile import (
    FakeFileDescriptorStringIO,
    setup_pidfile_fixtures,
    )

from daemon import pidlockfile
import daemon


class Exception_TestCase(scaffold.Exception_TestCase):
    """ Test cases for module exception classes. """

    def __init__(self, *args, **kwargs):
        """ Set up a new instance. """
        super(Exception_TestCase, self).__init__(*args, **kwargs)

        self.valid_exceptions = {
            daemon.daemon.DaemonError: dict(
                min_args = 1,
                types = (Exception,),
            ),
            daemon.daemon.DaemonOSEnvironmentError: dict(
                min_args = 1,
                types = (daemon.daemon.DaemonError, OSError),
            ),
            daemon.daemon.DaemonProcessDetachError: dict(
                min_args = 1,
                types = (daemon.daemon.DaemonError, OSError),
            ),
        }


def setup_daemon_context_fixtures(testcase):
    """ Set up common test fixtures for DaemonContext test case. """
    testcase.mock_tracker = scaffold.MockTracker()

    setup_streams_fixtures(testcase)

    setup_pidfile_fixtures(testcase)

    testcase.mock_pidfile_path = tempfile.mktemp()
    testcase.mock_pidlockfile = scaffold.Mock(
        "pidlockfile.PIDLockFile",
        tracker=testcase.mock_tracker)
    testcase.mock_pidlockfile.path = testcase.mock_pidfile_path

    scaffold.mock(
        "daemon.daemon.is_detach_process_context_required",
        returns=True,
        tracker=testcase.mock_tracker)
    scaffold.mock(
        "daemon.daemon.make_default_signal_map",
        returns=object(),
        tracker=testcase.mock_tracker)

    scaffold.mock(
        "os.getuid",
        returns=object(),
        tracker=testcase.mock_tracker)
    scaffold.mock(
        "os.getgid",
        returns=object(),
        tracker=testcase.mock_tracker)

    testcase.daemon_context_args = dict(
        stdin = testcase.stream_files_by_name['stdin'],
        stdout = testcase.stream_files_by_name['stdout'],
        stderr = testcase.stream_files_by_name['stderr'],
        )
    testcase.test_instance = daemon.DaemonContext(
        **testcase.daemon_context_args)


class DaemonContext_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext class. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_instantiate(self):
        """ New instance of DaemonContext should be created. """
        self.failUnlessIsInstance(
            self.test_instance, daemon.daemon.DaemonContext)

    def test_minimum_zero_arguments(self):
        """ Initialiser should not require any arguments. """
        instance = daemon.daemon.DaemonContext()
        self.failIfIs(None, instance)

    def test_has_specified_chroot_directory(self):
        """ Should have specified chroot_directory option. """
        args = dict(
            chroot_directory = object(),
            )
        expect_directory = args['chroot_directory']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_directory, instance.chroot_directory)

    def test_has_specified_working_directory(self):
        """ Should have specified working_directory option. """
        args = dict(
            working_directory = object(),
            )
        expect_directory = args['working_directory']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_directory, instance.working_directory)

    def test_has_default_working_directory(self):
        """ Should have default working_directory option. """
        args = dict()
        expect_directory = '/'
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_directory, instance.working_directory)

    def test_has_specified_creation_mask(self):
        """ Should have specified umask option. """
        args = dict(
            umask = object(),
            )
        expect_mask = args['umask']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_mask, instance.umask)

    def test_has_default_creation_mask(self):
        """ Should have default umask option. """
        args = dict()
        expect_mask = 0
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_mask, instance.umask)

    def test_has_specified_uid(self):
        """ Should have specified uid option. """
        args = dict(
            uid = object(),
            )
        expect_id = args['uid']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_id, instance.uid)

    def test_has_derived_uid(self):
        """ Should have uid option derived from process. """
        args = dict()
        expect_id = os.getuid()
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_id, instance.uid)

    def test_has_specified_gid(self):
        """ Should have specified gid option. """
        args = dict(
            gid = object(),
            )
        expect_id = args['gid']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_id, instance.gid)

    def test_has_derived_gid(self):
        """ Should have gid option derived from process. """
        args = dict()
        expect_id = os.getgid()
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_id, instance.gid)

    def test_has_specified_detach_process(self):
        """ Should have specified detach_process option. """
        args = dict(
            detach_process = object(),
            )
        expect_value = args['detach_process']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_value, instance.detach_process)

    def test_has_derived_detach_process(self):
        """ Should have detach_process option derived from environment. """
        args = dict()
        func = daemon.daemon.is_detach_process_context_required
        expect_value = func()
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_value, instance.detach_process)

    def test_has_specified_files_preserve(self):
        """ Should have specified files_preserve option. """
        args = dict(
            files_preserve = object(),
            )
        expect_files_preserve = args['files_preserve']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_files_preserve, instance.files_preserve)

    def test_has_specified_pidfile(self):
        """ Should have the specified pidfile. """
        args = dict(
            pidfile = object(),
            )
        expect_pidfile = args['pidfile']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_pidfile, instance.pidfile)

    def test_has_specified_stdin(self):
        """ Should have specified stdin option. """
        args = dict(
            stdin = object(),
            )
        expect_file = args['stdin']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_file, instance.stdin)

    def test_has_specified_stdout(self):
        """ Should have specified stdout option. """
        args = dict(
            stdout = object(),
            )
        expect_file = args['stdout']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_file, instance.stdout)

    def test_has_specified_stderr(self):
        """ Should have specified stderr option. """
        args = dict(
            stderr = object(),
            )
        expect_file = args['stderr']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_file, instance.stderr)

    def test_has_specified_signal_map(self):
        """ Should have specified signal_map option. """
        args = dict(
            signal_map = object(),
            )
        expect_signal_map = args['signal_map']
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_signal_map, instance.signal_map)

    def test_has_derived_signal_map(self):
        """ Should have signal_map option derived from system. """
        args = dict()
        expect_signal_map = daemon.daemon.make_default_signal_map()
        instance = daemon.daemon.DaemonContext(**args)
        self.failUnlessEqual(expect_signal_map, instance.signal_map)


class DaemonContext_is_open_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.is_open property. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_begin_false(self):
        """ Initial value of is_open should be False. """
        instance = self.test_instance
        self.failUnlessEqual(False, instance.is_open)

    def test_write_fails(self):
        """ Writing to is_open should fail. """
        instance = self.test_instance
        self.failUnlessRaises(
            AttributeError,
            setattr, instance, 'is_open', object())


class DaemonContext_open_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.open method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)
        self.mock_tracker.clear()

        self.test_instance._is_open = False

        scaffold.mock(
            "daemon.daemon.detach_process_context",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.change_working_directory",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.change_root_directory",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.change_file_creation_mask",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.change_process_owner",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.prevent_core_dump",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.close_all_open_files",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.redirect_stream",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.set_signal_handlers",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.register_atexit_function",
            tracker=self.mock_tracker)

        self.test_files_preserve_fds = object()
        scaffold.mock(
            "daemon.daemon.DaemonContext._get_exclude_file_descriptors",
            returns=self.test_files_preserve_fds,
            tracker=self.mock_tracker)

        self.test_signal_handler_map = object()
        scaffold.mock(
            "daemon.daemon.DaemonContext._make_signal_handler_map",
            returns=self.test_signal_handler_map,
            tracker=self.mock_tracker)

        scaffold.mock(
            "sys.stdin",
            tracker=self.mock_tracker)
        scaffold.mock(
            "sys.stdout",
            tracker=self.mock_tracker)
        scaffold.mock(
            "sys.stderr",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_performs_steps_in_expected_sequence(self):
        """ Should perform daemonisation steps in expected sequence. """
        instance = self.test_instance
        instance.chroot_directory = object()
        instance.detach_process = True
        instance.pidfile = self.mock_pidlockfile
        expect_mock_output = """\
            Called daemon.daemon.change_root_directory(...)
            Called daemon.daemon.prevent_core_dump()
            Called daemon.daemon.change_file_creation_mask(...)
            Called daemon.daemon.change_working_directory(...)
            Called daemon.daemon.change_process_owner(...)
            Called daemon.daemon.detach_process_context()
            Called daemon.daemon.DaemonContext._make_signal_handler_map()
            Called daemon.daemon.set_signal_handlers(...)
            Called daemon.daemon.DaemonContext._get_exclude_file_descriptors()
            Called daemon.daemon.close_all_open_files(...)
            Called daemon.daemon.redirect_stream(...)
            Called daemon.daemon.redirect_stream(...)
            Called daemon.daemon.redirect_stream(...)
            Called pidlockfile.PIDLockFile.__enter__()
            Called daemon.daemon.register_atexit_function(...)
            """ % vars()
        self.mock_tracker.clear()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_returns_immediately_if_is_open(self):
        """ Should return immediately if is_open property is true. """
        instance = self.test_instance
        instance._is_open = True
        expect_mock_output = """\
            """
        self.mock_tracker.clear()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_root_directory_to_chroot_directory(self):
        """ Should change root directory to `chroot_directory` option. """
        instance = self.test_instance
        chroot_directory = object()
        instance.chroot_directory = chroot_directory
        expect_mock_output = """\
            Called daemon.daemon.change_root_directory(
                %(chroot_directory)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_omits_chroot_if_no_chroot_directory(self):
        """ Should omit changing root directory if no `chroot_directory`. """
        instance = self.test_instance
        instance.chroot_directory = None
        unwanted_output = """\
            ...Called daemon.daemon.change_root_directory(...)..."""
        instance.open()
        self.failIfMockCheckerMatch(unwanted_output)

    def test_prevents_core_dump(self):
        """ Should request prevention of core dumps. """
        instance = self.test_instance
        expect_mock_output = """\
            Called daemon.daemon.prevent_core_dump()
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_closes_open_files(self):
        """ Should close all open files, excluding `files_preserve`. """
        instance = self.test_instance
        expect_exclude = self.test_files_preserve_fds
        expect_mock_output = """\
            ...
            Called daemon.daemon.close_all_open_files(
                exclude=%(expect_exclude)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_directory_to_working_directory(self):
        """ Should change current directory to `working_directory` option. """
        instance = self.test_instance
        working_directory = object()
        instance.working_directory = working_directory
        expect_mock_output = """\
            ...
            Called daemon.daemon.change_working_directory(
                %(working_directory)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_creation_mask_to_umask(self):
        """ Should change file creation mask to `umask` option. """
        instance = self.test_instance
        umask = object()
        instance.umask = umask
        expect_mock_output = """\
            ...
            Called daemon.daemon.change_file_creation_mask(%(umask)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_owner_to_specified_uid_and_gid(self):
        """ Should change process UID and GID to `uid` and `gid` options. """
        instance = self.test_instance
        uid = object()
        gid = object()
        instance.uid = uid
        instance.gid = gid
        expect_mock_output = """\
            ...
            Called daemon.daemon.change_process_owner(%(uid)r, %(gid)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_detaches_process_context(self):
        """ Should request detach of process context. """
        instance = self.test_instance
        expect_mock_output = """\
            ...
            Called daemon.daemon.detach_process_context()
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_omits_process_detach_if_not_required(self):
        """ Should omit detach of process context if not required. """
        instance = self.test_instance
        instance.detach_process = False
        unwanted_output = """\
            ...Called daemon.daemon.detach_process_context(...)..."""
        instance.open()
        self.failIfMockCheckerMatch(unwanted_output)

    def test_sets_signal_handlers_from_signal_map(self):
        """ Should set signal handlers according to `signal_map`. """
        instance = self.test_instance
        instance.signal_map = object()
        expect_signal_handler_map = self.test_signal_handler_map
        expect_mock_output = """\
            ...
            Called daemon.daemon.set_signal_handlers(
                %(expect_signal_handler_map)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_redirects_standard_streams(self):
        """ Should request redirection of standard stream files. """
        instance = self.test_instance
        (system_stdin, system_stdout, system_stderr) = (
            sys.stdin, sys.stdout, sys.stderr)
        (target_stdin, target_stdout, target_stderr) = (
            self.stream_files_by_name[name]
            for name in ['stdin', 'stdout', 'stderr'])
        expect_mock_output = """\
            ...
            Called daemon.daemon.redirect_stream(
                %(system_stdin)r, %(target_stdin)r)
            Called daemon.daemon.redirect_stream(
                %(system_stdout)r, %(target_stdout)r)
            Called daemon.daemon.redirect_stream(
                %(system_stderr)r, %(target_stderr)r)
            ...
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_enters_pidfile_context(self):
        """ Should enter the PID file context manager. """
        instance = self.test_instance
        instance.pidfile = self.mock_pidlockfile
        expect_mock_output = """\
            ...
            Called pidlockfile.PIDLockFile.__enter__()
            ...
            """
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_sets_is_open_true(self):
        """ Should set the `is_open` property to True. """
        instance = self.test_instance
        instance.open()
        self.failUnlessEqual(True, instance.is_open)

    def test_registers_close_method_for_atexit(self):
        """ Should register the `close` method for atexit processing. """
        instance = self.test_instance
        close_method = instance.close
        expect_mock_output = """\
            ...
            Called daemon.daemon.register_atexit_function(%(close_method)r)
            """ % vars()
        instance.open()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class DaemonContext_close_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.close method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)
        self.mock_tracker.clear()

        self.test_instance._is_open = True

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_immediately_if_not_is_open(self):
        """ Should return immediately if is_open property is false. """
        instance = self.test_instance
        instance._is_open = False
        instance.pidfile = object()
        expect_mock_output = """\
            """
        self.mock_tracker.clear()
        instance.close()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_exits_pidfile_context(self):
        """ Should exit the PID file context manager. """
        instance = self.test_instance
        instance.pidfile = self.mock_pidlockfile
        expect_mock_output = """\
            Called pidlockfile.PIDLockFile.__exit__()
            """
        instance.close()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_returns_none(self):
        """ Should return None. """
        instance = self.test_instance
        expect_result = None
        result = instance.close()
        self.failUnlessIs(expect_result, result)

    def test_sets_is_open_false(self):
        """ Should set the `is_open` property to False. """
        instance = self.test_instance
        instance.close()
        self.failUnlessEqual(False, instance.is_open)


class DaemonContext_context_manager_enter_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.__enter__ method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)
        self.mock_tracker.clear()

        scaffold.mock(
            "daemon.daemon.DaemonContext.open",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_opens_daemon_context(self):
        """ Should open the DaemonContext. """
        instance = self.test_instance
        expect_mock_output = """\
            Called daemon.daemon.DaemonContext.open()
            """
        instance.__enter__()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_returns_self_instance(self):
        """ Should return DaemonContext instance. """
        instance = self.test_instance
        expect_result = instance
        result = instance.__enter__()
        self.failUnlessIs(expect_result, result)


class DaemonContext_context_manager_exit_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.__exit__ method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)
        self.mock_tracker.clear()

        self.test_args = dict(
            exc_type = object(),
            exc_value = object(),
            traceback = object(),
            )

        scaffold.mock(
            "daemon.daemon.DaemonContext.close",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_closes_daemon_context(self):
        """ Should close the DaemonContext. """
        instance = self.test_instance
        args = self.test_args
        expect_mock_output = """\
            Called daemon.daemon.DaemonContext.close()
            """
        instance.__exit__(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_returns_none(self):
        """ Should return None, indicating exception was not handled. """
        instance = self.test_instance
        args = self.test_args
        expect_result = None
        result = instance.__exit__(**args)
        self.failUnlessIs(expect_result, result)


class DaemonContext_terminate_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext.terminate method. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

        self.test_signal = signal.SIGTERM
        self.test_frame = None
        self.test_args = (self.test_signal, self.test_frame)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_raises_system_exit(self):
        """ Should raise SystemExit. """
        instance = self.test_instance
        args = self.test_args
        expect_exception = SystemExit
        self.failUnlessRaises(
            expect_exception,
            instance.terminate, *args)

    def test_exception_message_contains_signal_number(self):
        """ Should raise exception with a message containing signal number. """
        instance = self.test_instance
        args = self.test_args
        signal_number = self.test_signal
        expect_exception = SystemExit
        try:
            instance.terminate(*args)
        except expect_exception, exc:
            pass
        self.failUnlessIn(str(exc), str(signal_number))


class DaemonContext_get_exclude_file_descriptors_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext._get_exclude_file_descriptors function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

        self.test_files = {
            2: FakeFileDescriptorStringIO(),
            5: 5,
            11: FakeFileDescriptorStringIO(),
            17: None,
            23: FakeFileDescriptorStringIO(),
            37: 37,
            42: FakeFileDescriptorStringIO(),
            }
        for (fileno, item) in self.test_files.items():
            if hasattr(item, '_fileno'):
                item._fileno = fileno
        self.test_file_descriptors = set(
            fd for (fd, item) in self.test_files.items()
            if item is not None)
        self.test_file_descriptors.update(
            self.stream_files_by_name[name].fileno()
            for name in ['stdin', 'stdout', 'stderr']
            )

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_expected_file_descriptors(self):
        """ Should return expected set of file descriptors. """
        instance = self.test_instance
        instance.files_preserve = self.test_files.values()
        expect_result = self.test_file_descriptors
        result = instance._get_exclude_file_descriptors()
        self.failUnlessEqual(expect_result, result)

    def test_returns_stream_redirects_if_no_files_preserve(self):
        """ Should return only stream redirects if no files_preserve. """
        instance = self.test_instance
        instance.files_preserve = None
        expect_result = set(
            stream.fileno()
            for stream in self.stream_files_by_name.values())
        result = instance._get_exclude_file_descriptors()
        self.failUnlessEqual(expect_result, result)

    def test_returns_empty_set_if_no_files(self):
        """ Should return empty set if no file options. """
        instance = self.test_instance
        for name in ['files_preserve', 'stdin', 'stdout', 'stderr']:
            setattr(instance, name, None)
        expect_result = set()
        result = instance._get_exclude_file_descriptors()
        self.failUnlessEqual(expect_result, result)

    def test_return_set_omits_streams_without_file_descriptors(self):
        """ Should omit any stream without a file descriptor. """
        instance = self.test_instance
        instance.files_preserve = self.test_files.values()
        stream_files = self.stream_files_by_name
        stream_names = stream_files.keys()
        expect_result = self.test_file_descriptors.copy()
        for (pseudo_stream_name, pseudo_stream) in stream_files.items():
            setattr(instance, pseudo_stream_name, StringIO())
            stream_fd = pseudo_stream.fileno()
            expect_result.discard(stream_fd)
        result = instance._get_exclude_file_descriptors()
        self.failUnlessEqual(expect_result, result)


class DaemonContext_make_signal_handler_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext._make_signal_handler function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_ignore_for_none(self):
        """ Should return SIG_IGN when None handler specified. """
        instance = self.test_instance
        target = None
        expect_result = signal.SIG_IGN
        result = instance._make_signal_handler(target)
        self.failUnlessEqual(expect_result, result)

    def test_returns_method_for_name(self):
        """ Should return method of DaemonContext when name specified. """
        instance = self.test_instance
        target = 'terminate'
        expect_result = instance.terminate
        result = instance._make_signal_handler(target)
        self.failUnlessEqual(expect_result, result)

    def test_raises_error_for_unknown_name(self):
        """ Should raise AttributeError for unknown method name. """
        instance = self.test_instance
        target = 'b0gUs'
        expect_error = AttributeError
        self.failUnlessRaises(
            expect_error,
            instance._make_signal_handler, target)

    def test_returns_object_for_object(self):
        """ Should return same object for any other object. """
        instance = self.test_instance
        target = object()
        expect_result = target
        result = instance._make_signal_handler(target)
        self.failUnlessEqual(expect_result, result)


class DaemonContext_make_signal_handler_map_TestCase(scaffold.TestCase):
    """ Test cases for DaemonContext._make_signal_handler_map function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_daemon_context_fixtures(self)

        self.test_instance.signal_map = {
            object(): object(),
            object(): object(),
            object(): object(),
            }

        self.test_signal_handlers = dict(
            (key, object())
            for key in self.test_instance.signal_map.values())
        self.test_signal_handler_map = dict(
            (key, self.test_signal_handlers[target])
            for (key, target) in self.test_instance.signal_map.items())

        def mock_make_signal_handler(target):
            return self.test_signal_handlers[target]
        scaffold.mock(
            "daemon.daemon.DaemonContext._make_signal_handler",
            returns_func=mock_make_signal_handler,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_constructed_signal_handler_items(self):
        """ Should return items as constructed via make_signal_handler. """
        instance = self.test_instance
        expect_result = self.test_signal_handler_map
        result = instance._make_signal_handler_map()
        self.failUnlessEqual(expect_result, result)


class change_working_directory_TestCase(scaffold.TestCase):
    """ Test cases for change_working_directory function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "os.chdir",
            tracker=self.mock_tracker)

        self.test_directory = object()
        self.test_args = dict(
            directory=self.test_directory,
            )

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_changes_working_directory_to_specified_directory(self):
        """ Should change working directory to specified directory. """
        args = self.test_args
        directory = self.test_directory
        expect_mock_output = """\
            Called os.chdir(%(directory)r)
            """ % vars()
        daemon.daemon.change_working_directory(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_daemon_error_on_os_error(self):
        """ Should raise a DaemonError on receiving and OSError. """
        args = self.test_args
        test_error = OSError(errno.ENOENT, "No such directory")
        os.chdir.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_working_directory, **args)

    def test_error_message_contains_original_error_message(self):
        """ Should raise a DaemonError with original message. """
        args = self.test_args
        test_error = OSError(errno.ENOENT, "No such directory")
        os.chdir.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        try:
            daemon.daemon.change_working_directory(**args)
        except expect_error, exc:
            pass
        self.failUnlessIn(str(exc), str(test_error))


class change_root_directory_TestCase(scaffold.TestCase):
    """ Test cases for change_root_directory function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "os.chdir",
            tracker=self.mock_tracker)
        scaffold.mock(
            "os.chroot",
            tracker=self.mock_tracker)

        self.test_directory = object()
        self.test_args = dict(
            directory=self.test_directory,
            )

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_changes_working_directory_to_specified_directory(self):
        """ Should change working directory to specified directory. """
        args = self.test_args
        directory = self.test_directory
        expect_mock_output = """\
            Called os.chdir(%(directory)r)
            ...
            """ % vars()
        daemon.daemon.change_root_directory(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_root_directory_to_specified_directory(self):
        """ Should change root directory to specified directory. """
        args = self.test_args
        directory = self.test_directory
        expect_mock_output = """\
            ...
            Called os.chroot(%(directory)r)
            """ % vars()
        daemon.daemon.change_root_directory(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_daemon_error_on_os_error_from_chdir(self):
        """ Should raise a DaemonError on receiving an OSError from chdir. """
        args = self.test_args
        test_error = OSError(errno.ENOENT, "No such directory")
        os.chdir.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_root_directory, **args)

    def test_raises_daemon_error_on_os_error_from_chroot(self):
        """ Should raise a DaemonError on receiving an OSError from chroot. """
        args = self.test_args
        test_error = OSError(errno.EPERM, "No chroot for you!")
        os.chroot.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_root_directory, **args)

    def test_error_message_contains_original_error_message(self):
        """ Should raise a DaemonError with original message. """
        args = self.test_args
        test_error = OSError(errno.ENOENT, "No such directory")
        os.chdir.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        try:
            daemon.daemon.change_root_directory(**args)
        except expect_error, exc:
            pass
        self.failUnlessIn(str(exc), str(test_error))


class change_file_creation_mask_TestCase(scaffold.TestCase):
    """ Test cases for change_file_creation_mask function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "os.umask",
            tracker=self.mock_tracker)

        self.test_mask = object()
        self.test_args = dict(
            mask=self.test_mask,
            )

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_changes_umask_to_specified_mask(self):
        """ Should change working directory to specified directory. """
        args = self.test_args
        mask = self.test_mask
        expect_mock_output = """\
            Called os.umask(%(mask)r)
            """ % vars()
        daemon.daemon.change_file_creation_mask(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_daemon_error_on_os_error_from_chdir(self):
        """ Should raise a DaemonError on receiving an OSError from umask. """
        args = self.test_args
        test_error = OSError(errno.EINVAL, "Whatchoo talkin' 'bout?")
        os.umask.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_file_creation_mask, **args)

    def test_error_message_contains_original_error_message(self):
        """ Should raise a DaemonError with original message. """
        args = self.test_args
        test_error = OSError(errno.ENOENT, "No such directory")
        os.umask.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        try:
            daemon.daemon.change_file_creation_mask(**args)
        except expect_error, exc:
            pass
        self.failUnlessIn(str(exc), str(test_error))


class change_process_owner_TestCase(scaffold.TestCase):
    """ Test cases for change_process_owner function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "os.setuid",
            tracker=self.mock_tracker)
        scaffold.mock(
            "os.setgid",
            tracker=self.mock_tracker)

        self.test_uid = object()
        self.test_gid = object()
        self.test_args = dict(
            uid=self.test_uid,
            gid=self.test_gid,
            )

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_changes_gid_and_uid_in_order(self):
        """ Should change process GID and UID in correct order.

            Since the process requires appropriate privilege to use
            either of `setuid` or `setgid`, changing the UID must be
            done last.

            """
        args = self.test_args
        expect_mock_output = """\
            Called os.setgid(...)
            Called os.setuid(...)
            """ % vars()
        daemon.daemon.change_process_owner(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_group_id_to_gid(self):
        """ Should change process GID to specified value. """
        args = self.test_args
        gid = self.test_gid
        expect_mock_output = """\
            Called os.setgid(%(gid)r)
            ...
            """ % vars()
        daemon.daemon.change_process_owner(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_changes_user_id_to_uid(self):
        """ Should change process UID to specified value. """
        args = self.test_args
        uid = self.test_uid
        expect_mock_output = """\
            ...
            Called os.setuid(%(uid)r)
            """ % vars()
        daemon.daemon.change_process_owner(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_daemon_error_on_os_error_from_setgid(self):
        """ Should raise a DaemonError on receiving an OSError from setgid. """
        args = self.test_args
        test_error = OSError(errno.EPERM, "No switching for you!")
        os.setgid.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_process_owner, **args)

    def test_raises_daemon_error_on_os_error_from_setuid(self):
        """ Should raise a DaemonError on receiving an OSError from setuid. """
        args = self.test_args
        test_error = OSError(errno.EPERM, "No switching for you!")
        os.setuid.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.change_process_owner, **args)

    def test_error_message_contains_original_error_message(self):
        """ Should raise a DaemonError with original message. """
        args = self.test_args
        test_error = OSError(errno.EINVAL, "Whatchoo talkin' 'bout?")
        os.setuid.mock_raises = test_error
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        try:
            daemon.daemon.change_process_owner(**args)
        except expect_error, exc:
            pass
        self.failUnlessIn(str(exc), str(test_error))


class prevent_core_dump_TestCase(scaffold.TestCase):
    """ Test cases for prevent_core_dump function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        self.RLIMIT_CORE = object()
        scaffold.mock(
            "resource.RLIMIT_CORE", mock_obj=self.RLIMIT_CORE,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.getrlimit", returns=None,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.setrlimit", returns=None,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_sets_core_limit_to_zero(self):
        """ Should set the RLIMIT_CORE resource to zero. """
        expect_resource = self.RLIMIT_CORE
        expect_limit = (0, 0)
        expect_mock_output = """\
            Called resource.getrlimit(
                %(expect_resource)r)
            Called resource.setrlimit(
                %(expect_resource)r,
                %(expect_limit)r)
            """ % vars()
        daemon.daemon.prevent_core_dump()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_error_when_no_core_resource(self):
        """ Should raise DaemonError if no RLIMIT_CORE resource. """
        def mock_getrlimit(res):
            if res == resource.RLIMIT_CORE:
                raise ValueError("Bogus platform doesn't have RLIMIT_CORE")
            else:
                return None
        resource.getrlimit.mock_returns_func = mock_getrlimit
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.prevent_core_dump)


class close_file_descriptor_if_open_TestCase(scaffold.TestCase):
    """ Test cases for close_file_descriptor_if_open function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        self.test_fd = 274

        scaffold.mock(
            "os.close",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_requests_file_descriptor_close(self):
        """ Should request close of file descriptor. """
        fd = self.test_fd
        expect_mock_output = """\
            Called os.close(%(fd)r)
            """ % vars()
        daemon.daemon.close_file_descriptor_if_open(fd)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_ignores_badfd_error_on_close(self):
        """ Should ignore OSError EBADF when closing. """
        fd = self.test_fd
        test_error = OSError(errno.EBADF, "Bad file descriptor")
        def os_close(fd):
            raise test_error
        os.close.mock_returns_func = os_close
        expect_mock_output = """\
            Called os.close(%(fd)r)
            """ % vars()
        daemon.daemon.close_file_descriptor_if_open(fd)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_raises_error_if_error_on_close(self):
        """ Should raise DaemonError if an OSError occurs when closing. """
        fd = self.test_fd
        test_error = OSError(object(), "Unexpected error")
        def os_close(fd):
            raise test_error
        os.close.mock_returns_func = os_close
        expect_error = daemon.daemon.DaemonOSEnvironmentError
        self.failUnlessRaises(
            expect_error,
            daemon.daemon.close_file_descriptor_if_open, fd)


class maxfd_TestCase(scaffold.TestCase):
    """ Test cases for module MAXFD constant. """

    def test_positive(self):
        """ Should be a positive number. """
        maxfd = daemon.daemon.MAXFD
        self.failUnless(maxfd > 0)

    def test_integer(self):
        """ Should be an integer. """
        maxfd = daemon.daemon.MAXFD
        self.failUnlessEqual(int(maxfd), maxfd)

    def test_reasonably_high(self):
        """ Should be reasonably high for default open files limit.

            If the system reports a limit of “infinity” on maximum
            file descriptors, we still need a finite number in order
            to close “all” of them. Ensure this is reasonably high
            to catch most use cases.

            """
        expect_minimum = 2048
        maxfd = daemon.daemon.MAXFD
        self.failUnless(
            expect_minimum <= maxfd,
            msg="MAXFD should be at least %(expect_minimum)r (got %(maxfd)r)"
                % vars())


class get_maximum_file_descriptors_TestCase(scaffold.TestCase):
    """ Test cases for get_maximum_file_descriptors function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        self.RLIMIT_NOFILE = object()
        self.RLIM_INFINITY = object()
        self.test_rlimit_nofile = 2468

        def mock_getrlimit(resource):
            result = (object(), self.test_rlimit_nofile)
            if resource != self.RLIMIT_NOFILE:
                result = NotImplemented
            return result

        self.test_maxfd = object()
        scaffold.mock(
            "daemon.daemon.MAXFD", mock_obj=self.test_maxfd,
            tracker=self.mock_tracker)

        scaffold.mock(
            "resource.RLIMIT_NOFILE", mock_obj=self.RLIMIT_NOFILE,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.RLIM_INFINITY", mock_obj=self.RLIM_INFINITY,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.getrlimit", returns_func=mock_getrlimit,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_system_hard_limit(self):
        """ Should return process hard limit on number of files. """
        expect_result = self.test_rlimit_nofile
        result = daemon.daemon.get_maximum_file_descriptors()
        self.failUnlessEqual(expect_result, result)

    def test_returns_module_default_if_hard_limit_infinity(self):
        """ Should return module MAXFD if hard limit is infinity. """
        self.test_rlimit_nofile = self.RLIM_INFINITY
        expect_result = self.test_maxfd
        result = daemon.daemon.get_maximum_file_descriptors()
        self.failUnlessEqual(expect_result, result)


class close_all_open_files_TestCase(scaffold.TestCase):
    """ Test cases for close_all_open_files function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        self.RLIMIT_NOFILE = object()
        self.RLIM_INFINITY = object()
        self.test_rlimit_nofile = self.RLIM_INFINITY

        def mock_getrlimit(resource):
            result = (self.test_rlimit_nofile, object())
            if resource != self.RLIMIT_NOFILE:
                result = NotImplemented
            return result

        self.test_maxfd = 8
        scaffold.mock(
            "daemon.daemon.get_maximum_file_descriptors",
            returns=self.test_maxfd,
            tracker=self.mock_tracker)

        scaffold.mock(
            "resource.RLIMIT_NOFILE", mock_obj=self.RLIMIT_NOFILE,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.RLIM_INFINITY", mock_obj=self.RLIM_INFINITY,
            tracker=self.mock_tracker)
        scaffold.mock(
            "resource.getrlimit", returns_func=mock_getrlimit,
            tracker=self.mock_tracker)

        scaffold.mock(
            "daemon.daemon.close_file_descriptor_if_open",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_requests_all_open_files_to_close(self):
        """ Should request close of all open files. """
        expect_file_descriptors = reversed(range(self.test_maxfd))
        expect_mock_output = "...\n" + "".join(
            "Called daemon.daemon.close_file_descriptor_if_open(%(fd)r)\n"
                % vars()
            for fd in expect_file_descriptors)
        daemon.daemon.close_all_open_files()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_requests_all_but_excluded_files_to_close(self):
        """ Should request close of all open files but those excluded. """
        test_exclude = set([3, 7])
        args = dict(
            exclude = test_exclude,
            )
        expect_file_descriptors = (
            fd for fd in reversed(range(self.test_maxfd))
            if fd not in test_exclude)
        expect_mock_output = "...\n" + "".join(
            "Called daemon.daemon.close_file_descriptor_if_open(%(fd)r)\n"
                % vars()
            for fd in expect_file_descriptors)
        daemon.daemon.close_all_open_files(**args)
        self.failUnlessMockCheckerMatch(expect_mock_output)


class detach_process_context_TestCase(scaffold.TestCase):
    """ Test cases for detach_process_context function. """

    class FakeOSExit(SystemExit):
        """ Fake exception raised for os._exit(). """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        test_pids = [0, 0]
        scaffold.mock(
            "os.fork", returns_iter=test_pids,
            tracker=self.mock_tracker)
        scaffold.mock(
            "os.setsid",
            tracker=self.mock_tracker)

        def raise_os_exit(status=None):
            raise self.FakeOSExit(status)

        scaffold.mock(
            "os._exit", returns_func=raise_os_exit,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_parent_exits(self):
        """ Parent process should exit. """
        parent_pid = 23
        scaffold.mock("os.fork", returns_iter=[parent_pid],
            tracker=self.mock_tracker)
        expect_mock_output = """\
            Called os.fork()
            Called os._exit(0)
            """
        self.failUnlessRaises(
            self.FakeOSExit,
            daemon.daemon.detach_process_context)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_first_fork_error_raises_error(self):
        """ Error on first fork should raise DaemonProcessDetachError. """
        fork_errno = 13
        fork_strerror = "Bad stuff happened"
        fork_error = OSError(fork_errno, fork_strerror)
        test_pids_iter = iter([fork_error])

        def mock_fork():
            next = test_pids_iter.next()
            if isinstance(next, Exception):
                raise next
            else:
                return next

        scaffold.mock("os.fork", returns_func=mock_fork,
            tracker=self.mock_tracker)
        expect_mock_output = """\
            Called os.fork()
            """
        self.failUnlessRaises(
            daemon.daemon.DaemonProcessDetachError,
            daemon.daemon.detach_process_context)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_child_starts_new_process_group(self):
        """ Child should start new process group. """
        expect_mock_output = """\
            Called os.fork()
            Called os.setsid()
            ...
            """
        daemon.daemon.detach_process_context()
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_child_forks_next_parent_exits(self):
        """ Child should fork, then exit if parent. """
        test_pids = [0, 42]
        scaffold.mock("os.fork", returns_iter=test_pids,
            tracker=self.mock_tracker)
        expect_mock_output = """\
            Called os.fork()
            Called os.setsid()
            Called os.fork()
            Called os._exit(0)
            """
        self.failUnlessRaises(
            self.FakeOSExit,
            daemon.daemon.detach_process_context)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_second_fork_error_reports_to_stderr(self):
        """ Error on second fork should cause report to stderr. """
        fork_errno = 17
        fork_strerror = "Nasty stuff happened"
        fork_error = OSError(fork_errno, fork_strerror)
        test_pids_iter = iter([0, fork_error])

        def mock_fork():
            next = test_pids_iter.next()
            if isinstance(next, Exception):
                raise next
            else:
                return next

        scaffold.mock("os.fork", returns_func=mock_fork,
            tracker=self.mock_tracker)
        expect_mock_output = """\
            Called os.fork()
            Called os.setsid()
            Called os.fork()
            """
        self.failUnlessRaises(
            daemon.daemon.DaemonProcessDetachError,
            daemon.daemon.detach_process_context)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_child_forks_next_child_continues(self):
        """ Child should fork, then continue if child. """
        expect_mock_output = """\
            Called os.fork()
            Called os.setsid()
            Called os.fork()
            """ % vars()
        daemon.daemon.detach_process_context()
        self.failUnlessMockCheckerMatch(expect_mock_output)


class is_process_started_by_init_TestCase(scaffold.TestCase):
    """ Test cases for is_process_started_by_init function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        self.test_ppid = 765

        scaffold.mock(
            "os.getppid",
            returns=self.test_ppid,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_false_by_default(self):
        """ Should return False under normal circumstances. """
        expect_result = False
        result = daemon.daemon.is_process_started_by_init()
        self.failUnlessIs(expect_result, result)

    def test_returns_true_if_parent_process_is_init(self):
        """ Should return True if parent process is `init`. """
        init_pid = 1
        os.getppid.mock_returns = init_pid
        expect_result = True
        result = daemon.daemon.is_process_started_by_init()
        self.failUnlessIs(expect_result, result)


class is_socket_TestCase(scaffold.TestCase):
    """ Test cases for is_socket function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        def mock_getsockopt(level, optname, buflen=None):
            result = object()
            if optname is socket.SO_TYPE:
                result = socket.SOCK_RAW
            return result

        self.mock_socket_getsockopt_func = mock_getsockopt

        self.mock_socket_error = socket.error(
            errno.ENOTSOCK,
            "Socket operation on non-socket")

        self.mock_socket = scaffold.Mock(
            "socket.socket",
            tracker=self.mock_tracker)
        self.mock_socket.getsockopt.mock_raises = self.mock_socket_error

        def mock_socket_fromfd(fd, family, type, proto=None):
            return self.mock_socket

        scaffold.mock(
            "socket.fromfd",
            returns_func=mock_socket_fromfd,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_false_by_default(self):
        """ Should return False under normal circumstances. """
        test_fd = 23
        expect_result = False
        result = daemon.daemon.is_socket(test_fd)
        self.failUnlessIs(expect_result, result)

    def test_returns_true_if_stdin_is_socket(self):
        """ Should return True if `stdin` is a socket. """
        test_fd = 23
        getsockopt = self.mock_socket.getsockopt
        getsockopt.mock_raises = None
        getsockopt.mock_returns_func = self.mock_socket_getsockopt_func
        expect_result = True
        result = daemon.daemon.is_socket(test_fd)
        self.failUnlessIs(expect_result, result)

    def test_returns_false_if_stdin_socket_raises_error(self):
        """ Should return True if `stdin` is a socket and raises error. """
        test_fd = 23
        getsockopt = self.mock_socket.getsockopt
        getsockopt.mock_raises = socket.error(
            object(), "Weird socket stuff")
        expect_result = True
        result = daemon.daemon.is_socket(test_fd)
        self.failUnlessIs(expect_result, result)


class is_process_started_by_superserver_TestCase(scaffold.TestCase):
    """ Test cases for is_process_started_by_superserver function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        def mock_is_socket(fd):
            if sys.__stdin__.fileno() == fd:
                result = self.mock_stdin_is_socket_func()
            else:
                result = False
            return result

        self.mock_stdin_is_socket_func = (lambda: False)

        scaffold.mock(
            "daemon.daemon.is_socket",
            returns_func=mock_is_socket,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_false_by_default(self):
        """ Should return False under normal circumstances. """
        expect_result = False
        result = daemon.daemon.is_process_started_by_superserver()
        self.failUnlessIs(expect_result, result)

    def test_returns_true_if_stdin_is_socket(self):
        """ Should return True if `stdin` is a socket. """
        self.mock_stdin_is_socket_func = (lambda: True)
        expect_result = True
        result = daemon.daemon.is_process_started_by_superserver()
        self.failUnlessIs(expect_result, result)


class is_detach_process_context_required_TestCase(scaffold.TestCase):
    """ Test cases for is_detach_process_context_required function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "daemon.daemon.is_process_started_by_init",
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.is_process_started_by_superserver",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_true_by_default(self):
        """ Should return False under normal circumstances. """
        expect_result = True
        result = daemon.daemon.is_detach_process_context_required()
        self.failUnlessIs(expect_result, result)

    def test_returns_false_if_started_by_init(self):
        """ Should return False if current process started by init. """
        daemon.daemon.is_process_started_by_init.mock_returns = True
        expect_result = False
        result = daemon.daemon.is_detach_process_context_required()
        self.failUnlessIs(expect_result, result)

    def test_returns_true_if_started_by_superserver(self):
        """ Should return False if current process started by superserver. """
        daemon.daemon.is_process_started_by_superserver.mock_returns = True
        expect_result = False
        result = daemon.daemon.is_detach_process_context_required()
        self.failUnlessIs(expect_result, result)


def setup_streams_fixtures(testcase):
    """ Set up common test fixtures for standard streams. """
    testcase.mock_tracker = scaffold.MockTracker()

    testcase.stream_file_paths = dict(
        stdin = tempfile.mktemp(),
        stdout = tempfile.mktemp(),
        stderr = tempfile.mktemp(),
        )

    testcase.stream_files_by_name = dict(
        (name, FakeFileDescriptorStringIO())
        for name in ['stdin', 'stdout', 'stderr']
        )

    testcase.stream_files_by_path = dict(
        (testcase.stream_file_paths[name],
            testcase.stream_files_by_name[name])
        for name in ['stdin', 'stdout', 'stderr']
        )

    scaffold.mock(
        "os.dup2",
        tracker=testcase.mock_tracker)


class redirect_stream_TestCase(scaffold.TestCase):
    """ Test cases for redirect_stream function. """

    def setUp(self):
        """ Set up test fixtures. """
        setup_streams_fixtures(self)

        self.test_system_stream = FakeFileDescriptorStringIO()
        self.test_target_stream = FakeFileDescriptorStringIO()
        self.test_null_file = FakeFileDescriptorStringIO()

        def mock_open(path, flag, mode=None):
            if path == os.devnull:
                result = self.test_null_file.fileno()
            else:
                raise OSError(errno.NOENT, "No such file", path)
            return result

        scaffold.mock(
            "os.open",
            returns_func=mock_open,
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_duplicates_target_file_descriptor(self):
        """ Should duplicate file descriptor from target to system stream. """
        system_stream = self.test_system_stream
        system_fileno = system_stream.fileno()
        target_stream = self.test_target_stream
        target_fileno = target_stream.fileno()
        expect_mock_output = """\
            Called os.dup2(%(target_fileno)r, %(system_fileno)r)
            """ % vars()
        daemon.daemon.redirect_stream(system_stream, target_stream)
        self.failUnlessMockCheckerMatch(expect_mock_output)

    def test_duplicates_null_file_descriptor_by_default(self):
        """ Should by default duplicate the null file to the system stream. """
        system_stream = self.test_system_stream
        system_fileno = system_stream.fileno()
        target_stream = None
        null_path = os.devnull
        null_flag = os.O_RDWR
        null_file = self.test_null_file
        null_fileno = null_file.fileno()
        expect_mock_output = """\
            Called os.open(%(null_path)r, %(null_flag)r)
            Called os.dup2(%(null_fileno)r, %(system_fileno)r)
            """ % vars()
        daemon.daemon.redirect_stream(system_stream, target_stream)
        self.failUnlessMockCheckerMatch(expect_mock_output)


class make_default_signal_map_TestCase(scaffold.TestCase):
    """ Test cases for make_default_signal_map function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        mock_signal_module = ModuleType('signal')
        mock_signal_names = [
            'SIGHUP',
            'SIGCLD',
            'SIGSEGV',
            'SIGTSTP',
            'SIGTTIN',
            'SIGTTOU',
            'SIGTERM',
            ]
        for name in mock_signal_names:
            setattr(mock_signal_module, name, object())

        scaffold.mock(
            "signal",
            mock_obj=mock_signal_module,
            tracker=self.mock_tracker)
        scaffold.mock(
            "daemon.daemon.signal",
            mock_obj=mock_signal_module,
            tracker=self.mock_tracker)

        default_signal_map_by_name = {
            'SIGTSTP': None,
            'SIGTTIN': None,
            'SIGTTOU': None,
            'SIGTERM': 'terminate',
            }

        self.default_signal_map = dict(
            (getattr(signal, name), target)
            for (name, target) in default_signal_map_by_name.items())

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_returns_constructed_signal_map(self):
        """ Should return map per default. """
        expect_result = self.default_signal_map
        result = daemon.daemon.make_default_signal_map()
        self.failUnlessEqual(expect_result, result)

    def test_returns_signal_map_with_only_ids_in_signal_module(self):
        """ Should return map with only signals in the `signal` module.

            The `signal` module is documented to only define those
            signals which exist on the running system. Therefore the
            default map should not contain any signals which are not
            defined in the `signal` module.

            """
        del(self.default_signal_map[signal.SIGTTOU])
        del(signal.SIGTTOU)
        expect_result = self.default_signal_map
        result = daemon.daemon.make_default_signal_map()
        self.failUnlessEqual(expect_result, result)


class set_signal_handlers_TestCase(scaffold.TestCase):
    """ Test cases for set_signal_handlers function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "signal.signal",
            tracker=self.mock_tracker)

        self.signal_handler_map = {
            signal.SIGQUIT: object(),
            signal.SIGSEGV: object(),
            signal.SIGINT: object(),
            }

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_sets_signal_handler_for_each_item(self):
        """ Should set signal handler for each item in map. """
        signal_handler_map = self.signal_handler_map
        expect_mock_output = "".join(
            "Called signal.signal(%(signal_number)r, %(handler)r)\n"
                % vars()
            for (signal_number, handler) in signal_handler_map.items())
        daemon.daemon.set_signal_handlers(signal_handler_map)
        self.failUnlessMockCheckerMatch(expect_mock_output)


class register_atexit_function_TestCase(scaffold.TestCase):
    """ Test cases for register_atexit_function function. """

    def setUp(self):
        """ Set up test fixtures. """
        self.mock_tracker = scaffold.MockTracker()

        scaffold.mock(
            "atexit.register",
            tracker=self.mock_tracker)

    def tearDown(self):
        """ Tear down test fixtures. """
        scaffold.mock_restore()

    def test_registers_function_for_atexit_processing(self):
        """ Should register specified function for atexit processing. """
        func = object()
        expect_mock_output = """\
            Called atexit.register(%(func)r)
            """ % vars()
        daemon.daemon.register_atexit_function(func)
        self.failUnlessMockCheckerMatch(expect_mock_output)
