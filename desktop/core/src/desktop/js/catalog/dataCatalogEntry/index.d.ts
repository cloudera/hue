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

import CancellableJqPromise from 'api/cancellableJqPromise';
import { UdfDetails } from 'sql/reference/types';

export = DataCatalogEntry;

declare class DataCatalogEntry {
  name: string;
  optimizerPopularity: {
    [attr: string]: DataCatalogEntry.OptimizerPopularity | number;
  };
  getChildren(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry[]>;
  getQualifiedPath(): string;
  getSourceMeta(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry.SourceMeta>;
  getType(): string;
  getTopJoins(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry.TopJoins>;
  getTopAggs(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry.TopAggs>;
  getTopFilters(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry.TopFilters>;
  isArray(): boolean;
  isComplex(): boolean;
  isMap(): boolean;
  isTable(): boolean;
  isView(): boolean;
  loadOptimizerPopularityForChildren(
    options: DataCatalogEntry.CatalogGetOptions
  ): CancellableJqPromise<DataCatalogEntry[]>;
}

declare namespace DataCatalogEntry {
  export interface CatalogGetOptions {
    silenceErrors?: boolean;
    cachedOnly?: boolean;
    refreshCache?: boolean;
    cancellable?: boolean;
  }

  export interface OptimizerPopularity {
    columnCount: number;
    dbName?: string;
    tableName?: string;
    columnName?: string;
  }

  export interface Field {
    type: string;
    name: string;
  }

  export interface SourceMeta {
    type?: string;
    samples?: string[];
    value?: { fields?: Field[] };
    item?: { fields?: Field[] };
    extended_columns?: { type: string; name: string }[];
  }

  export interface TopJoinValue {
    totalQueryCount: number;
    joinType: string;
    tables: string[];
    joinCols: { columns: string[] }[];
    relativePopularity?: number;
  }

  export interface TopJoins {
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

  export interface TopAggs {
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

  export interface TopFilters {
    values: {
      tableName: string;
      count: number;
      popularValues?: TopFilterValue[];
    }[];
  }
}
