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
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executableStatement';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';

export const NAME = 'snippet-execute-actions';

const TEMPLATE = `
<div class="snippet-execute-actions">
  <div class="btn-group">
    <!-- ko if: status() !== '${EXECUTION_STATUS.running}' -->
    <button class="btn btn-primary btn-mini btn-execute" data-bind="click: execute"><i class="fa fa-play fa-fw"></i> ${I18n(
      'Execute'
    )}</button>
    <!-- /ko -->
    <!-- ko if: status() === '${EXECUTION_STATUS.running}' -->
    <!-- ko ifnot: stopping -->
    <button class="btn btn-primary btn-mini btn-execute" data-bind="click: stop"><i class="fa fa-stop fa-fw"></i> ${I18n(
      'Stop'
    )}</button>
    <!-- /ko -->
    <!-- ko if: stopping -->
    <button class="btn btn-primary btn-mini btn-execute disabled"><i class="fa fa-spinner fa-spin fa-fw"></i> ${I18n(
      'Stop'
    )}</button>
    <!-- /ko -->
    <!-- /ko -->
  </div>
</div>
`;

class SnippetExecuteActions {
  constructor(params) {
    this.disposals = [];
    this.stopping = ko.observable(false);
    this.snippet = params.snippet;
    this.status = ko.observable(EXECUTION_STATUS.ready);
    const updateSub = huePubSub.subscribe('hue.executor.updated', executorUpdate => {
      if (this.snippet.executor() === executorUpdate.executor) {
        this.status(executorUpdate.executable.status);
      }
    });
    this.disposals.push(() => {
      updateSub.remove();
    });
  }

  async stop() {
    if (this.stopping()) {
      return;
    }
    if (this.snippet.executor()) {
      this.stopping(true);
      await this.snippet.executor().cancel();
      this.stopping(false);
    }
  }

  execute() {
    this.snippet.execute();
  }

  dispose() {
    while (this.disposals.length) {
      this.disposals.pop()();
    }
  }
}

componentUtils.registerComponent(NAME, SnippetExecuteActions, TEMPLATE);
