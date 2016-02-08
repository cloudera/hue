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

echo "Compiling and copying Perfect Scrollbar for Hue"
rm ../../desktop/core/src/desktop/static/desktop/js/perfect-scrollbar.jquery.min.js "Skipping removal of JS file"
rm ../../desktop/core/src/desktop/static/desktop/css/perfect-scrollbar.min.css "Skipping removal of CSS file"
gulp
mv dist/js/min/perfect-scrollbar.jquery.min.js ../../desktop/core/src/desktop/static/desktop/js/perfect-scrollbar.jquery.min.js
mv dist/css/perfect-scrollbar.min.css ../../desktop/core/src/desktop/static/desktop/css/perfect-scrollbar.min.css
echo "Done!"
