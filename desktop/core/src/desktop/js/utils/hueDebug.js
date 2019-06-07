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

import localforage from 'localforage';

const hueDebug = {
  clearCaches: function() {
    const promises = [];
    const clearInstance = function(prefix) {
      promises.push(localforage.createInstance({ name: prefix + window.LOGGED_USERNAME }).clear());
    };
    clearInstance('HueContextCatalog_');
    clearInstance('HueDataCatalog_');
    clearInstance('HueDataCatalog_hive_');
    clearInstance('HueDataCatalog_hive_multiTable_');
    clearInstance('HueDataCatalog_impala_');
    clearInstance('HueDataCatalog_impala_multiTable_');
    Promise.all(promises).then(() => {
      console.log('Done! Refresh the browser.');
    });
  }
};

export default hueDebug;
