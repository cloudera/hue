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
import hueAnalytics from 'utils/hueAnalytics';
import I18n from 'utils/i18n';
import {
  leafletMapChartTransformer,
  mapChartTransformer,
  multiSerieChartTransformer,
  pieChartTransformer,
  scatterChartTransformer,
  timelineChartTransformer
} from './chartTransformers';
import $ from 'jquery';
import { UUID } from 'utils/hueUtils';
import { REDRAW_CHART_EVENT } from 'apps/editor/events';
import { attachTracker } from 'apps/editor/components/executableStateHandler';

export const RESULT_CHART_COMPONENT = 'result-chart';

const TYPES = window.HUE_CHARTS.TYPES;

export const CHART_MAP_TYPE = {
  HEAT: 'heat',
  MARKER: 'marker'
};

export const CHART_SCOPE = {
  AUS: 'aus',
  BRA: 'bra',
  CAN: 'can',
  CHN: 'chn',
  DEU: 'deu',
  EUROPE: 'europe',
  FRA: 'fra',
  GBR: 'gbr',
  ITA: 'ita',
  JPN: 'jpn',
  USA: 'usa',
  WORLD: 'world'
};

export const CHART_SORTING = {
  ASC: 'asc',
  DESC: 'desc',
  NONE: 'none'
};

export const CHART_TIMELINE_TYPE = {
  BAR: 'bar',
  LINE: 'line'
};

// prettier-ignore
const TEMPLATE = `
<div class="snippet-tab-actions-append">
  <div class="btn-group">
    <button class="btn btn-mini btn-editor dropdown-toggle" data-toggle="dropdown">
      <!-- ko if: isBarChart -->
      <i class="hcha fa-fw hcha-bar-chart"></i> ${ I18n('Bar Chart') }
      <!-- /ko -->
      <!-- ko if: isTimelineChart -->
      <i class="hcha fa-fw hcha-timeline-chart"></i> ${ I18n('Timeline Chart') }
      <!-- /ko -->
      <!-- ko if: isPieChart -->
      <i class="hcha fa-fw hcha-pie-chart"></i> ${ I18n('Pie Chart') }
      <!-- /ko -->
      <!-- ko if: isScatterChart -->
      <i class="fa fa-fw fa-dot-circle-o"></i> ${ I18n('Scatter Plot') }
      <!-- /ko -->
      <!-- ko if: isMapChart -->
      <i class="fa fa-fw fa-map-marker"></i> ${ I18n('Marker Map') }
      <!-- /ko -->
      <!-- ko if: isGradientMapChart -->
      <i class="hcha fa-fw hcha-map-chart"></i> ${ I18n('Gradient Map') }
      <!-- /ko -->
      <span class="caret"></span>
    </button>
    <ul class="dropdown-menu">
      <li>
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.BARCHART); }">
          <i class="hcha fa-fw hcha-bar-chart"></i> ${ I18n('Bar Chart') }
        </a>
      </li>
      <li data-bind="if: cleanedDateTimeMeta().length">
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.TIMELINECHART); }">
          <i class="hcha fa-fw hcha-timeline-chart"></i> ${ I18n('Timeline Chart') }
        </a>
      </li>
      <li>
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.PIECHART); }">
          <i class="hcha fa-fw hcha-pie-chart"></i> ${ I18n('Pie Chart') }
        </a>
      </li>
      <li>
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.SCATTERCHART); }">
          <i class="fa fa-fw fa-dot-circle-o"></i> ${ I18n('Scatter Plot') }
        </a>
      </li>
      <li>
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.MAP); }">
          <i class="fa fa-fw fa-map-marker"></i> ${ I18n('Marker Map') }
        </a>
      </li>
      <li>
        <a href="javascript:void(0);" data-bind="click: function() { chartType(window.HUE_CHARTS.TYPES.GRADIENTMAP); }">
          <i class="hcha fa-fw hcha-map-chart"></i> ${ I18n('Gradient Map') }
        </a>
      </li>
    </ul>
  </div>
  <div class="btn-group">
    <button class="btn btn-editor btn-mini disable-feedback" data-bind="toggle: chartSettingsVisible, css: { 'active' : chartSettingsVisible }">
      <i class="fa fa-cog"></i> ${ I18n('Settings') }
    </button>
  </div>
</div>

<div class="split-result-container">
  <div class="result-settings-panel" style="display: none;" data-bind="visible: chartSettingsVisible">
    <div>
      <!-- ko if: chartType -->
      <!-- ko if: isTimelineChart() || isBarChart() -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('type') }</li>
      </ul>
      <div>
        <select data-bind="
            selectedOptions: chartTimelineType,
            optionsCaption: '${ I18n('Choose a type...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a type...") }',
              update: chartTimelineType,
              dropdownAutoWidth: true
            }
          ">
          <option value="${ CHART_TIMELINE_TYPE.BAR }">${ I18n("Bars") }</option>
          <option value="${ CHART_TIMELINE_TYPE.LINE }">${ I18n("Lines") }</option>
        </select>
      </div>
      <!-- /ko -->

      <!-- ko if: isPieChart -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('value') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedNumericMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a column...") }',
              update: chartYSingle,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('legend') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a column...") }',
              update: chartX,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <!-- /ko -->

      <!-- ko ifnot: isPieChart -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li data-bind="visible: !isMapChart() && !isGradientMapChart()" class="nav-header">${ I18n('x-axis') }</li>
        <li data-bind="visible: isGradientMapChart" class="nav-header">${ I18n('region') }</li>
        <li data-bind="visible: isMapChart" class="nav-header">${ I18n('latitude') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: chartMetaOptions,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a column...") }',
              update: chartX,
              dropdownAutoWidth: true
            }
          "></select>
      </div>

      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li data-bind="visible: !isMapChart() && !isGradientMapChart()" class="nav-header">${ I18n('y-axis') }</li>
        <li data-bind="visible: isGradientMapChart" class="nav-header">${ I18n('value') }</li>
        <li data-bind="visible: isMapChart" class="nav-header">${ I18n('longitude') }</li>
      </ul>

      <div style="max-height: 220px" data-bind="
          delayedOverflow,
          visible: ((isBarChart() && !chartXPivot()) || isLineChart() || isTimelineChart())
        ">
        <ul class="unstyled" data-bind="foreach: cleanedNumericMeta" style="margin-bottom: 0">
          <li><label class="checkbox"><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></label></li>
        </ul>
      </div>
      <div class="input-medium" data-bind="visible: (isBarChart() && chartXPivot()) || isMapChart() || isGradientMapChart() || isScatterChart()">
        <select data-bind="
            options: isGradientMapChart() ? cleanedMeta : cleanedNumericMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a column...") }',
              update: chartYSingle,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <!-- /ko -->

      <ul class="nav nav-list" style="border: none; background-color: #FFF" data-bind="visible: isBarChart">
        <li class="nav-header">${ I18n('group') }</li>
      </ul>
      <div data-bind="visible: isBarChart">
        <select class="input-medium" data-bind="
            options: cleanedMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column to pivot...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n("Choose a column to pivot...") }',
              update: chartXPivot,
              dropdownAutoWidth: true
            }
          "></select>
      </div>

      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('limit') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
          options: chartLimits,
          optionsCaption: '${ I18n('Limit the number of results to...') }',
          select2: {
            width: '100%',
            placeholder: '${ I18n('Limit the number of results to...') }',
            update: chartLimit,
            dropdownAutoWidth: true
          }
        "></select>
      </div>

      <!-- ko if: isMapChart -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('type') }</li>
      </ul>
      <div>
        <select data-bind="
            selectedOptions: chartMapType,
            optionsCaption: '${ I18n('Choose a type...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a type...') }',
              update: chartMapType,
              dropdownAutoWidth: true
            }
          ">
          <option value="${ CHART_MAP_TYPE.MARKER }">${ I18n("Markers") }</option>
          <option value="${ CHART_MAP_TYPE.HEAT }">${ I18n("Heatmap") }</option>
        </select>
      </div>

      <!-- ko if: chartMapType() === '${ CHART_MAP_TYPE.MARKER }' -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('label') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a column...') }',
              update: chartMapLabel,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <!-- /ko -->

      <!-- ko if: chartMapType() === '${ CHART_MAP_TYPE.HEAT }' -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('intensity') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedNumericMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a column...') }',
              update: chartMapHeat,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <!-- /ko -->
      <!-- /ko -->

      <!-- ko if: isScatterChart -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('scatter size') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedNumericMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a column...') }',
              update: chartScatterSize,
              dropdownAutoWidth: true
            }
          "></select>
      </div>

      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('scatter group') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedMeta,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a column...') }',
              update: chartScatterGroup,
              dropdownAutoWidth: true
            }
          "></select>
      </div>
      <!-- /ko -->

      <!-- ko if: isGradientMapChart -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('scope') }</li>
      </ul>
      <div data-bind="visible: chartType() != ''">
        <select data-bind="
            selectedOptions: chartScope,
            optionsCaption: '${ I18n('Choose a scope...') }',
            select2: {
              width: '100%',
              placeholder: '${ I18n('Choose a scope...') }',
              update: chartScope,
              dropdownAutoWidth: true
            }
          ">
          <option value="${ CHART_SCOPE.WORLD }">${ I18n("World") }</option>
          <option value="${ CHART_SCOPE.EUROPE }">${ I18n("Europe") }</option>
          <option value="${ CHART_SCOPE.AUS }">${ I18n("Australia") }</option>
          <option value="${ CHART_SCOPE.BRA }">${ I18n("Brazil") }</option>
          <option value="${ CHART_SCOPE.CAN }">${ I18n("Canada") }</option>
          <option value="${ CHART_SCOPE.CHN }">${ I18n("China") }</option>
          <option value="${ CHART_SCOPE.FRA }">${ I18n("France") }</option>
          <option value="${ CHART_SCOPE.DEU }">${ I18n("Germany") }</option>
          <option value="${ CHART_SCOPE.ITA }">${ I18n("Italy") }</option>
          <option value="${ CHART_SCOPE.JPN }">${ I18n("Japan") }</option>
          <option value="${ CHART_SCOPE.GBR }">${ I18n("UK") }</option>
          <option value="${ CHART_SCOPE.USA }">${ I18n("USA") }</option>
        </select>
      </div>
      <!-- /ko -->

      <!-- ko ifnot: isMapChart() || isGradientMapChart() || isScatterChart()-->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('sorting') }</li>
      </ul>
      <div class="btn-group" data-toggle="buttons-radio">
        <a rel="tooltip" data-placement="top" title="${ I18n('No sorting') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() === '${ CHART_SORTING.NONE }' },
            click: function() { chartSorting('${ CHART_SORTING.NONE }'); }
          "><i class="fa fa-align-left fa-rotate-270"></i></a>
        <a rel="tooltip" data-placement="top" title="${ I18n('Sort ascending') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() == '${ CHART_SORTING.ASC }' },
            click: function() { chartSorting('${ CHART_SORTING.ASC }'); }
          "><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
        <a rel="tooltip" data-placement="top" title="${ I18n('Sort descending') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() == '${ CHART_SORTING.DESC }' },
            click: function(){ chartSorting('${ CHART_SORTING.DESC }'); }
          "><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
      </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
  </div>

  <div class="split-result-resizer" style="display: none;" data-bind="
      visible: chartSettingsVisible,
      splitFlexDraggable : {
        containerSelector: '.split-result-container',
        sidePanelSelector: '.result-settings-panel',
        sidePanelVisible: chartSettingsVisible,
        orientation: 'left',
        appName: 'result_chart',
        onPosition: function() {  }
      }
    "><div class="resize-bar"></div>
  </div>

  <div class="split-result-content chart-container">
    <h1 class="empty" data-bind="visible: !hasDataForChart()" style="display:none">${ I18n('Select the chart parameters on the left') }</h1>

    <div data-bind="visible: hasDataForChart" style="display:none">
      <!-- ko if: isPieChart -->
      <div class="chart" data-bind="attr: { 'id': chartId }, pieChart: pieChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isBarChart -->
      <div class="chart" data-bind="attr: { 'id': chartId }, barChart: barChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isLineChart -->
      <div class="chart" data-bind="attr: { 'id': chartId }, lineChart: lineChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isTimelineChart -->
      <div class="chart" data-bind="attr:{ 'id': chartId }, timelineChart: timeLineChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isMapChart -->
      <div class="chart" data-bind="attr:{ 'id': chartId }, leafletMapChart: leafletMapChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isGradientMapChart -->
      <div class="chart" data-bind="attr:{ 'id': chartId }, mapChart: mapChartParams()"></div>
      <!-- /ko -->

      <!-- ko if: isScatterChart -->
      <div class="chart" data-bind="attr:{ 'id': chartId }, scatterChart: scatterChartParams()"></div>
      <!-- /ko -->
    </div>
  </div>
</div>
`;

class ResultChart extends DisposableComponent {
  constructor(params) {
    super();

    this.data = params.data;
    this.id = params.id;
    this.activeExecutable = params.activeExecutable;

    this.meta = params.meta;
    this.cleanedMeta = params.cleanedMeta;
    this.cleanedDateTimeMeta = params.cleanedDateTimeMeta;
    this.cleanedNumericMeta = params.cleanedNumericMeta;
    this.cleanedStringMeta = params.cleanedNumericMeta;
    this.showChart = params.showChart;

    const trackedObservables = {
      chartLimit: undefined,
      chartMapHeat: undefined,
      chartMapLabel: undefined,
      chartMapType: CHART_MAP_TYPE.MARKER,
      chartScatterGroup: undefined,
      chartScatterSize: undefined,
      chartScope: CHART_SCOPE.WORLD,
      chartSettingsVisible: true,
      chartSorting: CHART_SORTING.NONE,
      chartTimelineType: CHART_TIMELINE_TYPE.BAR,
      chartX: undefined,
      chartXPivot: undefined,
      chartYMulti: [],
      chartYSingle: undefined,
      chartType: window.HUE_CHARTS.TYPES.BARCHART
    };

    this.chartLimit = ko.observable(trackedObservables.chartLimit).extend({ notify: 'always' });
    this.chartLimits = ko.observableArray([5, 10, 25, 50, 100]);
    this.chartMapHeat = ko.observable(trackedObservables.chartMapHeat);
    this.chartMapLabel = ko.observable(trackedObservables.chartMapLabel);
    this.chartMapType = ko.observable(trackedObservables.chartMapType);
    this.chartScatterGroup = ko.observable(trackedObservables.chartScatterGroup);
    this.chartScatterSize = ko.observable(trackedObservables.chartScatterSize);
    this.chartScope = ko.observable(trackedObservables.chartScope);
    this.chartSettingsVisible = ko.observable(trackedObservables.chartSettingsVisible);
    this.chartSorting = ko.observable(trackedObservables.chartSorting);
    this.chartTimelineType = ko.observable(trackedObservables.chartTimelineType);
    this.chartX = ko.observable(trackedObservables.chartX).extend({ notify: 'always' });
    this.chartXPivot = ko.observable(trackedObservables.chartXPivot).extend({ notify: 'always' });
    this.chartYMulti = ko.observableArray(trackedObservables.chartYMulti);
    this.chartYSingle = ko.observable(trackedObservables.chartYSingle);
    this.chartType = ko.observable(trackedObservables.chartType);

    attachTracker(this.activeExecutable, RESULT_CHART_COMPONENT, this, trackedObservables);

    this.chartId = ko.pureComputed(() => this.chartType() + '_' + this.id());
    this.isBarChart = ko.pureComputed(() => TYPES.BARCHART === this.chartType());
    this.isLineChart = ko.pureComputed(() => TYPES.LINECHART === this.chartType());
    this.isMapChart = ko.pureComputed(() => TYPES.MAP === this.chartType());
    this.isScatterChart = ko.pureComputed(() => TYPES.SCATTERCHART === this.chartType());
    this.isGradientMapChart = ko.pureComputed(() => TYPES.GRADIENTMAP === this.chartType());
    this.isPieChart = ko.pureComputed(() => TYPES.PIECHART === this.chartType());
    this.isTimelineChart = ko.pureComputed(() => TYPES.TIMELINECHART === this.chartType());

    this.hasDataForChart = ko.pureComputed(() => {
      if (this.isBarChart() || this.isLineChart() || this.isTimelineChart()) {
        return (
          typeof this.chartX() !== 'undefined' &&
          this.chartX() !== null &&
          this.chartYMulti().length
        );
      }
      return (
        typeof this.chartX() !== 'undefined' &&
        this.chartX() !== null &&
        typeof this.chartYSingle() !== 'undefined' &&
        this.chartYSingle() !== null
      );
    });

    this.subscribe(this.chartType, this.redrawChart.bind(this));

    this.subscribe(this.meta, () => {
      if (this.chartX()) {
        this.chartX(this.guessMetaField(this.chartX()));
      }
      if (this.chartXPivot()) {
        this.chartXPivot(this.guessMetaField(this.chartXPivot()));
      }
      if (this.chartYSingle()) {
        this.chartYSingle(this.guessMetaField(this.chartYSingle()));
      }
      if (this.chartMapLabel()) {
        this.chartMapLabel(this.guessMetaField(this.chartMapLabel()));
      }
      if (this.chartYMulti()) {
        this.chartYMulti(this.guessMetaFields(this.chartYMulti()));
      }
    });

    this.subscribe(this.showChart, this.prepopulateChart.bind(this));
    this.subscribe(this.chartType, this.prepopulateChart.bind(this));
    this.subscribe(this.chartXPivot, this.prepopulateChart.bind(this));

    this.subscribe(this.hasDataForChart, () => {
      this.chartX.notifySubscribers();
      this.chartX.valueHasMutated();
    });

    this.hideStacked = ko.pureComputed(() => !this.chartYMulti().length);

    this.chartMetaOptions = ko.pureComputed(() => {
      if (this.isBarChart() || this.isGradientMapChart()) {
        return this.cleanedMeta();
      }
      if (this.isTimelineChart()) {
        return this.cleanedDateTimeMeta();
      }
      return this.cleanedNumericMeta();
    });

    this.pieChartParams = ko.pureComputed(() => ({
      data: this,
      transformer: pieChartTransformer,
      maxWidth: 350,
      parentSelector: '.chart-container'
    }));

    this.barChartParams = ko.pureComputed(() => ({
      skipWindowResize: true,
      datum: this,
      hideSelection: true,
      enableSelection: false,
      hideStacked: this.hideStacked,
      transformer: multiSerieChartTransformer,
      stacked: false,
      showLegend: true,
      isPivot: typeof this.chartXPivot() !== 'undefined',
      type: this.chartTimelineType
    }));

    this.lineChartParams = ko.pureComputed(() => ({
      datum: this,
      transformer: multiSerieChartTransformer,
      showControls: false,
      enableSelection: false
    }));

    this.timeLineChartParams = ko.pureComputed(() => ({
      type: this.chartTimelineType,
      skipWindowResize: true,
      datum: this,
      hideSelection: true,
      enableSelection: false,
      hideStacked: this.hideStacked,
      transformer: timelineChartTransformer,
      stacked: false,
      showLegend: true
    }));

    this.leafletMapChartParams = ko.pureComputed(() => ({
      datum: this,
      transformer: leafletMapChartTransformer,
      showControls: false,
      height: 380,
      forceRedraw: true
    }));

    this.mapChartParams = ko.pureComputed(() => ({
      data: this,
      transformer: mapChartTransformer,
      isScale: true,
      showControls: false,
      height: 380,
      maxWidth: 750,
      parentSelector: '.chart-container'
    }));

    this.scatterChartParams = ko.pureComputed(() => ({
      datum: this,
      transformer: scatterChartTransformer,
      maxWidth: 350,
      y: this.chartYSingle(),
      x: this.chartX(),
      size: this.chartScatterSize(),
      group: this.chartScatterGroup()
    }));

    this.subscribe(REDRAW_CHART_EVENT, this.redrawChart.bind(this));

    const resizeId = UUID();
    let resizeTimeout = -1;
    $(window).on('resize.' + resizeId, () => {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(() => {
        this.redrawChart();
      }, 100);
    });
    this.disposals.push(() => {
      window.clearTimeout(resizeTimeout);
      $(window).off('resize.' + resizeId);
    });
  }

  guessMetaField(originalField) {
    let newField = undefined;
    this.cleanedMeta().some(fld => {
      if (
        fld.name.toLowerCase() === originalField.toLowerCase() ||
        originalField.toLowerCase() === fld.name.toLowerCase()
      ) {
        newField = fld.name;
        return true;
      }
    });
    return newField;
  }

  guessMetaFields(originalFields) {
    const newFields = [];
    originalFields.forEach(field => {
      const newField = this.guessMetaField(field);
      if (newField) {
        newFields.push(newField);
      }
    });
    return newFields;
  }

  prepopulateChart() {
    const type = this.chartType();
    hueAnalytics.log('notebook', 'chart/' + type);

    if (this.isMapChart() && this.cleanedNumericMeta().length >= 2) {
      if (this.chartX() === null || typeof this.chartX() === 'undefined') {
        let name = this.cleanedNumericMeta()[0].name;
        this.cleanedNumericMeta().some(column => {
          if (
            column.name.toLowerCase().indexOf('lat') > -1 ||
            column.name.toLowerCase().indexOf('ltd') > -1
          ) {
            name = column.name;
            return true;
          }
        });
        this.chartX(name);
      }
      if (this.chartYSingle() === null || typeof this.chartYSingle() === 'undefined') {
        let name = this.cleanedNumericMeta()[1].name;
        this.cleanedNumericMeta().some(column => {
          if (
            column.name.toLowerCase().indexOf('lon') > -1 ||
            column.name.toLowerCase().indexOf('lng') > -1
          ) {
            name = column.name;
            return true;
          }
        });
        this.chartYSingle(name);
      }
      return;
    }

    if (
      (this.chartX() === null || typeof this.chartX() === 'undefined') &&
      (this.isBarChart() || this.isPieChart() || this.isGradientMapChart()) &&
      this.cleanedStringMeta().length
    ) {
      this.chartX(this.cleanedStringMeta()[0].name);
    }

    if (this.cleanedNumericMeta().length) {
      if (!this.chartYMulti().length && (this.isBarChart() || this.isLineChart())) {
        this.chartYMulti.push(
          this.cleanedNumericMeta()[Math.min(this.cleanedNumericMeta().length - 1, 1)].name
        );
      } else if (
        (this.chartYSingle() === null || typeof this.chartYSingle() === 'undefined') &&
        (this.isPieChart() ||
          this.isMapChart() ||
          this.isGradientMapChart() ||
          this.isScatterChart() ||
          (this.isBarChart() && this.chartXPivot() !== null))
      ) {
        if (!this.chartYMulti().length) {
          this.chartYSingle(
            this.cleanedNumericMeta()[Math.min(this.cleanedNumericMeta().length - 1, 1)].name
          );
        } else {
          this.chartYSingle(this.chartYMulti()[0]);
        }
      }
    }
  }

  redrawChart() {
    this.chartX.notifySubscribers();
    this.chartX.valueHasMutated();
  }
}

componentUtils.registerComponent(RESULT_CHART_COMPONENT, ResultChart, TEMPLATE);
