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
const COMPONENTS = ['apps/jobBrowser/components/queriesList/QueriesList.vue'];

module.exports = shared => {
  const baseDir = path.resolve(__dirname, 'desktop/core/src/desktop/js');
  const internalBaseDir = path.resolve(__dirname, 'desktop/core/src/desktop/js/internal');

  COMPONENTS.forEach(componentPath => {
    const fromPath = path.resolve(baseDir, componentPath);
    const toPath = path.resolve(internalBaseDir, componentPath);
    shared.resolve.alias[fromPath] = toPath;
    console.info(`Added webpack alias From:${fromPath} To: ${toPath}`);
  });
};
