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

nv.models.legend = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const margin = { top: 5, right: 0, bottom: 5, left: 0 };
  let width = 400,
    height = 20,
    getKey = function(d) {
      return d.key;
    },
    color = nv.utils.defaultColor(),
    align = true,
    rightAlign = true,
    updateState = true, //If true, legend will update data.disabled and trigger a 'stateChange' dispatch.
    radioButtonMode = false; //If true, clicking legend items will cause it to behave like a radio button. (only one can be selected at a time)

  const dispatch = d3v3.dispatch(
    'legendClick',
    'legendDblclick',
    'legendMouseover',
    'legendMouseout',
    'stateChange'
  );
  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const availableWidth = width - margin.left - margin.right,
        container = d3v3.select(this);

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-legend').data([data]);
      wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-legend')
        .append('g');
      const g = wrap.select('g');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      //------------------------------------------------------------

      const series = g.selectAll('.nv-series').data(d => {
        return d;
      });
      const seriesEnter = series
        .enter()
        .append('g')
        .attr('class', 'nv-series')
        .on('mouseover', (d, i) => {
          dispatch.legendMouseover(d, i); //TODO: Make consistent with other event objects
        })
        .on('mouseout', (d, i) => {
          dispatch.legendMouseout(d, i);
        })
        .on('click', (d, i) => {
          dispatch.legendClick(d, i);
          if (updateState) {
            if (radioButtonMode) {
              //Radio button mode: set every series to disabled,
              //  and enable the clicked series.
              data.forEach(series => {
                series.disabled = true;
              });
              d.disabled = false;
            } else {
              d.disabled = !d.disabled;
              if (
                data.every(series => {
                  return series.disabled;
                })
              ) {
                //the default behavior of NVD3 legends is, if every single series
                // is disabled, turn all series' back on.
                data.forEach(series => {
                  series.disabled = false;
                });
              }
            }
            dispatch.stateChange({
              disabled: data.map(d => {
                return !!d.disabled;
              })
            });
          }
        })
        .on('dblclick', (d, i) => {
          dispatch.legendDblclick(d, i);
          if (updateState) {
            //the default behavior of NVD3 legends, when double clicking one,
            // is to set all other series' to false, and make the double clicked series enabled.
            data.forEach(series => {
              series.disabled = true;
            });
            d.disabled = false;
            dispatch.stateChange({
              disabled: data.map(d => {
                return !!d.disabled;
              })
            });
          }
        });
      seriesEnter
        .append('circle')
        .style('stroke-width', 2)
        .attr('class', 'nv-legend-symbol')
        .attr('r', 5)
        .style('display', d => {
          return d.checkbox ? 'none' : 'inline';
        });

      seriesEnter
        .append('rect')
        .style('stroke-width', 2)
        .attr('class', 'nv-legend-symbol')
        .attr('width', 10)
        .attr('height', 10)
        .attr('transform', 'translate(-5,-5)')
        .style('display', d => {
          return d.checkbox ? 'inline' : 'none';
        });

      seriesEnter
        .append('text')
        .attr('text-anchor', 'start')
        .attr('class', 'nv-legend-text')
        .attr('dy', '.32em')
        .attr('dx', '8');
      series.classed('disabled', d => {
        return d.disabled;
      });
      series.exit().remove();
      series
        .select('circle')
        .style('fill', (d, i) => {
          return d.color || color(d, i);
        })
        .style('stroke', (d, i) => {
          return d.color || color(d, i);
        });
      series
        .select('rect')
        .style('fill', (d, i) => {
          return d.color || color(d, i);
        })
        .style('stroke', (d, i) => {
          return d.color || color(d, i);
        });
      series.select('text').text(getKey);

      //TODO: implement fixed-width and max-width options (max-width is especially useful with the align option)

      // NEW ALIGNING CODE, TODO: clean up
      if (align) {
        const seriesWidths = [];
        series.each(function() {
          const legendText = d3v3.select(this).select('text');
          let nodeTextLength;
          try {
            nodeTextLength = legendText.getComputedTextLength();
            // If the legendText is display:none'd (nodeTextLength == 0), simulate an error so we approximate, instead
            if (nodeTextLength <= 0) {
              throw Error();
            }
          } catch (e) {
            nodeTextLength = nv.utils.calcApproxTextWidth(legendText);
          }

          seriesWidths.push(nodeTextLength + 28); // 28 is ~ the width of the circle plus some padding
        });

        let seriesPerRow = 0;
        let legendWidth = 0;
        let columnWidths = [];

        while (legendWidth < availableWidth && seriesPerRow < seriesWidths.length) {
          columnWidths[seriesPerRow] = seriesWidths[seriesPerRow];
          legendWidth += seriesWidths[seriesPerRow++];
        }
        if (seriesPerRow === 0) {
          seriesPerRow = 1;
        } //minimum of one series per row

        while (legendWidth > availableWidth && seriesPerRow > 1) {
          columnWidths = [];
          seriesPerRow--;

          for (let k = 0; k < seriesWidths.length; k++) {
            if (seriesWidths[k] > (columnWidths[k % seriesPerRow] || 0)) {
              columnWidths[k % seriesPerRow] = seriesWidths[k];
            }
          }

          legendWidth = columnWidths.reduce((prev, cur) => {
            return prev + cur;
          });
        }

        const xPositions = [];
        for (let i = 0, curX = 0; i < seriesPerRow; i++) {
          xPositions[i] = curX;
          curX += columnWidths[i];
        }

        series.attr('transform', (d, i) => {
          return (
            'translate(' +
            xPositions[i % seriesPerRow] +
            ',' +
            (5 + Math.floor(i / seriesPerRow) * 20) +
            ')'
          );
        });

        //position legend as far right as possible within the total width
        if (rightAlign) {
          g.attr(
            'transform',
            'translate(' +
              nv.utils.NaNtoZero(width - margin.right - legendWidth) +
              ',' +
              margin.top +
              ')'
          );
        } else {
          g.attr('transform', 'translate(0' + ',' + margin.top + ')');
        }

        height = margin.top + margin.bottom + Math.ceil(seriesWidths.length / seriesPerRow) * 20;
      } else {
        let ypos = 5,
          newxpos = 5,
          maxwidth = 0,
          xpos;
        series.attr('transform', function() {
          const length =
            d3v3
              .select(this)
              .select('text')
              .node()
              .getComputedTextLength() + 28;
          xpos = newxpos;

          if (width < margin.left + margin.right + xpos + length) {
            newxpos = xpos = 5;
            ypos += 20;
          }

          newxpos += length;
          if (newxpos > maxwidth) {
            maxwidth = newxpos;
          }

          return 'translate(' + xpos + ',' + ypos + ')';
        });

        //position legend as far right as possible within the total width
        g.attr(
          'transform',
          'translate(' + (width - margin.right - maxwidth) + ',' + margin.top + ')'
        );

        height = margin.top + margin.bottom + ypos + 15;
      }
    });

    return chart;
  }

  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  chart.dispatch = dispatch;
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

  chart.key = function(_) {
    if (!arguments.length) {
      return getKey;
    }
    getKey = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) {
      return color;
    }
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.align = function(_) {
    if (!arguments.length) {
      return align;
    }
    align = _;
    return chart;
  };

  chart.rightAlign = function(_) {
    if (!arguments.length) {
      return rightAlign;
    }
    rightAlign = _;
    return chart;
  };

  chart.updateState = function(_) {
    if (!arguments.length) {
      return updateState;
    }
    updateState = _;
    return chart;
  };

  chart.radioButtonMode = function(_) {
    if (!arguments.length) {
      return radioButtonMode;
    }
    radioButtonMode = _;
    return chart;
  };

  //============================================================

  return chart;
};
