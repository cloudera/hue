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

import hueUtils from 'utils/hueUtils';
import nv from 'ext/nv.d3.1.1.15b.custom';

nv.models.multiBarWithBrushChart = function() {
  'use strict';
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  const LABELS = {
    STACKED: 'Stacked',
    GROUPED: 'Grouped',
    SELECT: 'Enable selection'
  };

  const multibar = nv.models.growingMultiBar(),
    xAxis = nv.models.axis(),
    yAxis = nv.models.axis(),
    legend = nv.models.legend(),
    controls = nv.models.legend(),
    margin = { top: 30, right: 20, bottom: 50, left: 60 };
  let brush = d3v3.svg.brush(),
    width = null,
    height = null,
    color = nv.utils.defaultColor(),
    showControls = true,
    showLegend = true,
    showXAxis = true,
    showYAxis = true,
    rightAlignYAxis = false,
    reduceXTicks = true, // if false a tick will show for every data point
    staggerLabels = false,
    rotateLabels = 0,
    tooltips = true,
    tooltip = null,
    minTickWidth = 60,
    displayValuesInLegend = false,
    tooltipContent = null,
    x, //can be accessed via chart.xScale()
    y, //can be accessed via chart.yScale()
    state = { stacked: false, selectionEnabled: false },
    defaultState = null,
    noData = 'No Data Available.';
  const tooltipSimple = function(value) {
      return (
        '<h3>' +
        hueUtils.htmlEncode(value.key) +
        '</h3>' +
        '<p>' +
        hueUtils.htmlEncode(value.x) +
        '</p>'
      );
    },
    tooltipMultiple = function(values) {
      return (
        '<h3>' +
        hueUtils.htmlEncode(values[0] && values[0].x) +
        '</h3>' +
        values
          .map(value => {
            return (
              '<p><span class="circle" style="background-color:' +
              value.color +
              '"></span><b>' +
              hueUtils.htmlEncode(value.key) +
              '</b> ' +
              hueUtils.htmlEncode(value.y) +
              '</p>'
            );
          })
          .join('')
      );
    },
    getX = function(d) {
      return d.x;
    }, // accessor to get the x value
    getY = function(d) {
      return d.y;
    }, // accessor to get the y value
    dispatch = d3v3.dispatch('tooltipShow', 'tooltipHide', 'stateChange', 'changeState', 'brush'),
    controlWidth = function() {
      return showControls ? (selectionHidden ? 240 : 300) : 0;
    },
    legendWidth = 175;
  let transitionDuration = 250,
    extent,
    selectionEnabled = false,
    selectionHidden = false,
    stackedHidden = false,
    onSelectRange = null,
    onStateChange = null,
    onLegendChange = null,
    onChartUpdate = null,
    selectedBars = null,
    selectBars = null;
  multibar.stacked(false);
  xAxis
    .orient('bottom')
    .tickPadding(7)
    .highlightZero(true)
    .showMaxMin(false)
    .tickFormat(d => {
      return d;
    });
  yAxis.orient(rightAlignYAxis ? 'right' : 'left').tickFormat(d3v3.format(',.1f'));

  controls.updateState(false);
  //============================================================

  //============================================================
  // Private Variables
  //------------------------------------------------------------

  const showTooltip = function(e, offsetElement) {
    let values;
    if (!tooltipContent) {
      values = (e.list || [e]).map(e => {
        const x = xAxis.tickFormat()(multibar.x()(e.point, e.pointIndex)),
          y = yAxis.tickFormat()(multibar.y()(e.point, e.pointIndex));
        return {
          x: x,
          y: y,
          key:
            (displayValuesInLegend &&
              (e.point.obj.field || (e.point.obj.fq_fields && e.point.obj.fq_fields[0]))) ||
            e.series.key,
          color: e.series.color || color(e.series, e.point.series)
        };
      });
    } else {
      values = tooltipContent(
        (e.list || [e]).map(e => {
          const x = multibar.x()(e.point, e.pointIndex),
            y = multibar.y()(e.point, e.pointIndex);
          return {
            x: x,
            y: y,
            key:
              (displayValuesInLegend &&
                (e.point.obj.field || (e.point.obj.fq_fields && e.point.obj.fq_fields[0]))) ||
              e.series.key,
            color: e.series.color || color(e.series, e.point.series)
          };
        })
      );
    }

    const left = e.pos[0] + (offsetElement.offsetLeft || 0),
      top = e.pos[1] + (offsetElement.offsetTop || 0),
      content = displayValuesInLegend ? tooltipSimple(values[0]) : tooltipMultiple(values);

    nv.tooltip.show([left, top], content, e.value < 0 ? 'n' : 's', null, offsetElement);
  };

  //============================================================

  function chart(selection) {
    selection.each(function(data) {
      const container = d3v3.select(this),
        that = this;

      const availableWidth =
          (width || parseInt(container.style('width')) || 960) - margin.left - margin.right,
        availableChartWidth = Math.max(availableWidth - showLegend * legendWidth, 0),
        availableHeight =
          (height || parseInt(container.style('height')) || 400) - margin.top - margin.bottom;

      chart.recommendedTicks = function() {
        return Math.floor(availableWidth / minTickWidth);
      };
      chart.update = function() {
        if (!data) {
          return;
        }
        container
          .transition()
          .duration(transitionDuration)
          .each('end', onChartUpdate)
          .call(chart);
        filteredData = data.filter(series => {
          return !series.disabled;
        });
        if (selectionEnabled) {
          enableBrush();
        } else {
          disableBrush();
        }
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
      // Display noData message if there's nothing to show.

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

        container.selectAll('.nv-multiBarWithLegend').style('visibility', 'hidden');
        container.selectAll('.nv-noData').style('visibility', 'visible');

        return chart;
      } else {
        container.selectAll('.nv-multiBarWithLegend').style('visibility', 'visible');
        container.selectAll('.nv-noData').style('visibility', 'hidden');
      }

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup Scales

      x = multibar.xScale();
      y = multibar.yScale();

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      const wrap = container.selectAll('g.nv-wrap.nv-multiBarWithLegend').data([data]);
      const gEnter = wrap
        .enter()
        .append('g')
        .attr('class', 'nvd3 nv-wrap nv-multiBarWithLegend')
        .append('g');
      const g = wrap.select('g');

      gEnter.append('rect').style('opacity', 0);
      gEnter.append('g').attr('class', 'nv-x nv-axis');
      gEnter.append('g').attr('class', 'nv-y nv-axis');
      gEnter.append('g').attr('class', 'nv-barsWrap');
      // We put the legend in an another SVG to support scrolling
      const legendDiv = d3v3.select(container.node().parentNode).select('div');
      const legendSvg =
        legendDiv.select('svg').size() === 0 ? legendDiv.append('svg') : legendDiv.select('svg');
      legendSvg
        .style('height', data.length * 20 + 6 + 'px')
        .selectAll('g')
        .remove();
      const legendG = legendSvg.append('g').attr('class', 'nvd3 nv-wrap nv-legendWrap');
      gEnter.append('g').attr('class', 'nv-controlsWrap');

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Legend

      if (showLegend) {
        legend.width(legendWidth / 2);
        legend.height(availableHeight);
        legend.rightAlign(false);
        legend.margin({ top: 5, right: 0, left: 10, bottom: 0 });
        if (multibar.barColor()) {
          data.forEach((series, i) => {
            series.color = d3v3
              .rgb('#ccc')
              .darker(i * 1.5)
              .toString();
          });
        } else {
          data.forEach((series, i) => {
            series.color = color(series, i);
          });
        }

        try {
          legendG
            .datum(data)
            .call(legend)
            .selectAll('text')
            .text(d => {
              const value = d.key && d.key + '';
              if (displayValuesInLegend) {
                const addEllipsis = value && value.length > 12;
                return value && value.substring(0, 12) + (addEllipsis ? '...' : '');
              } else {
                return value;
              }
            })
            .append('title')
            .text(d => {
              return d.key;
            });
          if (displayValuesInLegend) {
            legendG
              .selectAll('g.nv-series')
              .append('text')
              .classed('nv-series-value', true)
              .text(() => {
                return '';
              })
              .attr('dx', 125)
              .attr('dy', '.32em')
              .attr('text-anchor', 'end')
              .append('title')
              .text(() => {
                return '';
              });
          }
        } catch (e) {}
      }

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Controls

      let controlsData = [];
      if (showControls) {
        if (!stackedHidden) {
          controlsData.push({ key: LABELS.GROUPED, disabled: multibar.stacked() });
          controlsData.push({ key: LABELS.STACKED, disabled: !multibar.stacked() });
        }

        if (!selectionHidden) {
          controlsData.push({
            key: LABELS.SELECT,
            disabled: !selectionEnabled,
            checkbox: selectionEnabled
          });
        }

        controls.width(controlWidth()).color(['#444', '#444', '#444']);
        g.select('.nv-controlsWrap')
          .datum(controlsData)
          .attr('transform', 'translate(0,' + -margin.top + ')')
          .call(controls);
      }

      //------------------------------------------------------------

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      if (rightAlignYAxis) {
        g.select('.nv-y.nv-axis').attr('transform', 'translate(' + availableChartWidth + ',0)');
      }

      //------------------------------------------------------------
      // Main Chart Component(s)
      let filteredData = data.filter(series => {
        return !series.disabled;
      });
      multibar
        .disabled(
          data.map(series => {
            return series.disabled;
          })
        )
        .width(availableChartWidth)
        .height(availableHeight)
        .color(
          data
            .map((d, i) => {
              return d.color || color(d, i);
            })
            .filter((d, i) => {
              return !data[i].disabled;
            })
        );

      selectBars = multibar.selectBars;

      const barsWrap = g.select('.nv-barsWrap').datum(
        data.filter(d => {
          return !d.disabled;
        })
      );

      barsWrap.transition().call(multibar);

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup Brush
      let overlay;
      if (selectionEnabled) {
        enableBrush();
        overlay = g.select('rect');
        overlay.style('display', 'none');
      } else {
        disableBrush();
        overlay = g.select('rect');
        overlay
          .style('display', 'inherit')
          .attr('height', availableHeight)
          .attr('width', availableWidth)
          .on('mousemove', onMouseMove)
          .on('mouseout', onMouseOut)
          .on('click', onClick);
      }
      if (selectBars && selectedBars) {
        selectBars(selectedBars);
      }

      function enableBrush() {
        if (!g) {
          // Can happen if the state change before the charts has been created.
          return;
        }
        brush
          .x(x)
          .on('brush', onBrush)
          .on('brushstart', onBrushStart)
          .on('brushend', onBrushEnd);
        if (chart.brushDomain) {
          const selection = fromSelection(chart.brushDomain);
          if (!selection.isWholeDomain) {
            // If brush is the whole domain, don't display brush
            brush.extent(fromSelection(chart.brushDomain).range);
          } else {
            brush.clear();
          }
        } else {
          brush.clear();
        }
        let gBrush;

        if (g.selectAll('.nv-brush')[0].length === 0) {
          g.append('g').attr('class', 'nv-brushBackground');
          g.append('g').attr('class', 'nv-x nv-brush');

          const brushBG = g
            .select('.nv-brushBackground')
            .selectAll('g')
            .data([chart.brushExtent || brush.extent()]);
          const brushBGenter = brushBG.enter().append('g');

          brushBGenter
            .append('rect')
            .attr('class', 'left')
            .attr('x', 0)
            .attr('y', 0)
            .attr('height', availableHeight);

          brushBGenter
            .append('rect')
            .attr('class', 'right')
            .attr('x', 0)
            .attr('y', 0)
            .attr('height', availableHeight);

          gBrush = g.select('.nv-x.nv-brush').call(brush);
        } else {
          g.selectAll('.nv-brush').attr('display', 'inline');
          gBrush = g.select('.nv-x.nv-brush').call(brush);
        }
        gBrush
          .selectAll('rect')
          .attr('height', availableHeight)
          .on('mousemove', onMouseMove)
          .on('mouseout', onMouseOut);
      }

      function disableBrush() {
        try {
          g.selectAll('.nv-brush').attr('display', 'none');
        } catch (e) {}
      }

      //------------------------------------------------------------
      // Setup Axes

      if (showXAxis) {
        const tickSkip = () => Math.ceil(minTickWidth / xAxis.rangeBand());

        xAxis
          .scale(x)
          .tickValues(
            x.domain().filter((d, i) => {
              return reduceXTicks && !(i % tickSkip());
            })
          )
          .tickSize(-availableHeight, 0);

        g.select('.nv-x.nv-axis').attr('transform', 'translate(0,' + y.range()[0] + ')');
        g.select('.nv-x.nv-axis')
          .transition()
          .call(xAxis);

        const xTicks = g.selectAll('.nv-x.nv-axis g.tick');

        xTicks.selectAll('line, text').style('opacity', 1);

        if (staggerLabels) {
          const getTranslate = function(x, y) {
            return 'translate(' + x + ',' + y + ')';
          };

          const rangeBand = x.rangeBand();

          const staggerUp = 5,
            staggerDown = 17; //pixels to stagger by
          // Issue #140
          xTicks.selectAll('text').attr('transform', function(d, i, j) {
            const self = d3v3.select(this);
            let textLength = self.node().getComputedTextLength(),
              text = self.text();
            while (textLength > rangeBand && text.length > 0) {
              text = text.slice(0, -1);
              self.text(text + '...');
              textLength = self.node().getComputedTextLength();
            }
            return getTranslate(0, j % 2 === 0 ? staggerUp : staggerDown);
          });

          const totalInBetweenTicks = d3v3.selectAll('.nv-x.nv-axis .nv-wrap g g text')[0].length;
          g.selectAll('.nv-x.nv-axis .nv-axisMaxMin text').attr('transform', (d, i) => {
            return getTranslate(
              0,
              i === 0 || totalInBetweenTicks % 2 !== 0 ? staggerDown : staggerUp
            );
          });
        }
        if (rotateLabels) {
          xTicks
            .selectAll('.tick text')
            .attr('transform', 'rotate(' + rotateLabels + ' 0,0)')
            .style('text-anchor', rotateLabels > 0 ? 'start' : 'end');
        }

        g.select('.nv-x.nv-axis')
          .selectAll('g.nv-axisMaxMin text')
          .style('opacity', 1);
      }

      if (showYAxis) {
        yAxis
          .scale(y)
          .ticks(availableHeight / 36)
          .tickSize(-availableChartWidth, 0);

        g.select('.nv-y.nv-axis')
          .transition()
          .call(yAxis);
      }

      //------------------------------------------------------------

      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------

      legend.dispatch.on('stateChange', newState => {
        state = newState;
        dispatch.stateChange(state);
        if (onLegendChange != null) {
          onLegendChange(state);
        }
        chart.update();
      });

      controls.dispatch.on('legendClick', d => {
        if (typeof d.checkbox == 'undefined') {
          if (!d.disabled) {
            return;
          }
          controlsData = controlsData.map(s => {
            s.disabled = true;
            return s;
          });
          d.disabled = false;
        }

        switch (d.key) {
          case LABELS.GROUPED:
            multibar.stacked(false);
            break;
          case LABELS.STACKED:
            multibar.stacked(true);
            break;
          case LABELS.SELECT:
            selectionEnabled = !selectionEnabled;
            break;
        }

        state.stacked = multibar.stacked();
        state.selectionEnabled = selectionEnabled;
        if (onStateChange != null) {
          onStateChange(state);
        }
        dispatch.stateChange(state);
        chart.update();
      });

      dispatch.on('tooltipShow', e => {
        showTooltip(e, that.parentNode);
      });

      // Update chart from a state object passed to event handler
      dispatch.on('changeState', e => {
        if (typeof e.disabled !== 'undefined') {
          data.forEach((series, i) => {
            series.disabled = e.disabled[i];
          });

          state.disabled = e.disabled;
        }

        if (typeof e.stacked !== 'undefined') {
          multibar.stacked(e.stacked);
          state.stacked = e.stacked;
        }

        chart.update();
      });

      //============================================================
      function fGetNumericValue(o) {
        return o instanceof Date ? o.getTime() : o;
      }

      function onBrush() {
        chart.brushExtent = brush.empty() ? null : brush.extent();
        extent = brush.empty() ? x.domain() : brush.extent();

        dispatch.brush({ extent: extent, brush: brush });
      }

      function onBrushStart() {
        gEnter
          .select('.nv-brush')
          .select('.extent')
          .style('display', 'block');
      }

      function onBrushEnd() {
        extent = brush.empty() ? [d3v3.mouse(this)[0], d3v3.mouse(this)[0]] : brush.extent();
        const _leftEdges = x.range();
        const _width = x.rangeBand() + multibar.groupSpacing() * x.rangeBand();
        let _l, _j;
        for (_l = 0; extent[0] > _leftEdges[_l] + _width; _l++) {}
        _l = typeof x.domain()[_l] !== 'undefined' ? _l : 0;
        const _from = x.domain()[_l];

        for (_j = 0; extent[1] > _leftEdges[_j] + _width; _j++) {}
        const _to =
          typeof x.domain()[_j + 1] !== 'undefined'
            ? x.domain()[_j + 1]
            : filteredData[0].values[filteredData[0].values.length - 1].x_end;
        const range = [
          x.range()[_l],
          typeof x.range()[_j + 1] !== 'undefined' ? x.range()[_j + 1] : x.range()[_j] + _width
        ];
        brush.extent((chart.brushExtent = range));
        g.select('.nv-x.nv-brush').call(brush);
        if (onSelectRange != null) {
          if (_from > _to) {
            onSelectRange(_to, _from);
          } else {
            onSelectRange(_from, _to);
          }
        }
      }

      function getElByMouse(coords, allSeries) {
        const xy = d3v3.mouse(this);
        const extent = coords || xy[0];
        let _l;
        const _width = x.rangeBand();
        const _leftEdges = x.range();
        for (_l = 0; extent >= _leftEdges[_l]; _l++) {}
        _l = Math.max(_l - 1, 0);
        const value = fGetNumericValue(x.domain()[_l]);
        let values = [];
        let i, j;
        if (allSeries) {
          for (j = 0; j < filteredData.length; j++) {
            for (i = 0; i < filteredData[j].values.length; i++) {
              if (fGetNumericValue(getX(filteredData[j].values[i])) === value) {
                values.push(filteredData[j].values[i]);
              }
            }
          }
        } else if (!multibar.stacked()) {
          const serieIndex = Math.floor(
            Math.min(extent - _leftEdges[_l], _width - 0.001) / (_width / filteredData.length)
          ); // Math.min(extent - _leftEdges[_l], _width - 0.001) to handle the padding at the end. Would it make sense to remove the padding?
          let i;
          if (serieIndex < 0) {
            return null;
          }
          for (i = 0; i < filteredData[serieIndex].values.length; i++) {
            if (fGetNumericValue(getX(filteredData[serieIndex].values[i])) === value) {
              values.push(filteredData[serieIndex].values[i]);
              break;
            }
          }
        } else {
          // serieIndex depends on the y position of the bar
          // y(getY(d) + (multibar.stacked() ? d.y0 : 0)
          // get all series for the x value
          const py = Math.round(y.invert(xy[1]));
          let mindy = Number.MAX_VALUE;
          const distances = {};
          for (j = 0; j < filteredData.length; j++) {
            for (i = 0; i < filteredData[j].values.length; i++) {
              if (fGetNumericValue(getX(filteredData[j].values[i])) === value) {
                if (py >= filteredData[j].values[i].y0 && py <= filteredData[j].values[i].y1) {
                  values.push(filteredData[j].values[i]);
                } else {
                  const ym =
                    filteredData[j].values[i].y0 +
                    (filteredData[j].values[i].y1 - filteredData[j].values[i].y0) / 2;
                  const dy = Math.abs(py - ym);
                  if (!distances[dy]) {
                    distances[dy] = [];
                  }
                  distances[dy].push(filteredData[j].values[i]);
                  if (dy < mindy) {
                    mindy = dy;
                  }
                }
              }
            }
          }
          if (!values.length) {
            values = distances[mindy];
          }
        }
        return values;
      }

      function fromSelection(selection) {
        const _width = x.rangeBand() + multibar.groupSpacing() * x.rangeBand();
        const _leftEdges = x.domain();
        if (!_leftEdges.length) {
          return null;
        }
        let _l, _j;
        const isDescending = _leftEdges[0] < _leftEdges[1];
        if (!isDescending) {
          selection = [Math.max(selection[0], selection[1]), Math.min(selection[0], selection[1])];
        }
        if (isDescending) {
          for (_l = 0; selection[0] >= _leftEdges[_l]; _l++) {}
        } else {
          for (_l = _leftEdges.length - 1; selection[0] > _leftEdges[_l]; _l--) {}
        }

        _l =
          x.range()[_l + typeof (isDescending ? -1 : 0)] !== 'undefined'
            ? _l + (isDescending ? -1 : 0)
            : isDescending
            ? _leftEdges.length - 1
            : 0;
        const _fromRange = typeof x.range()[_l] !== 'undefined' ? x.range()[_l] : 0;

        if (isDescending) {
          for (_j = 0; selection[1] > _leftEdges[_j]; _j++) {}
        } else {
          for (_j = _leftEdges.length - 1; selection[1] > _leftEdges[_j]; _j--) {}
        }
        const _toRange =
          typeof x.range()[_j] !== 'undefined'
            ? x.range()[_j]
            : x.range()[_leftEdges.length - 1] + _width;
        return {
          range: [_fromRange, _fromRange === _toRange ? _fromRange + x.rangeBand() : _toRange],
          isWholeDomain:
            selection[0] <= _leftEdges[0] && selection[1] >= _leftEdges[_leftEdges.length - 1]
        };
      }

      function onMouseMove() {
        const el = getElByMouse.call(this);
        // If we're mousing over a rectangle that doesn't have class hover, set class and dispatch mouseover
        const target = container
          .selectAll('g.nv-wrap.nv-multiBarWithLegend rect:not(.hover)')
          .filter(rect => {
            return (
              el &&
              el.some(d => {
                return (
                  fGetNumericValue(getX(rect)) === fGetNumericValue(getX(d)) &&
                  d.series === rect.series
                );
              })
            );
          });

        if (el && el.length && displayValuesInLegend) {
          const legendG = legendSvg.select('.nvd3.nv-wrap.nv-legendWrap');
          const elBySerie = el.reduce((elBySerie, el) => {
            elBySerie[el.seriesKey] = el;
            return elBySerie;
          }, {});
          legendG
            .selectAll('g.nv-series text.nv-series-value')
            .text(d => {
              if (elBySerie[d.key]) {
                const value = yAxis.tickFormat()(d.values[elBySerie[d.key].index].y) + '';
                const addEllipsis = value.length > 5;
                return value && (addEllipsis ? '...' : '') + value.substring(value.length - 5);
              } else {
                return '';
              }
            })
            .append('title')
            .text(d => {
              if (elBySerie[d.key]) {
                return yAxis.tickFormat()(d.values[elBySerie[d.key].index].y);
              } else {
                return '';
              }
            });
        }

        // If there's rectangle with the hover class that are not the target, remove the class and dispatch mouseout
        const others = container
          .selectAll('g.nv-wrap.nv-multiBarWithLegend rect.hover')
          .filter(rect => {
            return (
              !el ||
              !el.some(d => {
                return (
                  fGetNumericValue(getX(rect)) === fGetNumericValue(getX(d)) &&
                  d.series === rect.series
                );
              })
            );
          });
        if (others.size()) {
          others.classed('hover', false).each((d, i) => {
            multibar.dispatch.elementMouseout({
              value: getY(d, i),
              point: d,
              series: filteredData[d.series],
              pointIndex: i,
              seriesIndex: d.series,
              e: d3v3.event
            });
          });
        }
        if (target.size()) {
          const e = d3v3.event; // Keep reference to event for setTimeout
          setTimeout(() => {
            // Delayed to conteract conflict with elementMouseout.
            target.classed('hover', true);
            let max,
              maxi = 0;
            target.each((d, i) => {
              if (isNaN(max) || max < getY(d)) {
                max = getY(d);
                maxi = i;
              }
            });
            const width = x.rangeBand();
            d3v3.select(target[0][maxi]).each((d, i) => {
              multibar.dispatch.elementMouseover({
                value: getY(d),
                point: d,
                series: filteredData[d.series],
                pos: [x(getX(d)) + width * 0.5, y(getY(d) + (multibar.stacked() ? d.y0 : 0))],
                pointIndex: i,
                seriesIndex: d.series,
                list: el.map(d => {
                  return {
                    value: getY(d),
                    point: d,
                    series: filteredData[d.series],
                    pos: [x(getX(d)) + width * 0.5, y(getY(d) + (multibar.stacked() ? d.y0 : 0))],
                    pointIndex: -1,
                    seriesIndex: d.series
                  };
                }),
                e: e
              });
            });
          }, 0);
        }
      }

      function onMouseOut() {
        const others = container.selectAll('g.nv-wrap.nv-multiBarWithLegend rect.hover');
        if (others.size()) {
          others.classed('hover', false).each((d, i) => {
            multibar.dispatch.elementMouseout({
              value: getY(d, i),
              point: d,
              series: filteredData[d.series],
              pointIndex: d.index,
              seriesIndex: d.series,
              e: d3v3.event
            });
          });
        }
      }

      function onClick() {
        const el = getElByMouse.call(this);
        const d = el[0];
        multibar.dispatch.elementClick({
          value: getY(d),
          point: d,
          series: filteredData[d.series],
          pointIndex: d.index,
          seriesIndex: d.series,
          e: d3v3.event
        });
      }
    });

    return chart;
  }

  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  multibar.dispatch.on('elementMouseover.tooltip', e => {
    e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  multibar.dispatch.on('elementMouseout.tooltip', e => {
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
  chart.multibar = multibar;
  chart.legend = legend;
  chart.xAxis = xAxis;
  chart.yAxis = yAxis;
  chart.xScale = multibar.xScale;
  chart.LABELS = LABELS;

  d3v3.rebind(
    chart,
    multibar,
    'x',
    'y',
    'xDomain',
    'yDomain',
    'xRange',
    'yRange',
    'forceX',
    'forceY',
    'clipEdge',
    'id',
    'stacked',
    'stackOffset',
    'delay',
    'barColor',
    'groupSpacing'
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
    return chart;
  };

  chart.showControls = function(_) {
    if (!arguments.length) {
      return showControls;
    }
    showControls = _;
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) {
      return showLegend;
    }
    showLegend = _;
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

  chart.reduceXTicks = function(_) {
    if (!arguments.length) {
      return reduceXTicks;
    }
    reduceXTicks = _;
    return chart;
  };

  chart.rotateLabels = function(_) {
    if (!arguments.length) {
      return rotateLabels;
    }
    rotateLabels = _;
    return chart;
  };

  chart.staggerLabels = function(_) {
    if (!arguments.length) {
      return staggerLabels;
    }
    staggerLabels = _;
    return chart;
  };

  chart.tooltip = function(_) {
    if (!arguments.length) {
      return tooltip;
    }
    tooltip = _;
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
      return tooltipContent;
    }
    tooltipContent = _;
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

  chart.transitionDuration = function(_) {
    if (!arguments.length) {
      return transitionDuration;
    }
    transitionDuration = _;
    return chart;
  };

  chart.enableSelection = function() {
    selectionEnabled = true;
    return chart;
  };

  chart.disableSelection = function() {
    selectionEnabled = false;
    return chart;
  };

  chart.isSelectionEnabled = function() {
    return selectionEnabled;
  };

  chart.hideSelection = function() {
    selectionHidden = true;
    return chart;
  };

  chart.showSelection = function() {
    selectionHidden = false;
    return chart;
  };

  chart.showStacked = function() {
    stackedHidden = false;
  };

  chart.hideStacked = function() {
    stackedHidden = true;
  };

  chart.onSelectRange = function(_) {
    if (!arguments.length) {
      return onSelectRange;
    }
    onSelectRange = _;
    return chart;
  };

  chart.onStateChange = function(_) {
    if (!arguments.length) {
      return onStateChange;
    }
    onStateChange = _;
    return chart;
  };

  chart.onLegendChange = function(_) {
    if (!arguments.length) {
      return onLegendChange;
    }
    onLegendChange = _;
    return chart;
  };

  chart.onChartUpdate = function(_) {
    if (!arguments.length) {
      return onChartUpdate;
    }
    onChartUpdate = _;
    return chart;
  };

  chart.minTickWidth = function(val) {
    if (!arguments.length) {
      return minTickWidth;
    }
    minTickWidth = val;
    return chart;
  };

  chart.selectBars = function(args) {
    if (!arguments.length) {
      return selectBars;
    }
    if (args && args.rangeValues) {
      chart.brushDomain = [args.rangeValues[0].from, args.rangeValues[0].to];
    } else {
      chart.brushDomain = null;
    }
    selectedBars = args;
    if (selectBars) {
      selectBars(args);
    }
    return chart;
  };

  chart.displayValuesInLegend = function(val) {
    if (!arguments.length) {
      return displayValuesInLegend;
    }
    displayValuesInLegend = val;
    return chart;
  };

  chart.brush = function(val) {
    if (!arguments.length) {
      return brush;
    }
    brush = val;
    return chart;
  };

  //============================================================

  return chart;
};
