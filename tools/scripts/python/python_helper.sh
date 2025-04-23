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

# Some helper functions to find the latest python bin and venv path
set -ex

# Find the latest Python binary in build/env/bin
LATEST_PYTHON=$([ -d "$HUE_HOME_DIR/build/env/bin" ] && find "$HUE_HOME_DIR/build/env/bin" -name "python3*" -exec basename {} \; | sort -V | tail -n 1 || echo "")

# Extract version from the latest python binary (e.g., python3.11 → 3.11)
LATEST_PYTHON_VERSION=$(echo "$LATEST_PYTHON" | grep -oP '\d+\.\d+' || echo "")

# Find all supported python versions from build/venvs and include latest version
readarray -t SUPPORTED_VERSIONS < <(
  (
    [ -d "$HUE_HOME_DIR/build/venvs" ] && find "$HUE_HOME_DIR/build/venvs" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | grep -oP '\d+\.\d+'
    echo "$LATEST_PYTHON_VERSION"
  ) | sort -Vr | uniq
)

# Create array of supported versions
SUPPORTED_PYTHON_VERSIONS=("${SUPPORTED_VERSIONS[@]}")

_python_bin_path() {
  # Searches for the provided python version in various locations on the node
  PYTHON_VERSION="$1"
  PYTHON_VERSION_NO_DOT="${PYTHON_VERSION//./}"

  # First check in PATH if it exists
  if [ -n "$PATH" ]; then
    IFS=: read -ra PATH_DIRS <<< "$PATH"
    for DIR in "${PATH_DIRS[@]}"; do
      # Skip cm-agent/bin directories
      if [[ "$DIR" == *"cm-agent/bin"* ]]; then
        continue
      fi
      PY_PATH="$DIR/python$PYTHON_VERSION"
      if [[ -x "$PY_PATH" ]]; then
        echo "$PY_PATH"
        return 0
      fi
    done
  fi

  # Fall back to hardcoded directories
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

_choose_python_version() {
  # returns the latest py version, e.g., 3.11, 3.9 or 3.8
  # if HUE_PYTHON_VERSION is set, use it
  if [ -n "$HUE_PYTHON_VERSION" ]; then
    echo "$HUE_PYTHON_VERSION" | grep -oP '\d+\.\d+'
    return 0
  else
    for PYTHON_VERSION in "${SUPPORTED_PYTHON_VERSIONS[@]}"; do
      if _python_bin_path "$PYTHON_VERSION" > /dev/null; then
        echo "$PYTHON_VERSION"
        return 0
      fi
    done
  fi

  echo "No supported Python versions found in expected locations."
  return 1
}

_venv_path() {
  # returns the path to the env/bin of the latest python,
  # relative to the top-level hue directory.
  local version="$1"

  if [ -z "$version" ]; then
    return 1  # Return error if no version provided/found
  fi

  if [ "$version" = "$LATEST_PYTHON_VERSION" ]; then
    echo "build/env/bin"
  else
    echo "build/venvs/python${version}/bin"
  fi
}

export SELECTED_PYTHON_VERSION="$(_choose_python_version)"
export VENV_BIN_PATH=${HUE_HOME_DIR}/$(_venv_path "$SELECTED_PYTHON_VERSION")