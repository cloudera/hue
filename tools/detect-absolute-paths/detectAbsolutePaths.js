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

const TARGET_EXTENSIONS = /\.(js|map|css)$/i;
const FOLDERS_TO_CHECK = ['desktop/core/src/desktop/static'];
const HUE_ABSOLUTE_PATH = __dirname.replace('/tools/detect-absolute-paths', '');

const scanFile = async path =>
  new Promise(resolve => {
    fs.readFile(path, (err, data) => {
      if (!err) {
        if (data.indexOf(HUE_ABSOLUTE_PATH) !== -1) {
          resolve(path);
        }
      }
      resolve();
    });
  });

const appendFilesRecursively = (path, foundFiles) => {
  const files = fs.readdirSync(path, { withFileTypes: true });
  files.forEach(file => {
    const absolutePath = path + '/' + file.name;
    if (file.isFile() && TARGET_EXTENSIONS.test(file.name)) {
      foundFiles.push(absolutePath);
    } else if (file.isDirectory()) {
      appendFilesRecursively(absolutePath, foundFiles);
    }
  });
};

const runCheck = () => {
  // eslint-disable-next-line no-restricted-syntax
  console.log('Checking if files contain the absolute path "' + HUE_ABSOLUTE_PATH + '"...');

  const filesToScan = [];

  FOLDERS_TO_CHECK.forEach(folder =>
    appendFilesRecursively(HUE_ABSOLUTE_PATH + '/' + folder, filesToScan)
  );

  Promise.all(filesToScan.map(scanFile)).then(results => {
    const foundFilesWithAbsolutePath = results.filter(result => result);
    if (foundFilesWithAbsolutePath.length) {
      console.warn(
        `Found in ${
          foundFilesWithAbsolutePath.length
        } file(s):\n  ${foundFilesWithAbsolutePath.join('\n  ')}`
      );
      process.exitCode = 1;
    } else {
      // eslint-disable-next-line no-restricted-syntax
      console.log(`Done! Scanned ${filesToScan.length} files.`);
    }
  });
};

runCheck();
