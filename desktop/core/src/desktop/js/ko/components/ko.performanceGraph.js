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

import * as d3 from 'd3';
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import componentUtils from './componentUtils';
import I18n from 'utils/i18n';

const TEMPLATE = `
<script type="text/html" id="performance-graph-d3-template">
  <div style="position:relative;"
      data-bind="attr: { 'id': id }, style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></div>
</script>

<div style="position: relative" data-bind="template: { afterRender: componentRendered }">
  <div style="padding: 10px; float: right;" data-bind="foreach: availableGranularities">
    <!-- ko if: $data === $parent.selectedGranularity() -->
    <span class="margin-right-20" data-bind="text: label"></span>
    <!-- /ko -->
    <!-- ko if: $data !== $parent.selectedGranularity() -->
    <a class="margin-right-20" href="javascript: void(0);" data-bind="text: label, click: function () { $parent.selectedGranularity($data); }"></a>
    <!-- /ko -->
  </div>
  <div style="clear: both;" class="performance-graph" data-bind="style: { height: graphHeight + 'px', width: graphWidth + 'px' }"></div>
</div>
`;

class PerformanceGraph {
  constructor(params) {
    const self = this;

    self.graphHeight = 500;
    self.graphWidth = 1000;

    self.data = undefined;
    self.graphElement = undefined;

    self.availableGranularities = [
      {
        label: I18n('1 hour'),
        totalTime: 1000 * 60 * 60,
        initialWindow: 1000 * 60 * 10,
        step: 5 * 1000 // 5 seconds
      },
      {
        label: I18n('8 hours'),
        totalTime: 1000 * 60 * 60 * 8,
        initialWindow: 1000 * 60 * 60 * 2,
        step: 15 * 1000 // 15 seconds
      },
      {
        label: I18n('1 week'),
        totalTime: 1000 * 60 * 60 * 24 * 7,
        initialWindow: 1000 * 60 * 60 * 24,
        step: 5 * 60 * 1000 // Every 5 minutes
      }
    ];

    self.selectedGranularity = ko.observable(
      self.availableGranularities[
        apiHelper.getFromTotalStorage('warehouses', 'performanceGraphGranularity', 0)
      ]
    );
    self.clusterName = ko.observable(params.clusterName);

    // Load the initial data
    const initialLoadPromise = self.loadData();
    self.appendTimeout = -1;

    self.componentRendered = function(elements) {
      elements.some(element => {
        if (element.className === 'performance-graph') {
          self.graphElement = element;
          return true;
        }
      });

      if (!self.data || !self.data.length) {
        self.showLoadingMessage();
      }

      initialLoadPromise.done(() => {
        self.redrawGraph();
        self.selectedGranularity.subscribe(granularity => {
          for (let i = 0; i < self.availableGranularities.length; i++) {
            if (granularity === self.availableGranularities[i]) {
              apiHelper.setInTotalStorage('warehouses', 'performanceGraphGranularity', i);
              break;
            }
          }
          window.clearTimeout(self.appendTimeout);
          self.data = undefined;
          self.loadData().done(() => {
            self.redrawGraph();
          });
        });
      });
    };
  }

  showLoadingMessage() {
    const self = this;

    d3.select(self.graphElement)
      .select('svg')
      .remove();

    const svg = d3
      .select(self.graphElement)
      .append('svg')
      .attr('width', self.graphWidth)
      .attr('height', self.graphHeight);

    svg
      .selectAll('.loading-text')
      .data([I18n('Loading metrics...')])
      .enter()
      .append('text', 'rect')
      .attr('class', 'loading-text')
      .text(d => {
        return d;
      })
      .attr('text-anchor', 'middle')
      .attr('dy', self.graphHeight / 2)
      .attr('dx', self.graphWidth / 2);
  }

  redrawGraph() {
    const self = this;

    // Wait for data to appear
    if (!self.data.length) {
      self.showLoadingMessage();

      window.setTimeout(() => {
        self.loadData().done(() => {
          self.redrawGraph();
        });
      }, 3000);
      return;
    }

    // Margins and sizes
    const subTop = self.graphHeight - 150;
    const legendTop = self.graphHeight - 50;

    const mainMargin = { top: 10, right: 70, left: 70, bottom: self.graphHeight - subTop + 40 };
    const subMargin = { top: subTop, right: 70, bottom: 40, left: 70 };
    const legendMargin = { top: legendTop, right: 70, bottom: 10, left: 70 };

    const width = self.graphWidth - mainMargin.left - mainMargin.right;
    const mainHeight = self.graphHeight - mainMargin.top - mainMargin.bottom;
    const subHeight = self.graphHeight - subMargin.top - subMargin.bottom - 50;

    // Scales
    const percentageYScale = d3.scaleLinear().range([mainHeight, 0]);
    const queryYScale = d3.scaleLinear().range([mainHeight, 0]);
    const mainXScale = d3.scaleTime().range([0, width]);
    const subPercentageYScale = d3.scaleLinear().range([subHeight, 0]);
    const subQueryYScale = d3.scaleLinear().range([subHeight, 0]);
    const subXScale = d3.scaleTime().range([0, width]);

    // Axes
    const mainXAxis = d3.axisBottom(mainXScale).tickPadding(7);
    const subXAxis = d3
      .axisBottom(subXScale)
      .tickPadding(7)
      .tickSize(0);

    const queryYAxis = d3.axisLeft(queryYScale).tickPadding(7);
    const percentageYAxis = d3
      .axisRight(percentageYScale)
      .tickPadding(7)
      .tickFormat(y => {
        return y + '%';
      });

    // Update scale domains from data
    mainXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);
    percentageYScale.domain([0, 100]);
    let queryMax = 15;
    self.data.forEach(row => {
      if (row[4] + row[5] > queryMax) {
        queryMax = row[4] + row[5];
      }
    });
    queryYScale.domain([0, queryMax + 2]);

    subXScale.domain(mainXScale.domain());
    subPercentageYScale.domain(percentageYScale.domain());
    subQueryYScale.domain(queryYScale.domain());

    d3.select(self.graphElement)
      .select('svg')
      .remove();

    // Draw the graphs
    const svg = d3
      .select(self.graphElement)
      .append('svg')
      .attr('width', self.graphWidth)
      .attr('height', self.graphHeight);

    // Clipping path
    svg
      .append('defs')
      .append('clipPath')
      .attr('id', 'clip')
      .append('rect')
      .attr('width', width)
      .attr('height', mainHeight);

    // Containers for the graphs and legend
    const mainGroup = svg
      .append('g')
      .attr('class', 'main-group')
      .attr('transform', 'translate(' + mainMargin.left + ',' + mainMargin.top + ')');

    const subGroup = svg
      .append('g')
      .attr('class', 'sub-group')
      .attr('transform', 'translate(' + subMargin.left + ',' + subMargin.top + ')');

    const legendGroup = svg
      .append('g')
      .attr('class', 'legend-group')
      .attr('transform', 'translate(' + legendMargin.left + ',' + legendMargin.top + ')');

    // Draw the query and resource graphs
    const createLineGraph = function(options) {
      let line;
      let enabled = options.enabled;
      if (options.area) {
        line = d3
          .area()
          .curve(d3.curveStep)
          .x(d => {
            return mainXScale(d[0]);
          })
          .y0(mainHeight)
          .y1(options.y);
      } else {
        line = d3
          .line()
          .curve(d3.curveMonotoneX)
          .x(d => {
            return mainXScale(d[0]);
          })
          .y(options.y);
      }

      const path = mainGroup
        .append('path')
        .datum(self.data)
        .attr('stroke', () => {
          return options.color;
        })
        .attr('stroke-width', options.area ? 0 : 2)
        .style('opacity', enabled ? 1 : 0)
        .attr('fill', options.area ? options.color : 'none')
        .attr('clip-path', 'url(#clip)')
        .classed('line line-' + options.id, true)
        .attr('d', line);

      let subRefresh;
      if (options.subLine) {
        let subLine;
        if (options.area) {
          subLine = d3
            .area()
            .curve(d3.curveStep)
            .x(d => {
              return subXScale(d[0]);
            })
            .y0(subHeight)
            .y1(options.subY);
        } else {
          subLine = d3
            .line()
            .curve(d3.curveMonotoneX)
            .x(d => {
              return subXScale(d[0]);
            })
            .y(options.subY);
        }
        const subPath = subGroup
          .append('path')
          .datum(self.data)
          .attr('stroke', () => {
            return options.subLineColor || options.color;
          })
          .style('opacity', enabled ? 1 : 0)
          .attr('fill', options.area ? options.subLineColor || options.color : 'none')
          .attr('clip-path', 'url(#clip)')
          .classed('line line-' + options.id, true)
          .attr('d', subLine);
        subRefresh = function() {
          subPath.datum(self.data);
          subPath.attr('d', subLine);
        };
      }

      let stackedGraph;
      if (options.stackedGraph) {
        stackedGraph = options.stackedGraph();
      }

      return {
        refresh: function() {
          path.datum(self.data);
          path.attr('d', line);
          if (subRefresh) {
            subRefresh();
          }
          if (stackedGraph) {
            stackedGraph.refresh();
          }
        },
        id: options.id,
        enabled: function() {
          return enabled;
        },
        color: options.color,
        label: options.label,
        tooltip: options.tooltip,
        toggle: function() {
          enabled = !enabled;
          apiHelper.setInTotalStorage('warehouses', options.id + 'GraphEnabled', enabled);
          mainGroup
            .select('.highlight-point-' + options.id)
            .style('display', enabled ? null : 'none');
          mainGroup
            .select('.line-' + options.id)
            .transition()
            .style('opacity', enabled ? 1 : 0);
          subGroup
            .select('.line-' + options.id)
            .transition()
            .style('opacity', enabled ? 1 : 0);
          if (stackedGraph) {
            stackedGraph.enabled = enabled;
            mainGroup
              .select('.highlight-point-' + stackedGraph.id)
              .style('display', enabled ? null : 'none');
            mainGroup
              .select('.line-' + stackedGraph.id)
              .transition()
              .style('opacity', enabled ? 1 : 0);
            subGroup
              .select('.line-' + stackedGraph.id)
              .transition()
              .style('opacity', enabled ? 1 : 0);
          }
        },
        highlightPoint: function(dataPoint) {
          if (!options.disableHighlight) {
            mainGroup.select('.highlight-point-' + options.id).remove();

            mainGroup
              .insert('circle', '.overlay')
              .attr('class', 'highlight-point highlight-point-' + options.id)
              .style('display', enabled ? null : 'none')
              .attr('stroke', '#FFF')
              .attr('stroke-width', 2)
              .attr('fill', () => {
                return options.color;
              })
              .attr('r', 4)
              .attr(
                'transform',
                'translate(' + mainXScale(dataPoint[0]) + ',' + options.y(dataPoint) + ')'
              );
          }
        }
      };
    };

    const graphs = [
      createLineGraph({
        id: 'queries',
        label: I18n('Queries'),
        enabled: apiHelper.getFromTotalStorage('warehouses', 'queriesGraphEnabled', true),
        color: '#A9DBF1',
        subLineColor: '#DCDCDC',
        area: true,
        subLine: true,
        tooltip: function(d) {
          return d[4] + (d[5] ? ' (' + d[5] + ' ' + I18n('queued') : '');
        },
        y: function(d) {
          return queryYScale(d[4]);
        },
        subY: function(d) {
          return subQueryYScale(d[4]);
        },
        stackedGraph: function() {
          return createLineGraph({
            id: 'query-count-queued',
            enabled: true,
            color: '#0B7FAD',
            area: true,
            disableHighlight: true,
            y: function(d) {
              return queryYScale(d[5]);
            }
          });
        }
      }),
      createLineGraph({
        id: 'cpu',
        enabled: apiHelper.getFromTotalStorage('warehouses', 'cpuGraphEnabled', false),
        label: I18n('CPU'),
        color: '#654C94',
        subLine: true,
        tooltip: function(d) {
          return d[1] + '%';
        },
        y: function(d) {
          return percentageYScale(d[1]);
        },
        subY: function(d) {
          return subPercentageYScale(d[1]);
        }
      }),
      createLineGraph({
        id: 'memory',
        enabled: apiHelper.getFromTotalStorage('warehouses', 'memoryGraphEnabled', false),
        label: I18n('Memory'),
        color: '#83C1B9',
        subLine: true,
        tooltip: function(d) {
          return d[2] + '%';
        },
        y: function(d) {
          return percentageYScale(d[2]);
        },
        subY: function(d) {
          return subPercentageYScale(d[2]);
        }
      }),
      createLineGraph({
        id: 'io',
        enabled: apiHelper.getFromTotalStorage('warehouses', 'ioGraphEnabled', false),
        label: I18n('IO'),
        color: '#D4965E',
        subLine: true,
        tooltip: function(d) {
          return d[3] + '%';
        },
        y: function(d) {
          return percentageYScale(d[3]);
        },
        subY: function(d) {
          return subPercentageYScale(d[3]);
        }
      })
    ];

    // Draw the axes
    mainGroup
      .append('g')
      .attr('class', 'main-axis main-axis-x')
      .attr('transform', 'translate(0,' + mainHeight + ')')
      .call(mainXAxis);

    mainGroup
      .append('g')
      .attr('class', 'main-axis main-axis-y main-axis-query-count')
      .call(queryYAxis);

    mainGroup
      .append('g')
      .attr('class', 'main-axis main-axis-y main-axis-percentage')
      .attr('transform', 'translate(' + width + ' ,0)')
      .call(percentageYAxis);

    subGroup
      .append('g')
      .attr('class', 'sub-axis sub-axis-x')
      .attr('transform', 'translate(0,' + subHeight + ')')
      .call(subXAxis);

    mainGroup
      .append('text')
      .attr('class', 'y-label y-label-queries')
      .attr('transform', 'rotate(-90)')
      .attr('x', -mainHeight / 2)
      .attr('y', -45)
      .attr('dy', '1em')
      .style('text-anchor', 'middle');

    mainGroup
      .append('text')
      .attr('class', 'y-label y-label-resources')
      .attr('transform', 'rotate(90)')
      .attr('x', mainHeight / 2)
      .attr('y', -width - 55)
      .attr('dy', '1em')
      .style('text-anchor', 'middle');

    const updateAxesLabels = function() {
      let queriesLabel = '';
      let resourcesLabel = '';
      for (let i = 0; i < graphs.length; i++) {
        if (i === 0 && graphs[i].enabled()) {
          queriesLabel = graphs[i].label;
        } else if (graphs[i].enabled()) {
          if (resourcesLabel !== '') {
            resourcesLabel += ' ';
          }
          resourcesLabel += graphs[i].label;
        }
      }
      mainGroup.select('.y-label-queries').text(queriesLabel);
      mainGroup.select('.y-label-resources').text(resourcesLabel);
      mainGroup
        .select('.main-axis-query-count')
        .attr('display', queriesLabel === '' ? 'none' : null);
      mainGroup
        .select('.main-axis-percentage')
        .attr('display', resourcesLabel === '' ? 'none' : null);
    };

    updateAxesLabels();

    // Add brush
    const brushed = function() {
      const s = d3.event.selection || subXScale.range();
      mainXScale.domain(s.map(subXScale.invert, subXScale));

      graphs.forEach(graph => {
        graph.refresh();
      });

      mainGroup.select('.main-axis-x').call(mainXAxis);

      handle.attr('transform', (d, i) => {
        return 'translate(' + s[i] + ',' + subHeight / 2 + ')';
      });
    };

    const brush = d3
      .brushX()
      .extent([[0, 0], [width, subHeight]])
      .on('start brush end', brushed);

    const brushG = subGroup
      .append('g')
      .attr('class', 'brush')
      .call(brush);

    const handle = brushG
      .selectAll('.handle--custom')
      .data([{ type: 'w' }, { type: 'e' }])
      .enter()
      .append('circle')
      .classed('handle--custom', true)
      .attr('cursor', 'ew-resize')
      .attr('fill', '#FFF')
      .attr('r', 8)
      .attr('stroke', '#787878')
      .attr('stroke-width', 7);

    brushG.call(brush.move, [
      mainXScale(
        Math.max(
          self.data[self.data.length - 1][0] - self.selectedGranularity().initialWindow,
          self.data[0][0]
        )
      ),
      mainXScale(self.data[self.data.length - 1][0])
    ]);

    // Mouse hover overlay
    const dateBisector = d3.bisector(d => {
      return d[0];
    }).left;

    const pointFocus = function(mouseCoord, focusX) {
      const x = focusX;
      const j = dateBisector(self.data, x, 1);
      const d0 = self.data[j - 1];
      const d1 = self.data[j];
      const closest = x - d0[0] > d1[0] - x ? d1 : d0;

      graphs.forEach(graph => {
        graph.highlightPoint(closest);
      });

      const generateTooltipHtml = function(dataPoint) {
        let html =
          '<div class="performance-tooltip-time">' + moment(dataPoint[0]).toISOString() + '</div>';
        graphs.forEach(graph => {
          if (graph.tooltip && graph.enabled()) {
            html +=
              '<div><div class="performance-tooltip-indicator"><div style="background-color: ' +
              graph.color +
              '">&nbsp;</div></div><span class="performance-tooltip-label">' +
              graph.label +
              '</span> ' +
              graph.tooltip(dataPoint) +
              '</div>';
          }
        });
        return html;
      };

      d3.select(self.graphElement)
        .select('.performance-tooltip')
        .html(generateTooltipHtml(closest))
        .style('left', lastMouseCoord[0] + mainMargin.left + 15 + 'px')
        .style('top', lastMouseCoord[1] + mainMargin.top + 'px');
    };

    let lastMouseCoord = [0, 0];
    let lastFocusX = 0;
    mainGroup
      .append('rect')
      .attr('class', 'overlay')
      .attr('fill-opacity', '0')
      .attr('fill', 'white')
      .attr('width', width)
      .attr('height', mainHeight)
      .on('mouseout', () => {
        mainGroup.selectAll('.highlight-point').remove();
        d3.select(self.graphElement)
          .selectAll('.performance-tooltip')
          .remove();
      })
      .on('mouseover', () => {
        d3.select(self.graphElement)
          .append('div')
          .attr('class', 'performance-tooltip');
      })
      .on('mousemove', function() {
        lastMouseCoord = d3.mouse(this);
        lastFocusX = mainXScale.invert(lastMouseCoord[0]);
        pointFocus(lastMouseCoord, lastFocusX);
      });

    // Add Legend
    const legendSerie = legendGroup
      .selectAll('.legend-serie')
      .data(graphs)
      .enter()
      .append('g')
      .attr('class', 'legend-serie')
      .on('click', function(d) {
        d.toggle();
        d3.select(this)
          .select('rect')
          .transition()
          .attr('fill', d => {
            return d.enabled() ? d.color : '#FFF';
          });
        d3.select(this)
          .select('path')
          .transition()
          .attr('opacity', d => {
            return d.enabled() ? 1 : 0;
          });
        updateAxesLabels();
      });

    legendSerie
      .append('rect')
      .attr('class', 'legend-radio')
      .attr('fill', d => {
        return d.enabled() ? d.color : '#FFF';
      })
      .attr('stroke', d => {
        return d.color;
      })
      .attr('stroke-width', 2)
      .attr('rx', 2)
      .attr('ry', 2)
      .attr('width', 12)
      .attr('height', 12)
      .attr('transform', 'translate(-8, -6)');

    legendSerie
      .append('path')
      .attr('d', 'M-6,-1, -2,3, 2,-4')
      .attr('fill', 'none')
      .attr('stroke', (d, j) => {
        return j === 0 || j === 2 ? '#000' : '#FFF';
      })
      .transition()
      .attr('opacity', d => {
        return d.enabled() ? 1 : 0;
      })
      .attr('stroke-width', 2);

    legendSerie
      .append('text', 'rect')
      .text(d => {
        return d.label;
      })
      .attr('text-anchor', 'start')
      .attr('dy', '.32em')
      .attr('dx', '8');

    legendSerie.append('line');

    const knownLengths = [];

    legendSerie.attr('transform', function(d, j) {
      knownLengths[j] =
        d3
          .select(this)
          .select('text')
          .node()
          .getComputedTextLength() + 28;
      let x = 5;
      for (let i = 0; i < j; i++) {
        x += knownLengths[i];
      }
      return 'translate(' + x + ', 5)';
    });

    // Fetch and append data at set interval
    const appendData = function() {
      const currentDomain = mainXScale.domain();
      const currentSubDomain = subXScale.domain();

      const timeBetweenPoints = self.data[1][0] - self.data[0][0];
      const startTime = self.data[self.data.length - 1][0];
      const endTime = startTime + timeBetweenPoints;
      self.loadData(startTime, endTime, 1).done(() => {
        const mainStart =
          currentDomain[0].getTime() !== currentSubDomain[0].getTime()
            ? currentDomain[0]
            : self.data[0][0];
        const mainEnd =
          currentDomain[1].getTime() !== currentSubDomain[1].getTime()
            ? currentDomain[1]
            : self.data[self.data.length - 1][0];
        mainXScale.domain([mainStart, mainEnd]);
        subXScale.domain([self.data[0][0], self.data[self.data.length - 1][0]]);

        graphs.forEach(graph => {
          graph.refresh();
        });

        // Update highlight points and tip if data is appended when highlight is active
        if (mainGroup.selectAll('.highlight-point').size()) {
          pointFocus(lastMouseCoord, lastFocusX);
        }

        subGroup.select('.sub-axis-x').call(subXAxis);
        mainGroup.select('.main-axis-x').call(mainXAxis);
        subGroup.select('.brush').call(brush);

        self.appendTimeout = window.setTimeout(appendData, self.selectedGranularity().step);
      });
    };
    self.appendTimeout = window.setTimeout(appendData, self.selectedGranularity().step);
  }

  loadData() {
    const self = this;
    return apiHelper
      .fetchResourceStats({
        clusterName: self.clusterName(),
        pastMs: self.selectedGranularity().totalTime,
        stepMs: self.selectedGranularity().step
      })
      .done(data => {
        self.data = data;
      });
  }

  dispose() {
    const self = this;
    if (self.appendTimeout) {
      window.clearTimeout(self.appendTimeout);
    }
  }
}

componentUtils.registerComponent('performance-graph', PerformanceGraph, TEMPLATE);
