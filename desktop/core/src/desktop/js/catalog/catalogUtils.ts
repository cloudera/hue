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
import { CatalogGetOptions } from 'catalog/dataCatalog';
import { Compute, Connector } from 'config/types';

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
 * Helper function that adds sets the silence errors option to true if not specified
 */
export const forceSilencedErrors = (options?: {
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
  options?: Pick<CatalogGetOptions, 'cancellable'>
): CancellablePromise<T> => {
  if (promise && promise.preventCancel && (!options || !options.cancellable)) {
    promise.preventCancel();
  }
  return promise;
};
