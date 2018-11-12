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

  <style>

    ## TODO: proper clip in d3
    .line {
      clip-path: url(#clip);
    }

  </style>

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

      var AVAILABLE_TYPES = [{
        label: '${ _("CPU") }',
        color: '#29A7DE'
      }, {
        label: '${ _("Memory") }',
        color: '#5D8A8A'
      }];

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
        self.graphHeight = 500;
        self.graphWidth = 750;

        self.cpuStats = ko.observable({ average: '-', min: '-', max: '-', color: AVAILABLE_TYPES[0].color });
        self.memoryStats = ko.observable({ average: '-', min: '-', max: '-', color: AVAILABLE_TYPES[1].color });
        self.chartData = ko.observable();
        self.memoryLimit = 64 * 1024 * 1024 * 1024; // 64GB should be fetched from API

        self.fetchData();

        self.graphContainerRendered = function (domTree) {
          var graphElement = domTree[1];

          var maxQueryCount = 20;

          var subTop = self.graphHeight - 100;

          var mainMargin = { top: 10, right: 70, left: 70, bottom: self.graphHeight - subTop + 40 };
          var subMargin = { top: subTop, right: 70, bottom: 40, left: 70 };
          var height = self.graphHeight - mainMargin.top - mainMargin.bottom;
          var subHeight = self.graphHeight - subMargin.top - subMargin.bottom;
          var width = self.graphWidth - mainMargin.left - mainMargin.right;

          var mainHeight = self.graphHeight - mainMargin.top - mainMargin.bottom;
          var mainYScale = d3.scaleLinear().range([mainHeight, 0]);

          var subXScale = d3.scaleTime().range([0, width]);
          var subYScale = d3.scaleLinear().range([subHeight, 0]);

          var mainXScale = d3.scaleTime().range([0, width]);

          var mainXAxis = d3.axisBottom(mainXScale);
          var mainYAxis = d3.axisLeft(mainYScale).tickFormat(function (y) {
            return Math.round(maxQueryCount * y / 100);
          });

          var secondaryYAxis = d3.axisRight(mainYScale).tickFormat(function (y) {
            return y + '%';
          });

          var subXAxis = d3.axisBottom(subXScale);
          ##  var subYAxis = d3.axisLeft(subYScale).ticks(2);

          var graphCount = 2;

          var mainLines = [];
          var subLines = [];

          for (var i = 0; i < graphCount; i++) {
            mainLines.push(d3.line().curve(d3.curveMonotoneX).x(function (d) {
              return mainXScale(d[0]);
            }).y(function (d) {
              return mainYScale(d[this])
            }.bind(i + 1)));
            subLines.push(d3.line().curve(d3.curveMonotoneX).x(function (d) {
              return subXScale(d[0]);
            }).y(function (d) {
              return subYScale(d[this])
            }.bind(i + 1)));
          }

          var svg = d3.select(graphElement).append('svg').attr('width', self.graphWidth).attr('height', self.graphHeight);

          svg.append('defs')
            .append('clipPath')
            .attr('id', 'clip')
            .append('rect')
            .attr('width', width)
            .attr('height', mainHeight);

          var main = svg.append('g')
            .attr('class', 'focus')
            .attr('transform', 'translate(' + mainMargin.left + ',' + mainMargin.top + ')');

          var sub = svg.append('g')
            .attr('class', 'context')
            .attr('transform', 'translate(' + subMargin.left + ',' + subMargin.top + ')');

          var brush = d3.brushX()
            .extent([[0, 0], [width, subHeight]])
            .on('brush end', function () {
              if (d3.event.sourceEvent && d3.event.sourceEvent.type === 'zoom') {
                return;
              }
              var s = d3.event.selection || subXScale.range();
              mainXScale.domain(s.map(subXScale.invert, subXScale));
              for (var i = 0; i < mainLines.length; i++) {
                main.select('.line-' + i).attr('d', mainLines[i]);
              }
              main.select('.axis--x').call(mainXAxis);
              svg.select('.zoom').call(zoom.transform, d3.zoomIdentity.scale(width / (s[1] - s[0])).translate(-s[0], 0));
            });

          var zoom = d3.zoom()
            .scaleExtent([1, Infinity])
            .translateExtent([[0, 0], [width, mainHeight]])
            .extent([[0, 0], [width, mainHeight]])
            .on('zoom', function () {
              if (d3.event.sourceEvent && d3.event.sourceEvent.type === 'brush') {
                return;
              }
              var t = d3.event.transform;
              mainXScale.domain(t.rescaleX(subXScale).domain());
              for (var i = 0; i < mainLines.length; i++) {
                main.select('.line-' + i).attr('d', mainLines[i]);
              }
              main.select('.axis--x').call(mainXAxis);
              sub.select('.brush').call(brush.move, mainXScale.range().map(t.invertX, t));
            });

          var drawGraphs = function () {
            var data = self.chartData().slice(1);

            mainXScale.domain([data[0][0], data[data.length - 1][0]]);
            mainYScale.domain([0, 100]);
            subXScale.domain(mainXScale.domain());
            subYScale.domain(mainYScale.domain());

            main.append('g')
              .attr('class', 'axis axis--x')
              .attr('transform', 'translate(0,' + height + ')')
              .call(mainXAxis);

            main.append('g')
              .attr('class', 'axis axis--y')
              .call(mainYAxis);

            main.append('g')
              .attr('class', 'axis axis--y')
              .attr("transform", "translate(" + width + " ,0)")
              .call(secondaryYAxis);

            sub.append('g')
              .attr('class', 'axis axis--x')
              .attr('transform', 'translate(0,' + subHeight + ')')
              .call(subXAxis);

            sub.append('g')
              .attr('class', 'brush')
              .call(brush)
              .call(brush.move, mainXScale.range());

            svg.append('rect')
              .attr('class', 'zoom')
              .attr('fill', 'none')
              .attr('width', width)
              .attr('height', mainHeight)
              .attr('transform', 'translate(' + mainMargin.left + ',' + mainMargin.top + ')')
              .call(zoom);

            for (var i = 0; i < graphCount; i++) {
              main.append('path')
                .datum(data)
                .attr('stroke', function (d, j) { return AVAILABLE_TYPES[i].color })
                .attr('fill', 'none')
                .classed('line line-' + i, true)
                .attr('d', mainLines[i]);
              sub.append('path')
                .datum(data)
                .attr('stroke', function (d, j) { return AVAILABLE_TYPES[i].color })
                .attr('fill', 'none')
                .classed('line-' + i, true)
                .attr('d', subLines[i]);
            }
          };

          drawGraphs();
        }
      }

      PerformanceGraph.prototype.fetchData = function () {
        var self = this;

        var chartData = generateFakeData();
        var cpuStats = { average: 0, min: 0, max: 0, color: AVAILABLE_TYPES[0].color };
        var memoryStats = { average: 0, min: 0, max: 0, color: AVAILABLE_TYPES[1].color };
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
