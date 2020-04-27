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
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

const TEMPLATE = `
  <div class="assist-inner-panel">
    <div class="assist-flex-panel">
      <!-- ko if: selectedNotebook() && selectedNotebook().isBatchable() -->
      <!-- ko with: selectedNotebook() -->
      <div class="tab-pane" id="scheduleTab">
        <!-- ko ifnot: isSaved() && ! isHistory() -->
        ${I18n('Query needs to be saved.')}
        <!-- /ko -->
        <!-- ko if: isSaved() && ! isHistory() -->
          <!-- ko if: schedulerViewModelIsLoaded() && schedulerViewModel.coordinator.isDirty() -->
          <a data-bind="click: saveScheduler" href="javascript: void(0);">${I18n(
            'Save changes'
          )}</a>
          <!-- /ko -->
          <!-- ko if: schedulerViewModelIsLoaded() && ! schedulerViewModel.coordinator.isDirty() && (! viewSchedulerId() || isSchedulerJobRunning() == false )-->
          <a data-bind="click: showSubmitPopup" href="javascript: void(0);">${I18n('Start')}</a>
          <!-- /ko -->
          <!-- ko if: schedulerViewModelIsLoaded() && viewSchedulerId()-->
          <a data-bind="click: function() { huePubSub.publish('show.jobs.panel', {id: viewSchedulerId(), interface: 'schedules'}) }, clickBubble: false" href="javascript: void(0);">
            ${I18n('View')}
          </a>
          <!-- ko if: isSchedulerJobRunning() -->
            ${I18n('Running')}
          <!-- /ko -->
          <!-- ko if: isSchedulerJobRunning() == false -->
            ${I18n('Stopped')}
          <!-- /ko -->
        <!-- /ko -->
        <!-- /ko -->
        <br>
        <br>
        <div id="schedulerEditor"></div>
      </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </div>
`;

class AssistSchedulePanel {
  constructor() {
    this.selectedNotebook = ko.observable();

    // TODO: Move all the scheduler logic out of the notebook to here.

    this.selectedNotebook.subscribe(notebook => {
      // Happening 4 times for each notebook loaded
      if (
        notebook &&
        notebook.schedulerViewModel == null &&
        notebook.isSaved() &&
        !notebook.isHistory()
      ) {
        notebook.loadScheduler();
        if (notebook.viewSchedulerId()) {
          huePubSub.publish('check.schedules.browser');
        }
      }
    });

    huePubSub.subscribe('jobbrowser.schedule.data', jobs => {
      if (this.selectedNotebook() && this.selectedNotebook().viewSchedulerId()) {
        const job = jobs.filter(job => this.selectedNotebook().viewSchedulerId() === job.id);
        this.selectedNotebook().isSchedulerJobRunning(
          job.length > 0 && job[0].apiStatus === 'RUNNING'
        );
      }
    });

    // Hue 3
    huePubSub.subscribe('set.selected.notebook', this.selectedNotebook);

    huePubSub.subscribe('selected.notebook.changed', this.selectedNotebook);
    huePubSub.publish('get.selected.notebook');

    // Hue 4
    huePubSub.subscribe('set.current.app.view.model', viewModel => {
      if (viewModel.selectedNotebook) {
        if (viewModel.selectedNotebook()) {
          this.selectedNotebook(viewModel.selectedNotebook());
        } else {
          const subscription = viewModel.selectedNotebook.subscribe(notebook => {
            this.selectedNotebook(notebook);
            subscription.dispose();
          });
        }
      } else {
        this.selectedNotebook(null);
      }
    });
  }
}

componentUtils.registerStaticComponent('assist-schedule-panel', AssistSchedulePanel, TEMPLATE);
