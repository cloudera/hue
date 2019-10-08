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
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';
import DisposableComponent from 'ko/components/DisposableComponent';

export const NAME = 'snippet-execute-actions';

const TEMPLATE = `
<div class="snippet-execute-actions" data-test="${NAME}">
  <div class="btn-group">
    <!-- ko if: status() !== '${EXECUTION_STATUS.running}' -->
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
    <!-- ko if: status() === '${EXECUTION_STATUS.running}' -->
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

class SnippetExecuteActions extends DisposableComponent {
  constructor(params) {
    super();
    this.stopping = ko.observable(false);
    this.snippet = params.snippet;
    this.status = ko.observable(EXECUTION_STATUS.ready);
    this.hasMoreToExecute = ko.observable(false);
    this.trackPubSub(
      huePubSub.subscribe(EXECUTOR_UPDATED_EVENT, executorUpdate => {
        if (this.snippet.executor === executorUpdate.executor) {
          this.hasMoreToExecute(!!executorUpdate.executor.hasMoreToExecute());
          this.status(executorUpdate.executable.status);
        }
      })
    );
  }

  async stop() {
    if (this.stopping()) {
      return;
    }
    this.stopping(true);
    await this.snippet.executor.cancel();
    this.stopping(false);
  }

  execute() {
    this.snippet.execute();
  }

  executeNext() {
    this.snippet.executeNext();
  }

  dispose() {
    while (this.disposals.length) {
      this.disposals.pop()();
    }
  }
}

componentUtils.registerComponent(NAME, SnippetExecuteActions, TEMPLATE);
