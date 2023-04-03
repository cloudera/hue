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

const checker = require('license-checker');

checker.init(
  {
    start: './'
  },
  (err, packages) => {
    if (err) {
      console.error(err);
      process.exitCode = 1;
    } else {
      let packageCount = 0;
      Object.keys(packages).forEach(packageName => {
        packageCount++;
        const licenses =
          typeof packages[packageName].licenses === 'string'
            ? packages[packageName].licenses
            : packages[packageName].licenses.join(', ');
        const lowerLicenses = licenses.toLowerCase();
        if (!licenses) {
          console.warn(`Unknown license for "${packageName}".`);
        } else if (
          lowerLicenses.indexOf('mit') === -1 &&
          lowerLicenses.indexOf('bsd') === -1 &&
          lowerLicenses.indexOf('apache') === -1 &&
          lowerLicenses.indexOf('isc') === -1 &&
          lowerLicenses.indexOf('unlicense') === -1 &&
          lowerLicenses.indexOf('cc') === -1 &&
          lowerLicenses.indexOf('python-2.0') === -1 &&
          // lz-string is marked as WTFPL license on NPM but the valid license is MIT from the github repo
          // https://github.com/pieroxy/lz-string/issues/147
          !packageName.startsWith('lz-string@')
        ) {
          console.warn(`Found invalid license in "${packageName}", license: "${licenses}".`);
          process.exitCode = 1;
        }
      });
      // eslint-disable-next-line no-restricted-syntax
      console.log(`Done! Scanned ${packageCount} packages.`);
    }
  }
);
