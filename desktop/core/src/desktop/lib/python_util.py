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
from desktop.lib.i18n import smart_str


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
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.bind(('127.0.0.1', 0))
    sock.listen(socket.SOMAXCONN)
    _, port = sock.getsockname()
  finally:
    sock.close()

  return port


def force_list_to_strings(lst):
  if not lst:
    return lst

  new_list = []
  for item in lst:
    if isinstance(item, basestring):
      # Strings should not be unicode.
      new_list.append(smart_str(item))
    elif isinstance(item, dict):
      # Recursively force dicts to strings.
      new_list.append(force_dict_to_strings(item))
    elif isinstance(item, list):
      new_list.append(force_list_to_strings(item))
    else:
      # Normal objects, or other literals, should not be converted.
      new_list.append(item)

  return new_list


def force_dict_to_strings(dictionary):
  if not dictionary:
    return dictionary

  new_dict = {}
  for k in dictionary:
    new_key = smart_str(k)
    if isinstance(dictionary[k], basestring):
      # Strings should not be unicode.
      new_dict[new_key] = smart_str(dictionary[k])
    elif isinstance(dictionary[k], dict):
      # Recursively force dicts to strings.
      new_dict[new_key] = force_dict_to_strings(dictionary[k])
    elif isinstance(dictionary[k], list):
      new_dict[new_key] = force_list_to_strings(dictionary[k])
    else:
      # Normal objects, or other literals, should not be converted.
      new_dict[new_key] = dictionary[k]

  return new_dict
