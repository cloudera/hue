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

from builtins import object
from six import string_types

import datetime
import select
import socket
import sys

from django.utils.translation import ugettext as _
from desktop import conf
from desktop.lib.i18n import smart_str

from codecs import BOM_UTF8, BOM_UTF16_BE, BOM_UTF16_LE, BOM_UTF32_BE, BOM_UTF32_LE

BOMS = (
    (BOM_UTF8, "UTF-8"),
    (BOM_UTF32_BE, "UTF-32-BE"),
    (BOM_UTF32_LE, "UTF-32-LE"),
    (BOM_UTF16_BE, "UTF-16-BE"),
    (BOM_UTF16_LE, "UTF-16-LE"),
)

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
    return CaseInsensitiveDict([(isinstance(key, string_types) and key.lower() or key, _dict[key]) for key in _dict])


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
    if isinstance(item, string_types):
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
    if isinstance(dictionary[k], string_types):
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


def from_string_to_bits(str_value):
  return ''.join(format(ord(byte), '08b') for byte in str_value)


def get_bytes_from_bits(bit_string):
  """
  This should be used in py3 or above
  """
  padded_bits = bit_string + '0' * (8 - len(bit_string) % 8)
  return list(int(padded_bits, 2).to_bytes(len(padded_bits) // 8, 'big'))


def isASCII(data):
  try:
    data.decode('ASCII')
  except UnicodeDecodeError:
    return False
  else:
    return True


def isUTF8(data):
  try:
    data.decode('UTF-8')
  except UnicodeDecodeError:
    return False
  else:
    return True


def isGB2312(data):
  try:
    data.decode('gb2312')
  except UnicodeDecodeError:
    return False
  else:
    return True


def isUTF8Strict(data):
  try:
    decoded = data.decode('UTF-8')
  except UnicodeDecodeError:
    return False
  else:
    for ch in decoded:
      if 0xD800 <= ord(ch) <= 0xDFFF:
        return False
    return True


def check_bom(data):
  return [encoding for bom, encoding in BOMS if data.startswith(bom)]


def check_encoding(data):
  """
  this is a simplified alternative to GPL chardet
  """
  if isASCII(data):
    return 'ASCII'
  elif sys.version_info[0] == 2 and isUTF8(data):
    return 'utf-8'
  elif sys.version_info[0] > 2 and isUTF8Strict(data):
    return 'utf-8'
  else:
    encoding = check_bom(data)
    if encoding:
      return encoding[0]
    elif isGB2312(data):
      return 'gb2312'
    else:
      return 'cp1252'

def current_ms_from_utc():
  return (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(0)).total_seconds() * 1000
