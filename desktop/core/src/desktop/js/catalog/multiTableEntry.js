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

import $ from 'jquery';

import catalogUtils from 'catalog/catalogUtils';
import { getOptimizer } from './optimizer/optimizer';

/**
 * Helper function to reload a Optimizer multi table attribute, like topAggs or topFilters
 *
 * @param {MultiTableEntry} multiTableEntry
 * @param {Object} [options]
 * @param {boolean} [options.silenceErrors] - Default true
 * @param {string} promiseAttribute
 * @param {string} dataAttribute
 * @param {Function} apiHelperFunction
 * @return {CancellablePromise}
 */
const genericOptimizerReload = function(
  multiTableEntry,
  options,
  promiseAttribute,
  dataAttribute,
  apiHelperFunction
) {
  if (multiTableEntry.dataCatalog.canHaveOptimizerMeta()) {
    return multiTableEntry.trackedPromise(
      promiseAttribute,
      catalogUtils.fetchAndSave(apiHelperFunction, dataAttribute, multiTableEntry, options)
    );
  }
  multiTableEntry[promiseAttribute] = $.Deferred().reject();
  return multiTableEntry[promiseAttribute];
};

/**
 * Helper function to get a Optimizer multi table attribute, like topAggs or topFilters
 *
 * @param {MultiTableEntry} multiTableEntry
 * @param {Object} [options]
 * @param {boolean} [options.silenceErrors] - Default false
 * @param {boolean} [options.refreshCache] - Default false
 * @param {boolean} [options.cachedOnly] - Default false
 * @param {boolean} [options.cancellable] - Default false
 * @param {string} promiseAttribute
 * @param {string} dataAttribute
 * @param {Function} apiHelperFunction
 * @return {CancellablePromise}
 */
const genericOptimizerGet = function(
  multiTableEntry,
  options,
  promiseAttribute,
  dataAttribute,
  apiHelperFunction
) {
  if (options && options.cachedOnly) {
    return (
      catalogUtils.applyCancellable(multiTableEntry[promiseAttribute], options) ||
      $.Deferred()
        .reject(false)
        .promise()
    );
  }
  if (options && options.refreshCache) {
    return catalogUtils.applyCancellable(
      genericOptimizerReload(
        multiTableEntry,
        options,
        promiseAttribute,
        dataAttribute,
        apiHelperFunction
      ),
      options
    );
  }
  return catalogUtils.applyCancellable(
    multiTableEntry[promiseAttribute] ||
      genericOptimizerReload(
        multiTableEntry,
        options,
        promiseAttribute,
        dataAttribute,
        apiHelperFunction
      ),
    options
  );
};

class MultiTableEntry {
  /**
   *
   * @param {Object} options
   * @param {string} options.identifier
   * @param {DataCatalog} options.dataCatalog
   * @param {string[][]} options.paths
   * @constructor
   */
  constructor(options) {
    const self = this;
    self.identifier = options.identifier;
    self.dataCatalog = options.dataCatalog;
    self.paths = options.paths;

    self.topAggs = undefined;
    self.topAggsPromise = undefined;

    self.topColumns = undefined;
    self.topColumnsPromise = undefined;

    self.topFilters = undefined;
    self.topFiltersPromise = undefined;

    self.topJoins = undefined;
    self.topJoinsPromise = undefined;
  }

  /**
   * Save the multi table entry to cache
   *
   * @return {Promise}
   */
  save() {
    const self = this;
    window.clearTimeout(self.saveTimeout);
    return self.dataCatalog.persistMultiTableEntry(self);
  }

  /**
   * Save the multi table entry at a later point of time
   */
  saveLater() {
    const self = this;
    if (CACHEABLE_TTL.default > 0) {
      window.clearTimeout(self.saveTimeout);
      self.saveTimeout = window.setTimeout(() => {
        self.save();
      }, 1000);
    }
  }
  /**
   * Helper function that ensure that cancellable promises are not tracked anymore when cancelled
   *
   * @param {string} promiseName - The attribute name to use
   * @param {CancellablePromise} cancellablePromise
   */
  trackedPromise(promiseName, cancellablePromise) {
    const self = this;
    self[promiseName] = cancellablePromise;
    return cancellablePromise.fail(() => {
      if (cancellablePromise.cancelled) {
        delete self[promiseName];
      }
    });
  }

  /**
   * Gets the top aggregate UDFs for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default false
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {boolean} [options.refreshCache] - Default false
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  getTopAggs(options) {
    return genericOptimizerGet(
      this,
      options,
      'topAggsPromise',
      'topAggs',
      getOptimizer(this.dataCatalog.connector).fetchTopAggs
    );
  }

  /**
   * Gets the top columns for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default false
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {boolean} [options.refreshCache] - Default false
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  getTopColumns(options) {
    return genericOptimizerGet(
      this,
      options,
      'topColumnsPromise',
      'topColumns',
      getOptimizer(this.dataCatalog.connector).fetchTopColumns
    );
  }

  /**
   * Gets the top filters for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default false
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {boolean} [options.refreshCache] - Default false
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  getTopFilters(options) {
    return genericOptimizerGet(
      this,
      options,
      'topFiltersPromise',
      'topFilters',
      getOptimizer(this.dataCatalog.connector).fetchTopFilters
    );
  }

  /**
   * Gets the top joins for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default false
   * @param {boolean} [options.cachedOnly] - Default false
   * @param {boolean} [options.refreshCache] - Default false
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  getTopJoins(options) {
    return genericOptimizerGet(
      this,
      options,
      'topJoinsPromise',
      'topJoins',
      getOptimizer(this.dataCatalog.connector).fetchTopJoins
    );
  }
}

export default MultiTableEntry;
