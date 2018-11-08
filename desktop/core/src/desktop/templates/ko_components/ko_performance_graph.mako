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

  <script type="text/html" id="performance-graph-stats">
    <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Min") } <span style="font-weight: 300;" data-bind="text: min"></span></div>
    <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Max") } <span style="font-weight: 300;" data-bind="text: max"></span></div>
    <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Avg") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: average"></span></div>
  </script>

  <script type="text/html" id="performance-graph-d3-template">
    <div data-bind="attr: { 'id': id }, style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></div>
  </script>

  <script type="text/html" id="performance-graph-template">
    <div class="performance-graph" style="position: relative">
      <h3>${ _('Resources') }</h3>
      <div style="font-size: 12px; position: absolute; right: 0; top: 0;" data-bind="template: { name: 'performance-graph-stats', data: cpuStats }"></div>
      <div style="font-size: 12px; position: absolute; right: 0; top: 14px;" data-bind="template: { name: 'performance-graph-stats', data: memoryStats }"></div>
      <!-- ko template: { name: 'performance-graph-d3-template', afterRender: graphContainerRendered } --><!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">


    (function () {
      var generateFakeData = function () {
        var entries = 100;
        var timeDiff = 300000; // 5 minutes
        var startTime = Date.now() - entries * timeDiff;
        var result = [['time', 'cpu', 'memory']];

        var lastCpuVal = 0;
        var lastMemVal = 0;
        for (var i = 0; i < 100; i++) {
          lastCpuVal = Math.round(Math.max(Math.min(lastCpuVal + (Math.random() - 0.5) * 20, 100), 0));
          lastMemVal = Math.round(Math.max(Math.min(lastMemVal + (Math.random() - 0.5) * 20, 100), 0)); // Percentage of total mem
          result.push([startTime + timeDiff * i, lastCpuVal, lastMemVal]);
        }
        return result;
      };

      var AVAILABLE_TYPES = {
        'cpu': {
          header: '${ _("CPU") }',
          color: '#29A7DE'
        },
        'memory': {
          header: '${ _("Memory") }',
          color: '#5D8A8A'
        }
      };

      function bytesToSize(bytes) {
        var sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) {
          return '0 B';
        }
        var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
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
        self.graphHeight = 500;
        self.graphWidth = 750;
        self.graphPadding = { top: 15, right: 50, bottom: 20, left: 40 };

        self.cpuStats = ko.observable({ average: '-', min: '-', max: '-', color: AVAILABLE_TYPES.cpu.color });
        self.memoryStats = ko.observable({ average: '-', min: '-', max: '-', color: AVAILABLE_TYPES.memory.color });
        self.chartData = ko.observable();
        self.memoryLimit = 64 * 1024 * 1024 * 1024; // 64GB should be fetched from API

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
                'cpu': AVAILABLE_TYPES.cpu.color,
                'memory': AVAILABLE_TYPES.memory.color
              },
              names: {
                cpu: AVAILABLE_TYPES.cpu.header,
                memory: AVAILABLE_TYPES.memory.header
              }
            },
            tooltip: {
              format: {
                value: function (value, ratio, id, index) {
                  if (id === 'cpu') {
                    return value + '%';
                  }
                  if (id === 'memory') {
                    return bytesToSize(self.memoryLimit * value / 100);
                  }
                  return value;
                }
              }
            },
            axes: {
              'cpu': 'y',
              'memory': 'y2'
            },
            grid: {
              y: {
                lines: [{ value: 80, text: '${ _("Auto resize") }', position: 'start' }]
              }
            },
            axis: {
              y: {
                default: [0, 100],
                min: 0,
                max: 100,
                padding: { top: 0, bottom: 0 },
                tick: {
                  format: function (value) { return value + '%' }
                }
              },
              y2: {
                default: [0, 100],
                min: 0,
                max: 100,
                show: true,
                padding: { top: 0, bottom: 0},
                tick: {
                  format: function (value) {
                    return bytesToSize(self.memoryLimit * value / 100);
                  }
                }
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
            },
            subchart: {
              show: true
            }
          });

        }
      }

      PerformanceGraph.prototype.fetchData = function () {
        var self = this;

        var chartData = generateFakeData();
        var cpuStats = { average: 0, min: 0, max: 0, color: AVAILABLE_TYPES.cpu.color };
        var memoryStats = { average: 0, min: 0, max: 0, color: AVAILABLE_TYPES.memory.color };
        chartData.slice(1).forEach(function (val) {
          cpuStats.max = Math.max(val[1], cpuStats.max);
          cpuStats.min = Math.min(val[1], cpuStats.min);
          cpuStats.average += val[1];
          memoryStats.max = Math.max(val[2], memoryStats.max);
          memoryStats.min = Math.min(val[2], memoryStats.min);
          memoryStats.average += val[2];
        });
        cpuStats.average = cpuStats.average / (chartData.length - 1);
        memoryStats.average = memoryStats.average / (chartData.length - 1);

        cpuStats.average += '%';
        cpuStats.min += '%';
        cpuStats.max += '%';
        memoryStats.average = bytesToSize(self.memoryLimit * memoryStats.average / 100);
        memoryStats.min = bytesToSize(self.memoryLimit * memoryStats.min / 100);
        memoryStats.max = bytesToSize(self.memoryLimit * memoryStats.max / 100);
        self.cpuStats(cpuStats);
        self.memoryStats(memoryStats);
        self.chartData(chartData);
      };

      ko.components.register('performance-graph', {
        viewModel: PerformanceGraph,
        template: { element: 'performance-graph-template' }
      });
    })();
  </script>
</%def>
