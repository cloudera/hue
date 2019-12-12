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

import 'apps/notebook2/components/resultChart/ko.resultChart';
import 'apps/notebook2/components/resultGrid/ko.resultGrid';
import { REDRAW_FIXED_HEADERS_EVENT } from 'apps/notebook2/events';
import { REDRAW_CHART_EVENT } from 'apps/notebook2/events';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import { RESULT_TYPE, RESULT_UPDATED_EVENT } from 'apps/notebook2/execution/executionResult';
import { attachTracker } from 'apps/notebook2/components/executableStateHandler';
import { defer } from 'utils/hueUtils';
import { CURRENT_QUERY_TAB_SWITCHED_EVENT } from 'apps/notebook2/snippet';

export const NAME = 'snippet-results';

const META_TYPE_TO_CSS = {
  TINYINT_TYPE: 'sort-numeric',
  SMALLINT_TYPE: 'sort-numeric',
  INT_TYPE: 'sort-numeric',
  BIGINT_TYPE: 'sort-numeric',
  FLOAT_TYPE: 'sort-numeric',
  DOUBLE_TYPE: 'sort-numeric',
  DECIMAL_TYPE: 'sort-numeric',
  TIMESTAMP_TYPE: 'sort-date',
  DATE_TYPE: 'sort-date',
  DATETIME_TYPE: 'sort-date'
};

const isNumericColumn = type =>
  ['tinyint', 'smallint', 'int', 'bigint', 'float', 'double', 'decimal', 'real'].indexOf(type) !==
  -1;

const isDateTimeColumn = type => ['timestamp', 'date', 'datetime'].indexOf(type) !== -1;

const isComplexColumn = type => ['array', 'map', 'struct'].indexOf(type) !== -1;

const isStringColumn = type =>
  !isNumericColumn(type) && !isDateTimeColumn(type) && !isComplexColumn(type);

// prettier-ignore
const TEMPLATE = `
<div class="snippet-row">
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
    <div class="table-results" data-bind="visible: type() === 'table'" style="display: none;">
      <div data-bind="visible: !executing() && hasData() && showGrid()" style="display: none; position: relative;">
        <!-- ko component: { 
          name: 'result-grid',
          params: {
            activeExecutable: activeExecutable,
            data: data,
            lastFetchedRows: lastFetchedRows,
            editorMode: editorMode,
            fetchResult: fetchResult.bind($data),
            hasMore: hasMore,
            isPresentationMode: isPresentationMode,
            isResultFullScreenMode: isResultFullScreenMode,
            meta: meta,
            resultsKlass: resultsKlass,
            status: status
          }
        } --><!-- /ko -->
      </div>
      <div data-bind="visible: !executing() && hasData() && showChart()" style="display: none; position: relative;">
        <!-- ko component: {
          name: 'result-chart',
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

    this.executing = ko.pureComputed(() => this.status() === EXECUTION_STATUS.running);

    this.hasData = ko.pureComputed(() => this.data().length);

    const trackedObservables = {
      showGrid: true,
      showChart: false
    };

    this.showGrid = ko.observable(trackedObservables.showGrid);
    this.showChart = ko.observable(trackedObservables.showChart);

    attachTracker(this.activeExecutable, NAME, this, trackedObservables);

    this.cleanedMeta = ko.pureComputed(() => this.meta().filter(item => item.name !== ''));

    this.cleanedDateTimeMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isDateTimeColumn(item.type))
    );

    self.cleanedStringMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isStringColumn(item.type))
    );

    this.cleanedNumericMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isNumericColumn(item.type))
    );

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
    this.subscribe(RESULT_UPDATED_EVENT, executionResult => {
      if (this.activeExecutable() === executionResult.executable) {
        const refresh = lastRenderedResult !== executionResult;
        this.updateFromExecutionResult(executionResult, refresh);
        lastRenderedResult = executionResult;
      }
    });

    this.subscribe(this.activeExecutable, executable => {
      if (executable && executable.result) {
        if (executable !== lastRenderedResult) {
          this.updateFromExecutionResult(executable.result, true);
          lastRenderedResult = executable;
        }
      } else {
        this.resetResultData();
      }
    });
  }

  resetResultData() {
    this.images([]);
    this.lastFetchedRows([]);
    this.data([]);
    this.meta([]);
    this.hasMore(false);
    this.type(RESULT_TYPE.TABLE);
  }

  updateFromExecutionResult(executionResult, refresh) {
    if (refresh) {
      this.resetResultData();
    }

    if (executionResult) {
      this.fetchedOnce(executionResult.fetchedOnce);
      this.hasMore(executionResult.hasMore);
      this.type(executionResult.type);

      if (!this.meta().length && executionResult.meta.length) {
        this.meta(
          executionResult.meta.map((item, index) => ({
            name: item.name,
            type: item.type.replace(/_type/i, '').toLowerCase(),
            comment: item.comment,
            cssClass: META_TYPE_TO_CSS[item.type] || 'sort-string',
            checked: ko.observable(true),
            originalIndex: index
          }))
        );
      }

      if (executionResult.lastRows.length) {
        this.data.push(...executionResult.lastRows);
      }
      this.lastFetchedRows(executionResult.lastRows);
    }
  }

  updateFromExecutable(executable) {
    this.status(executable.status);
    this.hasResultSet(executable.handle.has_result_set);
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
