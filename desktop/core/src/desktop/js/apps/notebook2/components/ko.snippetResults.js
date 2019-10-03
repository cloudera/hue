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
import DisposableComponent from 'ko/components/DisposableComponent';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';

import 'apps/notebook2/components/resultChart/ko.resultChart';
import 'apps/notebook2/components/resultGrid/ko.resultGrid';
import { REDRAW_FIXED_HEADERS_EVENT } from 'apps/notebook2/components/resultGrid/ko.resultGrid';
import { REDRAW_CHART_EVENT } from 'apps/notebook2/components/resultChart/ko.resultChart';

export const NAME = 'snippet-results';

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
  <div class="result-actions">
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
  
  <div class="result-body">
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
      <div data-bind="visible: showGrid" style="display: none; position: relative;">
        <!-- ko component: { 
          name: 'result-grid',
          params: {
            data: data,
            editorMode: editorMode,
            fetchResult: fetchResult,
            hasMore: hasMore,
            isPresentationMode: isPresentationMode,
            isResultFullScreenMode: isResultFullScreenMode,
            meta: meta,
            resultsKlass: resultsKlass,
            status: status
          }
        } --><!-- /ko -->
      </div>
      <div data-bind="visible: showChart" style="display: none; position: relative;">
        <!-- ko component: {
          name: 'result-chart',
          params: {
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
    </div>
  </div>
</div>
`;

class SnippetResults extends DisposableComponent {
  constructor(params, element) {
    super();
    this.element = element;

    this.type = params.type; // result
    this.hasSomeResults = params.hasSomeResults; // result
    this.images = params.images; // result
    this.data = params.data; // result
    this.meta = params.meta; // result

    // Grid specific
    this.editorMode = params.editorMode;
    this.fetchResult = params.fetchResult;
    this.hasMore = params.hasMore;
    this.isPresentationMode = params.isPresentationMode;
    this.isResultFullScreenMode = params.isResultFullScreenMode;
    this.resultsKlass = params.resultsKlass;
    this.status = params.status;

    // Chart specific
    this.id = params.id;

    this.showGrid = ko.observable(true); // TODO: Should be persisted
    this.showChart = ko.observable(false); // TODO: Should be persisted

    this.trackKoSub(
      this.showChart.subscribe(val => {
        if (val) {
          this.showGrid(false);
          huePubSub.publish(REDRAW_CHART_EVENT);
          huePubSub.publish('editor.chart.shown', this);
        }
      })
    );

    this.trackKoSub(
      this.showGrid.subscribe(val => {
        if (val) {
          this.showChart(false);
          huePubSub.publish('editor.grid.shown', this);
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
          huePubSub.publish('table.extender.redraw');
        }
      })
    );

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
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) => new SnippetResults(params, componentInfo.element)
  },
  TEMPLATE
);
