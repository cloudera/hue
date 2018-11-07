## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.

<%!
from desktop.views import _ko
from django.utils.translation import ugettext as _
%>

<%def name="performanceGraph()">

  <script type="text/html" id="performance-graph-d3-template">
    <div data-bind="attr: { 'id': id }, style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></div>
  </script>

  <script type="text/html" id="performance-graph-template">
    <div class="performance-graph" style="position: relative">
      <h3 data-bind="text: header"></h3>
      <div style="position: absolute; right: 20px; top: 3px;">
        ${ _("Min") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: min"></span> ${ _("Max") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: max"></span> ${ _("Average") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: average"></span>
      </div>
      <!-- ko template: { name: 'performance-graph-d3-template', afterRender: graphContainerRendered } --><!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">


    (function () {
      var generateFakeData = function (min, max) {
        var entries = 100;
        var timeDiff = 300000; // 5 minutes
        var startTime = Date.now() - entries * timeDiff;
        var result = [['time', 'worker 1', 'worker 2', 'worker 3']];

        var lastVal1 = min;
        var lastVal2 = min;
        var lastVal3 = min;
        for (var i = 0; i < 100; i++) {
          lastVal1 = Math.round(Math.max(Math.min(lastVal1 + (Math.random() - 0.5) * 20, max), min));
          lastVal2 = Math.round(Math.max(Math.min(lastVal2 + (Math.random() - 0.5) * 20, max), min));
          lastVal3 = Math.round(Math.max(Math.min(lastVal3 + (Math.random() - 0.5) * 20, max), min));
          result.push([startTime + timeDiff * i, lastVal1, lastVal2, lastVal3]);
        }
        return result;
      };

      var AVAILABLE_TYPES = {
        'cpu': {
          header: '${ _("CPU") }'
        }
      };

      /**
       * @param {object} params
       *
       * @constructor
       */
      function PerformanceGraph(params) {
        var self = this;
        self.id = UUID();
        self.type = params.type;
        self.header = AVAILABLE_TYPES[self.type].header;
        self.graphHeight = 300;
        self.graphWidth = 750;
        self.graphPadding = { top: 15, right: 30, bottom: 20, left: 30 };

        self.average = ko.observable('-');
        self.max = ko.observable('-');
        self.min = ko.observable('-');
        self.chartData = ko.observable();

        self.fetchData();

        self.graphContainerRendered = function (domTree) {
          var graphElement = domTree[1];

          c3.generate({
            bindto: graphElement,
            size: {
              height: self.graphHeight,
              width: self.graphWidth
            },
            padding: self.graphPadding,
            data: {
              x: 'time',
              rows: self.chartData(),
              colors: {
                'worker 1': '#29A7DE',
                'worker 2': '#B0BEC5',
                'worker 3': '#1C749B'
              }
            },
            grid: {
              y: {
                lines: [{ value: 80, text: '${ _("Auto resize") }' }]
              }
            },
            axis: {
              y: {
                default: [0, 100],
                min: 0,
                max: 100,
                padding: { top: 0, bottom: 0 }
              },
              x: {
                type: 'timeseries',
                tick: {
                  format: '%H:%M:%S',
                  count: 9
                }
              }
            },
            point: {
              r: 1.5
            },
            zoom: {
              enabled: true
            }
          });

        }
      }

      PerformanceGraph.prototype.fetchData = function () {
        var self = this;

        var chartData = generateFakeData(0, 100);
        var max = 0, min = 0, average = 0;
        chartData.slice(1).forEach(function (val) {
          max = Math.max(val[1], val[2], val[3], max);
          min = Math.min(val[1], val[2], val[3], min);
          average += (val[1] + val[2] + val[3]) / 3;
        });
        average = average / (chartData.length - 1);
        self.min(min + '%');
        self.max(max + '%');
        self.average(Math.round(average) + '%');
        self.chartData(chartData);
      };

      ko.components.register('performance-graph', {
        viewModel: PerformanceGraph,
        template: { element: 'performance-graph-template' }
      });
    })();
  </script>
</%def>
