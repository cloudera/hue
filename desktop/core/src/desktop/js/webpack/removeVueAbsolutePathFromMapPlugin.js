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

const fs = require('fs');

// Vue generates absolute paths in the .js.map files for vue-hot-reload-api, this replaces it
// with a relative path.
class RemoveVueAbsolutePathFromMapPlugin {
  apply(compiler) {
    compiler.hooks.afterEmit.tapAsync(
      'RemoveVueAbsolutePathFromMapPlugin',
      (compilation, callback) => {
        compilation.chunks.forEach(chunk => {
          chunk.files.forEach(filename => {
            if (/\.js\.map$/.test(filename)) {
              const source = compilation.assets[filename].source();
              if (/"[^"]+\/node_modules\/vue-hot-reload-api/.test(source)) {
                const actualFilename = filename.split('/').pop();
                const outputFilename = compilation.outputOptions.path + '/' + actualFilename;
                const cleanSource = source.replace(
                  /"[^"]+\/node_modules\/vue-hot-reload-api/gi,
                  '"../../../../../../../../node_modules/vue-hot-reload-api'
                );
                fs.writeFileSync(outputFilename, cleanSource);
              }
            }
          });
        });
        callback();
      }
    );
  }
}

module.exports = RemoveVueAbsolutePathFromMapPlugin;
