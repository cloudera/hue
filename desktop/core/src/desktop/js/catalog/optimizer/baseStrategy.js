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

import CancellableJqPromise from 'api/cancellableJqPromise';

export default class BaseStrategy {
  constructor(connector) {
    if (!connector) {
      console.warn('BaseStrategy instantiated without connector.');
    }
    this.connector = connector;
  }

  analyzeRisk(options) {
    return $.Deferred().reject();
  }

  analyzeSimilarity(options) {
    return $.Deferred().reject();
  }

  analyzeCompatibility(options) {
    return $.Deferred().reject();
  }

  /**
   * @typedef OptimizerOptions
   * @property {boolean} [options.silenceErrors]
   * @property {string[][]} options.paths
   */

  /**
   * Fetches optimizer popularity for the children of the given path
   *
   * @param {OptimizerOptions} options
   * @return {CancellableJqPromise}
   */
  fetchPopularity(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }

  /**
   * Fetches the popular aggregate functions for the given tables
   *
   * @param {OptimizerOptions} options
   * @return {CancellableJqPromise}
   */
  fetchTopAggs(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }

  /**
   * Fetches the popular columns for the given tables
   *
   * @param {OptimizerOptions} options
   * @return {CancellableJqPromise}
   */
  fetchTopColumns(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }

  /**
   * Fetches the popular filters for the given tables
   *
   * @param {OptimizerOptions} options
   * @return {CancellableJqPromise}
   */
  fetchTopFilters(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }

  /**
   * Fetches the popular joins for the given tables
   *
   * @param {OptimizerOptions} options
   * @return {CancellableJqPromise}
   */
  fetchTopJoins(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }

  /**
   * Fetches optimizer meta for the given path, only possible for tables atm.
   *
   * @param {Object} options
   * @param {boolean} [options.silenceErrors]
   * @param {string[]} options.path
   *
   * @return {CancellableJqPromise}
   */
  fetchOptimizerMeta(options) {
    return new CancellableJqPromise($.Deferred().reject());
  }
}
