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
import * as ko from 'knockout';

import CancellablePromise from 'api/cancellablePromise';
import { simplePost } from 'api/apiUtils';

const OPTIMIZER_URLS = {
  COMPATIBILITY: '/notebook/api/optimizer/statement/compatibility',
  RISK: '/notebook/api/optimizer/statement/risk',
  SIMILARITY: '/notebook/api/optimizer/statement/similarity',
  TOP_AGGS: '/metadata/api/optimizer/top_aggs',
  TOP_COLUMNS: '/metadata/api/optimizer/top_columns',
  TOP_FILTERS: '/metadata/api/optimizer/top_filters',
  TOP_JOINS: '/metadata/api/optimizer/top_joins',
  TOP_TABLES: '/metadata/api/optimizer/top_tables',
  TABLE_DETAILS: '/metadata/api/optimizer/table_details'
};

/**
 * Fetches the popularity for various aspects of the given tables
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @param {string} url
 * @return {CancellablePromise}
 */
const genericOptimizerMultiTableFetch = (options, url) => {
  const deferred = $.Deferred();

  const dbTables = {};
  options.paths.forEach(path => {
    dbTables[path.join('.')] = true;
  });
  const data = {
    dbTables: ko.mapping.toJSON(Object.keys(dbTables))
  };

  const request = simplePost(url, data, {
    silenceErrors: options.silenceErrors,
    successCallback: data => {
      data.hueTimestamp = Date.now();
      deferred.resolve(data);
    },
    errorCallback: deferred.reject
  });

  return new CancellablePromise(deferred, request);
};

export const analyzeRisk = options =>
  simplePost(OPTIMIZER_URLS.RISK, {
    notebook: options.notebookJson,
    snippet: options.snippetJson
  });

export const analyzeCompatibility = options =>
  simplePost(OPTIMIZER_URLS.COMPATIBILITY, {
    notebook: options.notebookJson,
    snippet: options.snippetJson,
    sourcePlatform: options.sourcePlatform,
    targetPlatform: options.targetPlatform
  });

export const analyzeSimilarity = options =>
  simplePost(OPTIMIZER_URLS.SIMILARITY, {
    notebook: options.notebookJson,
    snippet: options.snippetJson,
    sourcePlatform: options.sourcePlatform
  });

/**
 * Fetches optimizer popularity for the children of the given path
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @return {CancellablePromise}
 */
export const fetchPopularity = options => {
  const deferred = $.Deferred();
  let url, data;

  if (options.paths.length === 1 && options.paths[0].length === 1) {
    url = OPTIMIZER_URLS.TOP_TABLES;
    data = {
      database: options.paths[0][0]
    };
  } else {
    url = OPTIMIZER_URLS.TOP_COLUMNS;
    const dbTables = [];
    options.paths.forEach(path => {
      dbTables.push(path.join('.'));
    });
    data = {
      dbTables: ko.mapping.toJSON(dbTables)
    };
  }

  const request = simplePost(url, data, {
    silenceErrors: options.silenceErrors,
    successCallback: data => {
      data.hueTimestamp = Date.now();
      deferred.resolve(data);
    },
    errorCallback: deferred.reject
  });

  return new CancellablePromise(deferred, request);
};

/**
 * Fetches the popular aggregate functions for the given tables
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @return {CancellablePromise}
 */
export const fetchTopAggs = options =>
  genericOptimizerMultiTableFetch(options, OPTIMIZER_URLS.TOP_AGGS);

/**
 * Fetches the popular columns for the given tables
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @return {CancellablePromise}
 */
export const fetchTopColumns = options =>
  genericOptimizerMultiTableFetch(options, OPTIMIZER_URLS.TOP_COLUMNS);

/**
 * Fetches the popular filters for the given tables
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @return {CancellablePromise}
 */
export const fetchTopFilters = options =>
  genericOptimizerMultiTableFetch(options, OPTIMIZER_URLS.TOP_FILTERS);

/**
 * Fetches the popular joins for the given tables
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[][]} options.paths
 * @return {CancellablePromise}
 */
export const fetchTopJoins = options =>
  genericOptimizerMultiTableFetch(options, OPTIMIZER_URLS.TOP_JOINS);

/**
 * Fetches optimizer meta for the given path, only possible for tables atm.
 *
 * @param {Object} options
 * @param {boolean} [options.silenceErrors]
 * @param {string[]} options.path
 *
 * @return {CancellablePromise}
 */
export const fetchOptimizerMeta = options => {
  const deferred = $.Deferred();

  const request = simplePost(
    OPTIMIZER_URLS.TABLE_DETAILS,
    {
      databaseName: options.path[0],
      tableName: options.path[1]
    },
    {
      silenceErrors: options.silenceErrors,
      successCallback: response => {
        if (response.status === 0 && response.details) {
          response.details.hueTimestamp = Date.now();
          deferred.resolve(response.details);
        } else {
          deferred.reject();
        }
      },
      errorCallback: deferred.reject
    }
  );

  return new CancellablePromise(deferred, request);
};
