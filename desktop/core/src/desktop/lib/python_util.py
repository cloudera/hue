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
# 
# Extra python utils

import select
import socket
from django.utils.translation import ugettext as _
from desktop import conf


__all__ = ['CaseInsensitiveDict', 'create_synchronous_io_multiplexer']


class CaseInsensitiveDict(dict):
  def __setitem__(self, key, value):
    super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

  def __getitem__(self, key):
    return super(CaseInsensitiveDict, self).__getitem__(key.lower())

  def __contains__(self, key):
    return super(CaseInsensitiveDict, self).__contains__(key.lower())

  @classmethod
  def from_dict(cls, _dict):
    return CaseInsensitiveDict([(isinstance(key, basestring) and key.lower() or key, _dict[key]) for key in _dict])


class SynchronousIOMultiplexer(object):
  def read(self, rd):
    raise NotImplementedError(_('"read" method is not implemented'))

  def write(self, rd):
    raise NotImplementedError(_('"write" method is not implemented'))

  def error(self, rd):
    raise NotImplementedError(_('"error" method is not implemented'))


class SelectSynchronousIOMultiplexer(SynchronousIOMultiplexer):
  def __init__(self, timeout=0):
    self.timeout = 0

  def read(self, fds):
    rlist, wlist, xlist = select.select(fds, [], [], self.timeout)
    return rlist


class PollSynchronousIOMultiplexer(SynchronousIOMultiplexer):
  def __init__(self, timeout=0):
    self.timeout = 0

  def read(self, fds):
    poll_obj = select.poll()
    for fd in fds:
      poll_obj.register(fd, select.POLLIN)
    event_list = poll_obj.poll(self.timeout)
    return [fd_event_tuple[0] for fd_event_tuple in event_list]


def create_synchronous_io_multiplexer(timeout=0):
  if conf.POLL_ENABLED.get():
    try:
      from select import poll
      return PollSynchronousIOMultiplexer(timeout)
    except ImportError:
      pass
  return SelectSynchronousIOMultiplexer(timeout)


def find_unused_port():
  """
  Finds a port that's available.
  Unfortunately, this port may not be available by the time
  the subprocess uses it, but this generally works.
  """
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
  sock.bind(('127.0.0.1', 0))
  sock.listen(socket.SOMAXCONN)
  _, port = sock.getsockname()
  sock.close()
  return port
