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

import I18n from 'utils/i18n';

import { insertLinebreaks, lineChartBuilder } from 'ko/bindings/charts/chartUtils';
import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.lineChart = {
  init: function(element, valueAccessor) {
    window.setTimeout(() => {
      lineChartBuilder(element, valueAccessor(), false);
    }, 0);
  },
  update: function(element, valueAccessor) {
    const _options = valueAccessor();
    const _datum = _options.transformer(_options.datum);
    const _chart = $(element).data('chart');
    if (_chart) {
      window.setTimeout(() => {
        _chart.noData(_datum.message || I18n('No Data Available.'));
        const _d3 = d3v3.select($(element).find('svg')[0]);
        if (
          _datum.length > 0 &&
          _datum[0].values.length > 0 &&
          typeof _datum[0].values[0].x.isValid === 'function'
        ) {
          _chart.xAxis.tickFormat(d => {
            return d3v3.time.format('%Y-%m-%d %H:%M:%S')(new Date(d));
          });
          _chart.onChartUpdate(() => {
            _d3.selectAll('g.nv-x.nv-axis g text').each(function(d) {
              insertLinebreaks(_chart, d, this);
            });
          });
        }
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
    } else if (_datum.length > 0) {
      ko.bindingHandlers.lineChart.init(element, valueAccessor);
    }
  }
};
