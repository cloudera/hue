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

import $ from 'jquery';
import * as ko from 'knockout';

import 'ko/bindings/ko.publish';

import componentUtils from 'ko/components/componentUtils';
import { EXECUTABLE_UPDATED_EVENT, ExecutionStatus } from 'apps/editor/execution/executable';
import DisposableComponent from 'ko/components/DisposableComponent';
import { sleep } from 'utils/hueUtils';

export const NAME = 'executable-progress-bar';

const TEMPLATE = `
<div class="progress-snippet progress" data-test="${NAME}" data-bind="css: progressClass" style="background-color: #FFF;">
  <div class="bar" data-test="bar" data-bind="style: { 'width': progressWidth }"></div>
</div>
`;

class ExecutableProgressBar extends DisposableComponent {
  constructor(params, element) {
    super();
    this.activeExecutable = params.activeExecutable;

    this.status = ko.observable();
    this.progress = ko.observable(0);

    this.progressClass = ko.pureComputed(() => {
      if (this.status() === ExecutionStatus.failed) {
        return 'progress-danger';
      }
      if (
        this.progress() === 0 &&
        (this.status() === ExecutionStatus.running ||
          this.status() === ExecutionStatus.streaming ||
          this.status() === ExecutionStatus.starting)
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
      if (this.status() === ExecutionStatus.failed) {
        return '100%';
      }
      return Math.max(2, this.progress()) + '%';
    });

    this.subscribe(EXECUTABLE_UPDATED_EVENT, async executable => {
      if (this.activeExecutable() === executable) {
        this.status(executable.status);
        this.progress(executable.progress);
        if (executable.progress === 100) {
          await sleep(2000);
          $(element).parent().find('.progress-snippet').animate(
            {
              height: '0'
            },
            100
          );
        } else {
          $(element).parent().find('.progress-snippet').css('height', '');
        }
      }
    });

    this.subscribe(this.activeExecutable, executable => {
      this.status(executable.status);
      this.progress(executable.progress);
    });
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) =>
      new ExecutableProgressBar(params, componentInfo.element)
  },
  TEMPLATE
);
