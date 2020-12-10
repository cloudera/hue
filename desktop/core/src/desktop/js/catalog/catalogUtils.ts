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
import { CancellablePromise } from 'api/cancellablePromise';
import DataCatalogEntry from 'catalog/DataCatalogEntry';
import MultiTableEntry from 'catalog/MultiTableEntry';
import { Compute, Connector } from 'types/config';

export interface FetchOptions {
  sourceType: string;
  compute?: Compute;
  path?: string[];
  paths?: string[][];
  silenceErrors?: boolean;
  connector: Connector;
  isView?: boolean;
}

/**
 * Wrapper function around ApiHelper calls, it will also save the entry on success.
 */
export const fetchAndSave = <T>(
  apiHelperFunction: (option: FetchOptions) => CancellableJqPromise<T>,
  setFunction: (val: T) => void,
  entry: DataCatalogEntry | MultiTableEntry,
  apiOptions?: { silenceErrors?: boolean; refreshAnalysis?: boolean }
): CancellableJqPromise<T> => {
  const promise = apiHelperFunction({
    sourceType: entry.getConnector().id,
    compute: (<DataCatalogEntry>entry).compute,
    path: (<DataCatalogEntry>entry).path, // Set for DataCatalogEntry
    paths: (<MultiTableEntry>entry).paths, // Set for MultiTableEntry
    silenceErrors: apiOptions && apiOptions.silenceErrors,
    connector: entry.dataCatalog.connector,
    isView: (<DataCatalogEntry>entry).isView && (<DataCatalogEntry>entry).isView() // MultiTable entries don't have this property
  });
  promise.then(data => {
    setFunction(data);
    entry.saveLater();
  });
  return promise;
};

/**
 * Helper function that adds sets the silence errors option to true if not specified
 */
export const setSilencedErrors = (options?: {
  silenceErrors?: boolean;
}): { silenceErrors?: boolean } => {
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
 */
export const applyCancellable = <T>(
  promise: CancellablePromise<T>,
  options?: { cancellable?: boolean }
): CancellablePromise<T> => {
  if (promise && promise.preventCancel && (!options || !options.cancellable)) {
    promise.preventCancel();
  }
  return promise;
};
