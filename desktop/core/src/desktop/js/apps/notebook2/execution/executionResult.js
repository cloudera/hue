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

import apiHelper from 'api/apiHelper';

/**
 *  available +----> fetching +----> done
 *      ^                     |
 *      |                     +----> fail
 *      |                     |
 *      +---------------------+
 *
 * If the handle indidcates that there's no result set available the ExecutionResult will have initial status set to
 * RESULT_STATUS.done
 *
 * @type { { canceling: string, canceled: string, fail: string, ready: string, executing: string, done: string } }
 */
const RESULT_STATUS = {
  ready: 'ready',
  available: 'available',
  fetching: 'fetching',
  done: 'done',
  fail: 'fail'
};

class ExecutionResult {
  /**
   *
   * @param {ExecutableStatement} executable
   */
  constructor(executable) {
    this.executable = executable;
    this.status = executable.handle.has_result_set ? RESULT_STATUS.available : RESULT_STATUS.done;
  }

  async fetchResultSize(options) {
    return new Promise((resolve, reject) => {
      if (this.status === RESULT_STATUS.fail) {
        reject();
        return;
      }

      let attempts = 0;
      const waitForRows = () => {
        attempts++;
        if (attempts < 10) {
          apiHelper
            .fetchResultSize({
              executable: this.executable
            })
            .then(resultSizeResponse => {
              if (resultSizeResponse.rows !== null) {
                resolve(resultSizeResponse);
              } else {
                window.setTimeout(waitForRows, 1000);
              }
            })
            .catch(reject);
        } else {
          reject();
        }
      };

      waitForRows();
    });
  }

  /**
   * Fetches additional rows
   *
   * @param {Object} options
   * @param {number} options.rows
   * @param {boolean} [options.startOver]
   *
   * @return {Promise}
   */
  async fetchRows(options) {
    return new Promise((resolve, reject) => {
      if (this.status !== RESULT_STATUS.available) {
        reject();
        return;
      }
      this.status = RESULT_STATUS.fetching;
      apiHelper
        .fetchResults({
          executable: this.executable,
          rows: options.rows,
          startOver: !!options.startOver
        })
        .then(resultResponse => {
          if (resultResponse.has_more) {
            this.status = RESULT_STATUS.available;
          } else {
            this.status = RESULT_STATUS.done;
          }
          resolve(resultResponse);
        })
        .catch(error => {
          this.status = RESULT_STATUS.fail;
          reject(error);
        });
    });
  }
}

export { RESULT_STATUS, ExecutionResult };
