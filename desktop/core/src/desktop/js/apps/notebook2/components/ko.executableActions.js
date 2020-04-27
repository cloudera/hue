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

import * as ko from 'knockout';

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';

export const NAME = 'executable-actions';

export const EXECUTE_ACTIVE_EXECUTABLE_EVENT = 'executable.active.executable';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-execute-actions" data-test="${ NAME }">
  <div class="btn-group">
    <!-- ko if: status() !== '${ EXECUTION_STATUS.running }' && !waiting() -->
    <button class="btn btn-primary btn-mini btn-execute disable-feedback" data-test="execute" data-bind="click: execute, disable: disabled"><i class="fa fa-play fa-fw"></i> ${I18n(
      'Execute'
    )}</button>
    <!-- /ko -->
    <!-- ko if: status() === '${ EXECUTION_STATUS.running }' || waiting() -->
      <!-- ko ifnot: stopping -->
      <button class="btn btn-danger btn-mini btn-execute disable-feedback" data-test="stop" data-bind="click: stop"><i class="fa fa-stop fa-fw"></i>
      <!-- ko ifnot: waiting -->
        ${ I18n('Stop') }
      <!-- /ko -->
      <!-- ko if: waiting -->
        ${ I18n('Stop batch') }
      <!-- /ko -->
      </button>
      <!-- /ko -->
      <!-- ko if: stopping -->
      <button class="btn btn-primary btn-mini btn-execute disable-feedback disabled"><i class="fa fa-spinner fa-spin fa-fw"></i>${ I18n('Stopping') }</button>
      <!-- /ko -->
    <!-- /ko -->
  </div>
  <form autocomplete="off" class="inline-block margin-left-10">
    <input class="input-small limit-input" type="number" ${ window.PREVENT_AUTOFILL_INPUT_ATTRS } placeholder="${ I18n('Limit') }" data-bind="textInput: limit, autogrowInput: { minWidth: 50, maxWidth: 80, comfortZone: 25 }">
  </form>
</div>
`;

const WHITE_SPACE_REGEX = /^\s*$/;

class ExecutableActions extends DisposableComponent {
  constructor(params) {
    super();
    this.stopping = ko.observable(false);
    this.activeExecutable = params.activeExecutable;
    this.status = ko.observable(EXECUTION_STATUS.ready);
    this.partOfRunningExecution = ko.observable(false);
    this.beforeExecute = params.beforeExecute;

    this.limit = ko.observable();

    this.subscribe(this.limit, newVal => {
      if (this.activeExecutable()) {
        this.activeExecutable().executor.defaultLimit(newVal);
      }
    });

    this.waiting = ko.pureComputed(
      () =>
        this.activeExecutable() &&
        this.activeExecutable().isReady() &&
        this.partOfRunningExecution()
    );

    this.disabled = ko.pureComputed(() => {
      const executable = this.activeExecutable();

      return (
        !executable ||
        (executable.parsedStatement && WHITE_SPACE_REGEX.test(executable.parsedStatement.statement))
      );
    });

    this.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.updateFromExecutable(executable);
      }
    });

    this.subscribe(EXECUTE_ACTIVE_EXECUTABLE_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.execute();
      }
    });

    this.subscribe(this.activeExecutable, this.updateFromExecutable.bind(this));

    if (this.activeExecutable()) {
      this.updateFromExecutable(this.activeExecutable());
    }
  }

  updateFromExecutable(executable) {
    this.status(executable.status);
    this.partOfRunningExecution(executable.isPartOfRunningExecution());
    this.limit(executable.executor.defaultLimit());
  }

  async stop() {
    if (this.stopping() || !this.activeExecutable()) {
      return;
    }
    this.stopping(true);
    await this.activeExecutable().cancelBatchChain(true);
    this.stopping(false);
  }

  async execute() {
    huePubSub.publish('hue.ace.autocompleter.hide');
    if (this.beforeExecute) {
      await this.beforeExecute();
    }
    const executable = this.activeExecutable();
    if (executable) {
      await executable.reset();
      executable.execute();
    }
  }
}

componentUtils.registerComponent(NAME, ExecutableActions, TEMPLATE);
