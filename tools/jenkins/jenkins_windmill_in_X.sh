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
set -x
# Fluxbox does not need to be killed; it'll fall away when the X server dies.
fluxbox 2&>1 > /dev/null &
recordmydesktop --on-the-fly-encoding -v_quality 15 --no-sound -o recording.ogv &
RECORDER_PID=$!
rm -f desktop/desktop-test.db
build/env/bin/hue test windmill --with-xunit -v --nologcapture
EXIT=$?
kill $RECORDER_PID || true
sleep 20 # Wait for recording to finish
exit $EXIT
