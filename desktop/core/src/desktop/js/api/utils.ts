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

import axios, { AxiosError, AxiosTransformer } from 'axios';
import qs from 'qs';
import huePubSub from 'utils/huePubSub';

import { CancellablePromise } from './cancellablePromise';
import hueUtils from 'utils/hueUtils';

export interface DefaultApiResponse {
  status: number;
  code?: number;
  error?: string | unknown;
  message?: string;
  responseText?: string;
  statusText?: string;
  traceback?: string;
}

export const successResponseIsError = (responseData?: DefaultApiResponse): boolean => {
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
  errorResponse?: DefaultApiResponse | AxiosError | string
): string => {
  if (!errorResponse) {
    return UNKNOWN_ERROR_MESSAGE;
  }
  if (typeof errorResponse === 'string') {
    return errorResponse;
  }
  const defaultResponse = <DefaultApiResponse>errorResponse;
  if (defaultResponse.statusText && defaultResponse.statusText !== 'abort') {
    return defaultResponse.statusText;
  }
  if (defaultResponse.responseText) {
    try {
      const errorJs = JSON.parse(defaultResponse.responseText);
      if (errorJs.message) {
        return errorJs.message;
      }
    } catch (err) {}
    return defaultResponse.responseText;
  }
  if (errorResponse.message) {
    return errorResponse.message;
  }
  if (defaultResponse.statusText) {
    return defaultResponse.statusText;
  }
  if (defaultResponse.error && typeof defaultResponse.error === 'string') {
    return defaultResponse.error;
  }
  return UNKNOWN_ERROR_MESSAGE;
};

export const post = <T, U = unknown, E = string>(
  url: string,
  data?: U,
  options?: {
    silenceErrors?: boolean;
    ignoreSuccessErrors?: boolean;
    transformResponse?: AxiosTransformer;
    handleSuccess?: (
      response: T & DefaultApiResponse,
      resolve: (val: T) => void,
      reject: (err: unknown) => void
    ) => void;
    handleError?: (
      errorResponse: AxiosError<E>,
      resolve: (val: T) => void,
      reject: (err: unknown) => void
    ) => void;
  }
): CancellablePromise<T> =>
  new CancellablePromise((resolve, reject, onCancel) => {
    const notifyError = (message: string, response: unknown): void => {
      if (!options || !options.silenceErrors) {
        hueUtils.logError(response);
        if (message.indexOf('AuthorizationException') === -1) {
          huePubSub.publish('hue.error', message);
        }
      }
    };

    const handleErrorResponse = (err: AxiosError<DefaultApiResponse>): void => {
      const errorMessage = extractErrorMessage(err.response && err.response.data);
      reject(errorMessage);
      notifyError(errorMessage, (err && err.response) || err);
    };

    const cancelTokenSource = axios.CancelToken.source();
    let completed = false;

    axios
      .post<T & DefaultApiResponse>(url, qs.stringify(data), {
        cancelToken: cancelTokenSource.token,
        transformResponse: options && options.transformResponse
      })
      .then(response => {
        if (options && options.handleSuccess) {
          options.handleSuccess(response.data, resolve, reason => {
            reject(reason);
            notifyError(String(reason), response.data);
          });
        } else if (
          (!options || !options.ignoreSuccessErrors) &&
          successResponseIsError(response.data)
        ) {
          const errorMessage = extractErrorMessage(response && response.data);
          reject(errorMessage);
          notifyError(errorMessage, response);
        } else {
          resolve(response.data);
        }
      })
      .catch((err: AxiosError) => {
        if (options && options.handleError) {
          options.handleError(err, resolve, reason => {
            handleErrorResponse(err);
            notifyError(String(reason), err);
          });
        } else {
          handleErrorResponse(err);
        }
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
