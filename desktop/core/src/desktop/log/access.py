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
Decorators and methods related to access log.
This assumes a single-threaded server.
"""

import logging
import re
import resource
import sys
import threading
import time

import desktop.conf

ACCESS_LOG = logging.getLogger('access')

def access_log_level(lvl):
  """Decorator to set the access log level of a view function."""
  if lvl not in (logging.DEBUG, logging.WARN, logging.ERROR, logging.CRITICAL, logging.FATAL):
    raise ValueError('%s is not a valid logging level' % (lvl,))

  def deco_view(func):
    func.access_log_level = lvl
    return func
  return deco_view


#
# Keep most recent per user per app per view access info
#
# This is a dictionary (indexed by user)
# of dictionary (indexed by app)
# of dictionary (indexed by path)
# of list (of AccessInfo) sorted by time most recent first
#
recent_access_map = { }
_recent_access_map_lk = threading.Lock()
_per_user_lk = { }      # Indexed by username

# Store a map of usernames and a dictionary of
# their IP addresses and last access times
last_access_map = { }

# Max number of records per user per view to keep
_USER_ACCESS_HISTORY_SIZE = desktop.conf.USER_ACCESS_HISTORY_SIZE.get()


class AccessInfo(dict):
  """
  Represents details on a user access.

  In addition to the attributes specified in __init__, it may contain
  ``msg`` -- A message associated with the access
  ``app`` -- The top level package name of the view function, which
             need NOT be a valid Desktop application name
  """
  def __init__(self, request):
    self['username'] = request.user.username or '-anon-'
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
      self['remote_ip'] = request.META.get('HTTP_X_FORWARDED_FOR', '-')
    else:
      self['remote_ip'] = request.META.get('REMOTE_ADDR', '-')
    self['method'] = request.method
    self['path'] = request.path
    self['proto'] = request.META.get('SERVER_PROTOCOL', '-')
    self['agent'] = request.META.get('HTTP_USER_AGENT', '-')
    self['time'] = time.time()
    self['duration'] = None
    self['memory'] = None

  def memory_usage_resource(self):
    """
      This is a lightweight way to get the total peak memory as
       doing the diffing before/after request with guppy was too inconsistent and memory intensive.
      """
    rusage_denom = 1024
    if sys.platform == 'darwin':
      rusage_denom = rusage_denom * 1024
    # get peak memory usage, bytes on OSX, Kilobytes on Linux
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / rusage_denom

  def log(self, level, msg=None, start_time=None):
    is_instrumentation = desktop.conf.INSTRUMENTATION.get()
    self['duration'] = ' returned in %dms' % ((time.time() - start_time) * 1000) if start_time is not None else ''
    self['memory'] = ' (mem: %dmb)' % self.memory_usage_resource() if is_instrumentation else ''

    if msg is not None:
      self['msg'] = msg
      ACCESS_LOG.log(level, '%(remote_ip)s %(username)s - "%(method)s %(path)s %(proto)s"%(duration)s%(memory)s-- %(msg)s' % self)
    else:
      ACCESS_LOG.log(level, '%(remote_ip)s %(username)s - "%(method)s %(path)s %(proto)s"%(duration)s%(memory)s' % self)

  def add_to_access_history(self, app):
    """Record this user access to the recent access map"""
    self['app'] = app
    user = self['username']
    path = self['path']
    try:
      app_dict = recent_access_map[user]
    except KeyError:
      # Hold the global lock when modifying recent_access_map
      _recent_access_map_lk.acquire()
      try:
        app_dict = { }
        _per_user_lk[user] = threading.Lock()
        recent_access_map[user] = app_dict
      finally:
        _recent_access_map_lk.release()

    # Hold the per user lock when modifying adding the access record.
    # We could further break down the locking granularity but that seems silly.
    user_lk = _per_user_lk[user]
    user_lk.acquire()
    try:
      try:
        path_dict = app_dict[app]
      except KeyError:
        path_dict = { }
        app_dict[app] = path_dict

      try:
        view_access_list = path_dict[path]
      except KeyError:
        view_access_list = [ ]
        path_dict[path] = view_access_list

      # Most recent first
      view_access_list.insert(0, self)
      if len(view_access_list) > _USER_ACCESS_HISTORY_SIZE:
        view_access_list.pop()

      # Update the IP address and last access time of the user
      last_access_map[user] = {'ip': self['remote_ip'], 'time': self['time']}
    finally:
      user_lk.release()


_MODULE_RE = re.compile('[^.]*')

def log_page_hit(request, view_func, level=None, start_time=None):
  """Log the request to the access log"""
  if level is None:
    level = logging.INFO
  ai = AccessInfo(request)
  ai.log(level, start_time=start_time)

  # Disabled for now as not used
  # Find the app
#   app_re_match = _MODULE_RE.match(view_func.__module__)
#   app = app_re_match and app_re_match.group(0) or '-'
#   ai.add_to_access_history(app)


def access_log(request, msg=None, level=None):
  """
  access_log(request, msg=None, level=None) -> None

  Write to the access log. This could be a page hit, or general auditing information.
  """
  if level is None:
    level = logging.INFO
  ai = AccessInfo(request)
  ai.log(level, msg)


def access_warn(request, msg=None):
  """Write to access log with a WARN log level"""
  ai = AccessInfo(request)
  ai.log(logging.WARN, msg)
