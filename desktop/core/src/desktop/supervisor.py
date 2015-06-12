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
"""
Simple supervisor application that watches subprocesses and restarts them.

If a process appears to be continuously failing, it will kill the entire
supervisor, hopefully triggering some kind of external monitoring system.
This is usually preferable compared to a partially-up system.

This is heavily modeled after the one_for_one supervision policy in Erlang/OTP:

http://erlang.org/documentation/doc-4.8.2/doc/design_principles/sup_princ.html

In order to have your application managed by supervisor, you need to add
an entry_point to your application's egg with the name 'desktop.supervisor.specs'.
This entry point should point to a SuperviseeSpec instance in your module.
"""
from daemon.pidlockfile import PIDLockFile
import daemon
import exceptions
import grp
import logging
import optparse
import os
import pkg_resources
import pwd
import signal
import subprocess
import sys
import threading
import time

import desktop.lib.daemon_utils
import desktop.lib.paths
import desktop.log

# BaseException not available on python 2.4
try:
  MyBaseException = exceptions.BaseException
except AttributeError:
  MyBaseException = exceptions.Exception

PROC_NAME = 'supervisor'
LOG = logging.getLogger()

# If a process restarts mre than MAX_RESTARTS_IN_WINDOW times
# within TIME_WINDOW number of seconds, the supervisor shuts down
TIME_WINDOW = 120
MAX_RESTARTS_IN_WINDOW = 3

# User and group to setuid/setgid down to for any supervisees that don't have
# the drop_root option set to False
SETUID_USER = "hue"
SETGID_GROUP = "hue"
g_user_uid = None       # We figure out the numeric uid/gid later
g_user_gid = None

# The entry point group in which to find processes to supervise.
ENTRY_POINT_GROUP = "desktop.supervisor.specs"

# How long to wait while trying to acquire the supervisor pid lock
# file. We shouldn't spin long here - we'd rather fail to start up.
LOCKFILE_TIMEOUT = 2

# The hue program
HUE_BIN = os.path.join(desktop.lib.paths.get_run_root(),
                       'build', 'env', 'bin', 'hue')

######

CHILD_PIDS = []
SHOULD_STOP = False

# How long to wait for children processes to die gracefully before
# killing them forceably (seconds)
WAIT_FOR_DEATH = 5

class SuperviseeSpec(object):
  """
  A specification of something that should be supervised.
  Instances should have a .cmdv property which returns a list
  which will be passed through to subprocess.call.
  """

  def __init__(self, drop_root=True):
    """
    @param drop_root: if True, the supervisor will drop root privileges
      before calling the subprocess.
    """
    self.drop_root = drop_root

class DjangoCommandSupervisee(SuperviseeSpec):
  """A supervisee which is simply a desktop django management command."""
  def __init__(self, django_command, **kwargs):
    SuperviseeSpec.__init__(self, **kwargs)
    self.django_command = django_command

  @property
  def cmdv(self):
    return [ HUE_BIN, self.django_command ]


class TimeOutPIDLockFile(PIDLockFile):
  """A PIDLockFile subclass that passes through a timeout on acquisition."""
  def __init__(self, lockfile, timeout, **kwargs):
    PIDLockFile.__init__(self, lockfile, **kwargs)
    self.timeout = timeout

  def __enter__(self):
    super(TimeOutPIDLockFile, self).acquire(timeout=self.timeout)
    return self


class Supervisor(threading.Thread):
  """A thread responsible for keeping the supervised subprocess running"""
  # States of the subprocess
  STATES = (PENDING, RUNNING, FINISHED, ERROR) = range(4)

  def __init__(self, cmdv, **kwargs):
    super(Supervisor, self).__init__()
    self.cmdv = cmdv
    self.popen_kwargs = kwargs
    self.state = Supervisor.PENDING

  def run(self):
    global CHILD_PIDS

    try:
      restart_timestamps = []
      proc_str = " ".join(self.cmdv)
      while True:
        self.state = Supervisor.RUNNING
        LOG.info("Starting process %s" % proc_str)
        pipe = subprocess.Popen(self.cmdv, close_fds=True,
                                stdin=file("/dev/null"),
                                **self.popen_kwargs)
        LOG.info("Started proceses (pid %s) %s" % (pipe.pid, proc_str))
        CHILD_PIDS.append(pipe.pid)
        exitcode = pipe.wait()
        if exitcode == 0:
          LOG.info('Command "%s" exited normally.' % (proc_str,))
          self.state = Supervisor.FINISHED
          return
        if exitcode != 0:
          LOG.warn("Exit code for %s: %d" % (proc_str, exitcode))
          self.state = Supervisor.ERROR
        et = time.time()

        if SHOULD_STOP:
          LOG.info("Stopping %s because supervisor exiting" % proc_str)
          self.state = Supervisor.FINISHED
          return
        restart_timestamps.append(et)
        restart_timestamps = [t for t in restart_timestamps if t > et - TIME_WINDOW]
        if len(restart_timestamps) > MAX_RESTARTS_IN_WINDOW:
          earliest_restart = min(restart_timestamps)
          ago = et - earliest_restart
          LOG.error(
            "Process %s has restarted more than %d times in the last %d seconds" % (
              proc_str, MAX_RESTARTS_IN_WINDOW, int(ago)))
          self.state = Supervisor.ERROR
          return

        LOG.error("Process %s exited abnormally. Restarting it." % (proc_str,))
    except MyBaseException, ex:
      LOG.exception("Uncaught exception. Supervisor exiting.")
      self.state = Supervisor.ERROR


def shutdown(sups):
  global SHOULD_STOP
  SHOULD_STOP = True

  LOG.warn("Supervisor shutting down!")

  for pid in CHILD_PIDS:
    try:
      os.kill(pid, signal.SIGINT)
    except OSError:
      pass

  LOG.warn("Waiting for children to exit for %d seconds..." % WAIT_FOR_DEATH)
  t = time.time()
  still_alive = False
  while time.time() < t + WAIT_FOR_DEATH:
    still_alive = False
    for sup in sups:
      sup.join(0.2)
      still_alive = still_alive or sup.isAlive()
    if not still_alive:
      break
  if still_alive:
    LOG.warn("Children have not exited after %d seconds. Killing them with SIGKILL." %
             WAIT_FOR_DEATH)
    for pid in CHILD_PIDS:
      try:
        os.kill(pid, signal.SIGKILL)
      except OSError:
        pass

  sys.exit(1)

def sig_handler(signum, frame):
  raise SystemExit("Signal %d received. Exiting" % signum)

def parse_args():
  parser = optparse.OptionParser()
  parser.add_option("-d", "--daemon", dest="daemonize",
                    action="store_true", default=False)
  parser.add_option("-p", "--pid-file", dest="pid_file",
                    metavar="PID_FILE", default="supervisor.pid")
  parser.add_option("-l", "--log-dir", dest="log_dir",
                   metavar="DIR", default="logs")
  parser.add_option('-e', '--exclude', dest='supervisee_exclusions',
                    metavar='EXCLUSIONS', default=[], action='append',
                    help='Command NOT to run from supervisor. May be included more than once.')
  parser.add_option('-s', '--show', dest='show_supervisees',
                    action='store_true', default=False)
  parser.add_option('-u', '--user', dest='user',
                    action='store', default=SETUID_USER)
  parser.add_option('-g', '--group', dest='group',
                    action='store', default=SETGID_GROUP)
  (options, args) = parser.parse_args()
  return options

def get_pid_cmdline(pid):
  return subprocess.Popen(["ps", "-p", str(pid), "-o", "cmd", "h"],
                          stdout=subprocess.PIPE, close_fds=True).communicate()[0]

def get_supervisees():
  """Pull the supervisor specifications out of the entry point."""
  eps = list(pkg_resources.iter_entry_points(ENTRY_POINT_GROUP))
  return dict((ep.name, ep.load()) for ep in eps)


def setup_user_info():
  """Translate the user/group info into uid/gid."""
  if os.geteuid() != 0:
    return

  global g_user_uid, g_user_gid
  g_user_uid, g_user_gid = \
      desktop.lib.daemon_utils.get_uid_gid(SETUID_USER, SETGID_GROUP)


def drop_privileges():
  """Drop root privileges down to the specified SETUID_USER.

  N.B. DO NOT USE THE logging MODULE FROM WITHIN THIS FUNCTION.
  This function is run in forked processes right before it calls
  exec, but the fork may have occured while a different thread
  had locked the log. Since it's a forked process, the log will
  be locked forever in the subprocess and thus a logging.X may
  block forever.
  """
  we_are_root = os.getuid() == 0
  if not we_are_root:
    print >>sys.stdout, "[INFO] Not running as root, skipping privilege drop"
    return

  try:
    pw = pwd.getpwnam(SETUID_USER)
  except KeyError:
    print >>sys.stderr, "[ERROR] Couldn't get user information for user " + SETUID_USER
    raise

  try:
    gr = grp.getgrnam(SETGID_GROUP)
  except KeyError:
    print >>sys.stderr, "[ERROR] Couldn't get group information for group " + SETGID_GROUP
    raise

  # gid has to be set first
  os.setgid(gr.gr_gid)
  os.setuid(pw.pw_uid)


def _init_log(log_dir):
  """Initialize logging configuration"""
  desktop.log.basic_logging(PROC_NAME, log_dir)
  if os.geteuid() == 0:
    desktop.log.chown_log_dir(g_user_uid, g_user_gid)


def main():
  global SETUID_USER, SETGID_GROUP
  options = parse_args()
  SETUID_USER = options.user
  SETGID_GROUP = options.group
  root = desktop.lib.paths.get_run_root()
  log_dir = os.path.join(root, options.log_dir)

  if options.show_supervisees:
    for name, supervisee in get_supervisees().iteritems():
      if name not in options.supervisee_exclusions:
        print(name)
    sys.exit(0)

  # Let our children know
  os.environ['DESKTOP_LOG_DIR'] = log_dir

  if not os.path.exists(log_dir):
    os.makedirs(log_dir)

  setup_user_info()

  pid_file = os.path.abspath(os.path.join(root, options.pid_file))
  pidfile_context = TimeOutPIDLockFile(pid_file, LOCKFILE_TIMEOUT)

  existing_pid = pidfile_context.read_pid()
  if existing_pid:
    cmdline = get_pid_cmdline(existing_pid)
    if not cmdline.strip():
      # pid is not actually running
      pidfile_context.break_lock()
    else:
      LOG.error("Pid file %s indicates that Hue is already running (pid %d)" %
                (pid_file, existing_pid))
      sys.exit(1)
  elif pidfile_context.is_locked():
    # If there's no pidfile but there is a lock, it's a strange situation,
    # but we should break the lock because it doesn't seem to be actually running
    logging.warn("No existing pid file, but lock exists. Breaking lock.")
    pidfile_context.break_lock()

  if options.daemonize:
    outfile = file(os.path.join(log_dir, 'supervisor.out'), 'a+', 0)
    context = daemon.DaemonContext(
        working_directory=root,
        pidfile=pidfile_context,
        stdout=outfile,
        stderr=outfile,
        )

    context.signal_map = {
        signal.SIGTERM: sig_handler,
        }

    context.open()
  os.umask(022)

  # Log initialization must come after daemonization, which closes all open files.
  # Log statements before this point goes to stderr.
  _init_log(log_dir)

  sups = []
  try:
    for name, supervisee in get_supervisees().iteritems():

      if name in options.supervisee_exclusions:
        continue

      if supervisee.drop_root:
        preexec_fn = drop_privileges
      else:
        preexec_fn = None

      if options.daemonize:
        log_stdout = file(os.path.join(log_dir, name + '.out'), 'a+', 0)
        log_stderr = log_stdout
      else:
        # Passing None to subprocess.Popen later makes the subprocess inherit the
        # standard fds from the supervisor
        log_stdout = None
        log_stderr = None
      sup = Supervisor(supervisee.cmdv,
                       stdout=log_stdout, stderr=log_stderr,
                       preexec_fn=preexec_fn)
      sup.start()
      sups.append(sup)

    wait_loop(sups, options)
  except MyBaseException, ex:
    LOG.exception("Exception in supervisor main loop")
    shutdown(sups)      # shutdown() exits the process

  return 0


def wait_loop(sups, options):
  while True:
    time.sleep(1)
    for sup in sups:
      sup.join(0.1)
      if not sup.isAlive():
        if sup.state == Supervisor.FINISHED:
          sups.remove(sup)
        else:
          shutdown(sups)        # shutdown() exits the process


if __name__ == "__main__":
  sys.exit(main())
