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
import DataCatalogEntry from 'catalog/dataCatalogEntry';
import { Compute, Connector, Namespace } from 'types/config';

interface BaseOptions {
  namespace: Namespace;
  compute: Compute;
  definition?: unknown;
  silenceErrors?: boolean;
  cachedOnly?: boolean;
  refreshCache?: boolean;
  cancellable?: boolean;
  temporaryOnly?: boolean;
}

interface SingleEntryOptions extends BaseOptions {
  path: string | string[];
}

interface MultiEntryOptions extends BaseOptions {
  paths: (string | string[])[];
}

interface StaticSingleEntryOptions extends SingleEntryOptions {
  connector: Connector;
}

interface StaticMultiEntryOptions extends MultiEntryOptions {
  connector: Connector;
}

interface DataCatalog {
  getChildren(options: SingleEntryOptions): CancellableJqPromise<DataCatalogEntry[]>;
  getEntry(options: SingleEntryOptions): CancellableJqPromise<DataCatalogEntry>;
  getMultiTableEntry(options: MultiEntryOptions): CancellableJqPromise<DataCatalogEntry>;
  loadOptimizerPopularityForTables(
    options: MultiEntryOptions
  ): CancellableJqPromise<DataCatalogEntry[]>;
}

declare const dataCatalog: {
  getChildren(options: StaticSingleEntryOptions): CancellableJqPromise<DataCatalogEntry[]>;
  getEntry(options: StaticSingleEntryOptions): CancellableJqPromise<DataCatalogEntry>;
  getMultiTableEntry(options: StaticMultiEntryOptions): CancellableJqPromise<DataCatalogEntry>;
  loadOptimizerPopularityForTables(
    options: StaticMultiEntryOptions
  ): CancellableJqPromise<DataCatalogEntry[]>;
  getCatalog(connector: Connector): DataCatalog;
  applyCancellable(promise: CancellableJqPromise<unknown>, options: { cancellable: boolean }): void;
};

export = dataCatalog;
