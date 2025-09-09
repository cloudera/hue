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
Minimal test suite for log listener functionality - 5 essential tests
"""

import logging
import os
import pickle
import struct
import tempfile
import unittest
from unittest.mock import Mock, patch

from desktop.lib.gunicorn_cleanup_utils import cleanup_from_recovery_file, create_signal_handler, write_process_recovery_file
from desktop.lib.gunicorn_log_utils import ConfigStreamHandler, LogListenerThread, start_log_listener, stop_log_listener


class TestMinimalLogListener(unittest.TestCase):
  """Minimal test suite covering essential loglistener functionality"""

  def setUp(self):
    self.temp_dir = tempfile.mkdtemp()
    self.socket_path = os.path.join(self.temp_dir, 'test.sock')

  def tearDown(self):
    try:
      stop_log_listener()
    except Exception:
      pass

    import shutil
    shutil.rmtree(self.temp_dir, ignore_errors=True)

  def test_1_log_record_handling(self):
    """Test 1: Core log record processing functionality"""
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
    record = logging.LogRecord(
      name='test.logger',
      level=logging.INFO,
      pathname='/test/path.py',
      lineno=42,
      msg='Test message',
      args=(),
      exc_info=None
    )

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

  def test_2_thread_lifecycle(self):
    """Test 2: Log listener thread start/stop lifecycle"""
    thread = LogListenerThread(self.socket_path)

    # Test initialization
    self.assertEqual(thread.server_address, self.socket_path)
    self.assertFalse(thread.ready.is_set())
    self.assertTrue(thread.daemon)

    # Test stopped status
    self.assertTrue(thread.stopped())

  @patch('desktop.lib.gunicorn_log_utils.LogListenerThread')
  @patch('desktop.lib.gunicorn_log_utils.enable_log_listener_logging')
  def test_3_start_stop_log_listener(self, mock_enable_logging, mock_thread_class):
    """Test 3: Start and stop log listener functionality"""
    # Mock the thread
    mock_thread = Mock()
    mock_thread.ready.wait.return_value = True
    mock_thread_class.return_value = mock_thread

    # Start log listener
    thread = start_log_listener(self.socket_path)

    # Verify listener was created and started
    mock_thread_class.assert_called_once_with(server_address=self.socket_path, verify=None)
    self.assertEqual(thread, mock_thread)
    mock_thread.start.assert_called_once()
    mock_thread.ready.wait.assert_called_once()
    mock_enable_logging.assert_called_once_with(self.socket_path)

    # Test stop functionality
    stop_log_listener()  # Should complete without errors

  @patch('psutil.Process')
  def test_4_recovery_file_operations(self, mock_process_class):
    """Test 4: Process recovery file creation and cleanup"""
    # Mock process
    mock_process = Mock()
    mock_process.pid = 12345
    mock_process.create_time.return_value = 1234567890.0
    mock_process.children.return_value = []
    mock_process_class.return_value = mock_process

    recovery_file = os.path.join(self.temp_dir, 'hue_recovery.json')

    # Test writing recovery file
    with patch.dict(os.environ, {'DESKTOP_LOG_DIR': self.temp_dir}):
      write_process_recovery_file(
        socket_path=self.socket_path,
        pid_file='/tmp/test.pid'
      )

    # Verify recovery file was created
    self.assertTrue(os.path.exists(recovery_file))

    # Test cleanup from recovery file when no process is running
    mock_process.is_running.return_value = False
    mock_process_class.side_effect = lambda pid: mock_process

    with patch.dict(os.environ, {'DESKTOP_LOG_DIR': self.temp_dir}):
      cleanup_from_recovery_file()

    # Recovery file should be cleaned up
    self.assertFalse(os.path.exists(recovery_file))

  def test_5_signal_handler_integration(self):
    """Test 5: Signal handler creation and integration"""
    mock_log_listener = Mock()
    test_socket = os.path.join(self.temp_dir, 'signal_test.sock')
    test_pid_file = os.path.join(self.temp_dir, 'signal_test.pid')

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
    self.assertTrue(callable(handler))

    # Test signal handler execution
    with patch('os._exit') as mock_exit:
      with patch('desktop.lib.gunicorn_cleanup_utils.terminate_child_processes'):
        with patch('desktop.lib.gunicorn_cleanup_utils.cleanup_recovery_file'):
          handler(15, None)  # SIGTERM

    # Verify log listener was stopped
    mock_log_listener.stop.assert_called_once()
    mock_log_listener.join.assert_called_with(timeout=5)

    # Verify files were cleaned up
    self.assertFalse(os.path.exists(test_socket))
    self.assertFalse(os.path.exists(test_pid_file))

    # Verify exit was called
    mock_exit.assert_called_with(0)


if __name__ == '__main__':
  unittest.main()
