#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comprehensive test suite for Gunicorn log listener functionality.

This module contains pytest-based tests for the Gunicorn log listener components,
including ConfigStreamHandler, LogListenerThread, recovery file operations, and
signal handler integration.

The tests are organized into classes following pytest best practices:
- TestConfigStreamHandler: Tests for log record processing
- TestLogListenerThread: Tests for thread lifecycle and management
- TestRecoveryFileOperations: Tests for process recovery file handling
- TestSignalHandlerIntegration: Tests for signal handler functionality

Usage:
    Run all tests: pytest gunicorn_loglistener_minimal_test.py
    Run specific class: pytest gunicorn_loglistener_minimal_test.py::TestConfigStreamHandler
    Run specific test: pytest gunicorn_loglistener_minimal_test.py::TestConfigStreamHandler::test_log_record_handling
"""

import logging
import os
import pickle
import struct
import tempfile
from unittest.mock import Mock, patch

import pytest

from desktop.lib.gunicorn_cleanup_utils import cleanup_from_recovery_file, create_signal_handler, write_process_recovery_file
from desktop.lib.gunicorn_log_utils import ConfigStreamHandler, LogListenerThread, start_log_listener, stop_log_listener


@pytest.fixture
def temp_setup():
  """Fixture to set up temporary directory and socket path for tests"""
  temp_dir = tempfile.mkdtemp()
  socket_path = os.path.join(temp_dir, 'test.sock')

  yield temp_dir, socket_path

  # Cleanup
  try:
    stop_log_listener()
  except Exception:
    pass

  import shutil
  shutil.rmtree(temp_dir, ignore_errors=True)


class GunicornLogListenerTestBase:
  """Base class for gunicorn log listener tests with common utilities"""

  @classmethod
  def setup_class(cls):
    """Setup class-level test resources"""
    cls.test_data_dir = tempfile.mkdtemp(prefix='gunicorn_test_')

  @classmethod
  def teardown_class(cls):
    """Cleanup class-level test resources"""
    try:
      stop_log_listener()
    except Exception:
      pass

    import shutil
    if hasattr(cls, 'test_data_dir') and os.path.exists(cls.test_data_dir):
      shutil.rmtree(cls.test_data_dir, ignore_errors=True)

  def create_mock_log_record(self, name='test.logger', level=logging.INFO, msg='Test message'):
    """Create a mock log record for testing"""
    return logging.LogRecord(
      name=name,
      level=level,
      pathname='/test/path.py',
      lineno=42,
      msg=msg,
      args=(),
      exc_info=None
    )


class TestConfigStreamHandler(GunicornLogListenerTestBase):
  """Test cases for ConfigStreamHandler functionality"""

  @pytest.mark.parametrize("log_level,expected_level", [
    (logging.DEBUG, logging.DEBUG),
    (logging.INFO, logging.INFO),
    (logging.WARNING, logging.WARNING),
    (logging.ERROR, logging.ERROR),
    (logging.CRITICAL, logging.CRITICAL),
  ])
  def test_log_record_handling_different_levels(self, log_level, expected_level):
    """Test log record processing with different log levels"""
    mock_connection = Mock()
    mock_server = Mock()
    mock_server.ready = True
    mock_server.logname = None

    handler = ConfigStreamHandler(
      mock_connection,
      ('127.0.0.1', 12345),
      mock_server
    )

    # Create a test log record with specified level
    record = self.create_mock_log_record(level=log_level)

    # Serialize the record
    pickled_record = pickle.dumps(record.__dict__)
    record_length = struct.pack('>L', len(pickled_record))

    def mock_recv_side_effect(size):
      if not hasattr(mock_recv_side_effect, 'call_count'):
        mock_recv_side_effect.call_count = 0
      mock_recv_side_effect.call_count += 1

      if mock_recv_side_effect.call_count == 1:
        return record_length
      elif mock_recv_side_effect.call_count == 2:
        return pickled_record
      else:
        mock_server.ready = False
        return b''

    mock_connection.recv.side_effect = mock_recv_side_effect

    with patch('logging.getLogger') as mock_get_logger:
      mock_logger = Mock()
      mock_get_logger.return_value = mock_logger

      handler.handle()

      mock_get_logger.assert_called_with('test.logger')
      mock_logger.handle.assert_called_once()
      # Verify the log record has the expected level
      call_args = mock_logger.handle.call_args[0][0]
      assert call_args.levelno == expected_level

  def test_log_record_handling(self):
    """Test core log record processing functionality"""
    # Test ConfigStreamHandler can process log records
    mock_connection = Mock()
    mock_server = Mock()
    mock_server.ready = True  # Allow processing
    mock_server.logname = None

    handler = ConfigStreamHandler(
      mock_connection,
      ('127.0.0.1', 12345),
      mock_server
    )

    # Create a test log record
    record = self.create_mock_log_record()

    # Serialize the record
    pickled_record = pickle.dumps(record.__dict__)
    record_length = struct.pack('>L', len(pickled_record))

    # Mock connection.recv to return our data, then stop server
    def mock_recv_side_effect(size):
      if not hasattr(mock_recv_side_effect, 'call_count'):
        mock_recv_side_effect.call_count = 0
      mock_recv_side_effect.call_count += 1

      if mock_recv_side_effect.call_count == 1:
        return record_length
      elif mock_recv_side_effect.call_count == 2:
        return pickled_record
      else:
        # Stop server after processing
        mock_server.ready = False
        return b''

    mock_connection.recv.side_effect = mock_recv_side_effect

    # Mock the logger
    with patch('logging.getLogger') as mock_get_logger:
      mock_logger = Mock()
      mock_get_logger.return_value = mock_logger

      # Call handle method
      handler.handle()

      # Verify logger was called
      mock_get_logger.assert_called_with('test.logger')
      mock_logger.handle.assert_called_once()


class TestLogListenerThread(GunicornLogListenerTestBase):
  """Test cases for LogListenerThread functionality"""

  @pytest.mark.parametrize("invalid_socket_path", [
    "/invalid/path/that/does/not/exist.sock",
    "",
    None,
  ])
  def test_thread_initialization_with_invalid_paths(self, invalid_socket_path):
    """Test thread initialization with invalid socket paths"""
    # All these should work during initialization, but may fail during start
    thread = LogListenerThread(invalid_socket_path)
    assert thread.server_address == invalid_socket_path
    assert thread.daemon
    assert not thread.ready.is_set()
    assert thread.stopped()

  def test_thread_lifecycle(self, temp_setup):
    """Test log listener thread start/stop lifecycle"""
    temp_dir, socket_path = temp_setup
    thread = LogListenerThread(socket_path)

    # Test initialization
    assert thread.server_address == socket_path
    assert not thread.ready.is_set()
    assert thread.daemon

    # Test stopped status
    assert thread.stopped()

  def test_start_stop_log_listener(self, temp_setup):
    """Test start and stop log listener functionality"""
    temp_dir, socket_path = temp_setup

    with patch('desktop.lib.gunicorn_log_utils.LogListenerThread') as mock_thread_class:
      with patch('desktop.lib.gunicorn_log_utils.enable_log_listener_logging') as mock_enable_logging:
        # Mock the thread
        mock_thread = Mock()
        mock_thread.ready.wait.return_value = True
        mock_thread_class.return_value = mock_thread

        # Start log listener
        thread = start_log_listener(socket_path)

        # Verify listener was created and started
        mock_thread_class.assert_called_once_with(server_address=socket_path, verify=None)
        assert thread == mock_thread
        mock_thread.start.assert_called_once()
        mock_thread.ready.wait.assert_called_once()
        mock_enable_logging.assert_called_once_with(socket_path)

        # Test stop functionality
        stop_log_listener()  # Should complete without errors


class TestRecoveryFileOperations(GunicornLogListenerTestBase):
  """Test cases for process recovery file operations"""

  def test_recovery_file_creation_and_cleanup(self, temp_setup):
    """Test process recovery file creation and cleanup"""
    temp_dir, socket_path = temp_setup

    with patch('psutil.Process') as mock_process_class:
      # Mock process
      mock_process = Mock()
      mock_process.pid = 12345
      mock_process.create_time.return_value = 1234567890.0
      mock_process.children.return_value = []
      mock_process_class.return_value = mock_process

      recovery_file = os.path.join(temp_dir, 'hue_recovery.json')

      # Test writing recovery file
      with patch.dict(os.environ, {'DESKTOP_LOG_DIR': temp_dir}):
        write_process_recovery_file(
          socket_path=socket_path,
          pid_file='/tmp/test.pid'
        )

      # Verify recovery file was created
      assert os.path.exists(recovery_file)

      # Test cleanup from recovery file when no process is running
      mock_process.is_running.return_value = False
      mock_process_class.side_effect = lambda pid: mock_process

      with patch.dict(os.environ, {'DESKTOP_LOG_DIR': temp_dir}):
        cleanup_from_recovery_file()

      # Recovery file should be cleaned up
      assert not os.path.exists(recovery_file)


class TestSignalHandlerIntegration(GunicornLogListenerTestBase):
  """Test cases for signal handler functionality"""

  def test_signal_handler_creation_and_execution(self, temp_setup):
    """Test signal handler creation and integration"""
    temp_dir, socket_path = temp_setup

    mock_log_listener = Mock()
    test_socket = os.path.join(temp_dir, 'signal_test.sock')
    test_pid_file = os.path.join(temp_dir, 'signal_test.pid')

    # Create test files
    with open(test_socket, 'w') as f:
      f.write('')
    with open(test_pid_file, 'w') as f:
      f.write('12345')

    # Create signal handler
    handler = create_signal_handler(
      mock_log_listener,
      test_socket,
      test_pid_file
    )

    # Verify handler is callable
    assert callable(handler)

    # Test signal handler execution
    with patch('os._exit') as mock_exit:
      with patch('desktop.lib.gunicorn_cleanup_utils.terminate_child_processes'):
        with patch('desktop.lib.gunicorn_cleanup_utils.cleanup_recovery_file'):
          handler(15, None)  # SIGTERM

    # Verify log listener was stopped
    mock_log_listener.stop.assert_called_once()
    mock_log_listener.join.assert_called_with(timeout=5)

    # Verify files were cleaned up
    assert not os.path.exists(test_socket)
    assert not os.path.exists(test_pid_file)

    # Verify exit was called
    mock_exit.assert_called_with(0)
