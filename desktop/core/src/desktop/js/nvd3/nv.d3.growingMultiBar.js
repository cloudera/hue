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

nv.models.growingMultiBar = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const margin = { top: 0, right: 0, bottom: 0, left: 0 };
  let width = 960,
    height = 500,
    x = d3v3.scale.ordinal(),
    y = d3v3.scale.linear(),
    id = Math.floor(Math.random() * 10000), //Create semi-unique ID in case user doesn't select one
    getX = function(d) {
      return d.x;
    },
    getY = function(d) {
      return d.y;
    },
    forceY = [0], // 0 is forced by default.. this makes sense for the majority of bar graphs... user can always do chart.forceY([]) to remove
    clipEdge = true,
    stacked = false,
    stackOffset = 'zero', // options include 'silhouette', 'wiggle', 'expand', 'zero', or a custom function
    color = nv.utils.defaultColor(),
    hideable = false,
    barColor = null, // adding the ability to set the color for each rather than the whole group
    disabled, // used in conjunction with barColor to communicate from multiBarHorizontalChart what series are disabled
    delay = 0,
    xDomain,
    yDomain,
    xRange,
    yRange,
    groupSpacing = 0.1,
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

  let x0, y0; //used to store previous scales

  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const availableWidth = width - margin.left - margin.right,
        availableHeight = height - margin.top - margin.bottom,
        container = d3v3.select(this);

      if (hideable && data.length) {
        hideable = [
          {
            values: data[0].values.map(d => {
              return {
                x: d.x,
                y: 0,
                series: d.series,
                size: 0.01
              };
            })
          }
        ];
      }

      if (stacked) {
        data = d3v3.layout
          .stack()
          .offset(stackOffset)
          .values(d => {
            return d.values;
          })
          .y(getY)(!data.length && hideable ? hideable : data);
      }

      //add series index to each data point for reference
      data.forEach((series, i) => {
        series.values.forEach(point => {
          point.series = i;
          point.seriesKey = series.key;
        });
      });

      //------------------------------------------------------------
      // HACK for negative value stacking
      if (stacked) {
        data[0].values.map((d, i) => {
          let posBase = 0,
            negBase = 0;
          data.map(d => {
            const f = d.values[i];
            if (typeof f != 'undefined') {
              f.size = Math.abs(f.y);
              if (f.y < 0) {
                f.y1 = negBase;
                negBase = negBase - f.size;
              } else {
                f.y1 = f.size + posBase;
                posBase = posBase + f.size;
              }
            }
          });
        });
      }

      //------------------------------------------------------------
      // Setup Scales

      // remap and flatten the data for use in calculating the scales' domains
      const seriesData =
        xDomain && yDomain
          ? [] // if we know xDomain and yDomain, no need to calculate
          : data.map(d => {
              return d.values.map((d, i) => {
                return { x: getX(d, i), y: getY(d, i), y0: d.y0, y1: d.y1 };
              });
            });

      x.domain(
        xDomain ||
          d3v3.merge(seriesData).map(d => {
            return d.x;
          })
      ).rangeBands(xRange || [0, availableWidth], groupSpacing);

      //y   .domain(yDomain || d3v3.extent(d3v3.merge(seriesData).map(function(d) { return d.y + (stacked ? d.y1 : 0) }).concat(forceY)))
      y.domain(
        yDomain ||
          d3v3.extent(
            d3v3
              .merge(seriesData)
              .map(d => {
                return stacked ? (d.y > 0 ? d.y1 : d.y1 + d.y) : d.y;
              })
              .concat(forceY)
          )
      ).range(yRange || [availableHeight, 0]);

      // If scale's domain don't have a range, slightly adjust to make one... so a chart can show a single data point
      if (x.domain()[0] === x.domain()[1]) {
        x.domain()[0]
          ? x.domain([x.domain()[0] - x.domain()[0] * 0.01, x.domain()[1] + x.domain()[1] * 0.01])
          : x.domain([-1, 1]);
      }

      if (y.domain()[0] === y.domain()[1]) {
        y.domain()[0]
          ? y.domain([y.domain()[0] + y.domain()[0] * 0.01, y.domain()[1] - y.domain()[1] * 0.01])
          : y.domain([-1, 1]);
      }

      x0 = x0 || x;
      y0 = y0 || y;

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-wrap.nv-multibar').data([data]);
      const wrapEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-multibar');
      const defsEnter = wrapEnter.append('defs');
      const gEnter = wrapEnter.append('g');
      const g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-groups');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      //------------------------------------------------------------

      defsEnter
        .append('clipPath')
        .attr('id', 'nv-edge-clip-' + id)
        .append('rect');
      wrap
        .select('#nv-edge-clip-' + id + ' rect')
        .attr('width', availableWidth)
        .attr(
          'height',
          nv.utils.NaNtoZero(availableHeight) >= 0 ? nv.utils.NaNtoZero(availableHeight) : 0
        );

      g.attr('clip-path', clipEdge ? 'url(#nv-edge-clip-' + id + ')' : '');

      const groups = wrap
        .select('.nv-groups')
        .selectAll('.nv-group')
        .data(
          d => {
            return d;
          },
          (d, i) => {
            return i;
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
        .selectAll('rect.nv-bar')
        .delay((d, i) => {
          return (i * delay) / data[0].values.length;
        })
        .attr('y', d => {
          return stacked ? y0(d.y0) : y0(0);
        })
        .attr('height', 0)
        .remove();
      groups
        .attr('class', (d, i) => {
          return 'nv-group nv-series-' + i;
        })
        .classed('hover', d => {
          return d.hover;
        })
        .style('fill', (d, i) => {
          return color(d, i);
        })
        .style('stroke', (d, i) => {
          return color(d, i);
        });
      groups
        .transition()
        .style('stroke-opacity', 1)
        .style('fill-opacity', 0.75);

      const bars = groups
        .selectAll('rect.nv-bar')
        .data(d => {
          return hideable && !data.length ? hideable.values : d.values;
        })
        .classed('selected', false);

      bars.exit().remove();

      selectBars = function(selected) {
        if (selected.rangeValues) {
          $(selected.rangeValues).each((cnt, item) => {
            bars.each(function(d) {
              if (parseInt(d.x) >= parseInt(item.from) && parseInt(d.x_end) <= parseInt(item.to)) {
                d3v3.select(this).classed('selected', true);
              }
            });
          });
        } else {
          let _pivotField = null;
          if (!Array.isArray(selected)) {
            _pivotField = selected.field;
            selected = selected.selected;
          }

          $(selected).each((cnt, item) => {
            bars.each(function(d) {
              if (_pivotField != null) {
                if (
                  (Array.isArray(_pivotField)
                    ? ko.toJSON(d.obj.fq_fields) === ko.toJSON(_pivotField)
                    : d.obj.fq_fields === _pivotField) &&
                  (item.values
                    ? ko.toJSON(d.obj.fq_values) === ko.toJSON(item.values)
                    : d.obj.fq_values === item)
                ) {
                  d3v3.select(this).classed('selected', true);
                }
              } else if (d.x instanceof Date) {
                if (
                  moment(d.x)
                    .utc()
                    .format('YYYY-MM-DD[T]HH:mm:ss[Z]') === item
                ) {
                  d3v3.select(this).classed('selected', true);
                }
              } else if (d.x === item) {
                d3v3.select(this).classed('selected', true);
              }
            });
          });
        }
      };

      const barsEnter = bars
        .enter()
        .append('rect')
        .attr('class', (d, i) => {
          return getY(d, i) < 0 ? 'nv-bar negative' : 'nv-bar positive';
        })
        .attr('x', (d, i, j) => {
          return stacked ? 0 : (j * x.rangeBand()) / data.length;
        })
        .attr('y', d => {
          return y0(stacked ? d.y0 : 0);
        })
        .attr('height', 0)
        .attr('width', x.rangeBand() / (stacked ? 1 : data.length))
        .attr('transform', (d, i) => {
          return 'translate(' + x(getX(d, i)) + ',0)';
        });
      bars
        .style('fill', (d, i, j) => {
          return color(d, j, i);
        })
        .style('stroke', (d, i, j) => {
          return color(d, j, i);
        });
      barsEnter
        .on('mouseover', function(d, i) {
          d3v3.select(this).classed('hover', true);
          dispatch.elementMouseover({
            value: getY(d, i),
            point: d,
            series: data[d.series],
            pos: [
              x(getX(d, i)) +
                (x.rangeBand() * (stacked ? data.length / 2 : d.series + 0.5)) / data.length,
              y(getY(d, i) + (stacked ? d.y0 : 0))
            ], // TODO: Figure out why the value appears to be shifted
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
            pos: [
              x(getX(d, i)) +
                (x.rangeBand() * (stacked ? data.length / 2 : d.series + 0.5)) / data.length,
              y(getY(d, i) + (stacked ? d.y0 : 0))
            ], // TODO: Figure out why the value appears to be shifted
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
            pos: [
              x(getX(d, i)) +
                (x.rangeBand() * (stacked ? data.length / 2 : d.series + 0.5)) / data.length,
              y(getY(d, i) + (stacked ? d.y0 : 0))
            ], // TODO: Figure out why the value appears to be shifted
            pointIndex: i,
            seriesIndex: d.series,
            e: d3v3.event
          });
          d3v3.event.stopPropagation();
        });
      bars
        .attr('class', (d, i) => {
          return getY(d, i) < 0 ? 'nv-bar negative' : 'nv-bar positive';
        })
        .transition()
        .attr('transform', (d, i) => {
          return 'translate(' + x(getX(d, i)) + ',0)';
        });

      if (barColor) {
        if (!disabled) {
          disabled = data.map(() => {
            return true;
          });
        }
        bars
          .style('fill', (d, i, j) => {
            return d3v3
              .rgb(barColor(d, i))
              .darker(
                disabled
                  .map((d, i) => {
                    return i;
                  })
                  .filter((d, i) => {
                    return !disabled[i];
                  })[j]
              )
              .toString();
          })
          .style('stroke', (d, i, j) => {
            return d3v3
              .rgb(barColor(d, i))
              .darker(
                disabled
                  .map((d, i) => {
                    return i;
                  })
                  .filter((d, i) => {
                    return !disabled[i];
                  })[j]
              )
              .toString();
          });
      }

      if (stacked) {
        bars
          .transition()
          .delay((d, i) => {
            return (i * delay) / data[0].values.length;
          })
          .attr('y', d => {
            return y(stacked ? d.y1 : 0);
          })
          .attr('height', d => {
            return Math.max(Math.abs(y(d.y + (stacked ? d.y0 : 0)) - y(stacked ? d.y0 : 0)), 1);
          })
          .attr('x', d => {
            return stacked ? 0 : (d.series * x.rangeBand()) / data.length;
          })
          .attr('width', x.rangeBand() / (stacked ? 1 : data.length));
      } else {
        bars
          .transition()
          .delay((d, i) => {
            return (i * delay) / data[0].values.length;
          })
          .attr('x', d => {
            return (d.series * x.rangeBand()) / data.length;
          })
          .attr('width', x.rangeBand() / data.length)
          .attr('y', (d, i) => {
            return getY(d, i) < 0 ? y(0) : y(0) - y(getY(d, i)) < 1 ? y(0) - 1 : y(getY(d, i)) || 0;
          })
          .attr('height', (d, i) => {
            return Math.max(Math.abs(y(getY(d, i)) - y(0)), 1) || 0;
          });
      }

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

  chart.x = function(_) {
    if (!arguments.length) {
      return getX;
    }
    getX = _;
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) {
      return getY;
    }
    getY = _;
    return chart;
  };

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

  chart.xScale = function(_) {
    if (!arguments.length) {
      return x;
    }
    x = _;
    return chart;
  };

  chart.yScale = function(_) {
    if (!arguments.length) {
      return y;
    }
    y = _;
    return chart;
  };

  chart.xDomain = function(_) {
    if (!arguments.length) {
      return xDomain;
    }
    xDomain = _;
    return chart;
  };

  chart.yDomain = function(_) {
    if (!arguments.length) {
      return yDomain;
    }
    yDomain = _;
    return chart;
  };

  chart.xRange = function(_) {
    if (!arguments.length) {
      return xRange;
    }
    xRange = _;
    return chart;
  };

  chart.yRange = function(_) {
    if (!arguments.length) {
      return yRange;
    }
    yRange = _;
    return chart;
  };

  chart.forceY = function(_) {
    if (!arguments.length) {
      return forceY;
    }
    forceY = _;
    return chart;
  };

  chart.stacked = function(_) {
    if (!arguments.length) {
      return stacked;
    }
    stacked = _;
    return chart;
  };

  chart.stackOffset = function(_) {
    if (!arguments.length) {
      return stackOffset;
    }
    stackOffset = _;
    return chart;
  };

  chart.clipEdge = function(_) {
    if (!arguments.length) {
      return clipEdge;
    }
    clipEdge = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) {
      return color;
    }
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.barColor = function(_) {
    if (!arguments.length) {
      return barColor;
    }
    barColor = nv.utils.getColor(_);
    return chart;
  };

  chart.disabled = function(_) {
    if (!arguments.length) {
      return disabled;
    }
    disabled = _;
    return chart;
  };

  chart.id = function(_) {
    if (!arguments.length) {
      return id;
    }
    id = _;
    return chart;
  };

  chart.hideable = function(_) {
    if (!arguments.length) {
      return hideable;
    }
    hideable = _;
    return chart;
  };

  chart.delay = function(_) {
    if (!arguments.length) {
      return delay;
    }
    delay = _;
    return chart;
  };

  chart.groupSpacing = function(_) {
    if (!arguments.length) {
      return groupSpacing;
    }
    groupSpacing = _;
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
