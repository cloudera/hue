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

from __future__ import absolute_import

import errno

from boto.s3.keyfile import KeyFile

from aws.conf import get_key_expiry
from aws.s3 import translate_s3_error

DEFAULT_READ_SIZE = 1024 * 1024  # 1MB

def open(key, mode='r'):
  if mode == 'r':
    return _ReadableS3File(key)
  else:
    raise IOError(errno.EINVAL, 'Unavailable mode "%s"' % mode)


class _ReadableS3File(KeyFile):
  def __init__(self, key):
      key_copy = key.bucket.get_key(key.name, validate=False)
      KeyFile.__init__(self, key_copy)

  def read_url(self):
    return self.getkey().generate_url(get_key_expiry())

  @translate_s3_error
  def read(self, length=DEFAULT_READ_SIZE):
    return KeyFile.read(self, length)