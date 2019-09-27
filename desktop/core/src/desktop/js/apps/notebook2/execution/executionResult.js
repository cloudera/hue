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
import { sleep } from 'utils/hueUtils';

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
   * @param {Executable} executable
   */
  constructor(executable) {
    this.executable = executable;
    this.status = executable.handle.has_result_set ? RESULT_STATUS.available : RESULT_STATUS.done;
  }

  async fetchResultSize() {
    if (this.status === RESULT_STATUS.fail) {
      return;
    }

    let attempts = 0;
    const waitForRows = async () => {
      attempts++;
      if (attempts < 10) {
        const resultSizeResponse = await apiHelper.fetchResultSize2({
          executable: this.executable,
          silenceErrors: true
        });

        if (resultSizeResponse.rows !== null) {
          return resultSizeResponse;
        } else {
          await sleep(1000);
          return await waitForRows();
        }
      } else {
        return Promise.reject();
      }
    };

    return await waitForRows();
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
    if (this.status !== RESULT_STATUS.available) {
      return Promise.reject();
    }

    this.status = RESULT_STATUS.fetching;

    try {
      const resultResponse = await apiHelper.fetchResults({
        executable: this.executable,
        rows: options.rows,
        startOver: !!options.startOver
      });

      if (resultResponse.has_more) {
        this.status = RESULT_STATUS.available;
      } else {
        this.status = RESULT_STATUS.done;
      }

      return resultResponse;
    } catch (err) {
      this.status = RESULT_STATUS.fail;
      return Promise.reject(err);
    }
  }
}

export { RESULT_STATUS, ExecutionResult };
