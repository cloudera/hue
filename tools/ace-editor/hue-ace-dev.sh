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
# First install Ace
#
#   npm install
#   node ./Makefile.dryice.js
#
# https://github.com/ajaxorg/ace#building-ace

echo "Compiling and copying Ace Editor for Hue"
rm -rf ../../desktop/core/src/desktop/static/desktop/js/ace/* || echo "Skipping removal of folder"
node ./Makefile.dryice.js minimal --nc --s --target ../../desktop/core/src/desktop/static/desktop/js/ace/
mv ../../desktop/core/src/desktop/static/desktop/js/ace/src-noconflict/* ../../desktop/core/src/desktop/static/desktop/js/ace/
rmdir ../../desktop/core/src/desktop/static/desktop/js/ace/src-noconflict
echo "Done!"
