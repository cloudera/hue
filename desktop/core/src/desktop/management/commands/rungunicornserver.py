#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import unicode_literals

import atexit
import logging
import os
import signal
import sys
import threading
import time
from multiprocessing.util import _exit_function

import gunicorn
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

import desktop.conf
from desktop.lib.gunicorn_cleanup_utils import create_signal_handler, unified_cleanup, write_process_recovery_file
from desktop.lib.gunicorn_log_utils import LOG_LISTENER_SOCKET_PATH, LOG_LISTENER_THREAD, start_log_listener
from desktop.lib.gunicorn_server_utils import (
    activate_translation,
    enable_logging,
    initialize_free_disk_space_in_redis,
    process_arguments,
    run_gunicorn_server,
)

GUNICORN_SERVER_HELP = r"""
  Run Hue using the Gunicorn WSGI server in asynchronous mode.
"""


class Command(BaseCommand):
    help = _("Gunicorn Web server for Hue.")

    def add_arguments(self, parser):
        parser.add_argument('--bind', help=_("Bind Address"), action='store', default=None)

    def handle(self, *args, **options):
        start_server(args, options)

    def usage(self, subcommand):
        return GUNICORN_SERVER_HELP


def start_server(args, options):
    """Main server startup function"""
    global LOG_LISTENER_THREAD

    # Process command line arguments
    options = process_arguments(args, options)
    PID_FILE = options['pid_file']  # Get PID file from processed options

    # Hide the Server software version in the response body
    gunicorn.SERVER_SOFTWARE = "apache"
    os.environ["SERVER_SOFTWARE"] = gunicorn.SERVER_SOFTWARE

    # Activate django translation
    activate_translation()
    enable_logging(args, options)
    atexit.unregister(_exit_function)

    # Remove old rungunicornserver processes and log listener
    unified_cleanup()

    # Start the integrated log listener
    try:
        log_listener = start_log_listener()
        if log_listener:
            logging.info("Integrated log listener started successfully")
        else:
            logging.info("Log listener is disabled")
    except Exception as e:
        logging.error(f"Failed to start integrated log listener: {e}")
        # Continue without log listener if it fails to start

    # Register signal handlers for graceful shutdown
    signal_handler = create_signal_handler(LOG_LISTENER_THREAD, LOG_LISTENER_SOCKET_PATH, PID_FILE)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    # Note: SIGKILL cannot be caught, but we can prepare for cleanup after SIGKILL
    # by writing process info to a recovery file

    if desktop.conf.TASK_SERVER_V2.ENABLED.get():
        initialize_free_disk_space_in_redis()

    with open(PID_FILE, "a") as f:
        f.write("%s\n" % os.getpid())

    # Write initial recovery file for potential post-SIGKILL cleanup
    write_process_recovery_file(socket_path=LOG_LISTENER_SOCKET_PATH, pid_file=PID_FILE)

    # Set up a timer to periodically update the recovery file
    def update_recovery_file():
        while True:
            time.sleep(int(30 * 60))  # Update every 30 minutes
            try:
                write_process_recovery_file(socket_path=LOG_LISTENER_SOCKET_PATH, pid_file=PID_FILE)
            except Exception as e:
                logging.debug(f"Error updating recovery file: {e}")

    recovery_updater = threading.Thread(target=update_recovery_file, daemon=True)
    recovery_updater.start()

    try:
        run_gunicorn_server(args, options)
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logging.error(f"Error running gunicorn server: {e}")
        raise
    finally:
        # Ensure log listener is stopped on exit
        if LOG_LISTENER_THREAD:
            LOG_LISTENER_THREAD.stop()
            LOG_LISTENER_THREAD.join(timeout=5)


if __name__ == '__main__':
    start_server(args=sys.argv[1:], options={})
