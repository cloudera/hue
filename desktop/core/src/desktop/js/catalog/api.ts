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
import { DefaultApiResponse, extractErrorMessage, post, successResponseIsError } from 'api/utils';
import DataCatalogEntry, { NavigatorMeta, SourceMeta } from 'catalog/DataCatalogEntry';

const AUTOCOMPLETE_URL_PREFIX = '/notebook/api/autocomplete/';
const FIND_ENTITY_URL = '/metadata/api/catalog/find_entity';

export const fetchSourceMetadata = (options: {
  entry: DataCatalogEntry;
  silenceErrors?: boolean;
}): CancellablePromise<SourceMeta> =>
  post<SourceMeta>(
    `${AUTOCOMPLETE_URL_PREFIX}${options.entry.path.join('/')}${
      options.entry.path.length ? '/' : ''
    }`,
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
        const message = <string>response.error || response.message || '';
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

export const fetchNavigatorMetadata = (options: {
  entry: DataCatalogEntry;
  silenceErrors?: boolean;
}): CancellablePromise<NavigatorMeta> => {
  const params = new URLSearchParams();

  if (options.entry.path.length === 1) {
    params.append('type', 'database');
  } else if (options.entry.path.length === 2) {
    params.append('type', options.entry.isView() ? 'view' : 'table');
    params.append('database', options.entry.path[0]);
  } else if (options.entry.path.length === 3) {
    params.append('type', 'field');
    params.append('database', options.entry.path[1]);
    params.append('table', options.entry.path[1]);
  } else {
    return CancellablePromise.reject();
  }
  params.append('name', options.entry.path[options.entry.path.length - 1]);

  return post<NavigatorMeta>(
    `${FIND_ENTITY_URL}?${params}`,
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
      handleResponse: (
        response: (NavigatorMeta | { entity: NavigatorMeta }) & DefaultApiResponse
      ) => {
        const adjustedResponse = (<{ entity: NavigatorMeta }>response).entity || response;
        adjustedResponse.hueTimestamp = Date.now();

        const valid = !successResponseIsError(response);

        if (!valid) {
          return { valid, reason: extractErrorMessage(response) };
        }
        return { valid, adjustedResponse };
      }
    }
  );
};
