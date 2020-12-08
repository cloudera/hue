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

/**
 * Wrapper function around ApiHelper calls, it will also save the entry on success.
 *
 * @param {Function} apiHelperFunction - The name of the ApiHelper function to call
 * @param {Function} setFunction - The attribute to set
 * @param {DataCatalogEntry|MultiTableEntry} entry - The catalog entry
 * @param {Object} [apiOptions]
 * @param {boolean} [apiOptions.silenceErrors]
 */
const fetchAndSave = (apiHelperFunction, setFunction, entry, apiOptions) => {
  return apiHelperFunction({
    sourceType: entry.getConnector().id,
    compute: entry.compute,
    path: entry.path, // Set for DataCatalogEntry
    paths: entry.paths, // Set for MultiTableEntry
    silenceErrors: apiOptions && apiOptions.silenceErrors,
    connector: entry.dataCatalog.connector,
    isView: entry.isView && entry.isView() // MultiTable entries don't have this property
  }).done(data => {
    setFunction(data);
    entry.saveLater();
  });
};
/**
 * Helper function that adds sets the silence errors option to true if not specified
 *
 * @param {Object} [options]
 * @return {Object}
 */
const setSilencedErrors = options => {
  if (!options) {
    options = {};
  }
  if (typeof options.silenceErrors === 'undefined') {
    options.silenceErrors = true;
  }
  return options;
};

/**
 * Helper function to apply the cancellable option to an existing or new promise
 *
 * @param {CancellableJqPromise} [promise]
 * @param {Object} [options]
 * @param {boolean} [options.cancellable] - Default false
 *
 * @return {CancellableJqPromise}
 */
const applyCancellable = (promise, options) => {
  if (promise && promise.preventCancel && (!options || !options.cancellable)) {
    promise.preventCancel();
  }
  return promise;
};

export default {
  applyCancellable: applyCancellable,
  fetchAndSave: fetchAndSave,
  setSilencedErrors: setSilencedErrors
};
