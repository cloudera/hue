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

import 'ko/bindings/ko.publish';

import componentUtils from 'ko/components/componentUtils';
import { EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import huePubSub from 'utils/huePubSub';
import { EXECUTOR_UPDATED_EVENT } from 'apps/notebook2/execution/executor';
import DisposableComponent from 'ko/components/DisposableComponent';

export const NAME = 'executable-progress-bar';

const TEMPLATE = `
<div class="progress-snippet progress" data-test="${NAME}" data-bind="css: progressClass" style="background-color: #FFF;">
  <div class="bar" data-test="bar" data-bind="style: { 'width': progressWidth }"></div>
</div>
`;

class ExecutableProgressBar extends DisposableComponent {
  constructor(params) {
    super();
    this.snippet = params.snippet;

    this.status = ko.observable();
    this.progress = ko.observable(0);

    this.progressClass = ko.pureComputed(() => {
      if (this.status() === EXECUTION_STATUS.failed) {
        return 'progress-danger';
      }
      if (
        this.progress() === 0 &&
        (this.status() === EXECUTION_STATUS.running || this.status() === EXECUTION_STATUS.starting)
      ) {
        return 'progress-starting';
      }
      if (0 < this.progress() && this.progress() < 100) {
        return 'progress-running';
      }
      if (this.progress() === 100) {
        return 'progress-success';
      }
    });

    this.progressWidth = ko.pureComputed(() => {
      if (this.status() === EXECUTION_STATUS.failed) {
        return '100%';
      }
      return Math.max(2, this.progress()) + '%';
    });

    const updateSub = huePubSub.subscribe(EXECUTOR_UPDATED_EVENT, executorUpdate => {
      if (this.snippet.executor === executorUpdate.executor) {
        this.status(executorUpdate.executable.status);
        this.progress(executorUpdate.executable.progress);
      }
    });

    this.addDisposalCallback(() => {
      updateSub.remove();
    });
  }
}

componentUtils.registerComponent(NAME, ExecutableProgressBar, TEMPLATE);
