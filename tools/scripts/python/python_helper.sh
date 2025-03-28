#!/bin/bash
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
# Some helper functions to find the latest python bin and venv path
set -ex

SUPPORTED_PYTHON_VERSIONS=(3.11 3.9 3.8)  # List of pythons supported by Hue
LATEST_PYTHON_VERSION=3.11

python_bin_path() {
  # Searches for the provided python version in various locations on the node
  PYTHON_VERSION="$1"
  PYTHON_VERSION_NO_DOT="${PYTHON_VERSION//./}"
  SEARCH_DIRS=("/usr/local/bin" "/bin" "/usr/bin" "/opt/rh/rh-${PYTHON_VERSION_NO_DOT}/root/usr/bin")

  for DIR in "${SEARCH_DIRS[@]}"; do
    PY_PATH="$DIR/python$PYTHON_VERSION"
    if [[ -x "$PY_PATH" ]]; then
      echo "$PY_PATH"
      return 0
    fi
  done
  return 1
}

find_latest_python() {
  # returns the latest py version, e.g., 3.11, 3.9 or 3.8
  for PYTHON_VERSION in "${SUPPORTED_PYTHON_VERSIONS[@]}"; do
    if python_bin_path "$PYTHON_VERSION" > /dev/null; then
      echo "$PYTHON_VERSION"
      return 0
    fi
  done

  echo "No supported Python versions found in expected locations."
  return 1
}

latest_venv_bin_path() {
  # returns the path to the env/bin of the latest python,
  # relative to the top-level hue directory.
  local version="${1:-$(find_latest_python)}"
  if [ -z "$version" ]; then
    return 1  # Return error if no version provided and find_latest_python failed
  fi
  
  if [ "$version" = "$LATEST_PYTHON_VERSION" ]; then
    echo "build/env/bin"
  else
    echo "build/venvs/python${version}/bin"
  fi
}

