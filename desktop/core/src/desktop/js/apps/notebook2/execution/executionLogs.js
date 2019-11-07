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
import { EXECUTION_STATUS } from './executable';

export const LOGS_UPDATED_EVENT = 'hue.executable.logs.updated';

export default class ExecutionLogs {
  /**
   *
   * @param {Executable} executable
   */
  constructor(executable) {
    this.executable = executable;
    this.fullLog = '';
    this.logLines = 0;
    this.jobs = [];
    this.errors = [];
  }

  notify() {
    huePubSub.publish(LOGS_UPDATED_EVENT, this);
  }

  reset() {
    this.fullLog = '';
    this.logLines = 0;
    this.jobs = [];
    this.errors = [];
    this.notify();
  }

  async fetchLogs(finalFetch) {
    const logDetails = await apiHelper.fetchLogs(this);

    if (logDetails.logs.indexOf('Unable to locate') === -1 || logDetails.isFullLogs) {
      this.fullLog = logDetails.logs;
    } else {
      this.fullLog += '\n' + logDetails.logs;
    }
    this.logLines = this.fullLog.split(/\r\n|\r|\n/).length;

    if (logDetails.jobs) {
      logDetails.jobs.forEach(job => {
        if (typeof job.percentJob === 'undefined') {
          job.percentJob = -1;
        }
      });
      this.jobs = logDetails.jobs;
    } else {
      this.jobs = [];
    }

    huePubSub.publish(LOGS_UPDATED_EVENT, this);

    if (!finalFetch) {
      const delay = this.executable.getExecutionTime() > 45000 ? 5000 : 1000;
      const fetchLogsTimeout = window.setTimeout(async () => {
        await this.fetchLogs(
          this.executable.status !== EXECUTION_STATUS.running &&
            this.executable.status !== EXECUTION_STATUS.starting &&
            this.executable.status !== EXECUTION_STATUS.waiting
        );
      }, delay);

      this.executable.addCancellable({
        cancel: () => {
          window.clearTimeout(fetchLogsTimeout);
        }
      });
    }
  }

  toJs() {
    return {
      jobs: this.jobs,
      errors: this.errors
    };
  }
}
