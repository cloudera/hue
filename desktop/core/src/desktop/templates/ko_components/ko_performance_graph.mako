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
##     <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Min") } <span style="font-weight: 300;" data-bind="text: min"></span></div>
##     <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Max") } <span style="font-weight: 300;" data-bind="text: max"></span></div>
##     <div style="width: 70px; display:inline-block" data-bind="style: { color: color }">${ _("Avg") } <span style="font-weight: 300; margin-right: 10px" data-bind="text: average"></span></div>
  </script>

  <script type="text/html" id="performance-graph-d3-template">
    <div style="position:relative;"
         data-bind="attr: { 'id': id }, style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></div>
  </script>

  <script type="text/html" id="performance-graph-template">
    <div class="performance-graph" style="position: relative">
      <h3>${ _('Resources') }</h3>
      <div style="font-size: 12px; position: absolute; right: 0; top: 0;"
           data-bind="template: { name: 'performance-graph-stats', data: cpuStats }"></div>
      <div style="font-size: 12px; position: absolute; right: 0; top: 14px;"
           data-bind="template: { name: 'performance-graph-stats', data: memoryStats }"></div>
      <!-- ko template: { name: 'performance-graph-d3-template', afterRender: graphContainerRendered } --><!-- /ko -->
    </div>
  </script>

  <script type="text/javascript">
    (function () {

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
        self.graphWidth = 1000;

        self.data = [];

        self.cpuStats = ko.observable({average: '-', min: '-', max: '-', color: 'blue'});
        self.memoryStats = ko.observable({average: '-', min: '-', max: '-', color: 'gray'});
        self.memoryLimit = 64 * 1024 * 1024 * 1024; // 64GB should be fetched from API

        self.graphContainerRendered = function (domTree) {
          ApiHelper.getInstance().fetchResourceStats({
            startTime: Date.now() - 100000,
            endTime: Date.now(),
            points: 100
          }).done(function (data) {
            self.data = data;

            var graphElement = domTree[1];

            var subTop = self.graphHeight - 150;
            var legendTop = self.graphHeight - 50;

            var mainMargin = {top: 10, right: 70, left: 70, bottom: self.graphHeight - subTop + 40};
            var subMargin = {top: subTop, right: 70, bottom: 40, left: 70};
            var legendMargin = {top: legendTop, right: 70, bottom: 10, left: 70};

            var width = self.graphWidth - mainMargin.left - mainMargin.right;

            var mainHeight = self.graphHeight - mainMargin.top - mainMargin.bottom;
            var queryYScale = d3.scaleLinear().range([mainHeight, 0]);
            var percentageYScale = d3.scaleLinear().range([mainHeight, 0]);

            var subHeight = self.graphHeight - subMargin.top - subMargin.bottom - 50;

            var legendHeight = self.graphHeight - legendMargin.top - legendMargin.bottom;
            var subXScale = d3.scaleTime().range([0, width]);
            var subPercentageYScale = d3.scaleLinear().range([subHeight, 0]);
            var subQueryYScale = d3.scaleLinear().range([subHeight, 0]);

            var mainXScale = d3.scaleTime().range([0, width]);

            var mainXAxis = d3.axisBottom(mainXScale);

            var queryYAxis = d3.axisLeft(queryYScale);
            var percentageYAxis = d3.axisRight(percentageYScale).tickFormat(function (y) {
              return y + '%';
            });

            var subXAxis = d3.axisBottom(subXScale);

            ##  var tip = d3.select(graphElement).append('div').attr('class', 'graph-tip').style('opacity', 0).style('position', 'absolute');

            var series = [{
              label: '${ _("Queries") }',
              color: '#BEE4F5',
              enabled: true,
              line: d3.area().curve(d3.curveStep).x(function (d) {
                return mainXScale(d[0])
              }).y0(mainHeight).y1(function (d) {
                return queryYScale(d[4])
              }),
              subLine: d3.area().curve(d3.curveStep).x(function (d) {
                return subXScale(d[0])
              }).y0(subHeight).y1(function (d) {
                return subQueryYScale(d[4])
              }),
              fill: '#BEE4F5',
              showDot: false,
              dataIndex: 4,
              lineYScale: queryYScale,
              subLineYScale: subQueryYScale
            }, {
              label: '${ _("CPU") }',
              color: '#7B46AD',
              enabled: window.cpuEnabled || false,
              line: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return mainXScale(d[0])
              }).y(function (d) {
                return percentageYScale(d[1])
              }),
              subLine: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return subXScale(d[0])
              }).y(function (d) {
                return subPercentageYScale(d[1])
              }),
              fill: 'none',
              showDot: true,
              dataIndex: 1,
              lineYScale: percentageYScale,
              subLineYScale: subPercentageYScale
            }, {
              label: '${ _("Memory") }',
              color: '#00B9AA',
              enabled: window.memEnabled || false,
              line: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return mainXScale(d[0])
              }).y(function (d) {
                return percentageYScale(d[2])
              }),
              subLine: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return subXScale(d[0])
              }).y(function (d) {
                return subPercentageYScale(d[2])
              }),
              fill: 'none',
              showDot: true,
              dataIndex: 2,
              lineYScale: percentageYScale,
              subLineYScale: subPercentageYScale
            }, {
              label: '${ _("IO") }',
              color: '#1C749B',
              enabled: window.ioEnabled || false,
              line: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return mainXScale(d[0])
              }).y(function (d) {
                return percentageYScale(d[3])
              }),
              subLine: d3.line().curve(d3.curveMonotoneX).x(function (d) {
                return subXScale(d[0])
              }).y(function (d) {
                return subPercentageYScale(d[3])
              }),
              fill: 'none',
              showDot: true,
              dataIndex: 3,
              lineYScale: percentageYScale,
              subLineYScale: subPercentageYScale
            }];

            var dateBisector = d3.bisector(function (d) {
              return d[0];
            }).left;

            var toggleSeries = function (serie) {
              serie.enabled = !serie.enabled;
              if (serie.dataIndex === 3) {
                window.ioEnabled = serie.enabled;
              } else if (serie.dataIndex === 2) {
                window.memEnabled = serie.enabled;
              } else if (serie.dataIndex === 1) {
                window.cpuEnabled = serie.enabled;
              }
              svg.selectAll('.line-' + serie.dataIndex).style('display', serie.enabled ? null : 'none');
              svg.selectAll('.line-circle-' + serie.dataIndex).style('display', serie.enabled ? null : 'none');
              svg.select('.legend-circle-' + serie.dataIndex).attr('fill-opacity', serie.enabled ? 1 : 0.2);
            };

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

            series.forEach(function (serie) {
              var legendSerie = legend.append('g')
                      .on('click', function (d, j) {
                        toggleSeries(serie);
                      })
                      .on('mouseover', function (d, j) {

                      })
                      .on('mouseout', function (d, j) {

                      });

              legendSerie.append('circle')
                      .attr('class', 'legend-circle-' + serie.dataIndex)
                      .attr('fill-opacity', serie.enabled ? 1 : 0.2)
                      .style('fill', function (d, j) {
                        return serie.color
                      })
                      .style('stroke', function (d, j) {
                        return serie.color
                      })
                      .attr('r', 5);

              legendSerie.append('text')
                      .text(serie.label)
                      .attr('text-anchor', 'start')
                      .attr('dy', '.32em')
                      .attr('dx', '8');

              legendSerie.attr('transform', function (d, j) {
                var length = d3.select(this).select('text').node().getComputedTextLength() + 28;
                var xpos = nextSeriesX;
                nextSeriesX += length;
                return 'translate(' + xpos + ',' + 5 + ')'
              });
            });

            var brush = d3.brushX()
                    .extent([[0, 0], [width, subHeight]])
                    .on('brush end', function () {
                      if (d3.event.sourceEvent && d3.event.sourceEvent.type === 'zoom') {
                        return;
                      }
                      var s = d3.event.selection || subXScale.range();
                      mainXScale.domain(s.map(subXScale.invert, subXScale));
                      series.forEach(function (serie) {
                        main.select('.line-' + serie.dataIndex).attr('d', serie.line);
                        main.selectAll('.line-circle-' + serie.dataIndex)
                                .attr("cx", function (d) {
                                  return mainXScale(d[0]);
                                })
                                .attr("cy", function (d) {
                                  return serie.lineYScale(d[serie.dataIndex]);
                                })
                      });
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
                      series.forEach(function (serie) {
                        main.select('.line-' + serie.dataIndex).attr('d', serie.line);
                        main.selectAll('.line-circle-' + serie.dataIndex)
                                .attr("cx", function (d) {
                                  return mainXScale(d[0]);
                                })
                                .attr("cy", function (d) {
                                  return serie.lineYScale(d[serie.dataIndex]);
                                })
                      });
                      main.select('.axis--x').call(mainXAxis);
                      sub.select('.brush').call(brush.move, mainXScale.range().map(t.invertX, t));
                    });

            mainXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);
            percentageYScale.domain([0, 100]);
            var queryMax = 15;
            self.data.forEach(function (row) {
              if (row[4] > queryMax) {
                queryMax = row[4];
              }
            });
            queryYScale.domain([0, queryMax + 2]);

            subXScale.domain(mainXScale.domain());
            subPercentageYScale.domain(percentageYScale.domain());
            subQueryYScale.domain(queryYScale.domain());

            series.forEach(function (serie) {

              main.append('path')
                      .datum(self.data)
                      .attr('stroke', function (d, j) {
                        return serie.color
                      })
                      .attr('fill', serie.fill)
                      .style('display', serie.enabled ? null : 'none')
                      .attr("clip-path", "url(#clip)")
                      .classed('line line-' + serie.dataIndex, true)
                      .attr('d', serie.line);

              if (serie.showDot) {
                main.selectAll(".line-circle-" + serie.dataIndex)
                        .data(self.data)
                        .enter()
                        .append("circle")
                        .style('display', serie.enabled ? null : 'none')
                        .attr('fill', function (d, j) {
                          return serie.color
                        })
                        .attr("clip-path", "url(#clip)")
                        .attr("class", "line-circle-" + serie.dataIndex)
                        .attr("r", 1.5)
                        .attr("cx", function (d) {
                          return mainXScale(d[0]);
                        })
                        .attr("cy", function (d) {
                          return serie.lineYScale(d[serie.dataIndex]);
                        });
              }

              sub.append('path')
                      .datum(self.data)
                      .style('display', serie.enabled ? null : 'none')
                      .attr('stroke', function (d, j) {
                        return serie.color
                      })
                      .attr('fill', serie.fill)
                      .classed('line line-' + serie.dataIndex, true)
                      .attr('d', serie.subLine);

              var focus = svg.append("g")
                      .attr("class", "point-focus point-focus-" + serie.dataIndex)
                      .attr('fill', 'none')
                      .attr('stroke', function (d, j) {
                        return serie.color
                      })
                      .style("display", "none");

              focus.append("circle")
                      .attr("r", 5);
            });

            main.append('g')
                    .attr('class', 'axis axis--x')
                    .attr('transform', 'translate(0,' + mainHeight + ')')
                    .call(mainXAxis);

            main.append('g')
                    .attr('class', 'axis axis--y')
                    .call(queryYAxis);

            main.append('g')
                    .attr('class', 'axis axis--y')
                    .attr("transform", "translate(" + width + " ,0)")
                    .call(percentageYAxis);

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

            var lastMouseCoord = [0, 0];
            var lastFocusX = 0;

            var pointFocus = function (mouseCoord, focusX) {
              var x = focusX;
              var j = dateBisector(self.data, x, 1);
              var d0 = self.data[j - 1];
              var d1 = self.data[j];
              var closest = x - d0 > d1 - x ? d1 : d0;

              var showTip = false;
              series.forEach(function (serie) {
                if (serie.enabled) {
                  var point = svg.select('.point-focus-' + serie.dataIndex);
                  point.attr("transform", "translate(" + (mainXScale(closest[0]) + mainMargin.left) + "," + (serie.lineYScale(closest[serie.dataIndex]) + mainMargin.top) + ")");
                  if (point.style('display') !== 'none') {
                    showTip = true;
                  }
                }
              });
              if (showTip) {
                // TODO: show the tip
              }
            };

            // Hover overlay
            svg.append("rect")
                    .attr("class", "overlay")
                    .attr("fill-opacity", "0")
                    .attr("fill", "white")
                    .attr('transform', 'translate(' + mainMargin.left + ',' + mainMargin.top + ')')
                    .attr("width", width)
                    .attr("height", mainHeight)
                    .on("mouseover", function () {
                      series.forEach(function (serie) {
                        if (serie.enabled) {
                          svg.select('.point-focus-' + serie.dataIndex).style("display", null);
                          svg.select('.focus-tip').style("display", null);
                        }
                      });
                    })
                    .on("mouseout", function () {
                      svg.selectAll('.point-focus').style("display", "none");
                      svg.select('.focus-tip').style("display", 'none');
                    })
                    .on("mousemove", function () {
                      lastMouseCoord = d3.mouse(this);
                      lastFocusX = mainXScale.invert(lastMouseCoord[0]);
                      pointFocus(lastMouseCoord, lastFocusX);
                    });

            var appendInterval = 1000;
            var appendPoints = 1;

            var appendData = function () {
              var currentDomain = mainXScale.domain();
              var currentSubDomain = subXScale.domain();

              ApiHelper.getInstance().fetchResourceStats({
                startTime: self.data[self.data.length - 1][0],
                endTime: Date.now(),
                points: appendPoints
              }).done(function (data) {
                data.forEach(function (newEntry) {
                  self.data.push(newEntry);
                });

                var mainStart = currentDomain[0].getTime() !== currentSubDomain[0].getTime() ? currentDomain[0] : self.data[0][0];
                var mainEnd = currentDomain[1].getTime() !== currentSubDomain[1].getTime() ? currentDomain[1] : self.data[self.data.length - 1][0];
                mainXScale.domain([mainStart, mainEnd]);
                subXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);

                series.forEach(function (serie) {
                  main.select('.line-' + serie.dataIndex).attr('d', serie.line);
                  if (serie.showDot) {
                    main.selectAll(".line-circle-" + serie.dataIndex).remove();

                    main.selectAll(".line-circle-" + serie.dataIndex)
                            .data(self.data)
                            .enter()
                            .append("circle")
                            .style('display', serie.enabled ? null : 'none')
                            .attr('fill', function (d, j) {
                              return serie.color
                            })
                            .attr("clip-path", "url(#clip)")
                            .attr("class", "line-circle-" + serie.dataIndex)
                            .attr("r", 1.5)
                            .attr("cx", function (d) {
                              return mainXScale(d[0]);
                            })
                            .attr("cy", function (d) {
                              return serie.lineYScale(d[serie.dataIndex]);
                            });
                  }
                  sub.select('.line-' + serie.dataIndex).attr('d', serie.subLine);
                });

                pointFocus(lastMouseCoord, lastFocusX);

                sub.select('.axis--x').call(subXAxis);
                main.select('.axis--x').call(mainXAxis);

                sub.select('.brush').call(brush);

                self.appendTimeout = window.setTimeout(appendData, appendInterval);
              })
            };
            self.appendTimeout = window.setTimeout(appendData, appendInterval);
          });
        }
      }

      PerformanceGraph.prototype.dispose = function () {
        var self = this;
        if (self.appendTimeout) {
          window.clearTimeout(self.appendTimeout);
        }
      };

      ko.components.register('performance-graph', {
        viewModel: PerformanceGraph,
        template: {element: 'performance-graph-template'}
      });
    })();
  </script>
</%def>
