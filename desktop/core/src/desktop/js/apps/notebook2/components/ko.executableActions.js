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

import ko from 'knockout';

import componentUtils from 'ko/components/componentUtils';
import I18n from 'utils/i18n';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import DisposableComponent from 'ko/components/DisposableComponent';

export const NAME = 'executable-actions';

export const EXECUTE_ACTIVE_EXECUTABLE_EVENT = 'executable.active.executable';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-execute-actions" data-test="${NAME}">
  <div class="btn-group">
    <!-- ko if: status() !== '${ EXECUTION_STATUS.running }' -->
    <!-- ko ifnot: hasMoreToExecute -->
    <button class="btn btn-primary btn-mini btn-execute disable-feedback" data-test="execute" data-bind="click: execute"><i class="fa fa-play fa-fw"></i> ${I18n(
      'Execute'
    )}</button>
    <!-- /ko -->
    <!-- ko if: hasMoreToExecute -->
    <button class="btn btn-primary btn-mini btn-execute disable-feedback" data-test="execute" data-bind="click: executeNext"><i class="fa fa-play fa-fw"></i> ${I18n(
      'Continue'
    )}</button>
    <!-- /ko -->
    <!-- /ko -->
    <!-- ko if: status() === '${ EXECUTION_STATUS.running }' -->
    <!-- ko ifnot: stopping -->
    <button class="btn btn-primary btn-mini btn-execute disable-feedback" data-test="stop" data-bind="click: stop"><i class="fa fa-stop fa-fw"></i> ${I18n(
      'Stop'
    )}</button>
    <!-- /ko -->
    <!-- ko if: stopping -->
    <button class="btn btn-primary btn-mini btn-execute disable-feedback disabled"><i class="fa fa-spinner fa-spin fa-fw"></i> ${I18n(
      'Stop'
    )}</button>
    <!-- /ko -->
    <!-- /ko -->
  </div>
</div>
`;

class ExecutableActions extends DisposableComponent {
  constructor(params) {
    super();
    this.stopping = ko.observable(false);
    this.activeExecutable = params.activeExecutable;
    this.status = ko.observable(EXECUTION_STATUS.ready);
    this.hasMoreToExecute = ko.observable(false);
    this.beforeExecute = params.beforeExecute;

    this.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.hasMoreToExecute(!!executable.nextExecutable);
        this.status(executable.status);
      }
    });

    this.subscribe(EXECUTE_ACTIVE_EXECUTABLE_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.execute();
      }
    });

    this.subscribe(this.activeExecutable, executable => {
      // TODO: If previousExecutable show 'waiting...' ?
      this.hasMoreToExecute(!!executable.nextExecutable);
      this.status(executable.status);
    });
  }

  async stop() {
    if (this.stopping() || !this.activeExecutable()) {
      return;
    }
    this.stopping(true);
    await this.activeExecutable().cancel();
    this.stopping(false);
  }

  async execute() {
    if (this.beforeExecute) {
      await this.beforeExecute();
    }
    const executable = this.activeExecutable();
    if (executable) {
      await executable.reset();
      executable.execute();
    }
  }

  executeNext() {
    if (this.activeExecutable() && this.activeExecutable().nextExecutable) {
      this.activeExecutable(this.activeExecutable().nextExecutable);
    }
    this.execute();
  }
}

componentUtils.registerComponent(NAME, ExecutableActions, TEMPLATE);
