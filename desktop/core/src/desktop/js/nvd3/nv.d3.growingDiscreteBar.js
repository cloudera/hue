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

//TODO: consider deprecating by adding necessary features to multiBar model
nv.models.growingDiscreteBar = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const margin = { top: 0, right: 0, bottom: 0, left: 0 };
  let width = 960,
    height = 500,
    id = Math.floor(Math.random() * 10000), //Create semi-unique ID in case user doesn't select one
    x = d3v3.scale.ordinal(),
    y = d3v3.scale.linear(),
    getX = function(d) {
      return d.x;
    },
    getY = function(d) {
      return d.y;
    },
    forceY = [0], // 0 is forced by default.. this makes sense for the majority of bar graphs... user can always do chart.forceY([]) to remove
    color = nv.utils.defaultColor(),
    showValues = false,
    valueFormat = d3v3.format(',.2f'),
    xDomain,
    yDomain,
    xRange,
    yRange,
    rectClass = 'discreteBar',
    selectBars = null;

  const dispatch = d3v3.dispatch(
    'chartClick',
    'elementClick',
    'elementDblClick',
    'elementMouseover',
    'elementMouseout'
  );
  //============================================================

  //============================================================
  // Private Variables
  //------------------------------------------------------------

  let x0, y0;

  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const availableWidth = width - margin.left - margin.right,
        availableHeight = height - margin.top - margin.bottom,
        container = d3v3.select(this);

      //add series index to each data point for reference
      data.forEach((series, i) => {
        series.values.forEach(point => {
          point.series = i;
          point.seriesKey = series.key;
        });
      });

      //------------------------------------------------------------
      // Setup Scales

      // remap and flatten the data for use in calculating the scales' domains
      const seriesData =
        xDomain && yDomain
          ? [] // if we know xDomain and yDomain, no need to calculate
          : data.map(d => {
              return d.values.map((d, i) => {
                return { x: getX(d, i), y: getY(d, i), y0: d.y0 };
              });
            });

      x.domain(
        xDomain ||
          d3v3.merge(seriesData).map(d => {
            return d.x;
          })
      ).rangeBands(xRange || [0, availableWidth], 0.1);

      y.domain(
        yDomain ||
          d3v3.extent(
            d3v3
              .merge(seriesData)
              .map(d => {
                return d.y;
              })
              .concat(forceY)
          )
      );

      // If showValues, pad the Y axis range to account for label height
      if (showValues) {
        y.range(
          yRange || [availableHeight - (y.domain()[0] < 0 ? 12 : 0), y.domain()[1] > 0 ? 12 : 0]
        );
      } else {
        y.range(yRange || [availableHeight, 0]);
      }

      //store old scales if they exist
      x0 = x0 || x;
      y0 = y0 || y.copy().range([y(0), y(0)]);

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-wrap.nv-discretebar').data([data]);
      const wrapEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-discretebar');
      const gEnter = wrapEnter.append('g');
      wrap.select('g');

      gEnter.append('g').attr('class', 'nv-groups');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      //------------------------------------------------------------

      //TODO: by definition, the discrete bar should not have multiple groups, will modify/remove later
      const groups = wrap
        .select('.nv-groups')
        .selectAll('.nv-group')
        .data(
          d => {
            return d;
          },
          d => {
            return d.key;
          }
        );
      groups
        .enter()
        .append('g')
        .style('stroke-opacity', 1e-6)
        .style('fill-opacity', 1e-6);
      groups
        .exit()
        .transition()
        .style('stroke-opacity', 1e-6)
        .style('fill-opacity', 1e-6)
        .remove();
      groups
        .attr('class', (d, i) => {
          return 'nv-group nv-series-' + i;
        })
        .classed('hover', d => {
          return d.hover;
        });
      groups
        .transition()
        .style('stroke-opacity', 1)
        .style('fill-opacity', 0.75);

      const bars = groups
        .selectAll('g.nv-bar')
        .data(d => {
          return d.values;
        })
        .classed('selected', false);

      bars.exit().remove();

      selectBars = function(selected) {
        $(selected).each((cnt, item) => {
          bars.each(function(d) {
            if (d.x === item) {
              d3v3.select(this).classed('selected', true);
            }
          });
        });
      };

      const barsEnter = bars
        .enter()
        .append('g')
        .attr('transform', (d, i) => {
          return 'translate(' + (x(getX(d, i)) + x.rangeBand() * 0.05) + ', ' + y(0) + ')';
        })
        .on('mouseover', function(d, i) {
          //TODO: figure out why j works above, but not here
          d3v3.select(this).classed('hover', true);
          dispatch.elementMouseover({
            value: getY(d, i),
            point: d,
            series: data[d.series],
            pos: [x(getX(d, i)) + (x.rangeBand() * (d.series + 0.5)) / data.length, y(getY(d, i))], // TODO: Figure out why the value appears to be shifted
            pointIndex: i,
            seriesIndex: d.series,
            e: d3v3.event
          });
        })
        .on('mouseout', function(d, i) {
          d3v3.select(this).classed('hover', false);
          dispatch.elementMouseout({
            value: getY(d, i),
            point: d,
            series: data[d.series],
            pointIndex: i,
            seriesIndex: d.series,
            e: d3v3.event
          });
        })
        .on('click', (d, i) => {
          dispatch.elementClick({
            value: getY(d, i),
            point: d,
            series: data[d.series],
            pos: [x(getX(d, i)) + (x.rangeBand() * (d.series + 0.5)) / data.length, y(getY(d, i))], // TODO: Figure out why the value appears to be shifted
            pointIndex: i,
            seriesIndex: d.series,
            e: d3v3.event
          });
          d3v3.event.stopPropagation();
        })
        .on('dblclick', (d, i) => {
          dispatch.elementDblClick({
            value: getY(d, i),
            point: d,
            series: data[d.series],
            pos: [x(getX(d, i)) + (x.rangeBand() * (d.series + 0.5)) / data.length, y(getY(d, i))], // TODO: Figure out why the value appears to be shifted
            pointIndex: i,
            seriesIndex: d.series,
            e: d3v3.event
          });
          d3v3.event.stopPropagation();
        });

      barsEnter
        .append('rect')
        .attr('height', 0)
        .attr('x', (d, i, j) => {
          return (j * x.rangeBand()) / data.length;
        })
        .attr('width', x.rangeBand() / data.length);

      if (showValues) {
        barsEnter.append('text').attr('text-anchor', 'middle');

        bars
          .select('text')
          .text((d, i) => {
            return valueFormat(getY(d, i));
          })
          .transition()
          .attr('x', (d, i, j) => {
            return (j * x.rangeBand()) / data.length + (x.rangeBand() * 0.9) / data.length / 2;
          })
          .attr('y', (d, i) => {
            return getY(d, i) < 0 ? y(getY(d, i)) - y(0) + 12 : -4;
          });
      } else {
        bars.selectAll('text').remove();
      }

      bars
        .attr('class', (d, i) => {
          return getY(d, i) < 0 ? 'nv-bar negative' : 'nv-bar positive';
        })
        .style('fill', (d, i) => {
          return d.color || color(d, i);
        })
        .style('stroke', (d, i) => {
          return d.color || color(d, i);
        })
        .select('rect')
        .attr('class', rectClass)
        .transition()
        .attr('x', d => {
          return (d.series * x.rangeBand()) / data.length;
        })
        .attr('width', (x.rangeBand() / data.length) * 0.9);
      bars
        .transition()
        .attr('transform', (d, i) => {
          const left = x(getX(d, i)) + x.rangeBand() * 0.05,
            top =
              getY(d, i) < 0
                ? y(0)
                : y(0) - y(getY(d, i)) < 1
                ? y(0) - 1 //make 1 px positive bars show up above y=0
                : y(getY(d, i));

          return 'translate(' + left + ', ' + top + ')';
        })
        .select('rect')
        .attr('height', (d, i) => {
          return Math.max(Math.abs(y(getY(d, i)) - y((yDomain && yDomain[0]) || 0)) || 1);
        });

      //store old scales for use in transitions on update
      x0 = x.copy();
      y0 = y.copy();
    });

    return chart;
  }

  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  chart.dispatch = dispatch;

  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.x = function(val) {
    if (!arguments.length) {
      return getX;
    }
    getX = val;
    return chart;
  };

  chart.y = function(val) {
    if (!arguments.length) {
      return getY;
    }
    getY = val;
    return chart;
  };

  chart.margin = function(val) {
    if (!arguments.length) {
      return margin;
    }
    margin.top = typeof val.top != 'undefined' ? val.top : margin.top;
    margin.right = typeof val.right != 'undefined' ? val.right : margin.right;
    margin.bottom = typeof val.bottom != 'undefined' ? val.bottom : margin.bottom;
    margin.left = typeof val.left != 'undefined' ? val.left : margin.left;
    return chart;
  };

  chart.width = function(val) {
    if (!arguments.length) {
      return width;
    }
    width = val;
    return chart;
  };

  chart.height = function(val) {
    if (!arguments.length) {
      return height;
    }
    height = val;
    return chart;
  };

  chart.xScale = function(val) {
    if (!arguments.length) {
      return x;
    }
    x = val;
    return chart;
  };

  chart.yScale = function(val) {
    if (!arguments.length) {
      return y;
    }
    y = val;
    return chart;
  };

  chart.xDomain = function(val) {
    if (!arguments.length) {
      return xDomain;
    }
    xDomain = val;
    return chart;
  };

  chart.yDomain = function(val) {
    if (!arguments.length) {
      return yDomain;
    }
    yDomain = val;
    return chart;
  };

  chart.xRange = function(val) {
    if (!arguments.length) {
      return xRange;
    }
    xRange = val;
    return chart;
  };

  chart.yRange = function(val) {
    if (!arguments.length) {
      return yRange;
    }
    yRange = val;
    return chart;
  };

  chart.forceY = function(val) {
    if (!arguments.length) {
      return forceY;
    }
    forceY = val;
    return chart;
  };

  chart.color = function(val) {
    if (!arguments.length) {
      return color;
    }
    color = nv.utils.getColor(val);
    return chart;
  };

  chart.id = function(val) {
    if (!arguments.length) {
      return id;
    }
    id = val;
    return chart;
  };

  chart.showValues = function(val) {
    if (!arguments.length) {
      return showValues;
    }
    showValues = val;
    return chart;
  };

  chart.valueFormat = function(val) {
    if (!arguments.length) {
      return valueFormat;
    }
    valueFormat = val;
    return chart;
  };

  chart.rectClass = function(val) {
    if (!arguments.length) {
      return rectClass;
    }
    rectClass = val;
    return chart;
  };

  chart.selectBars = function(args) {
    if (!arguments.length) {
      return selectBars;
    }
    selectBars(args);
    return chart;
  };
  //============================================================

  return chart;
};
