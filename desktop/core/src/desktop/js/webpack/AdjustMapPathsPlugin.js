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

const path = require('path');
const fs = require('fs');

// Webpack automatically adds a reference to a js.map file in the sourceMappingUrl in the bottom of
// each chunk without the static path prefix. This plugin adds the missing static path to the variable.
class AdjustMapPathsPlugin {
  apply(compiler) {
    compiler.hooks.afterEmit.tapAsync('AdjustMapPathsPlugin', (compilation, callback) => {
      compilation.chunks.forEach(chunk => {
        chunk.files.forEach(filename => {
          if (/\.js$/.test(filename)) {
            const relativePathMatch = compilation.outputOptions.path.match(
              /.*(\/static\/desktop\/js\/bundles\/.*)$/
            );
            if (relativePathMatch) {
              const outputFilename =
                compilation.outputOptions.path + '/' + filename.split('/').pop();
              const source = fs.readFileSync(path.resolve(outputFilename), 'utf8');
              if (source.indexOf('//# sourceMappingURL=') !== -1) {
                const cleanSource = source.replace(
                  '//# sourceMappingURL=',
                  `//# sourceMappingURL=${relativePathMatch[1]}/`
                );
                fs.writeFileSync(outputFilename, cleanSource);
              }
            }
          }
        });
      });
      callback();
    });
  }
}

module.exports = AdjustMapPathsPlugin;
