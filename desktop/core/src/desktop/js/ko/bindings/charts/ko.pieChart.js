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

import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import I18n from 'utils/i18n';

ko.bindingHandlers.pieChart = {
  init: function(element, valueAccessor) {
    window.setTimeout(() => {
      const _options = valueAccessor();
      let _data = _options.transformer(_options.data);
      $(element).css('marginLeft', 'auto');
      $(element).css('marginRight', 'auto');
      if (typeof _options.maxWidth != 'undefined') {
        const _max = _options.maxWidth * 1;
        $(element).width(
          Math.min(
            $(element)
              .parent()
              .width(),
            _max
          )
        );
      }

      if ($(element).find('svg').length > 0 && _data.length === 0) {
        $(element)
          .find('svg')
          .empty();
      }

      if (_data.length > 0 && isNaN(_data[0].value)) {
        _data = [];
        $(element)
          .find('svg')
          .empty();
      }

      if ($(element).is(':visible')) {
        nv.addGraph(
          () => {
            const _chart = nv.models
              .growingPieChart()
              .x(d => {
                return d.label;
              })
              .y(d => {
                return d.value;
              })
              .height($(element).width())
              .showLabels(true)
              .showLegend(false)
              .tooltipContent((key, y) => {
                return '<h3>' + hueUtils.htmlEncode(key) + '</h3><p>' + y + '</p>';
              });
            _chart.noData(_data.message || I18n('No Data Available.'));
            const _d3 =
              $(element).find('svg').length > 0
                ? d3v3.select($(element).find('svg')[0])
                : d3v3.select($(element)[0]).append('svg');

            _d3
              .datum(_data)
              .transition()
              .duration(150)
              .each('end', _options.onComplete != null ? _options.onComplete : void 0)
              .call(_chart);

            if (_options.fqs) {
              $.each(_options.fqs(), (cnt, item) => {
                if (item.id() === _options.data.widget_id && item.field() === _options.field()) {
                  _chart.selectSlices(
                    $.map(item.filter(), it => {
                      return it.value();
                    })
                  );
                }
              });
            }

            $(element).data('chart', _chart);

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

            $(element).height($(element).width());
            const _parentSelector =
              typeof _options.parentSelector != 'undefined'
                ? _options.parentSelector
                : '.card-widget';
            $(element)
              .parents(_parentSelector)
              .on('resize', () => {
                if (typeof _options.maxWidth != 'undefined') {
                  const _max = _options.maxWidth * 1;
                  $(element).width(
                    Math.min(
                      $(element)
                        .parent()
                        .width(),
                      _max
                    )
                  );
                }
                $(element).height($(element).width());
                _chart.update();
              });

            return _chart;
          },
          () => {
            const _d3 =
              $(element).find('svg').length > 0
                ? d3v3.select($(element).find('svg')[0])
                : d3v3.select($(element)[0]).append('svg');
            _d3.selectAll('.nv-slice').on('click', d => {
              if (typeof _options.onClick != 'undefined') {
                huePubSub.publish('charts.state', { updating: true });
                _options.onClick(d);
              }
            });
          }
        );
      }
    }, 0);
  },
  update: function(element, valueAccessor) {
    const _options = valueAccessor();
    const _data = _options.transformer(_options.data);
    const _chart = $(element).data('chart');
    if (_chart) {
      _chart.noData(_data.message || I18n('No Data Available.'));
      const _d3 = d3v3.select($(element).find('svg')[0]);
      _d3
        .datum(_data)
        .transition()
        .duration(150)
        .each('end', _options.onComplete != null ? _options.onComplete : void 0)
        .call(_chart);

      if (_options.fqs) {
        $.each(_options.fqs(), (cnt, item) => {
          if (item.id() === _options.data.widget_id && item.field() === _options.field()) {
            _chart.selectSlices(
              $.map(item.filter(), it => {
                return it.value();
              })
            );
          }
        });
      }
      huePubSub.publish('charts.state');
    } else if (_data.length > 0) {
      ko.bindingHandlers.pieChart.init(element, valueAccessor);
    }
  }
};
