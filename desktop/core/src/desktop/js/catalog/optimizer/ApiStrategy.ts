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

import { CancellablePromise } from 'api/cancellablePromise';
import { extractErrorMessage, post, successResponseIsError } from 'api/utils';
import { OptimizerResponse, TimestampedData } from 'catalog/dataCatalog';
import { OptimizerMeta } from 'catalog/DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from 'catalog/MultiTableEntry';
import {
  CompatibilityOptions,
  MetaOptions,
  Optimizer,
  OptimizerRisk,
  PopularityOptions,
  RiskOptions,
  SimilarityOptions
} from 'catalog/optimizer/optimizer';

/**
 * Fetches the popularity for various aspects of the given tables
 */
const genericOptimizerMultiTableFetch = <T extends TimestampedData>(
  { silenceErrors, paths }: PopularityOptions,
  url: string
): CancellablePromise<T> => {
  const dbTables = new Set<string>();
  paths.forEach(path => {
    dbTables.add(path.join('.'));
  });
  const data = {
    dbTables: JSON.stringify([...dbTables.values()])
  };

  return post<T>(url, data, {
    silenceErrors,
    handleSuccess: (response, resolve, reject) => {
      if (successResponseIsError(response)) {
        reject(extractErrorMessage(response));
      } else {
        response.hueTimestamp = Date.now();
        resolve(response);
      }
    }
  });
};

const COMPATIBILITY_URL = '/notebook/api/optimizer/statement/compatibility';
const RISK_URL = '/notebook/api/optimizer/statement/risk';
const SIMILARITY_URL = '/notebook/api/optimizer/statement/similarity';
const TOP_AGGS_URL = '/metadata/api/optimizer/top_aggs';
const TOP_COLUMNS_URL = '/metadata/api/optimizer/top_columns';
const TOP_FILTERS_URL = '/metadata/api/optimizer/top_filters';
const TOP_JOINS_URL = '/metadata/api/optimizer/top_joins';
const TOP_TABLES_URL = '/metadata/api/optimizer/top_tables';
const TABLE_DETAILS_URL = '/metadata/api/optimizer/table_details';

export default class ApiStrategy implements Optimizer {
  analyzeCompatibility({
    notebookJson,
    snippetJson,
    sourcePlatform,
    targetPlatform,
    silenceErrors
  }: CompatibilityOptions): CancellablePromise<unknown> {
    return post<unknown>(
      COMPATIBILITY_URL,
      {
        notebook: notebookJson,
        snippet: snippetJson,
        sourcePlatform,
        targetPlatform
      },
      { silenceErrors }
    );
  }

  analyzeRisk({
    notebookJson,
    snippetJson,
    silenceErrors
  }: RiskOptions): CancellablePromise<OptimizerRisk> {
    return post<OptimizerRisk>(
      RISK_URL,
      {
        notebook: notebookJson,
        snippet: snippetJson
      },
      { silenceErrors }
    );
  }

  analyzeSimilarity({
    notebookJson,
    snippetJson,
    sourcePlatform,
    silenceErrors
  }: SimilarityOptions): CancellablePromise<unknown> {
    return post<unknown>(
      SIMILARITY_URL,
      {
        notebook: notebookJson,
        snippet: snippetJson,
        sourcePlatform
      },
      { silenceErrors }
    );
  }

  fetchPopularity({
    paths,
    silenceErrors
  }: PopularityOptions): CancellablePromise<OptimizerResponse> {
    let url, data;

    if (paths.length === 1 && paths[0].length === 1) {
      url = TOP_TABLES_URL;
      data = {
        database: paths[0][0]
      };
    } else {
      url = TOP_COLUMNS_URL;
      data = {
        dbTables: JSON.stringify(paths.map(path => path.join('.')))
      };
    }

    return post<OptimizerResponse>(url, data, {
      silenceErrors,
      handleSuccess: (response, resolve, reject) => {
        if (successResponseIsError(response)) {
          reject(extractErrorMessage(response));
        } else {
          response.hueTimestamp = Date.now();
          resolve(response);
        }
      }
    });
  }

  fetchTopAggs(options: PopularityOptions): CancellablePromise<TopAggs> {
    return genericOptimizerMultiTableFetch<TopAggs>(options, TOP_AGGS_URL);
  }

  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns> {
    return genericOptimizerMultiTableFetch<TopColumns>(options, TOP_COLUMNS_URL);
  }

  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters> {
    return genericOptimizerMultiTableFetch<TopFilters>(options, TOP_FILTERS_URL);
  }

  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins> {
    return genericOptimizerMultiTableFetch<TopJoins>(options, TOP_JOINS_URL);
  }

  fetchOptimizerMeta({ path, silenceErrors }: MetaOptions): CancellablePromise<OptimizerMeta> {
    return post<OptimizerMeta>(
      TABLE_DETAILS_URL,
      {
        databaseName: path[0],
        tableName: path[1]
      },
      {
        silenceErrors,
        handleSuccess: (response: { status: number; details?: OptimizerMeta }, resolve, reject) => {
          if (response.status === 0 && response.details) {
            response.details.hueTimestamp = Date.now();
            resolve(response.details);
          }
          reject(extractErrorMessage(response));
        }
      }
    );
  }
}
