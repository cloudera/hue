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

import DataCatalogEntry from 'catalog/DataCatalogEntry';
import { PopularityOptions, SqlAnalyzer } from './analyzer/types';
import { CatalogGetOptions, DataCatalog, TimestampedData } from './dataCatalog';
import { CancellablePromise } from 'api/cancellablePromise';
import { applyCancellable } from 'catalog/catalogUtils';
import { UdfDetails } from 'sql/reference/types';
import { Connector } from 'config/types';
import { hueWindow } from 'types/types';
import noop from 'utils/timing/noop';

export interface TopJoinValue {
  totalTableCount: number;
  totalQueryCount: number;
  joinType: string;
  tables: string[];
  joinCols: { columns: string[] }[];
  relativePopularity?: number;
}

export interface TopJoins extends TimestampedData {
  values: TopJoinValue[];
}

export interface TopAggValue {
  aggregateClause: string;
  aggregateFunction: string;
  aggregateInfo: {
    columnName: string;
    databaseName: string;
    tableName: string;
  }[];
  function?: UdfDetails;
  relativePopularity?: number;
  totalQueryCount: number;
}

export interface TopAggs extends TimestampedData {
  values: TopAggValue[];
}

export interface TopFilterValue {
  count: number;
  relativePopularity?: number;
  group?: {
    columnName: string;
    op: string;
    literal: string;
  }[];
}

export interface TopFilters extends TimestampedData {
  values: {
    tableName: string;
    count: number;
    popularValues?: TopFilterValue[];
  }[];
}

export interface TopColumns extends TimestampedData {
  values: unknown[];
}

const fetchAndSave = <T>(
  sqlAnalyzerFunction: (option: PopularityOptions) => CancellablePromise<T>,
  setFunction: (val: T) => void,
  entry: DataCatalogEntry | MultiTableEntry,
  apiOptions?: { silenceErrors?: boolean; refreshAnalysis?: boolean }
): CancellablePromise<T> => {
  const promise = sqlAnalyzerFunction({
    paths: (<MultiTableEntry>entry).paths, // Set for MultiTableEntry
    silenceErrors: apiOptions && apiOptions.silenceErrors
  });
  promise
    .then(data => {
      setFunction(data);
      entry.saveLater();
    })
    .catch(noop);
  return promise;
};

/**
 * Helper function to reload a SQL Analyzer multi table attribute, like topAggs or topFilters
 */
const genericSqlAnalyzerReload = <T>(
  multiTableEntry: MultiTableEntry,
  options: { silenceErrors?: boolean } | undefined,
  promiseSetter: (promise?: CancellablePromise<T>) => void,
  dataAttributeSetter: (val: T) => void,
  sqlAnalyzerFunction: (option: PopularityOptions) => CancellablePromise<T>
): CancellablePromise<T> => {
  const promise = new CancellablePromise<T>((resolve, reject, onCancel) => {
    if (!multiTableEntry.dataCatalog.canHaveSqlAnalyzerMeta()) {
      reject();
      return;
    }
    const fetchPromise = fetchAndSave(
      sqlAnalyzerFunction,
      dataAttributeSetter,
      multiTableEntry,
      options
    );
    onCancel(() => {
      if (fetchPromise.cancel) {
        fetchPromise.cancel();
      }
    });

    fetchPromise.then(resolve).catch(err => {
      if (fetchPromise.cancelled) {
        promiseSetter(undefined);
      }
      reject(err);
    });
  });

  promiseSetter(promise);
  return promise;
};

/**
 * Helper function to get a SQL Analyzer multi table attribute, like topAggs or topFilters
 */
const genericSqlAnalyzerGet = <T>(
  multiTableEntry: MultiTableEntry,
  options: CatalogGetOptions | undefined,
  promiseSetter: (promise?: CancellablePromise<T>) => void,
  promiseGetter: () => CancellablePromise<T> | undefined,
  dataAttributeSetter: (val: T) => void,
  apiHelperFunction: (option: PopularityOptions) => CancellablePromise<T>
): CancellablePromise<T> => {
  let promise = promiseGetter();
  if (DataCatalog.cacheEnabled() && options && options.cachedOnly) {
    return (promise && applyCancellable(promise)) || CancellablePromise.reject();
  }

  if (!promise || !DataCatalog.cacheEnabled() || (options && options.refreshCache)) {
    promise = genericSqlAnalyzerReload<T>(
      multiTableEntry,
      options,
      promiseSetter,
      dataAttributeSetter,
      apiHelperFunction
    );
  }

  return applyCancellable(promise, options);
};

class MultiTableEntry {
  dataCatalog: DataCatalog;
  identifier: string;
  paths: string[][];
  saveTimeout = -1;

  topAggs?: TopAggs;
  topAggsPromise?: CancellablePromise<TopAggs>;
  topColumns?: TopColumns;
  topColumnsPromise?: CancellablePromise<TopColumns>;
  topFilters?: TopFilters;
  topFiltersPromise?: CancellablePromise<TopFilters>;
  topJoins?: TopJoins;
  topJoinsPromise?: CancellablePromise<TopJoins>;

  constructor(options: { identifier: string; dataCatalog: DataCatalog; paths: string[][] }) {
    this.identifier = options.identifier;
    this.dataCatalog = options.dataCatalog;
    this.paths = options.paths;
  }

  /**
   * Save the multi table entry to cache
   *
   * @return {Promise}
   */
  save(): Promise<void> {
    window.clearTimeout(this.saveTimeout);
    return this.dataCatalog.persistMultiTableEntry(this);
  }

  /**
   * Save the multi table entry at a later point of time
   */
  saveLater(): void {
    const ttl = (<hueWindow>window).CACHEABLE_TTL;
    if (ttl && ttl.default && ttl.default > 0) {
      window.clearTimeout(this.saveTimeout);
      this.saveTimeout = window.setTimeout(() => {
        this.save().catch();
      }, 1000);
    }
  }

  /**
   * Returns the dialect of this entry.
   */
  getDialect(): string {
    return this.getConnector().dialect || this.getConnector().id; // .id for editor v1
  }

  /**
   * Returns the connector for this entry
   */
  getConnector(): Connector {
    return this.dataCatalog.connector;
  }

  /**
   * Gets the top aggregate UDFs for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getTopAggs(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopAggs> {
    return genericSqlAnalyzerGet<TopAggs>(
      this,
      options,
      promise => {
        this.topAggsPromise = promise;
      },
      () => this.topAggsPromise,
      val => {
        this.topAggs = val;
      },
      options.sqlAnalyzer.fetchTopAggs.bind(options.sqlAnalyzer)
    );
  }

  /**
   * Gets the top columns for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getTopColumns(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopColumns> {
    return genericSqlAnalyzerGet<TopColumns>(
      this,
      options,
      promise => {
        this.topColumnsPromise = promise;
      },
      () => this.topColumnsPromise,
      val => {
        this.topColumns = val;
      },
      options.sqlAnalyzer.fetchTopColumns.bind(options.sqlAnalyzer)
    );
  }

  /**
   * Gets the top filters for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getTopFilters(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopFilters> {
    return genericSqlAnalyzerGet<TopFilters>(
      this,
      options,
      promise => {
        this.topFiltersPromise = promise;
      },
      () => this.topFiltersPromise,
      val => {
        this.topFilters = val;
      },
      options.sqlAnalyzer.fetchTopFilters.bind(options.sqlAnalyzer)
    );
  }

  /**
   * Gets the top joins for the entry. It will fetch it if not cached or if the refresh option is set.
   */
  getTopJoins(
    options: CatalogGetOptions & { sqlAnalyzer: SqlAnalyzer }
  ): CancellablePromise<TopJoins> {
    return genericSqlAnalyzerGet<TopJoins>(
      this,
      options,
      promise => {
        this.topJoinsPromise = promise;
      },
      () => this.topJoinsPromise,
      val => {
        this.topJoins = val;
      },
      options.sqlAnalyzer.fetchTopJoins.bind(options.sqlAnalyzer)
    );
  }
}

export default MultiTableEntry;
