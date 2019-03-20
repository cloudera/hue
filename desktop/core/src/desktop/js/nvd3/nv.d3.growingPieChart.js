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

import d3v3 from 'd3v3';

import nv from 'ext/nv.d3.1.1.15b.custom';

nv.models.growingPieChart = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const pie = nv.models.growingPie(),
    legend = nv.models.legend(),
    margin = { top: 30, right: 20, bottom: 20, left: 20 };

  let width = null,
    height = null,
    showLegend = true,
    color = nv.utils.defaultColor(),
    tooltips = true,
    tooltip = function(key, y) {
      return '<h3>' + key + '</h3>' + '<p>' + y + '</p>';
    },
    state = {},
    defaultState = null,
    noData = 'No Data Available.',
    selectSlices = null;
  const dispatch = d3v3.dispatch('tooltipShow', 'tooltipHide', 'stateChange', 'changeState');
  //============================================================

  //============================================================
  // Private Variables
  //------------------------------------------------------------

  const showTooltip = function(e, offsetElement) {
    const tooltipLabel = pie.description()(e.point) || pie.x()(e.point);
    const left = e.pos[0] + ((offsetElement && offsetElement.offsetLeft) || 0),
      top = e.pos[1] + ((offsetElement && offsetElement.offsetTop) || 0),
      y = pie.valueFormat()(pie.y()(e.point)),
      content = tooltip(tooltipLabel, y, e, chart);

    nv.tooltip.show([left, top], content, e.value < 0 ? 'n' : 's', null, offsetElement);
  };

  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const container = d3v3.select(this);

      const availableWidth =
        (width || parseInt(container.style('width')) || 960) - margin.left - margin.right;
      let availableHeight =
        (height || parseInt(container.style('height')) || 400) - margin.top - margin.bottom;

      chart.update = function() {
        container.transition().call(chart);
      };
      chart.container = this;

      //set state.disabled
      state.disabled = data.map(d => {
        return !!d.disabled;
      });

      if (!defaultState) {
        let key;
        defaultState = {};
        for (key in state) {
          if (state[key] instanceof Array) {
            defaultState[key] = state[key].slice(0);
          } else {
            defaultState[key] = state[key];
          }
        }
      }

      //------------------------------------------------------------
      // Display No Data message if there's nothing to show.

      let _allDataIsZero = true;
      if (data) {
        data.forEach(obj => {
          if (obj.value > 0) {
            _allDataIsZero = false;
          }
        });
      }

      if (!data || !data.length || _allDataIsZero) {
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

        container.selectAll('.nv-pieChart').style('visibility', 'hidden');
        container.selectAll('.nv-noData').style('visibility', 'visible');

        return chart;
      } else {
        container.selectAll('.nv-pieChart').style('visibility', 'visible');
        container.selectAll('.nv-noData').style('visibility', 'hidden');
      }

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-wrap.nv-pieChart').data([data]);
      const gEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-pieChart')
        .append('g');
      const g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-pieWrap');
      gEnter.append('g').attr('class', 'nv-legendWrap');

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Legend

      if (showLegend) {
        legend.width(availableWidth).key(pie.x());

        wrap
          .select('.nv-legendWrap')
          .datum(data)
          .call(legend);

        if (legend.height() > 50) {
          wrap.select('.nv-legendWrap').style('visibility', 'hidden');
        } else {
          wrap.select('.nv-legendWrap').style('visibility', 'visible');
          if (margin.top !== legend.height()) {
            margin.top = legend.height();
            availableHeight =
              (height || parseInt(container.style('height')) || 400) - margin.top - margin.bottom;
          }
        }

        wrap.select('.nv-legendWrap').attr('transform', 'translate(0,' + -margin.top + ')');
      }

      //------------------------------------------------------------

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      //------------------------------------------------------------
      // Main Chart Component(s)

      pie.width(availableWidth).height(availableHeight);

      const pieWrap = g.select('.nv-pieWrap').datum([data]);

      selectSlices = pie.selectSlices;

      d3v3.transition(pieWrap).call(pie);

      //------------------------------------------------------------

      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------

      legend.dispatch.on('stateChange', newState => {
        state = newState;
        dispatch.stateChange(state);
        chart.update();
      });

      pie.dispatch.on('elementMouseout.tooltip', e => {
        dispatch.tooltipHide(e);
      });

      // Update chart from a state object passed to event handler
      dispatch.on('changeState', e => {
        if (typeof e.disabled !== 'undefined') {
          data.forEach((series, i) => {
            series.disabled = e.disabled[i];
          });

          state.disabled = e.disabled;
        }

        chart.update();
      });

      //============================================================
    });

    return chart;
  }

  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  pie.dispatch.on('elementMouseover.tooltip', e => {
    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  dispatch.on('tooltipShow', e => {
    if (tooltips) {
      showTooltip(e);
    }
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
  chart.legend = legend;
  chart.dispatch = dispatch;
  chart.pie = pie;

  d3v3.rebind(
    chart,
    pie,
    'valueFormat',
    'values',
    'x',
    'y',
    'description',
    'id',
    'showLabels',
    'donutLabelsOutside',
    'pieLabelsOutside',
    'labelType',
    'donut',
    'donutRatio',
    'labelThreshold'
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
    legend.color(color);
    pie.color(color);
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) {
      return showLegend;
    }
    showLegend = _;
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

  chart.state = function(_) {
    if (!arguments.length) {
      return state;
    }
    state = _;
    return chart;
  };

  chart.defaultState = function(_) {
    if (!arguments.length) {
      return defaultState;
    }
    defaultState = _;
    return chart;
  };

  chart.noData = function(_) {
    if (!arguments.length) {
      return noData;
    }
    noData = _;
    return chart;
  };

  chart.selectSlices = function(args) {
    if (!arguments.length) {
      return selectSlices;
    }
    selectSlices(args);
    return chart;
  };

  //============================================================

  return chart;
};
