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
# Utilities for dealing with file modes.

import stat

def filetype(mode):
  """
  Returns "dir" or "file" according to what type path is.

  @param mode: file mode from "stat" command.
  """
  if stat.S_ISLNK(mode):
    return "link"
  elif stat.S_ISDIR(mode):
    return "dir"
  elif stat.S_ISREG(mode):
    return "file"
  else:
    return "unknown"

def rwxtype(mode):
  """ Returns l/d/-/? for use in "rwx" style strings. """
  if stat.S_ISLNK(mode):
    return "l"
  elif stat.S_ISDIR(mode):
    return "d"
  elif stat.S_ISREG(mode):
    return "-"
  else:
    return "?"

BITS = (stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
    stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
    stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH,
    stat.S_ISVTX)

def expand_mode(mode):
  return map(lambda y: bool(mode & y), BITS)

def compress_mode(tup):
  mode = 0
  for b, n in zip(tup, BITS):
    if b:
      mode += n
  return mode

def rwx(mode, aclBit=False):
  """
  Returns "rwx"-style string like that ls would give you.

  I couldn't find much extant code along these lines;
  this is similar in spirit to the google-able "pathinfo.py".
  """
  bools = expand_mode(mode)
  s = list("rwxrwxrwxt")
  for (i, v) in enumerate(bools[:-1]):
    if not v:
      s[i] = "-"
  # Sticky bit should either be 't' or no char.
  if not bools[-1]:
    s = s[:-1]
  return rwxtype(mode) + "".join(s) + ('+' if aclBit else '')
