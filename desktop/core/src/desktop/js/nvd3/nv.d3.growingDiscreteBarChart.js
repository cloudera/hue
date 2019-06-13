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

import nv from 'ext/nv.d3.1.1.15b.custom';

nv.models.growingDiscreteBarChart = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const discretebar = nv.models.growingDiscreteBar(),
    xAxis = nv.models.axis(),
    yAxis = nv.models.axis();
  const margin = { top: 15, right: 10, bottom: 50, left: 60 };
  let width = null,
    height = null,
    color = nv.utils.getColor(),
    showXAxis = true,
    showYAxis = true,
    rightAlignYAxis = false,
    staggerLabels = false,
    tooltips = true,
    tooltip = function(key, x, y) {
      return '<h3>' + key + '</h3>' + '<p>' + y + ' on ' + x + '</p>';
    },
    x,
    y,
    noData = 'No Data Available.',
    transitionDuration = 250,
    selectBars = null;
  xAxis
    .orient('bottom')
    .highlightZero(false)
    .showMaxMin(false)
    .tickFormat(d => {
      return d;
    });

  const dispatch = d3v3.dispatch('tooltipShow', 'tooltipHide', 'beforeUpdate');
  yAxis.orient(rightAlignYAxis ? 'right' : 'left').tickFormat(d3v3.format(',.1f'));

  //============================================================

  //============================================================
  // Private Variables
  //------------------------------------------------------------

  const showTooltip = function(e, offsetElement) {
    const left = $.browser.msie && $.browser.version.indexOf('9.') > -1 ? e.e.clientX : e.e.layerX,
      top = e.pos[1] + (offsetElement.offsetTop || 0),
      x = xAxis.tickFormat()(discretebar.x()(e.point, e.pointIndex)),
      y = yAxis.tickFormat()(discretebar.y()(e.point, e.pointIndex)),
      content = tooltip(e.point.seriesKey, x, y, e, chart);

    nv.tooltip.show([left, top], content, e.value < 0 ? 'n' : 's', null, offsetElement);
  };

  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const container = d3v3.select(this),
        that = this;

      const availableWidth =
          (width || parseInt(container.style('width')) || 960) - margin.left - margin.right,
        availableHeight =
          (height || parseInt(container.style('height')) || 400) - margin.top - margin.bottom;

      chart.update = function() {
        dispatch.beforeUpdate();
        container
          .transition()
          .duration(transitionDuration)
          .call(chart);
      };
      chart.container = this;

      //------------------------------------------------------------
      // Display No Data message if there's nothing to show.

      if (
        !data ||
        !data.length ||
        !data.filter(d => {
          return d.values.length;
        }).length
      ) {
        const noDataText = container.selectAll('.nv-noData').data([noData]);

        noDataText
          .enter()
          .append('text')
          .attr('class', 'nvd3 nv-noData')
          .attr('dy', '-.7em')
          .style('text-anchor', 'middle');

        noDataText
          .attr('x', margin.left + availableWidth / 2)
          .attr('y', margin.top + availableHeight / 2)
          .text(d => {
            return d;
          });

        container.selectAll('.nv-discreteBarWithAxes').style('visibility', 'hidden');
        container.selectAll('.nv-noData').style('visibility', 'visible');

        return chart;
      } else {
        container.selectAll('.nv-discreteBarWithAxes').style('visibility', 'visible');
        container.selectAll('.nv-noData').style('visibility', 'hidden');
      }

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup Scales

      x = discretebar.xScale();
      y = discretebar.yScale().clamp(true);

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-wrap.nv-discreteBarWithAxes').data([data]);
      const gEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-discreteBarWithAxes')
        .append('g');
      const defsEnter = gEnter.append('defs');
      const g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-x nv-axis');
      gEnter
        .append('g')
        .attr('class', 'nv-y nv-axis')
        .append('g')
        .attr('class', 'nv-zeroLine')
        .append('line');

      gEnter.append('g').attr('class', 'nv-barsWrap');

      g.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      if (rightAlignYAxis) {
        g.select('.nv-y.nv-axis').attr('transform', 'translate(' + availableWidth + ',0)');
      }

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Main Chart Component(s)

      discretebar.width(availableWidth).height(availableHeight);

      selectBars = discretebar.selectBars;

      const barsWrap = g.select('.nv-barsWrap').datum(
        data.filter(d => {
          return !d.disabled;
        })
      );

      barsWrap.transition().call(discretebar);

      //------------------------------------------------------------

      defsEnter
        .append('clipPath')
        .attr('id', 'nv-x-label-clip-' + discretebar.id())
        .append('rect');

      g.select('#nv-x-label-clip-' + discretebar.id() + ' rect')
        .attr('width', x.rangeBand() * (staggerLabels ? 2 : 1))
        .attr('height', 16)
        .attr('x', -x.rangeBand() / (staggerLabels ? 1 : 2));

      //------------------------------------------------------------
      // Setup Axes

      if (showXAxis) {
        xAxis
          .scale(x)
          .ticks(availableWidth / 100)
          .tickSize(-availableHeight, 0);

        g.select('.nv-x.nv-axis').attr(
          'transform',
          'translate(0,' +
            (y.range()[0] + (discretebar.showValues() && y.domain()[0] < 0 ? 16 : 0)) +
            ')'
        );
        //d3v3.transition(g.select('.nv-x.nv-axis'))
        g.select('.nv-x.nv-axis')
          .transition()
          .call(xAxis);

        const xTicks = g.select('.nv-x.nv-axis').selectAll('g');

        if (staggerLabels) {
          const rangeBand = x.rangeBand();
          xTicks.selectAll('text').attr('transform', function(d, i, j) {
            const self = d3v3.select(this);
            let textLength = self.node().getComputedTextLength(),
              text = self.text();
            while (textLength > rangeBand * 2 && text.length > 0) {
              text = text.slice(0, -1);
              self.text(text + '...');
              textLength = self.node().getComputedTextLength();
              if (self.text() === '...') {
                self.text(' ');
                textLength = 0;
              }
            }
            return 'translate(0,' + (j % 2 === 0 ? '5' : '17') + ')';
          });
        }
      }

      if (showYAxis) {
        yAxis
          .scale(y)
          .ticks(availableHeight / 36)
          .tickSize(-availableWidth, 0);

        g.select('.nv-y.nv-axis')
          .transition()
          .call(yAxis);
      }

      // Zero line
      g.select('.nv-zeroLine line')
        .attr('x1', 0)
        .attr('x2', availableWidth)
        .attr('y1', y(0))
        .attr('y2', y(0));

      //------------------------------------------------------------

      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------

      dispatch.on('tooltipShow', e => {
        if (tooltips) {
          showTooltip(e, that.parentNode);
        }
      });

      //============================================================
    });

    return chart;
  }

  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  discretebar.dispatch.on('elementMouseover.tooltip', e => {
    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  discretebar.dispatch.on('elementMouseout.tooltip', e => {
    dispatch.tooltipHide(e);
  });

  dispatch.on('tooltipHide', () => {
    if (tooltips) {
      nv.tooltip.cleanup();
    }
  });

  //============================================================

  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  // expose chart's sub-components
  chart.dispatch = dispatch;
  chart.discretebar = discretebar;
  chart.xAxis = xAxis;
  chart.yAxis = yAxis;

  d3v3.rebind(
    chart,
    discretebar,
    'x',
    'y',
    'xDomain',
    'yDomain',
    'xRange',
    'yRange',
    'forceX',
    'forceY',
    'id',
    'showValues',
    'valueFormat'
  );

  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if (!arguments.length) {
      return margin;
    }
    margin.top = typeof _.top != 'undefined' ? _.top : margin.top;
    margin.right = typeof _.right != 'undefined' ? _.right : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left = typeof _.left != 'undefined' ? _.left : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) {
      return width;
    }
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) {
      return height;
    }
    height = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) {
      return color;
    }
    color = nv.utils.getColor(_);
    discretebar.color(color);
    return chart;
  };

  chart.showXAxis = function(_) {
    if (!arguments.length) {
      return showXAxis;
    }
    showXAxis = _;
    return chart;
  };

  chart.showYAxis = function(_) {
    if (!arguments.length) {
      return showYAxis;
    }
    showYAxis = _;
    return chart;
  };

  chart.rightAlignYAxis = function(_) {
    if (!arguments.length) {
      return rightAlignYAxis;
    }
    rightAlignYAxis = _;
    yAxis.orient(_ ? 'right' : 'left');
    return chart;
  };

  chart.staggerLabels = function(_) {
    if (!arguments.length) {
      return staggerLabels;
    }
    staggerLabels = _;
    return chart;
  };

  chart.tooltips = function(_) {
    if (!arguments.length) {
      return tooltips;
    }
    tooltips = _;
    return chart;
  };

  chart.tooltipContent = function(_) {
    if (!arguments.length) {
      return tooltip;
    }
    tooltip = _;
    return chart;
  };

  chart.noData = function(_) {
    if (!arguments.length) {
      return noData;
    }
    noData = _;
    return chart;
  };

  chart.transitionDuration = function(_) {
    if (!arguments.length) {
      return transitionDuration;
    }
    transitionDuration = _;
    return chart;
  };

  chart.selectBars = function(args) {
    if (!arguments.length) {
      return selectBars;
    }
    if (selectBars) {
      selectBars(args);
    }
    return chart;
  };

  //============================================================

  return chart;
};
