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

# Resolve Hue's Python 3.11 virtualenv bin directory (build/env/bin).
set -ex

HUE_SUPPORTED_PYTHON_VERSION="3.11"

if [ -n "$HUE_PYTHON_VERSION" ]; then
  export SELECTED_PYTHON_VERSION=$(echo "$HUE_PYTHON_VERSION" | grep -oE '[0-9]+\.[0-9]+')
else
  export SELECTED_PYTHON_VERSION="$HUE_SUPPORTED_PYTHON_VERSION"
fi

if [ "$SELECTED_PYTHON_VERSION" != "$HUE_SUPPORTED_PYTHON_VERSION" ]; then
  echo "Hue requires Python ${HUE_SUPPORTED_PYTHON_VERSION}; got ${SELECTED_PYTHON_VERSION} from HUE_PYTHON_VERSION." >&2
  exit 1
fi

export VENV_BIN_PATH="${HUE_HOME_DIR}/build/env/bin"
