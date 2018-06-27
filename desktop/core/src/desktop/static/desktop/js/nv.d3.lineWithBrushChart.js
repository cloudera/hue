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


nv.models.lineWithBrushChart = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var LABELS = {
    SELECT: "Enable selection"
  }


  var lines = nv.models.line()
    , xAxis = nv.models.axis()
    , yAxis = nv.models.axis()
    , legend = nv.models.legend()
    , controls = nv.models.legend()
    , interactiveLayer = nv.interactiveGuideline()
    , brush = d3v3.svg.brush()
    ;

  var margin = {top: 30, right: 20, bottom: 50, left: 60}
    , color = nv.utils.defaultColor()
    , width = null
    , height = null
    , showLegend = true
    , showControls = true
    , showXAxis = true
    , showYAxis = true
    , rightAlignYAxis = false
    , useInteractiveGuideline = false
    , tooltips = true
    , tooltip = null
    , displayValuesInLegend = false
    , tooltipSimple = function(value) {
      return '<h3>' + hueUtils.htmlEncode(value.key) + '</h3>' +
        '<p>' + hueUtils.htmlEncode(value.x) + '</p>';
    }
    , tooltipSingle = function(value) {
      return '<h3>' + hueUtils.htmlEncode(value.key) + '</h3>' +
        '<p>' + hueUtils.htmlEncode(value.y) + ' on ' + hueUtils.htmlEncode(value.x) + '</p>';
    }
    , tooltipMultiple = function (values) {
      return '<h3>' + hueUtils.htmlEncode(values[0] && values[0].x) + '</h3>' + values.map(function (value) {
          return '<p><span class="circle" style="background-color:'+value.color+'"></span><b>' + hueUtils.htmlEncode(value.key) + '</b> ' +  hueUtils.htmlEncode(value.y) + '</p>';
        }).join("");
    }
    , x
    , y
    , getX = function(d) { return d.x } // accessor to get the x value
    , getY = function(d) { return d.y } // accessor to get the y value
    , state = {}
    , defaultState = null
    , noData = 'No Data Available.'
    , dispatch = d3v3.dispatch('tooltipShow', 'tooltipHide', 'stateChange', 'changeState', 'brush')
    , controlWidth = function() { return showControls ? (selectionHidden ? 240 : 300) : 0 }
    , legendWidth = 175
    , transitionDuration = 250
    , extent
    , brushExtent = null
    , selectionEnabled = false
    , selectionHidden = false
    , onSelectRange = null
    , onStateChange = null
    , onLegendChange = null
    , onChartUpdate = null
    ;

  xAxis
    .orient('bottom')
    .tickPadding(7)
    ;
  yAxis
    .orient((rightAlignYAxis) ? 'right' : 'left')
    ;

  controls.updateState(false);

  //============================================================


  //============================================================
  // Private Variables
  //------------------------------------------------------------

  var showTooltip = function(e, offsetElement) {
    var values;
    if (!tooltip) {
      values = (e.list || [e]).map(function (e) {
        var x = xAxis.tickFormat()(lines.x()(e.point, e.pointIndex)),
        y = yAxis.tickFormat()(lines.y()(e.point, e.pointIndex));
        return {x: x, y: y, key: displayValuesInLegend && (e.point.obj.field || e.point.obj.fq_fields && e.point.obj.fq_fields[0]) || e.series.key, color: e.series.color || color(e.series, e.point.series)};
      });
    } else {
      values = tooltip((e.list || [e]).map(function (e) {
        var x = lines.x()(e.point, e.pointIndex),
        y = lines.y()(e.point, e.pointIndex);
        return {x: x, y: y, key: displayValuesInLegend && (e.point.obj.field || e.point.obj.fq_fields && e.point.obj.fq_fields[0]) || e.series.key, color: e.series.color || color(e.series, e.point.series)};
      }));
    }


    var left = e.pos[0] + ( offsetElement.offsetLeft || 0 ),
        top = e.pos[1] + ( offsetElement.offsetTop || 0),
        content = displayValuesInLegend ? tooltipSimple(values[0]) : tooltipMultiple(values);

    nv.tooltip.show([left, top], content, null, null, offsetElement);
  };

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var container = d3v3.select(this),
          that = this;

      var availableWidth = (width  || parseInt(container.style('width')) || 960)
                             - margin.left - margin.right,
          availableChartWidth = Math.max(availableWidth - showLegend * legendWidth, 0),
          availableHeight = (height || parseInt(container.style('height')) || 400)
                             - margin.top - margin.bottom;


      chart.update = function() {
        container.transition().duration(transitionDuration).each("end", onChartUpdate).call(chart);
        filteredData = data.filter(function(series) { return !series.disabled; });
        if (selectionEnabled){
          enableBrush();
        }
        else {
          disableBrush();
        }
      };
      chart.container = this;

      //set state.disabled
      state.disabled = data.map(function(d) { return !!d.disabled });


      if (!defaultState) {
        var key;
        defaultState = {};
        for (key in state) {
          if (state[key] instanceof Array)
            defaultState[key] = state[key].slice(0);
          else
            defaultState[key] = state[key];
        }
      }

      //------------------------------------------------------------
      // Display noData message if there's nothing to show.

      if (!data || !data.length || !data.filter(function(d) { return d.values.length }).length) {
        var noDataText = container.selectAll('.nv-noData').data([noData]);

        noDataText.enter().append('text')
          .attr('class', 'nvd3 nv-noData')
          .attr('dy', '-.7em')
          .style('text-anchor', 'middle');

        noDataText
          .attr('x', margin.left + availableWidth / 2)
          .attr('y', margin.top + availableHeight / 2)
          .text(function(d) { return d; });

        return chart;
      } else {
        container.selectAll('.nv-noData').remove();
      }

      //------------------------------------------------------------


      //------------------------------------------------------------
      // Setup Scales

      x = lines.xScale();
      y = lines.yScale();

      //------------------------------------------------------------


      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      var wrap = container.selectAll('g.nv-wrap.nv-lineChart').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-lineChart').append('g');
      var g = wrap.select('g');

      gEnter.append("rect").style("opacity",0);
      gEnter.append('g').attr('class', 'nv-x nv-axis');
      gEnter.append('g').attr('class', 'nv-y nv-axis');
      gEnter.append('g').attr('class', 'nv-linesWrap');
      // We put the legend in an another SVG to support scrolling
      var legendDiv = d3.select(container.node().parentNode).select('div');
      var legendSvg = legendDiv.select('svg').size() === 0 ? legendDiv.append('svg') : legendDiv.select('svg');
      legendSvg.style('height', (data.length * 20 + 6) + 'px').selectAll('g').remove();
      var legendG = legendSvg.append('g').attr('class', 'nvd3 nv-wrap nv-legendWrap');
      gEnter.append('g').attr('class', 'nv-interactive');
      gEnter.append('g').attr('class', 'nv-controlsWrap');

      g.select("rect")
        .attr("width",availableChartWidth)
        .attr("height",(availableHeight > 0) ? availableHeight : 0);
      //------------------------------------------------------------
      // Legend

      if (showLegend) {
        legend.width(legendWidth / 2);
        legend.height(availableHeight);
        legend.rightAlign(false);
        legend.margin({top: 5, right: 0, left: 10, bottom: 0});
        data.forEach(function(series,i) {
          series.color = color(series, i);
        });

        try {
          legendG
            .datum(data)
            .call(legend)
          .selectAll('text')
          .text(function (d) {
            if (displayValuesInLegend) {
              var addEllipsis = d.key && d.key.length > 12;
              return d.key && d.key.substring(0, 12) + (addEllipsis ? '...' : '');
            } else {
              return d.key;
            }
          })
          .append('title')
          .text(function(d){
            return d.key;
          });
          if (displayValuesInLegend) {
            legendG.selectAll('g.nv-series')
            .append('text')
            .classed('nv-series-value', true)
            .text(function (d, i) {
              return '';
            })
            .attr('dx', 125)
            .attr('dy', '.32em')
            .attr('text-anchor', 'end')
            .append('title')
            .classed('nv-series-value', true)
            .text(function (d, i) {
              return '';
            });
          }
        }
        catch (e){}
      }

      if (showControls) {
        var controlsData = [];
        if (! selectionHidden) {
          controlsData.push({ key: LABELS.SELECT, disabled: !selectionEnabled, checkbox: true });
        }

        controls.width(controlWidth()).color(['#444', '#444', '#444']);
        g.select('.nv-controlsWrap')
            .datum(controlsData)
            .attr('transform', 'translate(0,' + (-margin.top) +')')
            .call(controls);
      }


      //------------------------------------------------------------

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      if (rightAlignYAxis) {
          g.select(".nv-y.nv-axis")
              .attr("transform", "translate(" + availableChartWidth + ",0)");
      }

      //------------------------------------------------------------
      // Main Chart Component(s)


      //------------------------------------------------------------
      //Set up interactive layer
      if (useInteractiveGuideline) {
        interactiveLayer
           .width(availableChartWidth)
           .height(availableHeight)
           .margin({left:margin.left, top:margin.top})
           .svgContainer(container)
           .xScale(x);
        wrap.select(".nv-interactive").call(interactiveLayer);
      }

      var filteredData = data.filter(function(series) { return !series.disabled; });
      lines
        .width(availableChartWidth)
        .height(availableHeight)
        .color(data.map(function(d,i) {
          return d.color || color(d, i);
        }).filter(function(d,i) { return !data[i].disabled; }));


      var linesWrap = g.select('.nv-linesWrap')
          .datum(data.filter(function(d) { return !d.disabled; }));

      linesWrap.transition().call(lines);

      //------------------------------------------------------------

      //------------------------------------------------------------
      // Setup Brush
      var overlay;
      if (selectionEnabled){
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


      function enableBrush() {
        if (!g) { // Can happen if the state change before the charts has been created.
          return;
        }
        brush
          .x(x)
          .on('brush', onBrush)
          .on('brushend', onBrushEnd);
        if (chart.brushDomain) {
          var brushExtent = [fGetNumericValue(chart.brushDomain[0]), fGetNumericValue(chart.brushDomain[1])];
          var isWholeDomain =  xAxis.scale()(chart.brushDomain[0]) < 10 && xAxis.scale()(chart.brushDomain[1]) >= xAxis.range()[1];
          if (!isWholeDomain) { // If brush is the whole domain, don't display brush
            brush.extent(brushExtent);
          } else {
            brush.clear();
          }
        } else {
          brush.clear();
        }
        var gBrush;
        if (g.selectAll('.nv-brush')[0].length == 0) {
          g.append('g').attr('class', 'nv-brushBackground');
          g.append('g').attr('class', 'nv-x nv-brush');

          var brushBG = g.select('.nv-brushBackground').selectAll('g')
              .data([chart.brushExtent || brush.extent()])
          var brushBGenter = brushBG.enter()
              .append('g');

          brushBGenter.append('rect')
              .attr('class', 'left')
              .attr('x', 0)
              .attr('y', 0)
              .attr('height', availableHeight);

          brushBGenter.append('rect')
              .attr('class', 'right')
              .attr('x', 0)
              .attr('y', 0)
              .attr('height', availableHeight);

          gBrush = g.select('.nv-x.nv-brush').call(brush);
        }
        else {
          g.selectAll('.nv-brush').attr('display', 'inline');
          gBrush = g.select('.nv-x.nv-brush').call(brush);
        }
        gBrush.selectAll('rect')
          .attr('height', availableHeight)
          .on('mousemove', onMouseMove)
          .on('mouseout', onMouseOut);
      }

      function disableBrush() {
        if (g) g.selectAll('.nv-brush').attr('display', 'none');
      }


      //------------------------------------------------------------
      // Setup Axes

      if (showXAxis) {
        xAxis
          .scale(x)
          .ticks( availableChartWidth / 100 )
          .tickSize(-availableHeight, 0);

        g.select('.nv-x.nv-axis')
            .attr('transform', 'translate(0,' + y.range()[0] + ')');
        g.select('.nv-x.nv-axis')
            .transition()
            .call(xAxis);
      }

      if (showYAxis) {
        yAxis
          .scale(y)
          .ticks( availableHeight / 36 )
          .tickSize( -availableChartWidth, 0);

        g.select('.nv-y.nv-axis')
            .transition()
            .call(yAxis);
      }
      //------------------------------------------------------------


      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------

      legend.dispatch.on('stateChange', function(newState) {
          state = newState;
          dispatch.stateChange(state);
          if (onLegendChange) {
            onLegendChange(state);
          }
          chart.update();
      });

      controls.dispatch.on('legendClick', function(d,i) {
        if (typeof d.checkbox == "undefined"){
          if (!d.disabled) return;
          controlsData = controlsData.map(function(s) {
            s.disabled = true;
            return s;
          });
          d.disabled = false;
        }

        switch (d.key) {
          case LABELS.SELECT:
            selectionEnabled = !selectionEnabled;
            break;
        }
        chart.update();
      });

      interactiveLayer.dispatch.on('elementMousemove', function(e) {
          lines.clearHighlights();
          var singlePoint, pointIndex, pointXLocation, allData = [];
          data
          .filter(function(series, i) {
            series.seriesIndex = i;
            return !series.disabled;
          })
          .forEach(function(series,i) {
              pointIndex = nv.interactiveBisect(series.values, e.pointXValue, chart.x());
              lines.highlightPoint(i, pointIndex, true);
              var point = series.values[pointIndex];
              if (typeof point === 'undefined') return;
              if (typeof singlePoint === 'undefined') singlePoint = point;
              if (typeof pointXLocation === 'undefined') pointXLocation = chart.xScale()(chart.x()(point,pointIndex));
              allData.push({
                  key: series.key,
                  value: chart.y()(point, pointIndex),
                  color: color(series,series.seriesIndex)
              });
          });
          //Highlight the tooltip entry based on which point the mouse is closest to.
          if (allData.length > 2) {
            var yValue = chart.yScale().invert(e.mouseY);
            var domainExtent = Math.abs(chart.yScale().domain()[0] - chart.yScale().domain()[1]);
            var threshold = 0.03 * domainExtent;
            var indexToHighlight = nv.nearestValueIndex(allData.map(function(d){return d.value;}),yValue,threshold);
            if (indexToHighlight !== null)
              allData[indexToHighlight].highlight = true;
          }

          var xValue = xAxis.tickFormat()(chart.x()(singlePoint,pointIndex));
          interactiveLayer.tooltip
                  .position({left: pointXLocation + margin.left, top: e.mouseY + margin.top})
                  .chartContainer(that.parentNode)
                  .enabled(tooltips)
                  .valueFormatter(function(d,i) {
                     return yAxis.tickFormat()(d);
                  })
                  .data(
                      {
                        value: xValue,
                        series: allData
                      }
                  )();

          interactiveLayer.renderGuideLine(pointXLocation);

      });

      interactiveLayer.dispatch.on("elementMouseout",function(e) {
          dispatch.tooltipHide();
          lines.clearHighlights();
      });

      dispatch.on('tooltipShow', function(e) {
        if (tooltips) showTooltip(e, that.parentNode);
      });


      dispatch.on('changeState', function(e) {

        if (typeof e.disabled !== 'undefined' && data.length === e.disabled.length) {
          data.forEach(function(series,i) {
            series.disabled = e.disabled[i];
          });

          state.disabled = e.disabled;
        }

        chart.update();
      });

      //============================================================

      function onBrush(){
        chart.brushExtent = brush.empty() ? null : brush.extent();
        extent = brush.empty() ? x.domain() : brush.extent();

        dispatch.brush({extent: extent, brush: brush});
      }
      function fGetNumericValue (o) {
        return o instanceof Date ? o.getTime() : o;
      }

      function onBrushEnd(){
        var closest = function () {
          if (!data[0].values.length) {
            return [];
          }
          var xDate = x.invert(d3v3.mouse(this)[0]);

          var distances = {};
          var min = Number.MAX_VALUE;
          var next = -Number.MAX_VALUE;
          var diff;
          var i, j;
          for (j = 0; j < data.length; j++) {
            for (i = 0; i < data[j].values.length; i++) {
              diff = xDate - fGetNumericValue(data[j].values[i].x);
              if (diff >= 0 && diff < min) {
                min = diff;
              } else if (diff < 0 && diff > next) {
                next = diff;
              }
              if (!distances[diff]) {
                distances[diff] = [];
              }
              distances[diff].push(data[j].values[i]);
            }
          }
          if (distances[min][0].x_end) {
            return [distances[min][0].x, distances[min][0].x_end];
          } else if (distances[min] !== undefined && distances[next] !== undefined) {
            var _from = distances[min][0].x < distances[next][0].x ? distances[min][0].x : distances[next][0].x;
            var _to = distances[min][0].x < distances[next][0].x ? distances[next][0].x : distances[min][0].x;
            return [_from, _to];
          } else {
            return [];
          }
        };

        chart.brushExtent = extent = brush.empty() ? closest.call(this) : brush.extent();

        if (onSelectRange) {
          onSelectRange(fGetNumericValue(extent[0]), fGetNumericValue(extent[1]));
        }
      }

      function getElByMouse () {
        var xy = d3v3.mouse(this);
        var px = x.invert(xy[0]);
        if (!filteredData.length || !filteredData[0].values.length) {
          return null;
        }
        var minx = Math.abs(filteredData[0].values[0].x - px);
        var distances = {};
        var py = y.invert(xy[1]);
        var i, j, diff;
        // Find closest on x axis
        for (j = 0; j < filteredData.length; j++) {
          for (i = 0; i < filteredData[j].values.length; i++) {
            diff = Math.abs(fGetNumericValue(filteredData[j].values[i].x) - px);
            if (!distances[diff]) {
              distances[diff] = [];
            }
            filteredData[j].values[i].seriesKey = filteredData[j].key;
            distances[diff].push(filteredData[j].values[i]);
            if (diff < minx) {
              minx = diff;
            }
          }
        }
        // Find series with y axis
        var miny = Number.MAX_VALUE;
        var distancesy = {};
        for (i = 0; i < distances[minx].length; i++) {
          diff = Math.abs(distances[minx][i].y - py);
          if (!distancesy[diff]) {
            distancesy[diff] = [];
          }
          distancesy[diff].push(distances[minx][i]);
          if (diff < miny) {
            miny = diff;
          }
        };

        return distancesy[miny];
      }
      function onMouseMove () {
        var el = getElByMouse.call(this);
        // If we're mousing over a circle that doesn't have class hover, set class and dispatch mouseover
        var target = container.selectAll('g.nv-wrap.nv-lineChart circle:not(.hover)').filter(function(rect) {
          return el && el.some(function(d) {
            return fGetNumericValue(getX(rect)) === fGetNumericValue(getX(d)) && d.series === rect.series;
          });
        });

        if (el && el.length && displayValuesInLegend) {
          var legendG = legendSvg.select('.nvd3.nv-wrap.nv-legendWrap');
          var elBySerie = el.reduce(function (elBySerie, el) {
            elBySerie[el.seriesKey] = el;
            return elBySerie;
          }, {});
          legendG.selectAll('g.nv-series text.nv-series-value')
          .text(function (d, i) {
            if (elBySerie[d.key]) {
              var value = yAxis.tickFormat()(d.values[elBySerie[d.key].index].y)+'';
              var addEllipsis = value.length > 5;
              return value && (addEllipsis ? '...' : '') + value.substring(value.length - 5);
            } else {
              return '';
            }
          })
          .append('title')
          .text(function (d, i) {
            if (elBySerie[d.key]) {
              return yAxis.tickFormat()(d.values[elBySerie[d.key].index].y);
            } else {
              return '';
            }
          });
        }
        // If there's rectangle with the hover class that are not the target, remove the class and dispatch mouseout
        var others = container.selectAll('g.nv-wrap.nv-lineChart circle.hover').filter(function(rect) {
          return !el || !el.some(function(d) {
            return fGetNumericValue(getX(rect)) === fGetNumericValue(getX(d)) && d.series === rect.series;
          });
        });
        if (others.size()) {
          others.classed('hover', false)
          .each(function (d, i) {
            lines.dispatch.elementMouseout({
              value: getY(d),
              point: d,
              series: filteredData[d.series],
              pointIndex: i,
              seriesIndex: d.series,
              e: d3v3.event
            });
          });
        }
        if (target.size()) {
          var e = d3v3.event; // Keep reference to event for setTimeout
          setTimeout(function(){ // Delayed to conteract conflict with elementMouseout.
            target.classed('hover', true);
            var max, maxi;
            target.each(function (d, i) {
              if (isNaN(max) || max < getY(d)) {
                max = getY(d);
                maxi = i;
              }
            });
            d3v3.select(target[0][maxi])
            .each(function(d, i){
              lines.dispatch.elementMouseover({
                value: getY(d),
                point: d,
                series: filteredData[d.series],
                pos: [x(getX(d)), y(getY(d))],
                pointIndex: -1,
                seriesIndex: d.series,
                list: el.map(function (d) {
                  return {
                    value: getY(d),
                    point: d,
                    series: filteredData[d.series],
                    pos: [x(getX(d)), y(getY(d))],
                    pointIndex: -1,
                    seriesIndex: d.series,
                  };
                }),
                e: e,
              });
            });
          });
        }
      }
      function onMouseOut () {
        var others = container.selectAll('g.nv-wrap.nv-lineChart circle.hover');
        if (others.size()) {
           others.classed('hover', false)
          .each(function (d) {
            lines.dispatch.elementMouseout({
              value: getY(d),
              point: d,
              series: filteredData[d.series],
              pointIndex: d.index,
              seriesIndex: d.series,
              e: d3v3.event
            });
          });
        }
      }
      function onClick () {
        var el = getElByMouse.call(this);
        var d = el[0];
        lines.dispatch.elementClick({
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

  lines.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  lines.dispatch.on('elementMouseout.tooltip', function(e) {
    dispatch.tooltipHide(e);
  });

  dispatch.on('tooltipHide', function() {
    if (tooltips) nv.tooltip.cleanup();
  });

  //============================================================


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  // expose chart's sub-components
  chart.dispatch = dispatch;
  chart.lines = lines;
  chart.legend = legend;
  chart.xAxis = xAxis;
  chart.yAxis = yAxis;
  chart.xScale = lines.xScale;
  chart.interactiveLayer = interactiveLayer;

  d3v3.rebind(chart, lines, 'defined', 'isArea', 'x', 'y', 'size', 'xScale', 'yScale', 'xDomain', 'yDomain', 'xRange', 'yRange'
    , 'forceX', 'forceY', 'interactive', 'clipEdge', 'clipVoronoi', 'useVoronoi','id', 'interpolate');

  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    legend.color(color);
    return chart;
  };

  chart.showControls = function(_) {
    if (!arguments.length) return showControls;
    showControls = _;
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) return showLegend;
    showLegend = _;
    return chart;
  };

  chart.showXAxis = function(_) {
    if (!arguments.length) return showXAxis;
    showXAxis = _;
    return chart;
  };

  chart.showYAxis = function(_) {
    if (!arguments.length) return showYAxis;
    showYAxis = _;
    return chart;
  };

  chart.rightAlignYAxis = function(_) {
    if(!arguments.length) return rightAlignYAxis;
    rightAlignYAxis = _;
    yAxis.orient( (_) ? 'right' : 'left');
    return chart;
  };

  chart.useInteractiveGuideline = function(_) {
    if(!arguments.length) return useInteractiveGuideline;
    useInteractiveGuideline = _;
    if (_ === true) {
       chart.interactive(false);
       chart.useVoronoi(false);
    }
    return chart;
  };

  chart.tooltips = function(_) {
    if (!arguments.length) return tooltips;
    tooltips = _;
    return chart;
  };

  chart.tooltipContent = function(_) {
    if (!arguments.length) return tooltip;
    tooltip = _;
    return chart;
  };

  chart.state = function(_) {
    if (!arguments.length) return state;
    state = _;
    return chart;
  };

  chart.defaultState = function(_) {
    if (!arguments.length) return defaultState;
    defaultState = _;
    return chart;
  };

  chart.noData = function(_) {
    if (!arguments.length) return noData;
    noData = _;
    return chart;
  };

  chart.transitionDuration = function(_) {
    if (!arguments.length) return transitionDuration;
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

  chart.onSelectRange = function(_) {
    if (!arguments.length) return onSelectRange;
    onSelectRange = _;
    return chart;
  };

  chart.onChartUpdate = function(_) {
    if (!arguments.length) return onChartUpdate;
    onChartUpdate = _;
    return chart;
  };

  chart.onStateChange = function(_) {
    if (!arguments.length) return onStateChange;
    onStateChange = _;
    return chart;
  };

  chart.onLegendChange = function(_) {
    if (!arguments.length) return onLegendChange;
    onLegendChange = _;
    return chart;
  };

  chart.displayValuesInLegend = function(_) {
    if (!arguments.length) return displayValuesInLegend;
    displayValuesInLegend = _;
    return chart;
  };

  chart.brush = function(_) {
    if (!arguments.length) return brush;
    brush = _;
    return chart;
  };

  chart.selectBars = function(args) {
    if (!arguments.length) return selectBars;
    if (args && args.rangeValues) {
      chart.brushDomain = [args.rangeValues[0].from, args.rangeValues[0].to];
    } else {
      chart.brushDomain = null;
    }
    return chart;
  };

  //============================================================


  return chart;
}
