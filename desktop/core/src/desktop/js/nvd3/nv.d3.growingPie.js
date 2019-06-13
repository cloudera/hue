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

nv.models.growingPie = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const margin = { top: 0, right: 0, bottom: 0, left: 0 };
  let width = 500,
    height = 500,
    getX = function(d) {
      return d.x;
    },
    getY = function(d) {
      return d.y;
    },
    getDescription = function(d) {
      return d.description;
    },
    id = Math.floor(Math.random() * 10000), //Create semi-unique ID in case user doesn't select one
    color = nv.utils.defaultColor(),
    valueFormat = d3v3.format(',.2f'),
    showLabels = true,
    pieLabelsOutside = true,
    donutLabelsOutside = false,
    labelType = 'key',
    labelThreshold = 0.02, //if slice percentage is under this, don't show label
    donut = false,
    labelSunbeamLayout = false,
    startAngle = false,
    endAngle = false,
    donutRatio = 0.5,
    selectSlices = null;

  const dispatch = d3v3.dispatch(
    'chartClick',
    'elementClick',
    'elementDblClick',
    'elementMouseover',
    'elementMouseout'
  );
  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      let availableWidth = width - margin.left - margin.right,
        availableHeight = height - margin.top - margin.bottom,
        radius = Math.min(availableWidth, availableHeight) / 2,
        arcRadius = radius - radius / 5;
      const container = d3v3.select(this);

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      //let wrap = container.selectAll('.nv-wrap.nv-pie').data([data]);
      const wrap = container.selectAll('.nv-wrap.nv-pie').data(data);
      const wrapEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-pie nv-chart-' + id);
      const gEnter = wrapEnter.append('g');
      const g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-pie');
      gEnter.append('g').attr('class', 'nv-pieLabels');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
      g.select('.nv-pie').attr(
        'transform',
        'translate(' + availableWidth / 2 + ',' + availableHeight / 2 + ')'
      );
      g.select('.nv-pieLabels').attr(
        'transform',
        'translate(' + availableWidth / 2 + ',' + availableHeight / 2 + ')'
      );

      //------------------------------------------------------------

      container.on('click', (d, i) => {
        dispatch.chartClick({
          data: d,
          index: i,
          pos: d3v3.event,
          id: id
        });
      });

      function updateVariables() {
        availableWidth = width - margin.left - margin.right;
        availableHeight = height - margin.top - margin.bottom;
        radius = Math.min(availableWidth, availableHeight) / 2;
        arcRadius = radius - radius / 5;
      }

      const arcNormal = function() {
        updateVariables();
        return d3v3.svg.arc().outerRadius(arcRadius);
      };

      const arcOver = function() {
        updateVariables();
        return d3v3.svg.arc().outerRadius(arcRadius + 10);
      };

      if (startAngle) {
        arcNormal().startAngle(startAngle);
      }
      if (endAngle) {
        arcNormal().endAngle(endAngle);
      }
      if (donut) {
        arcNormal().innerRadius(radius * donutRatio);
      }

      // Setup the Pie chart and choose the data element
      const pie = d3v3.layout
        .pie()
        .sort(null)
        .value(d => {
          return d.disabled ? 0 : getY(d);
        });

      const slices = wrap
        .select('.nv-pie')
        .selectAll('.nv-slice')
        .data(pie)
        .classed('selected', false);

      const pieLabels = wrap
        .select('.nv-pieLabels')
        .selectAll('.nv-label')
        .data(pie);

      slices.exit().remove();
      pieLabels.exit().remove();

      selectSlices = function(selected) {
        $(selected).each((cnt, item) => {
          slices.each(function(d) {
            if (
              (typeof d.data.obj.from != 'undefined' && d.data.obj.from === item) ||
              d.data.obj.value === item
            ) {
              d3v3.select(this).classed('selected', true);
              d3v3
                .select(this)
                .select('path')
                .transition()
                .duration(100)
                .attr('d', arcOver());
            }
          });
        });
      };

      const ae = slices
        .enter()
        .append('g')
        .attr('class', 'nv-slice')
        .on('mouseover', function(d, i) {
          d3v3
            .select(this)
            .select('path')
            .transition()
            .duration(100)
            .attr('d', arcOver());
          d3v3.select(this).classed('hover', true);
          dispatch.elementMouseover({
            label: getX(d.data),
            value: getY(d.data),
            point: d.data,
            pointIndex: i,
            pos: [d3v3.event.pageX, d3v3.event.pageY],
            id: id
          });
        })
        .on('mouseout', function(d, i) {
          if (!d3v3.select(this).classed('selected')) {
            d3v3
              .select(this)
              .select('path')
              .transition()
              .duration(100)
              .attr('d', arcNormal());
          }
          d3v3.select(this).classed('hover', false);
          dispatch.elementMouseout({
            label: getX(d.data),
            value: getY(d.data),
            point: d.data,
            index: i,
            id: id
          });
        })
        .on('click', function(d, i) {
          d3v3
            .select(this)
            .select('path')
            .transition()
            .duration(100)
            .attr('d', arcOver());
          dispatch.elementClick({
            label: getX(d.data),
            value: getY(d.data),
            point: d.data,
            index: i,
            pos: d3v3.event,
            id: id
          });
          d3v3.event.stopPropagation();
        })
        .on('dblclick', function(d, i) {
          d3v3
            .select(this)
            .select('path')
            .transition()
            .duration(100)
            .attr('d', arcNormal());
          dispatch.elementDblClick({
            label: getX(d.data),
            value: getY(d.data),
            point: d.data,
            index: i,
            pos: d3v3.event,
            id: id
          });
          d3v3.event.stopPropagation();
        });

      slices
        .attr('fill', (d, i) => {
          return d.data.color || color(d, i);
        })
        .attr('stroke', (d, i) => {
          return d.data.color || color(d, i);
        });

      ae.append('path').each(function(d) {
        this._current = d;
      });

      slices
        .select('path')
        .transition()
        .attr('d', arcNormal())
        .attrTween('d', arcTween);

      if (showLabels) {
        // This does the normal label
        let labelsArc = d3v3.svg.arc().innerRadius(0);

        if (pieLabelsOutside) {
          labelsArc = arcNormal();
        }

        if (donutLabelsOutside) {
          labelsArc = d3v3.svg.arc().outerRadius(d3v3.svg.arc().outerRadius());
        }

        pieLabels
          .enter()
          .append('g')
          .classed('nv-label', true)
          .each(function(d) {
            if (d.value > 0) {
              const group = d3v3.select(this);

              group.attr('transform', d => {
                if (labelSunbeamLayout) {
                  d.outerRadius = arcRadius + 10; // Set Outer Coordinate
                  d.innerRadius = arcRadius + 15; // Set Inner Coordinate
                  let rotateAngle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI);
                  if ((d.startAngle + d.endAngle) / 2 < Math.PI) {
                    rotateAngle -= 90;
                  } else {
                    rotateAngle += 90;
                  }
                  return 'translate(' + labelsArc.centroid(d) + ') rotate(' + rotateAngle + ')';
                } else {
                  d.outerRadius = radius + 10; // Set Outer Coordinate
                  d.innerRadius = radius + 15; // Set Inner Coordinate
                  return 'translate(' + labelsArc.centroid(d) + ')';
                }
              });

              group
                .append('rect')
                .style('stroke', '#fff')
                .style('fill', '#fff')
                .attr('rx', 3)
                .attr('ry', 3);

              group
                .append('text')
                .style(
                  'text-anchor',
                  labelSunbeamLayout
                    ? (d.startAngle + d.endAngle) / 2 < Math.PI
                      ? 'start'
                      : 'end'
                    : 'middle'
                ) //center the text on it's origin or begin/end if orthogonal aligned
                .style('fill', '#000');
            }
          });

        const labelLocationHash = {};
        const avgHeight = 14;
        const avgWidth = 140;
        const createHashKey = function(coordinates) {
          return (
            Math.floor(coordinates[0] / avgWidth) * avgWidth +
            ',' +
            Math.floor(coordinates[1] / avgHeight) * avgHeight
          );
        };
        pieLabels.transition().attr('transform', d => {
          if (d.value > 0) {
            if (labelSunbeamLayout) {
              d.outerRadius = arcRadius + 10; // Set Outer Coordinate
              d.innerRadius = arcRadius + 15; // Set Inner Coordinate
              let rotateAngle = ((d.startAngle + d.endAngle) / 2) * (180 / Math.PI);
              if ((d.startAngle + d.endAngle) / 2 < Math.PI) {
                rotateAngle -= 90;
              } else {
                rotateAngle += 90;
              }
              return 'translate(' + labelsArc.centroid(d) + ') rotate(' + rotateAngle + ')';
            } else {
              d.outerRadius = radius + 10; // Set Outer Coordinate
              d.innerRadius = radius + 15; // Set Inner Coordinate

              /*
                Overlapping pie labels are not good. What this attempts to do is, prevent overlapping.
                Each label location is hashed, and if a hash collision occurs, we assume an overlap.
                Adjust the label's y-position to remove the overlap.
                */
              const center = labelsArc.centroid(d);
              const hashKey = createHashKey(center);
              if (labelLocationHash[hashKey]) {
                center[1] -= avgHeight;
              }
              labelLocationHash[createHashKey(center)] = true;
              return 'translate(' + center + ')';
            }
          }
        });
        pieLabels
          .select('.nv-label text')
          .style('text-anchor', d => {
            if (d.value > 0) {
              if (labelSunbeamLayout) {
                return (d.startAngle + d.endAngle) / 2 < Math.PI ? 'start' : 'end'; //center the text on it's origin or begin/end if orthogonal aligned
              } else {
                return 'middle';
              }
            }
          })
          .text(d => {
            if (d.value > 0) {
              const percent = (d.endAngle - d.startAngle) / (2 * Math.PI);
              const labelTypes = {
                key: getX(d.data),
                value: getY(d.data),
                percent: d3v3.format('%')(percent)
              };
              return d.value && percent > labelThreshold ? labelTypes[labelType] : '';
            } else {
              return '';
            }
          });
      }

      function arcTween(a) {
        a.endAngle = isNaN(a.endAngle) ? 0 : a.endAngle;
        a.startAngle = isNaN(a.startAngle) ? 0 : a.startAngle;
        if (!donut) {
          a.innerRadius = 0;
        }
        const i = d3v3.interpolate(this._current, a);
        this._current = i(0);
        return function(t) {
          return arcNormal()(i(t));
        };
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

  chart.values = function() {
    nv.log('pie.values() is no longer supported.');
    return chart;
  };

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
    getY = d3v3.functor(_);
    return chart;
  };

  chart.description = function(_) {
    if (!arguments.length) {
      return getDescription;
    }
    getDescription = _;
    return chart;
  };

  chart.showLabels = function(_) {
    if (!arguments.length) {
      return showLabels;
    }
    showLabels = _;
    return chart;
  };

  chart.labelSunbeamLayout = function(_) {
    if (!arguments.length) {
      return labelSunbeamLayout;
    }
    labelSunbeamLayout = _;
    return chart;
  };

  chart.donutLabelsOutside = function(_) {
    if (!arguments.length) {
      return donutLabelsOutside;
    }
    donutLabelsOutside = _;
    return chart;
  };

  chart.pieLabelsOutside = function(_) {
    if (!arguments.length) {
      return pieLabelsOutside;
    }
    pieLabelsOutside = _;
    return chart;
  };

  chart.labelType = function(_) {
    if (!arguments.length) {
      return labelType;
    }
    labelType = _;
    labelType = labelType || 'key';
    return chart;
  };

  chart.donut = function(_) {
    if (!arguments.length) {
      return donut;
    }
    donut = _;
    return chart;
  };

  chart.donutRatio = function(_) {
    if (!arguments.length) {
      return donutRatio;
    }
    donutRatio = _;
    return chart;
  };

  chart.startAngle = function(_) {
    if (!arguments.length) {
      return startAngle;
    }
    startAngle = _;
    return chart;
  };

  chart.endAngle = function(_) {
    if (!arguments.length) {
      return endAngle;
    }
    endAngle = _;
    return chart;
  };

  chart.id = function(_) {
    if (!arguments.length) {
      return id;
    }
    id = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) {
      return color;
    }
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.valueFormat = function(_) {
    if (!arguments.length) {
      return valueFormat;
    }
    valueFormat = _;
    return chart;
  };

  chart.labelThreshold = function(_) {
    if (!arguments.length) {
      return labelThreshold;
    }
    labelThreshold = _;
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
