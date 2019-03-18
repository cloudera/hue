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
import d3v3 from 'd3v3';
import ko from 'knockout';
import nv from 'ext/nv.d3.1.1.15b.custom';

import I18n from 'utils/i18n';

import {
  barChartBuilder,
  handleSelection,
  lineChartBuilder,
  numeric
} from 'ko/bindings/charts/chartUtils';
import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.barChart = {
  init: function(element, valueAccessor) {
    const _options = ko.unwrap(valueAccessor());
    if (_options.type && _options.type() === 'line') {
      window.setTimeout(() => {
        lineChartBuilder(element, valueAccessor(), false);
      }, 0);
      $(element).data('type', 'line');
    } else {
      window.setTimeout(() => {
        barChartBuilder(element, valueAccessor(), false);
      }, 0);
      $(element).data('type', 'bar');
    }
  },
  update: function(element, valueAccessor) {
    const _options = ko.unwrap(valueAccessor());
    if (_options.type && _options.type() !== $(element).data('type')) {
      if ($(element).find('svg').length > 0) {
        $(element)
          .find('svg')
          .remove();
      }
      if (_options.type() === 'line') {
        window.setTimeout(() => {
          lineChartBuilder(element, valueAccessor(), false);
        }, 0);
      } else {
        window.setTimeout(() => {
          barChartBuilder(element, valueAccessor(), false);
        }, 0);
      }
      $(element).data('type', _options.type());
    }
    const _datum = _options.transformer(_options.datum);
    const _chart = $(element).data('chart');
    const _isPivot = _options.isPivot != null ? _options.isPivot : false;

    if (_chart) {
      _chart.noData(_datum.message || I18n('No Data Available.'));
      if (_chart.multibar) {
        _chart.multibar.stacked(typeof _options.stacked != 'undefined' ? _options.stacked : false);
      }
      if (numeric(_datum)) {
        _chart.xAxis.showMaxMin(false).tickFormat(d3v3.format(',0f'));
        if (_chart.multibar) {
          _chart.multibar.barColor(null);
        }
      } else {
        _chart.xAxis.tickFormat(s => {
          return s;
        });
        if (_chart.multibar) {
          if (!_isPivot) {
            _chart.multibar.barColor(nv.utils.defaultColor());
          } else {
            _chart.multibar.barColor(null);
          }
        }
      }
      window.setTimeout(() => {
        handleSelection(_chart, _options, _datum);
        const _d3 = d3v3.select($(element).find('svg')[0]);
        _d3
          .datum(_datum)
          .transition()
          .duration(150)
          .each('end', () => {
            if (_options.onComplete != null) {
              _options.onComplete();
            }
          })
          .call(_chart);
        huePubSub.publish('charts.state');
      }, 0);
    }
  }
};
