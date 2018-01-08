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
# Writes some sample data to the LocalSubFileSystem.

import grp
import tempfile
import logging
import os

from django.utils import lorem_ipsum
from hadoop.fs import LocalSubFileSystem

logger = logging.getLogger(__name__)

def create(dir=None):
  """Creates a "filesystem" in a new temp dir and creates one file in it."""
  if not dir:
    dir = tempfile.mkdtemp()

  logger.info("Using %s as base dir." % dir)
  fs = LocalSubFileSystem(dir)

  def write(path, contents):
    f = fs.open(path, "w")
    f.write(contents)
    f.close()

  write("/hello.txt", "hello world\n")
  write("/goodbye.txt","goodbyte\n")
  write("/xss.html","<blink>escape!!!</blink><script>alert('hello')</script>\n")
  write("/evil path%-of&doom?.txt", "annoying, eh?\n")
  # no </script> tag in filename, since that's a path delimiter.
  write("/xsspath<i><script>alert('hello').txt", "definitely annoying.\n")
  # But we can do </script> as a multi-directory thing!
  fs.mkdir("/<script>alert('hello')<")
  write("/<script>alert('hello')</script>", "there")
  fs.mkdir("/sub?dir")
  write("/sub?dir/howdy.txt", "there\n")
  fs.mkdir("/bigfiles")
  write("/bigfiles/loremipsum.txt", "\n\n".join(lorem_ipsum.paragraphs(1000)))
  # 50K of dev random
  write("/bigfiles/random_binary.bin", open("/dev/urandom").read(1024*50))
  write("/count", "0123456789"*8)

  write("/chmod-unreadable", "")
  fs.chmod("/chmod-unreadable", 0000)
  write("/chown-staff-group", "")
  try:
    stats = fs.stats("/chown-staff-group")

    # Figure out a group id that is different from the one it already has
    cur_gid = grp.getgrnam(stats["group"]).gr_gid
    other_groups = [gid for gid in os.getgroups() if gid != cur_gid]
    new_gid = other_groups[0]

    fs.chown("/chown-staff-group", fs.stats("/chown-staff-group")["user"],
             grp.getgrgid(new_gid).gr_name)
  except OSError:
    logger.exception("Ignoring error.")
  return fs
