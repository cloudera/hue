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

import axios, { AxiosResponse, AxiosTransformer } from 'axios';
import qs from 'qs';

import { CancellablePromise } from './cancellablePromise';
import hueUtils from 'utils/hueUtils';

export const successResponseIsError = (responseData?: {
  traceback?: string;
  status?: number;
  code?: number;
}): boolean => {
  return (
    typeof responseData !== 'undefined' &&
    (typeof responseData.traceback !== 'undefined' ||
      (typeof responseData.status !== 'undefined' && responseData.status !== 0) ||
      responseData.code === 503 ||
      responseData.code === 500)
  );
};

const UNKNOWN_ERROR_MESSAGE = 'Unknown error occurred';

export const extractErrorMessage = (
  errorResponse?:
    | {
        statusText?: string;
        responseText?: string;
        message?: string;
        error?: string | unknown;
      }
    | string
): string => {
  if (!errorResponse) {
    return UNKNOWN_ERROR_MESSAGE;
  }
  if (typeof errorResponse === 'string') {
    return errorResponse;
  }
  if (errorResponse.statusText && errorResponse.statusText !== 'abort') {
    return errorResponse.statusText;
  }
  if (errorResponse.responseText) {
    try {
      const errorJs = JSON.parse(errorResponse.responseText);
      if (errorJs.message) {
        return errorJs.message;
      }
    } catch (err) {}
    return errorResponse.responseText;
  }
  if (errorResponse.message) {
    return errorResponse.message;
  }
  if (errorResponse.statusText) {
    return errorResponse.statusText;
  }
  if (errorResponse.error && typeof errorResponse.error === 'string') {
    return errorResponse.error;
  }
  return UNKNOWN_ERROR_MESSAGE;
};

export const post = <T, U = unknown>(
  url: string,
  data?: U,
  options?: {
    silenceErrors?: boolean;
    ignoreSuccessErrors?: boolean;
    transformResponse?: AxiosTransformer;
    handleResponse?: (
      response: T
    ) => { valid: boolean; reason?: unknown; adjustedResponse?: T } | undefined;
  }
): CancellablePromise<T> =>
  new CancellablePromise((resolve, reject, onCancel) => {
    const notifyError = (message: string, response: unknown): void => {
      if (!options || !options.silenceErrors) {
        hueUtils.logError(response);
        if (message.indexOf('AuthorizationException') === -1) {
          $(document).trigger('error', message);
        }
      }
    };

    const handleErrorResponse = (response: AxiosResponse<T>): void => {
      const errorMessage = extractErrorMessage(response.data);
      reject(errorMessage);
      notifyError(errorMessage, response.data);
    };

    const cancelTokenSource = axios.CancelToken.source();
    let completed = false;

    axios
      .post<T>(url, qs.stringify(data), {
        cancelToken: cancelTokenSource.token,
        transformResponse: options && options.transformResponse
      })
      .then(response => {
        if (options && options.handleResponse) {
          const handledResponse = options.handleResponse(response.data);
          if (handledResponse) {
            if (handledResponse.valid) {
              resolve(handledResponse.adjustedResponse || response.data);
            } else {
              reject(handledResponse.reason);
              notifyError(String(handledResponse.reason), response.data);
            }
            return;
          }
        }
        if ((!options || !options.ignoreSuccessErrors) && successResponseIsError(response.data)) {
          handleErrorResponse(response);
        } else {
          resolve(response.data);
        }
      })
      .catch(err => {
        handleErrorResponse(err);
      })
      .finally(() => {
        completed = true;
      });

    onCancel(() => {
      if (!completed) {
        cancelTokenSource.cancel();
      }
    });
  });

export const cancelActiveRequest = (request?: JQuery.jqXHR): void => {
  if (request && request.readyState < 4) {
    request.abort();
  }
};
