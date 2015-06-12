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

import grp
import os
import pwd
import desktop.log

def _change_uid_gid(uid, gid=None):
  """Try to change UID and GID to the provided values.
  UID and GID are given as integers.

  Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
  """
  if not os.geteuid() == 0:
    # Do not try to change the gid/uid if not root.
    return
  os.setgid(gid)
  os.setuid(uid)

def get_uid_gid(username, groupname=None):
  """Try to change UID and GID to the provided values.
  The parameters are given as names like 'nobody' not integer.
  May raise KeyError.

  Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
  """
  try:
    uid, default_grp = pwd.getpwnam(username)[2:4]
  except KeyError:
    raise KeyError("Couldn't get user id for user %s" % (username,))
  if groupname is None:
    gid = default_grp
  else:
    try:
      gid = grp.getgrnam(groupname)[2]
    except KeyError:
      raise KeyError("Couldn't get group id for group %s" % (groupname,))
  return (uid, gid)

def drop_privileges_if_necessary(options):
  if os.geteuid() == 0 and options['server_user'] and options['server_group']:
    # ensure the that the daemon runs as specified user
    (uid, gid) = get_uid_gid(options['server_user'], options['server_group'])
    desktop.log.chown_log_dir(uid, gid)
    _change_uid_gid(uid, gid)

