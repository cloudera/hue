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

import logging
import os
import os.path
import sys
import traceback

LOG = logging.getLogger(__name__)

def _deprecation_check(arg0):
  """HUE-71. Deprecate build/env/bin/desktop"""
  if os.path.basename(arg0) == 'desktop':
    to_use = os.path.join(os.path.dirname(arg0), 'hue')
    msg = "Warning: '%s' has been deprecated. Please use '%s' instead." % (arg0, to_use)
    print >> sys.stderr, msg
    LOG.warn(msg)

def entry():
  _deprecation_check(sys.argv[0])

  from django.core.management import execute_manager, find_commands, find_management_module
  from django.core.management import LaxOptionParser
  from django.core.management.base import BaseCommand
  try:
    from desktop import settings, appmanager
  except ImportError, ie:
    traceback.print_exc()
    sys.exit(1)

  # What's the subcommand being run?
  # This code uses the same logic from django.core.management to handle command args
  argv = sys.argv[:]
  parser = LaxOptionParser(option_list=BaseCommand.option_list)
  parser.parse_args(argv)
  if len(argv) > 1:
    prof_id = subcommand = argv[1]
  else:
    prof_id = str(os.getpid())

  # Let django handle the normal execution
  if os.getenv("DESKTOP_PROFILE"):
    _profile(prof_id, lambda: execute_manager(settings))
  else:
    execute_manager(settings)


def _profile(prof_id, func):
  """
  Wrap a call with a profiler
  """
  # Note that some distro don't come with pstats
  import pstats
  try:
    import cProfile as profile
  except ImportError:
    import profile

  PROF_DAT = '/tmp/desktop-profile-%s.dat' % (prof_id,)

  prof = profile.Profile()
  try:
    prof.runcall(func)
  finally:
    if os.path.exists(PROF_DAT):
      os.remove(PROF_DAT)
    prof.dump_stats(PROF_DAT)
    # Sort the calls by time spent and show top 50
    pstats.Stats(PROF_DAT).sort_stats('time').print_stats(50)
    print >>sys.stderr, "Complete profile data in %s" % (PROF_DAT,)
