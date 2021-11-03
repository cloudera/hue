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

import { ExecutionJob, fetchLogs } from 'apps/editor/execution/api';
import {
  EXECUTABLE_LOGS_UPDATED_TOPIC,
  ExecutableLogsUpdatedEvent
} from 'apps/editor/execution/events';
import huePubSub from 'utils/huePubSub';
import SqlExecutable, { ExecutionStatus } from './sqlExecutable';

export interface ExecutionError {
  row: number;
  column: number;
  message: string;
}

export interface ExecutionLogsRaw {
  jobs: ExecutionJob[];
  errors: string[];
}

export default class ExecutionLogs {
  executable: SqlExecutable;
  fullLog = '';
  logLines = 0;
  jobs: ExecutionJob[] = [];
  errors: ExecutionError[] = [];

  constructor(executable: SqlExecutable) {
    this.executable = executable;
  }

  notify(): void {
    huePubSub.publish<ExecutableLogsUpdatedEvent>(EXECUTABLE_LOGS_UPDATED_TOPIC, this);
  }

  reset(): void {
    this.fullLog = '';
    this.logLines = 0;
    this.jobs = [];
    this.errors = [];
    this.notify();
  }

  async fetchLogs(finalFetch?: boolean): Promise<void> {
    const logDetails = await fetchLogs({
      executable: this.executable,
      fullLog: this.fullLog,
      jobs: this.jobs
    });

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

    huePubSub.publish<ExecutableLogsUpdatedEvent>(EXECUTABLE_LOGS_UPDATED_TOPIC, this);

    if (!finalFetch) {
      const delay = this.executable.getExecutionTime() > 45000 ? 5000 : 1000;
      const fetchLogsTimeout = window.setTimeout(async () => {
        // TODO: Fetch logs for ExecutionStatus.streaming?
        await this.fetchLogs(
          this.executable.status !== ExecutionStatus.running &&
            this.executable.status !== ExecutionStatus.starting &&
            this.executable.status !== ExecutionStatus.waiting
        );
      }, delay);

      this.executable.addCancellable({
        cancel: () => {
          window.clearTimeout(fetchLogsTimeout);
        }
      });
    }
  }

  toJs(): ExecutionLogsRaw {
    return {
      jobs: this.jobs,
      errors: this.errors.map(err => err.message)
    };
  }
}
