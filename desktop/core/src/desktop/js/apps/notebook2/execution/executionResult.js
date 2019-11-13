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
import huePubSub from 'utils/huePubSub';
import { sleep } from 'utils/hueUtils';
import { EXECUTION_STATUS } from './executable';

export const RESULT_UPDATED_EVENT = 'hue.executable.result.updated';

export const RESULT_TYPE = {
  TABLE: 'table'
};

export default class ExecutionResult {
  /**
   *
   * @param {Executable} executable
   */
  constructor(executable) {
    this.executable = executable;

    this.type = RESULT_TYPE.TABLE;
    this.rows = [];
    this.meta = [];
    this.lastRows = [];
    this.images = [];
    this.type = undefined;
    this.hasMore = true;
    this.isEscaped = false;
    this.fetchedOnce = false;
  }

  async fetchResultSize() {
    if (this.executable.status === EXECUTION_STATUS.failed) {
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
   * @param {Object} [options]
   * @param {number} [options.rows]
   * @param {boolean} [options.startOver]
   *
   * @return {Promise}
   */
  async fetchRows(options) {
    if (this.executable.status !== EXECUTION_STATUS.available) {
      return Promise.reject();
    }

    const resultResponse = await apiHelper.fetchResults({
      executable: this.executable,
      rows: (options && options.rows) || 100,
      startOver: options && options.startOver
    });

    this.handleResultResponse(resultResponse);
  }

  handleResultResponse(resultResponse) {
    const initialIndex = this.rows.length;
    resultResponse.data.forEach((row, index) => {
      row.unshift(initialIndex + index + 1);
    });

    this.rows.push(...resultResponse.data);
    this.lastRows = resultResponse.data;
    if (!this.meta.length) {
      this.meta = resultResponse.meta;
      this.meta.unshift({ type: 'INT_TYPE', name: '', comment: null });
    }
    this.hasMore = resultResponse.has_more;
    this.isEscaped = resultResponse.isEscaped;
    this.type = resultResponse.type;
    this.fetchedOnce = true;
    huePubSub.publish(RESULT_UPDATED_EVENT, this);
  }
}
