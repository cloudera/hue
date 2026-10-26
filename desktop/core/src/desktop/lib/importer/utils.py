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

"""Path confinement for the v1 Importer local-file API.

Security rules are shared with the legacy indexer importer via
``indexer.utils.validate_local_upload_path`` (same tmpdir + ``{username}_``
prefix contract used by ``local_file_upload`` and ``upload_local_file``).
"""

from indexer.utils import validate_local_upload_path


def validate_local_file_path(path: str, username: str) -> str:
  """Validate that *path* refers to a file legitimately uploaded by *username*.

  This is the security gate that every ``import_type=local`` v1 operation must
  pass through before opening or deleting a file.

  Implementation is delegated to ``validate_local_upload_path`` so local-file
  confinement stays consistent across the legacy and new Importer APIs.

  Args:
    path: The file path supplied by the client (may be attacker-controlled).
    username: The authenticated username making the request.

  Returns:
    The resolved, absolute path string when all checks pass.

  Raises:
    ValueError: With a non-leaking static message on any violation.
  """
  return validate_local_upload_path(path, username)
