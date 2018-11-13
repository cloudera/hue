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

      var addFakeMeasurement = function (data, time) {
        var lastCpuVal = data.length ? data[data.length - 1][1] : 0;
        var lastMemVal = data.length ? data[data.length - 1][2] : 0;
        var lastQueryCount = data.length ? data[data.length - 1][3] : 0;
        var lastIO = data.length ? data[data.length - 1][3] : 0;

        var newQueryCount = Math.round(Math.max(Math.min(lastQueryCount + (Math.random() - 0.5) * 15, 25), 0));
        var diff = newQueryCount - lastQueryCount;
        if (diff > 0) {
          lastCpuVal = Math.round(Math.max(Math.min(lastCpuVal + Math.random() * 20, 100), 0));
          lastMemVal = Math.round(Math.max(Math.min(lastMemVal + Math.random() * 20, 100), 0));
          lastIO = Math.round(Math.max(Math.min(lastIO + Math.random() * 20, 100), 0));
        } else {
          lastCpuVal = Math.round(Math.max(Math.min(lastCpuVal - Math.random() * 20, 100), 0));
          lastMemVal = Math.round(Math.max(Math.min(lastMemVal - Math.random() * 20, 100), 0));
          lastIO = Math.round(Math.max(Math.min(lastIO - Math.random() * 20, 100), 0));
        }
        data.push([time, lastCpuVal, lastMemVal, lastIO, lastQueryCount]);
      };

      var generateFakeData = function (data, timeOffset, points) {
        var startTime = Date.now() - timeOffset;

        for (var i = 0; i < points; i++) {
          addFakeMeasurement(data, startTime + i * timeOffset/points )
        }
      };

      function bytesToSize(bytes) {
        var sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        if (bytes === 0) {
          return '0 B';
        }
        var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
        return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
      }

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

        self.data = [];
        self.series = [{
          label: '${ _("CPU") }',
          color: '#29A7DE',
          enabled: true
        }, {
          label: '${ _("Memory") }',
          color: '#ACA0A4',
          enabled: true
        }, {
          label: '${ _("IO") }',
          color: '#E4689A',
          enabled: true
        }, {
          label: '${ _("Queries") }',
          color: '#EBA81A',
          enabled: true
        }];

        self.cpuStats = ko.observable({ average: '-', min: '-', max: '-', color: self.series[0].color });
        self.memoryStats = ko.observable({ average: '-', min: '-', max: '-', color: self.series[1].color });
        self.memoryLimit = 64 * 1024 * 1024 * 1024; // 64GB should be fetched from API

        self.fetchData(300000, 100);

        self.graphContainerRendered = function (domTree) {
          var graphElement = domTree[1];

          var maxQueryCount = 20;

          var subTop = self.graphHeight - 150;
          var legendTop = self.graphHeight - 50;

          var mainMargin = { top: 10, right: 70, left: 70, bottom: self.graphHeight - subTop + 40 };
          var subMargin = { top: subTop, right: 70, bottom: 40, left: 70 };
          var legendMargin = { top: legendTop, right: 70, bottom: 10, left: 70 };

          var width = self.graphWidth - mainMargin.left - mainMargin.right;

          var mainHeight = self.graphHeight - mainMargin.top - mainMargin.bottom;
          var mainYScale = d3.scaleLinear().range([mainHeight, 0]);

          var subHeight = self.graphHeight - subMargin.top - subMargin.bottom - 50;

          var legendHeight = self.graphHeight - legendMargin.top - legendMargin.bottom;
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

          var dateBisector = d3.bisector(function(d) { return d[0]; }).left;

          var graphCount = 2;

          var mainLines = [];
          var subLines = [];

          var toggleSeries = function (i) {
            self.series[i].enabled = !self.series[i].enabled;
            svg.selectAll('.line-' + i).style('display', self.series[i].enabled ? null : 'none');
            svg.selectAll('.line-circle-' + i).style('display', self.series[i].enabled ? null : 'none');
            svg.select('.legend-circle-' + i).attr('fill-opacity', self.series[i].enabled ? 1 : 0.2);
          };

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

          var legend = svg.append('g')
                  .attr('class', 'context')
                  .attr('transform', 'translate(' + legendMargin.left + ',' + legendMargin.top + ')');

          var nextSeriesX = 5;
          for (var i = 0; i < graphCount; i++) {
            var legendSerie = legend.append('g')
              .on('click', function(d, j) {
                toggleSeries(this);
              }.bind(i))
              .on('mouseover', function(d, j) {

              })
              .on('mouseout', function(d, j) {

              });
            legendSerie.append('circle')
                    .attr('class', 'legend-circle-' + i)
                    .style('fill', function(d, j) { return self.series[i].color })
                    .style('stroke', function(d, j) { return self.series[i].color  })
                    .attr('r', 5);
            legendSerie.append('text')
                    .text(self.series[i].label)
                    .attr('text-anchor', 'start')
                    .attr('dy', '.32em')
                    .attr('dx', '8');

            legendSerie.attr('transform', function(d, j) {
              var length = d3.select(this).select('text').node().getComputedTextLength() + 28;
              var xpos = nextSeriesX;
              nextSeriesX += length;
              return 'translate(' + xpos + ',' + 5 + ')'
            });
          }

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
                      main.selectAll('.line-circle-' + i)
                              .attr("cx", function(d) { return mainXScale(d[0]); })
                              .attr("cy", function(d) { return mainYScale(d[i + 1]); });
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
                      main.selectAll('.line-circle-' + i)
                              .attr("cx", function(d) { return mainXScale(d[0]); })
                              .attr("cy", function(d) { return mainYScale(d[i + 1]); });
                    }
                    main.select('.axis--x').call(mainXAxis);
                    sub.select('.brush').call(brush.move, mainXScale.range().map(t.invertX, t));
                  });

          var drawGraphs = function () {
            mainXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);
            mainYScale.domain([0, 100]);
            subXScale.domain(mainXScale.domain());
            subYScale.domain(mainYScale.domain());

            main.append('g')
                    .attr('class', 'axis axis--x')
                    .attr('transform', 'translate(0,' + mainHeight + ')')
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
                      .datum(self.data)
                      .attr('stroke', function (d, j) { return self.series[i].color })
                      .attr('fill', 'none')
                      .attr("clip-path", "url(#clip)")
                      .classed('line line-' + i, true)
                      .attr('d', mainLines[i]);

              main.selectAll("line-circle-" + i)
                      .data(self.data)
                      .enter()
                      .append("circle")
                      .attr('stroke', function (d, j) { return 'white'; })
                      .attr('fill', function (d, j) { return self.series[i].color })
                      .attr("clip-path", "url(#clip)")
                      .attr("class", "line-circle-" + i)
                      .attr("r", 1.5)
                      .attr("cx", function(d) { return mainXScale(d[0]); })
                      .attr("cy", function(d) { return mainYScale(d[i + 1]); });

              sub.append('path')
                      .datum(self.data)
                      .attr('stroke', function (d, j) { return self.series[i].color })
                      .attr('fill', 'none')
                      .classed('line line-' + i, true)
                      .attr('d', subLines[i]);

              var focus = svg.append("g")
                      .attr("class", "point-focus point-focus-" + i)
                      .attr('fill', 'none')
                      .attr('stroke', function (d, j) { return self.series[i].color })
                      .style("display", "none");

              focus.append("circle")
                      .attr("r", 5);
            }

            // Hover overlay
            svg.append("rect")
                    .attr("class", "overlay")
                    .attr("fill-opacity", "0")
                    .attr("fill", "white")
                    .attr('transform', 'translate(' + mainMargin.left + ',' + mainMargin.top + ')')
                    .attr("width", width)
                    .attr("height", mainHeight)
                    .on("mouseover", function() {
                      for (var i = 0; i < graphCount; i++) {
                        if (self.series[i].enabled) {
                          svg.select('.point-focus-' + i).style("display", null);
                        }
                      }
                    })
                    .on("mouseout", function() {
                      svg.selectAll('.point-focus').style("display", "none");
                    })
                    .on("mousemove", function () {
                              var x = mainXScale.invert(d3.mouse(this)[0]);
                              var j = dateBisector(self.data, x, 1);
                              var d0 = self.data[j-1];
                              var d1 = self.data[j];
                              var closest = x - d0 > d1 - x ? d1 : d0;
                              for (var i = 0; i < graphCount; i++) {
                                if (self.series[i].enabled) {
                                  svg.select('.point-focus-' + i).attr("transform", "translate(" + (mainXScale(closest[0]) + mainMargin.left) + "," + (mainYScale(closest[i + 1]) + mainMargin.top) + ")");
                                }
                              }
                            }
                    );
          };

          drawGraphs();

          var fakeAppend = function () {
            var currentDomain = mainXScale.domain();
            var currentSubDomain = subXScale.domain();
            addFakeMeasurement(self.data, Date.now());
            var mainStart = currentDomain[0].getTime() !== currentSubDomain[0].getTime() ? currentDomain[0] : self.data[0][0];
            var mainEnd = currentDomain[1].getTime() !== currentSubDomain[1].getTime() ? currentDomain[1] : self.data[self.data.length - 1][0];
            mainXScale.domain([mainStart, mainEnd]);
            subXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);


            for (var i = 0; i < mainLines.length; i++) {
              main.select('.line-' + i).attr('d', mainLines[i]);
              main.selectAll('.line-circle-' + i)
                      .attr("cx", function(d) { return mainXScale(d[0]); })
                      .attr("cy", function(d) { return mainYScale(d[i + 1]); });
              sub.select('.line-' + i).attr('d', subLines[i]);
            }

            sub.select('.axis--x').call(subXAxis);
            main.select('.axis--x').call(mainXAxis);

             sub.select('.brush').call(brush);

            window.setTimeout(fakeAppend, 2000);
          };

          window.setTimeout(fakeAppend, 2000);
        }
      }

      PerformanceGraph.prototype.fetchData = function (timeOffset, points) {
        var self = this;

        generateFakeData(self.data, timeOffset, points);
        var cpuStats = { average: 0, min: 0, max: 0, color: self.series[0].color };
        var memoryStats = { average: 0, min: 0, max: 0, color: self.series[1].color };
        self.data.forEach(function (val) {
          cpuStats.max = Math.max(val[1], cpuStats.max);
          cpuStats.min = Math.min(val[1], cpuStats.min);
          cpuStats.average += val[1];
          memoryStats.max = Math.max(val[2], memoryStats.max);
          memoryStats.min = Math.min(val[2], memoryStats.min);
          memoryStats.average += val[2];
        });
        cpuStats.average = Math.round(cpuStats.average / self.data.length);
        memoryStats.average = Math.round(memoryStats.average / self.data.length);

        cpuStats.average += '%';
        cpuStats.min += '%';
        cpuStats.max += '%';
        memoryStats.average = bytesToSize(self.memoryLimit * memoryStats.average / 100);
        memoryStats.min = bytesToSize(self.memoryLimit * memoryStats.min / 100);
        memoryStats.max = bytesToSize(self.memoryLimit * memoryStats.max / 100);
        self.cpuStats(cpuStats);
        self.memoryStats(memoryStats);
      };

      ko.components.register('performance-graph', {
        viewModel: PerformanceGraph,
        template: { element: 'performance-graph-template' }
      });
    })();
  </script>
</%def>
