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

ko.bindingHandlers.scatterChart = {
  update: function(element, valueAccessor) {
    const options = valueAccessor();
    let _datum = options.transformer(options.datum);
    window.setTimeout(() => {
      $(element).height(300);
      if (
        $(element).find('svg').length > 0 &&
        (_datum.length === 0 || _datum[0].values.length === 0)
      ) {
        $(element)
          .find('svg')
          .empty();
      }
      if (
        _datum.length > 0 &&
        _datum[0].values.length > 0 &&
        (isNaN(_datum[0].values[0].x) || isNaN(_datum[0].values[0].y))
      ) {
        _datum = [];
        $(element)
          .find('svg')
          .empty();
      }

      if ($(element).is(':visible')) {
        nv.addGraph(() => {
          const _chart = nv.models
            .scatterChart()
            .transitionDuration(350)
            .color(d3v3.scale.category10().range())
            .useVoronoi(false);

          _chart.tooltipContent((key, x, y, obj) => {
            return '<h3>' + key + '</h3><div class="center">' + obj.point.size + '</div>';
          });

          _chart.xAxis.tickFormat(d3v3.format('.02f'));
          _chart.yAxis.tickFormat(d3v3.format('.02f'));
          _chart.scatter.onlyCircles(true);

          const _d3 =
            $(element).find('svg').length > 0
              ? d3v3.select($(element).find('svg')[0])
              : d3v3.select($(element)[0]).append('svg');
          _d3
            .datum(_datum)
            .transition()
            .duration(150)
            .each('end', options.onComplete != null ? options.onComplete : void 0)
            .call(_chart);

          let _resizeTimeout = -1;
          nv.utils.windowResize(() => {
            window.clearTimeout(_resizeTimeout);
            _resizeTimeout = window.setTimeout(() => {
              _chart.update();
            }, 200);
          });

          $(element).on('forceUpdate', () => {
            _chart.update();
          });

          return _chart;
        });
      }
    }, 0);
  }
};
