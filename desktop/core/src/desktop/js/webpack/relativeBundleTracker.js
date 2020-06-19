// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

const each = require('lodash/fp/each');
const BundleTracker = require('webpack-bundle-tracker');
const path = require('path');

// https://github.com/ezhome/webpack-bundle-tracker/issues/25
class RelativeBundleTracker extends BundleTracker {
  convertPathChunks(chunks) {
    each(
      each(chunk => {
        chunk.path = path.relative(this.options.path, chunk.path);
      })
    )(chunks);
  }
  writeOutput(compiler, contents) {
    if (contents.status === 'done') {
      this.convertPathChunks(contents.chunks);
    }

    super.writeOutput(compiler, contents);
  }
}

module.exports = RelativeBundleTracker;
