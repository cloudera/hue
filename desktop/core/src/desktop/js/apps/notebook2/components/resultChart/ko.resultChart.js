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
import I18n from 'utils/i18n';
import {
  leafletMapChartTransformer,
  mapChartTransformer,
  multiSerieChartTransformer,
  pieChartTransformer,
  scatterChartTransformer,
  timelineChartTransformer
} from './chartTransformers';

export const NAME = 'result-chart';

const TYPES = window.HUE_CHARTS.TYPES;

// prettier-ignore
const TEMPLATE = `
<div>
  <div class="column-side" style="position:relative; white-space: nowrap;" data-bind="
      visible: isResultSettingsVisible,
      css: { 'span3 result-settings': isResultSettingsVisible, 'hidden': ! isResultSettingsVisible() }
    ">
    <div>
      <!-- ko if: chartType -->
      <!-- ko if: isTimeLineChart() || isBarChart() -->
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
          <option value="bar">${ I18n("Bars") }</option>
          <option value="line">${ I18n("Lines") }</option>
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
            value: chartYSingle,
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
            value: chartX,
            optionsText: 'name',
            optionsValue: 'name',
            optionsCaption: '${ I18n('Choose a column...') }',
            select2: { 
              width: '100%',
              placeholder: '${ I18n("Choose a column...") }',
              update: chartX,
              dropdownAutoWidth: true
            }"></select>
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
            value: chartX,
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
          visible: ((isBarChart() && !chartXPivot()) || isLineChart() || isTimeLineChart())
        ">
        <ul class="unstyled" data-bind="foreach: cleanedNumericMeta" style="margin-bottom: 0">
          <li><label class="checkbox"><input type="checkbox" data-bind="checkedValue: name, checked: $parent.chartYMulti" /> <span data-bind="text: $data.name"></span></label></li>
        </ul>
      </div>
      <div class="input-medium" data-bind="visible: (isBarChart() && chartXPivot()) || isMapChart() || isGradientMapChart() || isScatterChart()">
        <select data-bind="
            options: isGradientMapChart() ? cleanedMeta : cleanedNumericMeta,
            value: chartYSingle,
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
            value: chartXPivot,
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
          value: chartLimit,
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
          <option value="marker">${ I18n("Markers") }</option>
          <option value="heat">${ I18n("Heatmap") }</option>
        </select>
      </div>

      <!-- ko if: chartMapType() === 'marker' -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('label') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedMeta,
            value: chartMapLabel,
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

      <!-- ko if: chartMapType() === 'heat' -->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('intensity') }</li>
      </ul>
      <div>
        <select class="input-medium" data-bind="
            options: cleanedNumericMeta,
            value: chartMapHeat,
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
            value: chartScatterSize,
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
            value: chartScatterGroup,
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
          <option value="world">${ I18n("World") }</option>
          <option value="europe">${ I18n("Europe") }</option>
          <option value="aus">${ I18n("Australia") }</option>
          <option value="bra">${ I18n("Brazil") }</option>
          <option value="can">${ I18n("Canada") }</option>
          <option value="chn">${ I18n("China") }</option>
          <option value="fra">${ I18n("France") }</option>
          <option value="deu">${ I18n("Germany") }</option>
          <option value="ita">${ I18n("Italy") }</option>
          <option value="jpn">${ I18n("Japan") }</option>
          <option value="gbr">${ I18n("UK") }</option>
          <option value="usa">${ I18n("USA") }</option>
        </select>
      </div>
      <!-- /ko -->

      <!-- ko ifnot: isMapChart() || isGradientMapChart() || isScatterChart()-->
      <ul class="nav nav-list" style="border: none; background-color: #FFF">
        <li class="nav-header">${ I18n('sorting') }</li>
      </ul>
      <div class="btn-group" data-toggle="buttons-radio">
        <a rel="tooltip" data-placement="top" title="${ I18n('No sorting') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() === 'none' },
            click: function() { chartSorting('none'); }
          "><i class="fa fa-align-left fa-rotate-270"></i></a>
        <a rel="tooltip" data-placement="top" title="${ I18n('Sort ascending') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() == 'asc' },
            click: function() { chartSorting('asc'); }
          "><i class="fa fa-sort-amount-asc fa-rotate-270"></i></a>
        <a rel="tooltip" data-placement="top" title="${ I18n('Sort descending') }" href="javascript:void(0)" class="btn" data-bind="
            css: { 'active': chartSorting() == 'desc' },
            click: function(){ chartSorting('desc'); }
          "><i class="fa fa-sort-amount-desc fa-rotate-270"></i></a>
      </div>
      <!-- /ko -->
      <!-- /ko -->
    </div>
    <div class="resize-bar" style="top: 0; right: -10px; cursor: col-resize;"></div>
  </div>
  <div class="grid-side" data-bind="css: { 'span9': isResultSettingsVisible, 'span12 nomargin': ! isResultSettingsVisible() }">
    <div class="chart-container">
      <h1 class="empty" data-bind="visible: !hasDataForChart()">${ I18n('Select the chart parameters on the left') }</h1>

      <div data-bind="visible: hasDataForChart">
        <!-- ko if: isPieChart -->
        <div class="chart" data-bind="attr: { 'id': chartId }, pieChart: pieChartParams()" />
        <!-- /ko -->

        <!-- ko if: isBarChart -->
        <div class="chart" data-bind="attr: { 'id': chartId }, barChart: barChartParams()" />
        <!-- /ko -->

        <!-- ko if: isLineChart -->
        <div class="chart" data-bind="attr: { 'id': chartId }, lineChart: lineChartParams()" />
        <!-- /ko -->

        <!-- ko if: isTimeLineChart -->
        <div class="chart" data-bind="attr:{ 'id': chartId }, timelineChart: timeLineChartParams()" />
        <!-- /ko -->

        <!-- ko if: isMapChart -->
        <div class="chart" data-bind="attr:{ 'id': chartId }, leafletMapChart: leafletMapChartParams()" />
        <!-- /ko -->

        <!-- ko if: isGradientMapChart -->
        <div class="chart" data-bind="attr:{ 'id': chartId }, mapChart: mapChartParams()" />
        <!-- /ko -->

        <!-- ko if: isScatterChart -->
        <div class="chart" data-bind="attr:{ 'id': chartId }, scatterChart: scatterChartParams()" />
        <!-- /ko -->
      </div>
    </div>
  </div>
</div>
`;

class ResultChart extends DisposableComponent {
  constructor(params) {
    super();

    this.data = params.data;
    this.id = params.id;
    this.isResultSettingsVisible = params.isResultSettingsVisible;
    this.chartLimit = params.chartLimit;
    this.chartMapHeat = params.chartMapHeat;
    this.chartMapLabel = params.chartMapLabel;
    this.chartMapType = params.chartMapType;
    this.chartScatterGroup = params.chartScatterGroup;
    this.chartScatterSize = params.chartScatterSize;
    this.chartScope = params.chartScope;
    this.chartSorting = params.chartSorting;
    this.chartTimelineType = params.chartTimelineType;
    this.chartType = params.chartType;
    this.chartX = params.chartX;
    this.chartXPivot = params.chartXPivot;
    this.chartYMulti = params.chartYMulti;
    this.chartYSingle = params.chartYSingle;

    this.meta = params.meta;
    this.cleanedMeta = params.cleanedMeta;
    this.cleanedDateTimeMeta = params.cleanedDateTimeMeta;
    this.cleanedNumericMeta = params.cleanedNumericMeta;

    this.chartLimits = ko.observableArray([5, 10, 25, 50, 100]);

    this.chartId = ko.pureComputed(() => this.chartType() + '_' + this.id());
    this.isBarChart = ko.pureComputed(() => TYPES.BARCHART === this.chartType());
    this.isLineChart = ko.pureComputed(() => TYPES.LINECHART === this.chartType());
    this.isMapChart = ko.pureComputed(() => TYPES.MAP === this.chartType());
    this.isScatterChart = ko.pureComputed(() => TYPES.SCATTERCHART === this.chartType());
    this.isGradientMapChart = ko.pureComputed(() => TYPES.GRADIENTMAP === this.chartType());
    this.isPieChart = ko.pureComputed(() => TYPES.PIECHART === this.chartType());
    this.isTimeLineChart = ko.pureComputed(() => TYPES.TIMELINECHART === this.chartType());

    this.hasDataForChart = ko.pureComputed(() => {
      if (this.isBarChart() || this.isLineChart() || this.isTimeLineChart()) {
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

    this.hasDataForChart.subscribe(() => {
      this.chartX.notifySubscribers();
      this.chartX.valueHasMutated();
    });

    this.hideStacked = ko.pureComputed(() => !this.chartYMulti().length);

    this.chartMetaOptions = ko.pureComputed(() => {
      if (this.isBarChart() || this.isGradientMapChart()) {
        return this.cleanedMeta();
      }
      if (this.isTimeLineChart()) {
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
  }
}

componentUtils.registerComponent(NAME, ResultChart, TEMPLATE);
