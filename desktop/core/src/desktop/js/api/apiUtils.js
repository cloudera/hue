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

import $ from 'jquery';

import logError from 'utils/logError';

/**
 * @param {Object} [response]
 * @param {number} [response.status]
 * @returns {boolean} - True if actually an error
 */
export const successResponseIsError = response => {
  return (
    typeof response !== 'undefined' &&
    (typeof response.traceback !== 'undefined' ||
      (typeof response.status !== 'undefined' && response.status !== 0) ||
      response.code === 503 ||
      response.code === 500)
  );
};

/**
 * @param {Object} options
 * @param {Function} [options.errorCallback]
 * @param {boolean} [options.silenceErrors]
 * @returns {Function}
 */
export const assistErrorCallback = options => {
  return errorResponse => {
    let errorMessage = 'Unknown error occurred';
    if (typeof errorResponse !== 'undefined' && errorResponse !== null) {
      if (typeof errorResponse.statusText !== 'undefined' && errorResponse.statusText === 'abort') {
        return;
      } else if (typeof errorResponse.responseText !== 'undefined') {
        try {
          const errorJs = JSON.parse(errorResponse.responseText);
          if (typeof errorJs.message !== 'undefined') {
            errorMessage = errorJs.message;
          } else {
            errorMessage = errorResponse.responseText;
          }
        } catch (err) {
          errorMessage = errorResponse.responseText;
        }
      } else if (typeof errorResponse.message !== 'undefined' && errorResponse.message !== null) {
        errorMessage = errorResponse.message;
      } else if (
        typeof errorResponse.statusText !== 'undefined' &&
        errorResponse.statusText !== null
      ) {
        errorMessage = errorResponse.statusText;
      } else if (
        errorResponse.error !== 'undefined' &&
        Object.prototype.toString.call(errorResponse.error) === '[object String]'
      ) {
        errorMessage = errorResponse.error;
      } else if (Object.prototype.toString.call(errorResponse) === '[object String]') {
        errorMessage = errorResponse;
      }
    }

    if (!options || !options.silenceErrors) {
      logError(errorResponse);
      if (errorMessage && errorMessage.indexOf('AuthorizationException') === -1) {
        $(document).trigger('error', errorMessage);
      }
    }

    if (options && options.errorCallback) {
      options.errorCallback(errorMessage);
    }
    return errorMessage;
  };
};

/**
 * @param {string} url
 * @param {Object} [data]
 * @param {Object} [options]
 * @param {function} [options.successCallback]
 * @param {function} [options.errorCallback]
 * @param {boolean} [options.silenceErrors]
 */
export const simpleGet = (url, data, options) => {
  if (!options) {
    options = {};
  }
  return $.get(url, data, data => {
    if (successResponseIsError(data)) {
      assistErrorCallback(options)(data);
    } else if (typeof options.successCallback !== 'undefined') {
      options.successCallback(data);
    }
  }).fail(assistErrorCallback(options));
};

/**
 * @param {string} url
 * @param {Object} data
 * @param {Object} [options]
 * @param {function} [options.successCallback]
 * @param {function} [options.errorCallback]
 * @param {boolean} [options.silenceErrors]
 * @param {string} [options.dataType] - Default: Intelligent Guess (xml, json, script, text, html)
 *
 * @return {JQueryPromise}
 */
export const simplePost = (url, data, options) => {
  const deferred = $.Deferred();

  const request = $.post({
    url: url,
    data: data,
    dataType: options && options.dataType
  })
    .done(data => {
      if (successResponseIsError(data)) {
        deferred.reject(assistErrorCallback(options)(data));
        return;
      }
      if (options && options.successCallback) {
        options.successCallback(data);
      }
      deferred.resolve(data);
    })
    .fail(assistErrorCallback(options));

  request.fail(data => {
    deferred.reject(assistErrorCallback(options)(data));
  });

  const promise = deferred.promise();

  promise.getReadyState = function () {
    return request.readyState;
  };

  promise.abort = () => {
    request.abort();
  };

  promise.cancel = promise.abort;

  return promise;
};

/**
 * @param {string} url
 * @param {Object} data
 * @param {Object} [options]
 * @param {boolean} [options.silenceErrors]
 * @param {string} [options.dataType] - Default: Intelligent Guess (xml, json, script, text, html)
 *
 * @return {Promise}
 */
export const simplePostAsync = async (url, data, options) =>
  new Promise((resolve, reject) => {
    simplePost(url, data, options).done(resolve).fail(reject);
  });

export const cancelActiveRequest = request => {
  if (typeof request !== 'undefined' && request !== null) {
    const readyState = request.getReadyState ? request.getReadyState() : request.readyState;
    if (readyState < 4) {
      request.abort();
    }
  }
};
