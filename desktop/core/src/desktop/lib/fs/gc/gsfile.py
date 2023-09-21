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
import errno

from boto.s3.keyfile import KeyFile
from aws.s3.s3file import _ReadableS3File


def open(key, mode='r'):
  """Open a Google Cloud Storage (GS) file.

  Args:
    key: The GS key object.
    mode (str): The mode for opening the file (default is 'r').

  Returns:
    _ReadableGSFile: A readable GS file object.
      
  Raises:
    IOError: If an unsupported mode is provided.
  """

  if mode == 'r':
    return _ReadableGSFile(key)
  else:
    raise IOError(errno.EINVAL, 'Unavailable mode "%s"' % mode)


class _ReadableGSFile(_ReadableS3File):
  """Readable GS file class.

  This class extends _ReadableS3File for reading GS files.
  """
  def __init__(self, key):
    key_copy = key.bucket.get_key(key.name)
    KeyFile.__init__(self, key_copy)

