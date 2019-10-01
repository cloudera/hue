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

import componentUtils from 'ko/components/componentUtils';
import DisposableComponent from 'ko/components/DisposableComponent';
import I18n from 'utils/i18n';

import 'apps/notebook2/components/resultChart/ko.resultChart';
import 'apps/notebook2/components/resultGrid/ko.resultGrid';

export const NAME = 'snippet-results';

// prettier-ignore
const TEMPLATE = `
<div class="snippet-row">
  <div class="result-left-bar">
    <!-- ko if: type() === 'table' && hasSomeResults() -->
    <div class="snippet-actions" style="opacity:1">
      <div style="margin-top:25px;">
        <a class="snippet-side-btn" href="javascript: void(0)" data-bind="
            click: function() { showGrid(true); huePubSub.publish('redraw.fixed.headers'); huePubSub.publish('table.extender.redraw'); },
            css: { 'active': showGrid }
          " title="${ I18n('Grid') }">
          <i class="fa fa-fw fa-th"></i>
        </a>
      </div>

      <div class="dropdown">
        <a class="snippet-side-btn" style="padding-right:0" href="javascript: void(0)" data-bind="css: { 'active': showChart }, click: function() { showChart(true); }" >
          <i class="hcha fa-fw hcha-bar-chart" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.BARCHART" title="${ I18n('Bars') }"></i>
          <i class="hcha fa-fw hcha-timeline-chart" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.TIMELINECHART" title="${ I18n('Time') }"></i>
          <i class="hcha fa-fw hcha-pie-chart" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.PIECHART" title="${ I18n('Pie') }"></i>
          <i class="fa fa-fw fa-dot-circle-o" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.SCATTERCHART" title="${ I18n('Scatter') }"></i>
          <i class="fa fa-fw fa-map-marker" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.MAP" title="${ I18n('Marker Map') }"></i>
          <i class="hcha fa-fw hcha-map-chart" data-bind="visible: chartType() === window.HUE_CHARTS.TYPES.GRADIENTMAP" title="${ I18n('Gradient Map') }"></i>
        </a>
        <a class="dropdown-toggle snippet-side-btn" style="padding:0" data-toggle="dropdown" href="javascript: void(0)" data-bind="css: { 'active': showChart }">
          <i class="fa fa-caret-down"></i>
        </a>

        <ul class="dropdown-menu less-padding">
          <li>
            <a href="javascript:void(0)" data-bind="css: { 'active': chartType() === window.HUE_CHARTS.TYPES.BARCHART }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.BARCHART); }">
              <i class="hcha hcha-bar-chart"></i> ${ I18n('Bars') }
            </a>
          </li>
          <li data-bind="visible: cleanedDateTimeMeta().length > 0">
            <a href="javascript:void(0)" data-bind="css: { 'active': chartType() === window.HUE_CHARTS.TYPES.TIMELINECHART }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.TIMELINECHART); }">
              <i class="hcha hcha-timeline-chart"></i> ${ I18n('Time') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="css: { 'active': chartType() === window.HUE_CHARTS.TYPES.PIECHART }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.PIECHART); }">
              <i class="hcha hcha-pie-chart"></i> ${ I18n('Pie') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="css: { 'active': chartType() === window.HUE_CHARTS.TYPES.SCATTERCHART }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.SCATTERCHART); }">
              <i class="fa fa-fw fa-dot-circle-o chart-icon"></i> ${ I18n('Scatter') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="css: { 'active': chartType() === window.HUE_CHARTS.TYPES.MAP }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.MAP); }">
              <i class="fa fa-fw fa-map-marker chart-icon"></i> ${ I18n('Marker Map') }
            </a>
          </li>
          <li>
            <a href="javascript:void(0)" data-bind="css: {' active': chartType() === window.HUE_CHARTS.TYPES.GRADIENTMAP }, click: function() { showChart(true); chartType(window.HUE_CHARTS.TYPES.GRADIENTMAP); }">
              <i class="hcha hcha-map-chart"></i> ${ I18n('Gradient Map') }
            </a>
          </li>
        </ul>
      </div>

      <div>
        <a class="snippet-side-btn" href="javascript:void(0)" data-bind="
            toggle: isResultSettingsVisible,
            publish: 'chart.hard.reset',
            css: { 'blue' : isResultSettingsVisible }
          " title="${ I18n('Columns') }">
          <!-- ko if: isResultSettingsVisible() -->
          <i class="fa fa-fw fa-chevron-left"></i>
          <!-- /ko -->
          <!-- ko ifnot: isResultSettingsVisible() -->
          <i class="fa fa-fw fa-columns"></i>
          <!-- /ko -->
        </a>
      </div>

      <!-- ko if: false && window.ENABLE_DOWNLOAD -->
        <div data-bind="
            component: {
              name: 'downloadSnippetResults',
              params: {
                gridSideBtn: false,
                snippet: $data,
                notebook: $parent 
              } 
            }
          " style="display:inline-block;"></div>
      <!-- /ko -->
    </div>
    <!-- /ko -->
  </div>
  <div class="result-body">
    <div data-bind="visible: type() !== 'table'" style="display:none; max-height: 400px; margin: 10px 0; overflow-y: auto">
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

    <div class="table-results" data-bind="visible: type() === 'table'" style="display: none; max-height: 400px; min-height: 290px;">
      <div data-bind="visible: showGrid" style="display: none;">
        <!-- ko component: { name: 'result-grid', params: {
          autocompleteFromEntries: autocompleteFromEntries,
          clickFilteredMetaCheck: clickFilteredMetaCheck,
          data: data,
          editorMode: editorMode,
          fetchResult: fetchResult,
          filteredColumnCount: filteredColumnCount,
          filteredMeta: filteredMeta,
          filteredMetaChecked: filteredMetaChecked,
          hasMore: hasMore,
          isMetaFilterVisible: isMetaFilterVisible,
          isPresentationMode: isPresentationMode,
          isResultFullScreenMode: isResultFullScreenMode,
          isResultSettingsVisible: isResultSettingsVisible,
          meta: meta,
          metaFilter: metaFilter,
          resultsKlass: resultsKlass,
          scrollToResultColumn: scrollToResultColumn,
          status: status,
          toggleResultColumn: toggleResultColumn,
        } } --><!-- /ko -->
      </div>
      <div data-bind="visible: showChart" style="display: none;">
        <!-- ko component: { name: 'result-chart', params: {
          chartLimit: chartLimit,
          chartMapHeat: chartMapHeat,
          chartMapLabel: chartMapLabel,
          chartMapType: chartMapType,
          chartScatterGroup: chartScatterGroup,
          chartScatterSize: chartScatterSize,
          chartScope: chartScope,
          chartSorting: chartSorting,
          chartTimelineType: chartTimelineType,
          chartType: chartType,
          chartX: chartX,
          chartXPivot: chartXPivot,
          chartYMulti: chartYMulti,
          chartYSingle: chartYSingle,
          cleanedDateTimeMeta: cleanedDateTimeMeta,
          cleanedMeta: cleanedMeta,
          cleanedNumericMeta: cleanedNumericMeta,
          data: data,
          id: id,
          isResultSettingsVisible: isResultSettingsVisible,
          meta: meta
        } } --><!-- /ko -->
      </div>
    </div>
  </div>
</div>
`;

class SnippetResults extends DisposableComponent {
  constructor(params, element) {
    super();
    this.element = element;

    // For this and possibly chart and grid
    this.chartType = params.chartType;
    this.type = params.type; // result
    this.hasSomeResults = params.hasSomeResults; // result
    this.images = params.images; // result
    this.showGrid = params.showGrid;
    this.showChart = params.showChart;
    this.cleanedDateTimeMeta = params.cleanedDateTimeMeta;
    this.isResultSettingsVisible = params.isResultSettingsVisible;
    this.data = params.data; // result
    this.meta = params.meta; // result

    // Grid specific
    this.autocompleteFromEntries = params.autocompleteFromEntries; // result
    this.clickFilteredMetaCheck = params.clickFilteredMetaCheck; // result
    this.editorMode = params.editorMode;
    this.fetchResult = params.fetchResult;
    this.filteredColumnCount = params.filteredColumnCount; // result
    this.filteredMeta = params.filteredMeta; // result
    this.filteredMetaChecked = params.filteredMetaChecked; // result
    this.hasMore = params.hasMore;
    this.isMetaFilterVisible = params.isMetaFilterVisible; // result
    this.isPresentationMode = params.isPresentationMode;
    this.isResultFullScreenMode = params.isResultFullScreenMode;
    this.metaFilter = params.metaFilter; // result
    this.resultsKlass = params.resultsKlass;
    this.scrollToResultColumn = params.scrollToResultColumn;
    this.status = params.status;
    this.toggleResultColumn = params.toggleResultColumn;

    // Chart specific
    this.chartLimit = params.chartLimit;
    this.chartMapHeat = params.chartMapHeat;
    this.chartMapLabel = params.chartMapLabel;
    this.chartMapType = params.chartMapType;
    this.chartScatterGroup = params.chartScatterGroup;
    this.chartScatterSize = params.chartScatterSize;
    this.chartScope = params.chartScope;
    this.chartSorting = params.chartSorting;
    this.chartTimelineType = params.chartTimelineType;
    this.chartX = params.chartX;
    this.chartXPivot = params.chartXPivot;
    this.chartYMulti = params.chartYMulti;
    this.chartYSingle = params.chartYSingle;
    this.cleanedMeta = params.cleanedMeta;
    this.cleanedNumericMeta = params.cleanedNumericMeta;
    this.id = params.id;
  }
}

componentUtils.registerComponent(
  NAME,
  {
    createViewModel: (params, componentInfo) => new SnippetResults(params, componentInfo.element)
  },
  TEMPLATE
);
