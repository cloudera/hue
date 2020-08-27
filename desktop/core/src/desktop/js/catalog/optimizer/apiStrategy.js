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

import CancellableJqPromise from 'api/cancellableJqPromise';
import { simplePost } from 'api/apiUtils';
import { OPTIMIZER_API } from 'api/urls';
import BaseStrategy from './baseStrategy';

/**
 * Fetches the popularity for various aspects of the given tables
 *
 * @param {OptimizerOptions} options
 * @param {string} url
 * @return {CancellableJqPromise}
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

  return new CancellableJqPromise(deferred, request);
};

export default class ApiStrategy extends BaseStrategy {
  analyzeCompatibility(options) {
    return simplePost(OPTIMIZER_API.COMPATIBILITY, {
      notebook: options.notebookJson,
      snippet: options.snippetJson,
      sourcePlatform: options.sourcePlatform,
      targetPlatform: options.targetPlatform
    });
  }

  analyzeRisk(options) {
    return simplePost(OPTIMIZER_API.RISK, {
      notebook: options.notebookJson,
      snippet: options.snippetJson
    });
  }

  analyzeSimilarity(options) {
    return simplePost(OPTIMIZER_API.SIMILARITY, {
      notebook: options.notebookJson,
      snippet: options.snippetJson,
      sourcePlatform: options.sourcePlatform
    });
  }

  fetchPopularity(options) {
    const deferred = $.Deferred();
    let url, data;

    if (options.paths.length === 1 && options.paths[0].length === 1) {
      url = OPTIMIZER_API.TOP_TABLES;
      data = {
        database: options.paths[0][0]
      };
    } else {
      url = OPTIMIZER_API.TOP_COLUMNS;
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

    return new CancellableJqPromise(deferred, request);
  }

  fetchTopAggs(options) {
    return genericOptimizerMultiTableFetch(options, OPTIMIZER_API.TOP_AGGS);
  }

  fetchTopColumns(options) {
    return genericOptimizerMultiTableFetch(options, OPTIMIZER_API.TOP_COLUMNS);
  }

  fetchTopFilters(options) {
    return genericOptimizerMultiTableFetch(options, OPTIMIZER_API.TOP_FILTERS);
  }

  fetchTopJoins(options) {
    return genericOptimizerMultiTableFetch(options, OPTIMIZER_API.TOP_JOINS);
  }

  fetchOptimizerMeta(options) {
    const deferred = $.Deferred();

    const request = simplePost(
      OPTIMIZER_API.TABLE_DETAILS,
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

    return new CancellableJqPromise(deferred, request);
  }
}
