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
import DataCatalogEntry, { Analysis, NavigatorMeta, SourceMeta } from 'catalog/DataCatalogEntry';
import { sleep } from 'utils/hueUtils';

interface AnalyzeResponse {
  status: number;
  isSuccess: boolean;
  isFailure: boolean;
}

interface SharedFetchOptions {
  entry: DataCatalogEntry;
  silenceErrors?: boolean;
}

const AUTOCOMPLETE_URL_PREFIX = '/notebook/api/autocomplete/';
const DESCRIBE_URL = '/notebook/api/describe/';
const FIND_ENTITY_URL = '/metadata/api/catalog/find_entity';

const performAnalyze = ({
  entry,
  silenceErrors
}: SharedFetchOptions): CancellablePromise<AnalyzeResponse> => {
  if (entry.isDatabase()) {
    return CancellablePromise.resolve();
  }
  let cancelled = false;

  const pollForAnalysis = async (url: string, delay: number): Promise<AnalyzeResponse> => {
    const analyzeResponse = await post<AnalyzeResponse>(url, undefined, { silenceErrors });
    if (cancelled) {
      throw new Error('Cancelled');
    }
    if (!analyzeResponse.isFailure && !analyzeResponse.isSuccess) {
      await sleep(delay);
      return pollForAnalysis(url, 1000);
    } else {
      return analyzeResponse;
    }
  };

  return new CancellablePromise<AnalyzeResponse>(async (resolve, reject, onCancel) => {
    onCancel(() => {
      cancelled = true;
    });
    try {
      const analyzeResponse = await post<DefaultApiResponse & { watch_url?: string }>(
        `/${
          entry.getConnector().id === 'hive' ? 'beeswax' : entry.getConnector().id
        }/api/analyze/${entry.path.join('/')}/`,
        undefined,
        { silenceErrors }
      );
      if (
        !cancelled &&
        analyzeResponse &&
        analyzeResponse.status === 0 &&
        analyzeResponse.watch_url
      ) {
        resolve(await pollForAnalysis(analyzeResponse.watch_url, 500));
      } else {
        reject('Analyze failed');
      }
    } catch (err) {
      reject(err || 'Analyze failed');
    }
  });
};

export const fetchDescribe = ({
  entry,
  silenceErrors,
  refreshAnalysis
}: SharedFetchOptions & {
  refreshAnalysis?: boolean;
}): CancellablePromise<Analysis> =>
  new CancellablePromise<Analysis>(async (resolve, reject, onCancel) => {
    if (entry.isSource()) {
      reject('Describe is not possible on the source');
      return;
    }

    if (refreshAnalysis) {
      const analyzePromise = performAnalyze({ entry, silenceErrors });
      onCancel(analyzePromise.cancel.bind(analyzePromise));
      try {
        await analyzePromise;
      } catch (err) {}
    }

    const [database, table, ...fields] = entry.path;
    let url = `${DESCRIBE_URL}${database}`;
    if (table && fields.length) {
      url += `/${table}/stats/${fields.join('/')}`;
    } else if (table) {
      url += `/${table}/`;
    }

    const describePromise = post<Analysis>(
      url,
      {
        format: 'json',
        cluster: JSON.stringify(entry.compute),
        source_type: entry.getConnector().id
      },
      {
        silenceErrors,
        handleResponse: (response: Analysis & DefaultApiResponse) => {
          if (successResponseIsError(response)) {
            return { valid: false, reason: extractErrorMessage(response) };
          }
          const adjustedResponse = response;
          adjustedResponse.hueTimestamp = Date.now();
          return { valid: true, adjustedResponse };
        }
      }
    );

    try {
      resolve(await describePromise);
    } catch (err) {
      reject(err || 'Describe failed');
    }
  });

export const fetchNavigatorMetadata = ({
  entry,
  silenceErrors
}: SharedFetchOptions): CancellablePromise<NavigatorMeta> => {
  const params = new URLSearchParams();

  const [database, tableOrView, field] = entry.path;
  if (database && tableOrView && field) {
    params.append('type', 'field');
    params.append('database', database);
    params.append('table', tableOrView);
  } else if (database && tableOrView) {
    params.append('type', entry.isView() ? 'view' : 'table');
    params.append('database', database);
  } else if (database) {
    params.append('type', 'database');
  } else {
    return CancellablePromise.reject('Navigator metadata is not possible on the source');
  }
  params.append('name', entry.name);

  return post<NavigatorMeta>(
    `${FIND_ENTITY_URL}?${params}`,
    {
      notebook: {},
      snippet: JSON.stringify({
        type: entry.getConnector().id,
        source: 'data'
      }),
      cluster: (entry.compute && JSON.stringify(entry.compute)) || '""'
    },
    {
      silenceErrors,
      handleResponse: (
        response: (NavigatorMeta | { entity: NavigatorMeta }) & DefaultApiResponse
      ) => {
        if (successResponseIsError(response)) {
          return {
            valid: false,
            reason: `Navigator meta failed: ${extractErrorMessage(response)}`
          };
        }
        const adjustedResponse = (<{ entity: NavigatorMeta }>response).entity || response;
        adjustedResponse.hueTimestamp = Date.now();

        return { valid: true, adjustedResponse };
      }
    }
  );
};

export const fetchSourceMetadata = ({
  entry,
  silenceErrors
}: SharedFetchOptions): CancellablePromise<SourceMeta> =>
  post<SourceMeta>(
    `${AUTOCOMPLETE_URL_PREFIX}${entry.path.join('/')}${entry.path.length ? '/' : ''}`,
    {
      notebook: {},
      snippet: JSON.stringify({
        type: entry.getConnector().id,
        source: 'data'
      }),
      cluster: (entry.compute && JSON.stringify(entry.compute)) || '""'
    },
    {
      silenceErrors,
      handleResponse: response => {
        const message = <string>response.error || response.message || '';
        const adjustedResponse = response || {};
        adjustedResponse.notFound =
          !!response &&
          response.status === 0 &&
          response.code === 500 &&
          (message.indexOf('Error 10001') !== -1 || message.indexOf('AnalysisException') !== -1);

        adjustedResponse.hueTimestamp = Date.now();

        if (!adjustedResponse.notFound && successResponseIsError(response)) {
          return { valid: false, reason: `Source meta failed: ${extractErrorMessage(response)}` };
        }
        return { valid: true, adjustedResponse };
      }
    }
  );
