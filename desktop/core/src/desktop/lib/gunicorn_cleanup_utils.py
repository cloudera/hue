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
Gunicorn Process Cleanup Utilities

This module contains utilities for cleaning up orphaned processes and handling
recovery from SIGKILL events in Gunicorn environments.
"""

import json
import logging
import os


def write_process_recovery_file(main_pid=None, socket_path=None, pid_file=None):
  """
  Write process information to a recovery file for post-SIGKILL cleanup
  """
  try:
    import psutil

    recovery_file = os.path.join(os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"), "hue_recovery.json")

    if main_pid is None:
      current_process = psutil.Process()
      main_pid = current_process.pid
    else:
      current_process = psutil.Process(main_pid)

    process_info = {
      "main_pid": main_pid,
      "start_time": current_process.create_time(),
      "socket_path": socket_path,
      "pid_file": pid_file,
      "children": []
    }

    # Record all child processes
    for child in current_process.children(recursive=True):
      try:
        process_info["children"].append({
          "pid": child.pid,
          "name": child.name(),
          "cmdline": child.cmdline(),
          "start_time": child.create_time()
        })
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

    with open(recovery_file, 'w') as f:
      json.dump(process_info, f, indent=2)

    logging.debug(f"Written recovery file: {recovery_file}")

  except Exception as e:
    logging.error(f"Error writing recovery file: {e}")


def cleanup_from_recovery_file():
  """
  Clean up processes using information from recovery file (for post-SIGKILL cleanup)
  """
  try:
    import psutil

    recovery_file = os.path.join(os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"), "hue_recovery.json")

    if not os.path.exists(recovery_file):
      logging.info("No recovery file found")
      return

    with open(recovery_file, 'r') as f:
      process_info = json.load(f)

    logging.info(f"Processing recovery file for main PID {process_info['main_pid']}")

    # Check if main process is still running
    try:
      main_proc = psutil.Process(process_info['main_pid'])
      if main_proc.is_running():
        logging.info(f"Main process {process_info['main_pid']} is still running, skipping cleanup")
        return
    except psutil.NoSuchProcess:
      logging.info(f"Main process {process_info['main_pid']} is no longer running, proceeding with cleanup")

    # Clean up child processes
    cleaned_count = 0
    for child_info in process_info['children']:
      try:
        child_proc = psutil.Process(child_info['pid'])
        if child_proc.is_running():
          # Verify it's the same process (check start time)
          if abs(child_proc.create_time() - child_info['start_time']) < 1.0:
            logging.info(f"Terminating orphaned child process: PID {child_info['pid']}, CMD: {' '.join(child_info['cmdline'])}")
            child_proc.terminate()
            try:
              child_proc.wait(timeout=5)
              cleaned_count += 1
            except psutil.TimeoutExpired:
              logging.warning(f"Force killing child process: PID {child_info['pid']}")
              child_proc.kill()
              cleaned_count += 1
      except (psutil.NoSuchProcess, psutil.AccessDenied):
        logging.info(f"Child process {child_info['pid']} is no longer running, proceeding with cleanup")
        continue

    # Clean up socket file
    if process_info.get('socket_path') and os.path.exists(process_info['socket_path']):
      try:
        os.unlink(process_info['socket_path'])
        logging.info(f"Cleaned up socket file: {process_info['socket_path']}")
      except OSError as e:
        logging.warning(f"Could not clean up socket file: {e}")

    # Clean up PID file
    if process_info.get('pid_file') and os.path.exists(process_info['pid_file']):
      try:
        os.unlink(process_info['pid_file'])
        logging.info(f"Cleaned up PID file: {process_info['pid_file']}")
      except OSError as e:
        logging.warning(f"Could not clean up PID file: {e}")

    # Remove recovery file
    os.unlink(recovery_file)
    logging.info(f"Recovery cleanup completed: {cleaned_count} processes cleaned up")

  except Exception as e:
    logging.error(f"Error during recovery cleanup: {e}")


def cleanup_orphaned_processes():
  """
  Clean up any orphaned processes that might be left behind
  """
  try:
    import psutil
    current_pid = os.getpid()

    # Look for processes that might be related to this Hue instance
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
      try:
        if proc.info['pid'] == current_pid:
          continue

        cmdline = ' '.join(proc.info['cmdline'] or [])

        # Check if this looks like a related Hue process
        if ('rungunicornserver' in cmdline or
          'hue' in proc.info['name'].lower() or
          ('python' in proc.info['name'].lower() and 'hue' in cmdline)):

          # Check if it's actually orphaned (parent is init or doesn't exist)
          try:
            parent = proc.parent()
            if parent is None or parent.pid == 1:
              logging.warning(f"Found orphaned process: PID {proc.info['pid']}, CMD: {cmdline}")
              proc.terminate()
              # Give it time to terminate gracefully
              try:
                proc.wait(timeout=5)
                logging.info(f"Successfully terminated orphaned process: PID {proc.info['pid']}")
              except psutil.TimeoutExpired:
                logging.warning(f"Force killing orphaned process: PID {proc.info['pid']}")
                proc.kill()
          except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

      except (psutil.NoSuchProcess, psutil.AccessDenied, IndexError):
        continue

  except Exception as e:
    logging.error(f"Error during orphaned process cleanup: {e}")


def unified_cleanup():
  """
  Unified cleanup function that handles both recovery file cleanup and general orphan cleanup
  """
  logging.info("Starting unified cleanup process...")

  # Step 1: Try recovery file cleanup first (more precise)
  try:
    recovery_file = os.path.join(os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"), "hue_recovery.json")
    if os.path.exists(recovery_file):
      logging.info("Found recovery file, attempting recovery cleanup...")
      cleanup_from_recovery_file()
      return  # If recovery cleanup worked, we're done
    else:
      logging.info("No recovery file found, proceeding with general cleanup...")
  except Exception as e:
    logging.warning(f"Recovery cleanup failed: {e}, falling back to general cleanup...")

  # Step 2: Fall back to general orphan cleanup
  cleanup_orphaned_processes()


def cleanup_recovery_file():
  """
  Clean up recovery file on normal shutdown
  """
  try:
    recovery_file = os.path.join(os.getenv("DESKTOP_LOG_DIR", "/var/log/hue"), "hue_recovery.json")
    if os.path.exists(recovery_file):
      os.unlink(recovery_file)
      logging.info("Cleaned up recovery file")
  except Exception as e:
    logging.warning(f"Could not clean up recovery file: {e}")


def terminate_child_processes():
  """
  Terminate all child processes (gunicorn workers) with timeout and force-kill fallback
  """
  try:
    import psutil
    current_process = psutil.Process()
    children = current_process.children(recursive=True)

    if children:
      logging.info(f"Terminating {len(children)} child processes...")
      for child in children:
        try:
          child.terminate()
        except psutil.NoSuchProcess:
          pass

      # Wait for children to terminate gracefully
      gone, alive = psutil.wait_procs(children, timeout=10)

      # Force kill any remaining processes
      if alive:
        logging.warning(f"Force killing {len(alive)} remaining child processes...")
        for child in alive:
          try:
            child.kill()
          except psutil.NoSuchProcess:
            pass
  except Exception as e:
    logging.error(f"Error terminating child processes: {e}")


def cleanup_pid_file(pid_file):
  """
  Clean up PID file
  """
  if pid_file and os.path.exists(pid_file):
    try:
      os.unlink(pid_file)
      logging.info(f"Cleaned up PID file: {pid_file}")
    except OSError as e:
      logging.warning(f"Could not clean up PID file {pid_file}: {e}")


def cleanup_socket_file(socket_path):
  """
  Clean up socket file
  """
  if socket_path and os.path.exists(socket_path):
    try:
      os.unlink(socket_path)
      logging.info(f"Cleaned up socket file: {socket_path}")
    except OSError as e:
      logging.warning(f"Could not clean up socket file {socket_path}: {e}")


def create_signal_handler(log_listener_thread, socket_path, pid_file):
  """
  Create a signal handler function with the necessary cleanup context
  """
  def signal_handler_with_log_listener(sig, frame):
    """
    Signal handler that properly shuts down both gunicorn and log listener
    """
    try:
      logging.info(f"Received signal {sig}, shutting down log listener and server...")

      # Stop log listener first
      if log_listener_thread:
        logging.info("Stopping log listener thread...")
        log_listener_thread.stop()
        log_listener_thread.join(timeout=5)  # Wait up to 5 seconds for clean shutdown
        logging.info("Log listener thread stopped")
    except Exception as e:
      logging.error(f"Error stopping log listener: {e}")

    # Clean up socket file
    cleanup_socket_file(socket_path)

    # Clean up PID file
    cleanup_pid_file(pid_file)

    # Terminate all child processes (gunicorn workers)
    terminate_child_processes()

    # Clean up recovery file on normal shutdown
    cleanup_recovery_file()

    logging.info("Graceful shutdown completed")
    os._exit(0)  # Use os._exit to avoid cleanup handlers that might hang

  return signal_handler_with_log_listener
