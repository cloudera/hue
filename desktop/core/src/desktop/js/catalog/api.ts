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
import DataCatalogEntry, { SourceMeta } from 'catalog/DataCatalogEntry';

const AUTOCOMPLETE_API_PREFIX = '/notebook/api/autocomplete/';

export const fetchSourceMeta = (options: {
  entry: DataCatalogEntry;
  silenceErrors?: boolean;
}): CancellablePromise<SourceMeta> => {
  const url =
    AUTOCOMPLETE_API_PREFIX + options.entry.path.join('/') + (options.entry.path.length ? '/' : '');

  return post<SourceMeta & { status: number; code?: number; error?: string; message?: string }>(
    url,
    {
      notebook: {},
      snippet: JSON.stringify({
        type: options.entry.getConnector().id,
        source: 'data'
      }),
      cluster: (options.entry.compute && JSON.stringify(options.entry.compute)) || '""'
    },
    {
      ...options,
      handleResponse: response => {
        const message = response.error || response.message || '';
        const adjustedResponse = response;
        adjustedResponse.notFound =
          response.status === 0 &&
          response.code === 500 &&
          (message.indexOf('Error 10001') !== -1 || message.indexOf('AnalysisException') !== -1);

        adjustedResponse.hueTimestamp = Date.now();

        const valid = adjustedResponse.notFound || !successResponseIsError(response);

        if (!valid) {
          return { valid, reason: extractErrorMessage(response) };
        }
        return { valid, adjustedResponse };
      }
    }
  );
};
