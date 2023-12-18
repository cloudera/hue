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
import io
import os
import logging
LOG = logging.getLogger()

from filebrowser.conf import ARCHIVE_UPLOAD_TEMPDIR
DEFAULT_WRITE_SIZE = 1024 * 1024 * 128

def calculate_total_size(uuid, totalparts):
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f'{uuid}_{i}') for i in range(totalparts)]
  for file_path in files:
    try:
      total += os.path.getsize(file_path)
    except FileNotFoundError:
      LOG.error(f"calculate_total_size: The file '{file_path}' does not exist.")
    except OSError as e:
      LOG.error(f"calculate_total_size: For the file '{file_path}' error occurred: {e}")
  return total

def generate_chunks(uuid, totalparts, default_write_size=DEFAULT_WRITE_SIZE):
  fp = io.BytesIO()
  total = 0
  files = [os.path.join(ARCHIVE_UPLOAD_TEMPDIR.get(), f'{uuid}_{i}') for i in range(totalparts)]
  for file_path in files:
    with open(file_path, 'rb') as f:
      while True:
        # Read the file in portions, e.g., 1MB at a time
        portion = f.read(1 * 1024 * 1024)
        if not portion:
          break
        fp.write(portion)
        total = total + len(portion)
        # If buffer size is more than 128MB, yield the chunk
        if fp.tell() >= default_write_size:
          fp.seek(0)
          yield fp, total
          fp.close()
          fp = io.BytesIO()
  # Yield any remaining data in the buffer
  if fp.tell() > 0:
    fp.seek(0)
    yield fp, total + fp.tell()
    fp.close()
  # chances are the chunk is zero and we never yielded
  else:
    fp.close()
  for file_path in files:
    os.remove(file_path)
