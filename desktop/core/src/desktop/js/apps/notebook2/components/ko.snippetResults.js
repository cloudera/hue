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

import { RESULT_CHART_COMPONENT } from 'apps/notebook2/components/resultChart/ko.resultChart';
import { RESULT_GRID_COMPONENT } from 'apps/notebook2/components/resultGrid/ko.resultGrid';
import { REDRAW_FIXED_HEADERS_EVENT } from 'apps/notebook2/events';
import { REDRAW_CHART_EVENT } from 'apps/notebook2/events';
import { EXECUTABLE_UPDATED_EVENT, ExecutionStatus } from 'apps/notebook2/execution/executable';
import { RESULT_TYPE, RESULT_UPDATED_EVENT } from 'apps/notebook2/execution/executionResult';
import { attachTracker } from 'apps/notebook2/components/executableStateHandler';
import { defer } from 'utils/hueUtils';
import { CURRENT_QUERY_TAB_SWITCHED_EVENT } from 'apps/notebook2/snippet';

export const NAME = 'snippet-results';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-row" data-bind="visible: visible" style="display: none;">
  <div class="snippet-tab-actions">
    <div class="btn-group">
      <button class="btn btn-editor btn-mini disable-feedback" data-bind="toggle: showGrid, css: { 'active': showGrid }"><i class="fa fa-fw fa-th"></i> ${ I18n('Grid') }</button>
      <button class="btn btn-editor btn-mini disable-feedback" data-bind="toggle: showChart, css: { 'active': showChart }"><i class="hcha fa-fw hcha-bar-chart"></i> ${ I18n('Chart') }</button>
    </div>
    <div class="btn-group pull-right">
      <button class="btn btn-editor btn-mini disable-feedback" data-bind="toggle: isResultFullScreenMode">
        <!-- ko if: isResultFullScreenMode -->
        <i class="fa fa-compress"></i> ${ I18n('Collapse') }
        <!-- /ko -->
        <!-- ko ifnot: isResultFullScreenMode -->
        <i class="fa fa-expand"></i> ${ I18n('Expand') }
        <!-- /ko -->
      </button>
    </div>
  </div>

  <div class="snippet-tab-body">
    <div data-bind="visible: type() !== 'table'" style="display:none; margin: 10px 0; overflow-y: auto">
      <!-- ko if: data().length && data()[0][1] != "" -->
      <pre data-bind="text: data()[0][1]" class="no-margin-bottom"></pre>
      <!-- /ko -->
      <!-- ko ifnot: data().length && data()[0][1] != "" -->
      <pre class="no-margin-bottom"><i class="fa fa-check muted"></i> ${ I18n('Done.') }</pre>
      <!-- /ko -->
      <!-- ko if: images().length -->
      <ul class="unstyled results-images" data-bind="foreach: images">
        <li>
          <img data-bind="attr: {'src': 'data:image/png;base64,' + $data}" class="margin-bottom-10"  alt="${ I18n('Result image') }"/>
        </li>
      </ul>
      <!-- /ko -->
    </div>
    <div class="table-results" data-bind="visible: type() === 'table', css: { 'table-results-notebook': notebookMode }" style="display: none;">
      <div data-bind="visible: !executing() && hasData() && showGrid()" style="display: none; position: relative;">
        <execution-results-ko-bridge data-bind="vueKoProps: {
          executableObservable: activeExecutable
        }"></execution-results-ko-bridge>
      </div>
      <div data-bind="visible: !executing() && hasData() && showChart()" style="display: none; position: relative;">
        <!-- ko component: {
          name: '${ RESULT_CHART_COMPONENT }',
          params: {
            activeExecutable: activeExecutable,
            cleanedMeta: cleanedMeta,
            cleanedDateTimeMeta: cleanedDateTimeMeta,
            cleanedNumericMeta: cleanedNumericMeta,
            cleanedStringMeta: cleanedStringMeta,
            data: data,
            id: id,
            meta: meta,
            showChart: showChart
          }
        } --><!-- /ko -->
      </div>
      <div data-bind="visible: !executing() && !hasData() && streaming()" style="display: none;">
        <h1 class="empty">${ I18n('Waiting for streaming data...') }</h1>
      </div>
      <div data-bind="visible: !executing() && !hasData() && !hasResultSet() && status() === 'available' && fetchedOnce()" style="display: none;">
        <h1 class="empty">${ I18n('Success.') }</h1>
      </div>
      <div data-bind="visible: !executing() && !hasData() && hasResultSet() && status() === 'available' && fetchedOnce()" style="display: none;">
        <h1 class="empty">${ I18n('Empty result.') }</h1>
      </div>
      <div data-bind="visible: !executing() && !hasData() && status() === 'expired'" style="display: none;">
        <h1 class="empty">${ I18n('Results have expired, rerun the query if needed.') }</h1>
      </div>
      <div data-bind="visible: executing" style="display: none;">
        <h1 class="empty"><i class="fa fa-spinner fa-spin"></i> ${ I18n('Executing...') }</h1>
      </div>
      <ul id="wsResult">
      </ul>
    </div>
  </div>
</div>
`;

class SnippetResults extends DisposableComponent {
  constructor(params, element) {
    super();
    this.element = element;

    this.activeExecutable = params.activeExecutable;

    this.editorMode = params.editorMode;
    this.isPresentationMode = params.isPresentationMode;
    this.isResultFullScreenMode = params.isResultFullScreenMode;
    this.resultsKlass = params.resultsKlass;
    this.id = params.id; // TODO: Get rid of

    this.status = ko.observable();
    this.type = ko.observable(RESULT_TYPE.TABLE);
    this.meta = ko.observableArray();
    this.streaming = ko.observable();
    this.data = ko.observableArray();
    this.lastFetchedRows = ko.observableArray();
    this.images = ko.observableArray();
    this.hasMore = ko.observable();
    this.hasResultSet = ko.observable();
    this.fetchedOnce = ko.observable(false);

    this.subscribe(CURRENT_QUERY_TAB_SWITCHED_EVENT, queryTab => {
      if (queryTab === 'queryResults') {
        defer(() => {
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
        });
      }
    });

    this.executing = ko.pureComputed(() => this.status() === ExecutionStatus.running);

    this.hasData = ko.pureComputed(() => this.data().length);

    this.notebookMode = ko.pureComputed(() => !this.editorMode() || this.isPresentationMode());

    this.visible = ko.pureComputed(
      () => !this.notebookMode() || this.executing() || this.hasResultSet()
    );

    const trackedObservables = {
      showGrid: true,
      showChart: false
    };

    this.showGrid = ko.observable(trackedObservables.showGrid);
    this.showChart = ko.observable(trackedObservables.showChart);

    attachTracker(this.activeExecutable, NAME, this, trackedObservables);

    this.cleanedMeta = ko.observableArray();
    this.cleanedDateTimeMeta = ko.observableArray();
    this.cleanedStringMeta = ko.observableArray();
    this.cleanedNumericMeta = ko.observableArray();

    this.subscribe(this.showChart, val => {
      if (val) {
        this.showGrid(false);
        huePubSub.publish(REDRAW_CHART_EVENT);
        huePubSub.publish('editor.chart.shown', this);
      }
    });

    this.subscribe(this.showGrid, val => {
      if (val) {
        this.showChart(false);
        huePubSub.publish('editor.grid.shown', this);
        defer(() => huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT));
        huePubSub.publish('table.extender.redraw');
      }
    });

    this.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.updateFromExecutable(executable);
      }
    });

    let lastRenderedResult = undefined;
    const handleResultChange = () => {
      if (this.activeExecutable() && this.activeExecutable().result) {
        const refresh = lastRenderedResult !== this.activeExecutable().result;
        this.updateFromExecutionResult(this.activeExecutable().result, refresh);
        lastRenderedResult = this.activeExecutable().result;
      } else {
        this.resetResultData();
      }
    };

    this.subscribe(RESULT_UPDATED_EVENT, executionResult => {
      if (this.activeExecutable() === executionResult.executable) {
        handleResultChange();
      }
    });

    this.subscribe(this.activeExecutable, handleResultChange);
  }

  resetResultData() {
    this.images([]);
    this.lastFetchedRows([]);
    this.data([]);
    this.meta([]);
    this.streaming(false);
    this.cleanedMeta([]);
    this.cleanedDateTimeMeta([]);
    this.cleanedNumericMeta([]);
    this.cleanedStringMeta([]);
    this.hasMore(false);
    this.type(RESULT_TYPE.TABLE);
    // eslint-disable-next-line no-undef
    $('#wsResult').empty();
  }

  updateFromExecutionResult(executionResult, refresh) {
    if (refresh) {
      this.resetResultData();
    }

    if (executionResult) {
      this.fetchedOnce(executionResult.fetchedOnce);
      this.hasMore(executionResult.hasMore);
      this.type(executionResult.type);
      this.streaming(executionResult.streaming);

      if (!this.meta().length && executionResult.meta.length) {
        this.meta(executionResult.koEnrichedMeta);
        this.cleanedMeta(executionResult.cleanedMeta);
        this.cleanedDateTimeMeta(executionResult.cleanedDateTimeMeta);
        this.cleanedStringMeta(executionResult.cleanedStringMeta);
        this.cleanedNumericMeta(executionResult.cleanedNumericMeta);
      }

      if (refresh) {
        this.data(executionResult.rows.concat());
      } else if (
        executionResult.lastRows.length &&
        this.data().length !== executionResult.rows.length
      ) {
        this.data.push(...executionResult.lastRows);
      }
      this.lastFetchedRows(executionResult.lastRows);
    }
  }

  updateFromExecutable(executable) {
    this.status(executable.status);
    this.hasResultSet(executable.handle && executable.handle.has_result_set);
    if (!this.hasResultSet) {
      this.resetResultData();
    }
  }

  fetchResult() {
    if (this.activeExecutable() && this.activeExecutable().result) {
      this.activeExecutable().result.fetchRows({ rows: 100 });
    }
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) => new SnippetResults(params, componentInfo.element)
  },
  TEMPLATE
);
