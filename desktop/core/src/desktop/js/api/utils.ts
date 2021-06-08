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

import axios, {
  AxiosError,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosTransformer,
  CancelToken
} from 'axios';
import qs from 'qs';

import { CancellablePromise } from './cancellablePromise';
import { hueWindow } from 'types/types';
import huePubSub from 'utils/huePubSub';
import logError from 'utils/logError';

export interface DefaultApiResponse {
  status: number;
  code?: number;
  error?: string | unknown;
  message?: string;
  responseText?: string;
  statusText?: string;
  traceback?: string;
}

export interface ApiFetchOptions<T, E = string> extends AxiosRequestConfig {
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

const axiosInstance = axios.create({ withCredentials: true });

let baseUrl = (window as hueWindow).HUE_BASE_URL;
let bearerToken: string | undefined;

axiosInstance.interceptors.request.use(config => {
  if (baseUrl) {
    config.baseURL = baseUrl;
  }
  if (bearerToken) {
    config.headers['Authorization'] = `Bearer ${bearerToken}`;
  }
  return config;
});

axiosInstance.interceptors.response.use(response => {
  if (response.data?.access) {
    bearerToken = response.data.access;
  }
  return response;
});

export const setBaseUrl = (newBaseUrl: string): void => {
  baseUrl = newBaseUrl;
};

export const setBearerToken = (newBearerToken: string): void => {
  bearerToken = newBearerToken;
};

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

const notifyError = <T>(
  message: string,
  response: unknown,
  options?: Pick<ApiFetchOptions<T>, 'silenceErrors'>
): void => {
  if (!options || !options.silenceErrors) {
    logError(response);
    if (message.indexOf('AuthorizationException') === -1) {
      huePubSub.publish('hue.error', message);
    }
  }
};

const handleErrorResponse = <T>(
  err: AxiosError<DefaultApiResponse>,
  reject: (reason?: unknown) => void,
  options?: Pick<ApiFetchOptions<T>, 'silenceErrors'>
): void => {
  const errorMessage = extractErrorMessage(err.response && err.response.data);
  reject(errorMessage);
  notifyError(errorMessage, (err && err.response) || err, options);
};

const handleResponse = <T>(
  response: AxiosResponse<T & DefaultApiResponse>,
  resolve: (value?: T) => void,
  reject: (reason?: unknown) => void,
  options?: ApiFetchOptions<T>
): void => {
  if (options && options.handleSuccess) {
    options.handleSuccess(response.data, resolve, reason => {
      reject(reason);
      notifyError(String(reason), response.data, options);
    });
  } else if ((!options || !options.ignoreSuccessErrors) && successResponseIsError(response.data)) {
    const errorMessage = extractErrorMessage(response && response.data);
    reject(errorMessage);
    notifyError(errorMessage, response, options);
  } else {
    resolve(response.data);
  }
};

const getCancelToken = (): { cancelToken: CancelToken; cancel: () => void } => {
  const cancelTokenSource = axios.CancelToken.source();
  return { cancelToken: cancelTokenSource.token, cancel: cancelTokenSource.cancel };
};

export const post = <T, U = unknown>(
  url: string,
  data?: U,
  options?: ApiFetchOptions<T>
): CancellablePromise<T> =>
  new CancellablePromise((resolve, reject, onCancel) => {
    const { cancelToken, cancel } = getCancelToken();
    let completed = false;

    axiosInstance
      .post<T & DefaultApiResponse>(url, qs.stringify(data), {
        cancelToken,
        ...options
      })
      .then(response => {
        handleResponse(response, resolve, reject, options);
      })
      .catch((err: AxiosError) => {
        if (options && options.handleError) {
          options.handleError(err, resolve, reason => {
            handleErrorResponse(err, reject, options);
            notifyError(String(reason), err, options);
          });
        } else {
          handleErrorResponse(err, reject, options);
        }
      })
      .finally(() => {
        completed = true;
      });

    onCancel(() => {
      if (!completed) {
        cancel();
      }
    });
  });

export const get = <T, U = unknown>(
  url: string,
  data?: U,
  options?: ApiFetchOptions<T>
): CancellablePromise<T> =>
  new CancellablePromise((resolve, reject, onCancel) => {
    const { cancelToken, cancel } = getCancelToken();
    let completed = false;

    axiosInstance
      .get<T & DefaultApiResponse>(url, {
        cancelToken,
        params: data
      })
      .then(response => {
        handleResponse(response, resolve, reject, options);
      })
      .catch((err: AxiosError) => {
        handleErrorResponse(err, reject, options);
      })
      .finally(() => {
        completed = true;
      });

    onCancel(() => {
      if (!completed) {
        cancel();
      }
    });
  });

export const upload = async <T>(
  url: string,
  data: FormData,
  progressCallback?: (progress: number) => void
): Promise<T> => {
  const response = await axiosInstance.post<T>(url, data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: progressEvent => {
      if (progressCallback) {
        progressCallback(Math.round((progressEvent.loaded * 100) / progressEvent.total));
      }
    }
  });
  return response.data;
};
