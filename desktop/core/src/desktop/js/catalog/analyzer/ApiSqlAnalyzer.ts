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
import { SqlAnalyzerResponse, TimestampedData } from 'catalog/dataCatalog';
import { SqlAnalyzerMeta } from 'catalog/DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from 'catalog/MultiTableEntry';
import {
  CompatibilityOptions,
  MetaOptions,
  SqlAnalyzer,
  AnalyzerRisk,
  PopularityOptions,
  PredictOptions,
  PredictResponse,
  RiskOptions,
  SimilarityOptions
} from 'catalog/analyzer/types';
import { Connector } from 'config/types';

/**
 * Fetches the popularity for various aspects of the given tables
 */
const genericSqlAnalyzerMultiTableFetch = <T extends TimestampedData>(
  { silenceErrors, paths, connector }: PopularityOptions & { connector: Connector },
  url: string
): CancellablePromise<T> => {
  const dbTables = new Set<string>();
  paths.forEach(path => {
    dbTables.add(path.join('.'));
  });
  const data = {
    connector: JSON.stringify(connector),
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

const COMPATIBILITY_URL = '/api/v1/optimizer/query_compatibility';
const PREDICT_URL = '/api/v1/optimizer/predict';
const RISK_URL = '/api/v1/optimizer/query_risk/';
const SIMILARITY_URL = '/api/v1/optimizer/similar_queries';
const TOP_AGGS_URL = '/api/v1/optimizer/top_aggs';
const TOP_COLUMNS_URL = '/api/v1/optimizer/top_columns';
const TOP_FILTERS_URL = '/api/v1/optimizer/top_filters';
const TOP_JOINS_URL = '/api/v1/optimizer/top_joins';
const TOP_TABLES_URL = '/api/v1/optimizer/top_tables';
const TABLE_DETAILS_URL = '/api/v1/optimizer/table_details';

export default class ApiSqlAnalyzer implements SqlAnalyzer {
  connector: Connector;

  constructor(connector: Connector) {
    this.connector = connector;
  }

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
        connector: JSON.stringify(this.connector),
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
  }: RiskOptions): CancellablePromise<AnalyzerRisk> {
    return post<AnalyzerRisk>(
      RISK_URL,
      {
        connector: JSON.stringify(this.connector),
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
        connector: JSON.stringify(this.connector),
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
  }: PopularityOptions): CancellablePromise<SqlAnalyzerResponse> {
    let url, data;

    if (paths.length === 1 && paths[0].length === 1) {
      url = TOP_TABLES_URL;
      data = {
        connector: JSON.stringify(this.connector),
        database: paths[0][0]
      };
    } else {
      url = TOP_COLUMNS_URL;
      data = {
        connector: JSON.stringify(this.connector),
        dbTables: JSON.stringify(paths.map(path => path.join('.')))
      };
    }

    return post<SqlAnalyzerResponse>(url, data, {
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
    return genericSqlAnalyzerMultiTableFetch<TopAggs>(
      { ...options, connector: this.connector },
      TOP_AGGS_URL
    );
  }

  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns> {
    return genericSqlAnalyzerMultiTableFetch<TopColumns>(
      { ...options, connector: this.connector },
      TOP_COLUMNS_URL
    );
  }

  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters> {
    return genericSqlAnalyzerMultiTableFetch<TopFilters>(
      { ...options, connector: this.connector },
      TOP_FILTERS_URL
    );
  }

  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins> {
    return genericSqlAnalyzerMultiTableFetch<TopJoins>(
      { ...options, connector: this.connector },
      TOP_JOINS_URL
    );
  }

  fetchSqlAnalyzerMeta({ path, silenceErrors }: MetaOptions): CancellablePromise<SqlAnalyzerMeta> {
    return post<SqlAnalyzerMeta>(
      TABLE_DETAILS_URL,
      {
        connector: JSON.stringify(this.connector),
        databaseName: path[0],
        tableName: path[1]
      },
      {
        silenceErrors,
        handleSuccess: (
          response: { status: number; details?: SqlAnalyzerMeta },
          resolve,
          reject
        ) => {
          if (response.status === 0 && response.details) {
            response.details.hueTimestamp = Date.now();
            resolve(response.details);
          }
          reject(extractErrorMessage(response));
        }
      }
    );
  }

  predict({ beforeCursor, afterCursor }: PredictOptions): CancellablePromise<PredictResponse> {
    return post<PredictResponse>(
      PREDICT_URL,
      {
        connector: JSON.stringify(this.connector),
        beforeCursor,
        afterCursor
      },
      {
        silenceErrors: true,
        handleSuccess: (response: PredictResponse, resolve) => {
          resolve(response);
        }
      }
    );
  }
}
