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

ko.HUE_CHARTS = {
  TYPES: {
    LINECHART: "lines",
    BARCHART: "bars",
    POINTCHART: "points",
    PIECHART: "pie",
    MAP: "map"
  }
};

ko.bindingHandlers.pieChart = {
  update: function (element, valueAccessor) {
    var _options = valueAccessor();
    var _data = _options.transformer(_options.data);
    $(element).css("marginLeft", "auto");
    $(element).css("marginRight", "auto");
    if (typeof _options.maxWidth != "undefined") {
      var _max = _options.maxWidth * 1;
      $(element).width(Math.min($(element).parent().width(), _max));
    }

    if ($(element).find("svg").length > 0 && _data.length == 0) {
      $(element).find("svg").empty();
    }

    if (_data.length > 0 && isNaN(_data[0].value)) {
      _data = [];
      $(element).find("svg").empty();
    }

    if ($(element).is(":visible")) {
      nv.addGraph(function () {
        var _chart = nv.models.growingPieChart()
            .x(function (d) {
              return d.label
            })
            .y(function (d) {
              return d.value
            })
            .height($(element).width())
            .showLabels(true).showLegend(false);

        var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");

        _d3.datum(_data)
            .transition().duration(150)
            .each("end", _options.onComplete != null ? _options.onComplete : void(0))
            .call(_chart);
        if (_options.fqs) {
          $.each(_options.fqs(), function (cnt, item) {
            if (item.field() == _options.field()) {
              _chart.selectSlices($.map(item.filter(), function(it) {return it.value();}));
            }
          });
        }

        nv.utils.windowResize(_chart.update);
        $(element).height($(element).width());
        $(element).parents(".card-widget").on("resize", function () {
          if (typeof _options.maxWidth != "undefined") {
            var _max = _options.maxWidth * 1;
            $(element).width(Math.min($(element).parent().width(), _max));
          }
          $(element).height($(element).width());
          _chart.update();
        });

        return _chart;
      }, function () {
        var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
        _d3.selectAll(".nv-slice").on("click",
            function (d, i) {
              if (typeof _options.onClick != "undefined") {
                chartsUpdatingState();
                _options.onClick(d);
              }
            });
      });
    }
  }
};

ko.bindingHandlers.barChart = {
  update: function (element, valueAccessor) {
    barChartBuilder(element, valueAccessor(), false);
  }
};

ko.bindingHandlers.timelineChart = {
  update: function (element, valueAccessor) {
    barChartBuilder(element, valueAccessor(), true);
  }
};

ko.bindingHandlers.lineChart = {
  update: function (element, valueAccessor) {
    lineChartBuilder(element, valueAccessor());
  }
};

ko.bindingHandlers.leafletMapChart = {
  update: function (element, valueAccessor) {
    var _options = valueAccessor();
    var _data = _options.transformer(valueAccessor().datum);

    function getMapBounds(lats, lngs) {
      lats = lats.sort();
      lngs = lngs.sort();
      return [
        [lats[lats.length - 1], lngs[lngs.length - 1]], // north-east
        [lats[0], lngs[0]] // south-west
      ]
    }

    if ($(element).data("map") != null) {
      try {
        $(element).data("map").remove();
      }
      catch (err) {
        if (typeof console != "undefined") {
          console.error(err);
        }
      }
    }

    var _lats = [];
    _data.forEach(function (item) {
      if (item.lat != null && $.isNumeric(item.lat)) {
        _lats.push(item.lat);
      }
    });
    var _lngs = [];
    _data.forEach(function (item) {
      if (item.lng != null && $.isNumeric(item.lng)) {
        _lngs.push(item.lng);
      }
    });

    if ($(element).parents(".tab-pane").length > 0){
      $(element).height($(element).parents(".tab-pane").height() - 100);
    }
    else {
      $(element).height(300);
    }

    if (((_options.visible != null && _options.visible) || _options.visible == null || typeof _options == "undefined") && _data.length > 0) {
      $(element).show();
    }
    else {
      $(element).hide();
    }

    var _map = null;
    if (element._map != null) {
      element._leaflet = false;
      element._map.remove();
    }

    if (_lats.length > 0 && _lngs.length > 0) {
      try {
        if (_map == null) {
          _map = L.map(element);
          L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
          }).addTo(_map);
        }

        _map.fitBounds(getMapBounds(_lats, _lngs));

        _data.forEach(function (item) {
          if (item.lng != null && item.lat != null) {
            var _addMarker = false;
            try {
              var _latLngObj = L.latLng(item.lat, item.lng);
              _addMarker = true;
             }
            catch (e){
              if (typeof console != "undefined") {
                console.error(e);
              }
            }
            if (_addMarker){
              var _marker = L.marker([item.lat, item.lng]).addTo(_map);
              if (item.label != null) {
                _marker.bindPopup(item.label);
              }
            }
          }
        });
        if (_options.onComplete != null) {
          _options.onComplete();
        }
      }
      catch (err) {
        $.jHueNotify.error(err.message);
      }
    }
    element._map = _map;

  }
};


ko.bindingHandlers.mapChart = {
  render: function (element, valueAccessor) {

    var _options = valueAccessor();

    $(element).empty();

    $(element).css("position", "relative");
    $(element).css("marginLeft", "auto");
    $(element).css("marginRight", "auto");

    if (typeof _options.maxWidth != "undefined") {
      var _max = _options.maxWidth * 1;
      $(element).width(Math.min($(element).parent().width(), _max));
    }

    $(element).height($(element).width() / 2.23);

    var _scope = typeof _options.data.scope != "undefined" ? String(_options.data.scope) : "world";
    var _data = _options.transformer(_options.data);
    var _maxWeight = 0;
    $(_data).each(function (cnt, item) {
      if (item.value > _maxWeight) _maxWeight = item.value;
    });

    var _chunk = _maxWeight / _data.length;

    var _mapdata = {};
    var _maphovers = {};
    var _fills = {};
    var _noncountries = [];

    if (_options.isScale) {
      _fills["defaultFill"] = HueColors.WHITE;
      var _colors = HueColors.scale(HueColors.LIGHT_BLUE, HueColors.DARK_BLUE, _data.length);
      $(_colors).each(function (cnt, item) {
        _fills["fill_" + cnt] = item;
      });
      $(_data).each(function (cnt, item) {
        var _place = item.label.toUpperCase();
        if (_place != null) {
          _mapdata[_place] = {
            fillKey: "fill_" + (Math.floor(item.value / _chunk) - 1),
            id: _place,
            cat: item.obj.cat,
            value: item.obj.value,
            selected: item.obj.selected
          };
          _maphovers[_place] = item.value;
        }
        else {
          _noncountries.push(item);
        }
      });
    }
    else {
      _fills["defaultFill"] = HueColors.LIGHT_BLUE;
      _fills["selected"] = HueColors.DARK_BLUE;
      $(_data).each(function (cnt, item) {
        var _place = item.label.toUpperCase();
        if (_place != null) {
          _mapdata[_place] = {
            fillKey: "selected",
            id: _place,
            cat: item.obj.cat,
            value: item.obj.value,
            selected: item.obj.selected
          };
          _maphovers[_place] = item.value;
        }
        else {
          _noncountries.push(item);
        }
      });
    }

    var _map = null;

    function createDatamap(element, options, fills, mapData, nonCountries, mapHovers) {
      _map = new Datamap({
        element: element,
        fills: fills,
        scope: _scope,
        data: mapData,
        onClick: function (data) {
          if (typeof options.onClick != "undefined") {
            chartsUpdatingState();
            options.onClick(data);
          }
        },
        done: function (datamap) {
          var _bubbles = [];
          if (options.enableGeocoding) {
            $(nonCountries).each(function (cnt, item) {
              HueGeo.getCityCoordinates(item.label, function (lat, lng) {
                _bubbles.push({
                  fillKey: "selected",
                  label: item.label,
                  value: item.value,
                  radius: 4,
                  latitude: lat,
                  longitude: lng
                });
                _map.bubbles(_bubbles, {
                  popupTemplate: function (geo, data) {
                    return '<div class="hoverinfo" style="text-align: center"><strong>' + data.label + '</strong><br/>' + item.value + '</div>'
                  }
                });
              });
            });
          }
        },
        geographyConfig: {
          hideAntarctica: true,
          borderWidth: 1,
          borderColor: HueColors.DARK_BLUE,
          highlightOnHover: true,
          highlightFillColor: HueColors.DARK_BLUE,
          highlightBorderColor: HueColors.BLUE,
          selectedFillColor: HueColors.DARKER_BLUE,
          selectedBorderColor: HueColors.DARKER_BLUE,
          popupTemplate: function (geography, data) {
            var _hover = '';
            if (data != null) {
              _hover = '<br/>' + mapHovers[data.id];
            }
            return '<div class="hoverinfo" style="text-align: center"><strong>' + geography.properties.name + '</strong>' + _hover + '</div>'
          }
        }
      });
      if (options.onComplete != null) {
        options.onComplete();
      }
    }

    createDatamap(element, _options, _fills, _mapdata, _noncountries, _maphovers)

    $(element).parents(".card-widget").one("resize", function () {
      ko.bindingHandlers.mapChart.render(element, valueAccessor);
    });
  },
  init: function (element, valueAccessor) {
    ko.bindingHandlers.mapChart.render(element, valueAccessor)
  },
  update: function (element, valueAccessor) {
    ko.bindingHandlers.mapChart.render(element, valueAccessor);
  }
};


function lineChartBuilder(element, options) {
  var _datum = options.transformer(options.datum);
  $(element).height(300);
  if ($(element).find("svg").length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
    $(element).find("svg").empty();
  }
  if (_datum.length > 0 && _datum[0].values.length > 0 && (isNaN(_datum[0].values[0].x) || isNaN(_datum[0].values[0].y))) {
    _datum = [];
    $(element).find("svg").empty();
  }

  if ($(element).is(":visible")) {
    nv.addGraph(function () {
      var _chart = nv.models.lineWithBrushChart();
      if (_datum.length > 0 && _datum[0].values.length > 10) {
        _chart.enableSelection();
      }
      if (options.showControls != null) {
        _chart.showControls(false);
      }
      _chart.onSelectRange(function (from, to) {
        chartsUpdatingState();
        options.onSelectRange(from, to);
      });
      _chart.xAxis.showMaxMin(false);

      _chart.yAxis
          .tickFormat(d3.format(",0f"));

      var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
      _d3.datum(_datum)
          .transition().duration(150)
          .each("end", options.onComplete != null ? options.onComplete : void(0))
          .call(_chart);

      nv.utils.windowResize(_chart.update);

      return _chart;
    }, function () {
      var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
      _d3.selectAll(".nv-line").on("click",
          function (d, i) {
            if (typeof options.onClick != "undefined") {
              chartsUpdatingState();
              options.onClick(d);
            }
          });
    });
  }
}


function barChartBuilder(element, options, isTimeline) {
  var _datum = options.transformer(options.datum);
  $(element).height(300);

  var _isPivot = options.isPivot != null ? options.isPivot : false;

  if ($(element).find("svg").length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
    $(element).find("svg").empty();
  }

  if (_datum.length > 0 && _datum[0].values.length > 0 && isNaN(_datum[0].values[0].y)) {
    _datum = [];
    $(element).find("svg").empty();
  }

  if ($(element).is(":visible")) {
    nv.addGraph(function () {
      var _chart;


      var insertLinebreaks = function (d) {
        var _el = d3.select(this);
        var _mom = moment(d);
        if (_mom != null && _mom.isValid()) {
          var _words = _mom.format("hh:mm:ss YYYY-MM-DD").split(" ");
          _el.text("");
          for (var i = 0; i < _words.length; i++) {
            var tspan = _el.append("tspan").text(_words[i]);
            if (i > 0) {
              tspan.attr("x", 0).attr("dy", "15");
            }
          }
        }
      };

      if (isTimeline) {
        if ($(element).find("svg").length > 0 && $(element).find(".nv-discreteBarWithAxes").length > 0) {
          $(element).find("svg").empty();
        }
        _chart = nv.models.multiBarWithBrushChart();
        if (_datum.length > 0 && _datum[0].values.length > 10) {
          _chart.enableSelection();
        }
        _chart.onSelectRange(function (from, to) {
          chartsUpdatingState();
          options.onSelectRange(from, to);
        });
        _chart.xAxis.tickFormat(d3.time.format("%Y-%m-%d %H:%M:%S"));
        _chart.multibar.hideable(true);
        _chart.multibar.stacked(typeof options.stacked != "undefined" ? options.stacked : false);
        _chart.onStateChange(options.onStateChange);
        _chart.onChartUpdate(function () {
          _d3.selectAll("g.nv-x.nv-axis g text").each(insertLinebreaks);
        });
      }
      else {
        var _isDiscrete = false;
        for (var j = 0; j < _datum.length; j++) {
          for (var i = 0; i < _datum[j].values.length; i++) {
            if (isNaN(_datum[j].values[i].x * 1)) {
              _isDiscrete = true;
              break;
            }
          }
        }
        if (_isDiscrete && ! _isPivot) {
          if ($(element).find("svg").length > 0 && $(element).find(".nv-multiBarWithLegend").length > 0) {
            $(element).find("svg").empty();
          }
          _chart = nv.models.growingDiscreteBarChart()
              .x(function (d) {
                return d.x
              })
              .y(function (d) {
                return d.y
              })
              .staggerLabels(true);
        }
        else {
          if ($(element).find("svg").length > 0 && $(element).find(".nv-discreteBarWithAxes").length > 0) {
            $(element).find("svg").empty();
          }
          _chart = nv.models.multiBarWithBrushChart();
          if (_datum.length > 0 && _datum[0].values.length > 10) {
            _chart.enableSelection();
          }

          if (_isPivot){
            _chart.hideSelection();
          }
          else {
            _chart.xAxis.showMaxMin(false).tickFormat(d3.format(",0f"));
          }
          _chart.multibar.hideable(true);
          _chart.multibar.stacked(typeof options.stacked != "undefined" ? options.stacked : false);
          _chart.onStateChange(options.onStateChange);
          _chart.onSelectRange(function (from, to) {
            chartsUpdatingState();
            options.onSelectRange(from, to);
          });
        }
      }
      _chart.transitionDuration(0);

      _chart.yAxis
          .tickFormat(d3.format(",0f"));

      var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
      _d3.datum(_datum)
          .transition().duration(150)
          .each("end", function () {
            if (options.onComplete != null) {
              options.onComplete();
            }
            if (isTimeline) {
              _d3.selectAll("g.nv-x.nv-axis g text").each(insertLinebreaks);
            }
          }).call(_chart);

      $.each(options.fqs(), function (cnt, item) {
        if (item.field() == options.field) {
          _chart.selectBars($.map(item.filter(), function(it) {return it.value();}));
        }
        if (item.field().indexOf(":") > -1){
          _chart.selectBars({
            field: item.field(),
            selected: $.map(item.filter(), function(it) {return it.value();})
          });
        }
      });

      nv.utils.windowResize(_chart.update);

      return _chart;
    }, function () {
      var _d3 = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
      _d3.selectAll(".nv-bar").on("click",
          function (d, i) {
            if (typeof options.onClick != "undefined") {
              chartsUpdatingState();
              options.onClick(d);
            }
          });
    });
  }
}

ko.bindingHandlers.partitionChart = {
  update: function (element, valueAccessor) {

    var MIN_HEIGHT_FOR_TOOLTIP = 24;

    var _options = valueAccessor();
    var _data = _options.transformer(valueAccessor().datum);

    var _w = $(element).width(),
        _h = 300,
        _x = d3.scale.linear().range([0, _w]),
        _y = d3.scale.linear().range([0, _h]);

    var _tip = d3.tip()
        .attr("class", "d3-tip")
        .html(function (d) {
          if (d.depth < 2) {
            return d.name + " (" + d.value + ")";
          }
          else {
            return d.parent.name + " - " + d.name + " (" + d.value + ")";
          }
        })
        .offset([-12, 0])


    var _svg = d3.select(element).append("svg:svg");
    _svg.call(_tip);


    var _vis = ($(element).find("svg").length > 0) ? d3.select($(element).find("svg")[0]) : d3.select($(element)[0]).append("svg");
    _vis.attr("class", "partitionChart")
        .style("width", _w + "px")
        .style("height", _h + "px")
        .append("svg:svg")
        .attr("width", _w)
        .attr("height", _h);

    var _partition = d3.layout.partition()
        .value(function (d) {
          return d.size;
        });

    var g = _vis.selectAll("g")
        .data(_partition.nodes(_data))
        .enter().append("svg:g")
        .attr("transform", function (d) {
          return "translate(" + _x(d.y) + "," + _y(d.x) + ")";
        })
        .on("click", click)
        .on("dblclick", function (d, i) {
          if (typeof _options.onClick != "undefined") {
            chartsUpdatingState();
            _options.onClick(d);
          }
        })
        .on("mouseover", function (d, i) {
          if (element.querySelectorAll("rect")[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP) {
            _tip.attr("class", "d3-tip").show(d);
          }

          if (this.__data__.parent == undefined) return;
          d3.select(this).select("rect").classed("mouseover", true)
        })
        .on("mouseout", function (d, i) {
          if (element.querySelectorAll("rect")[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP) {
            _tip.attr("class", "d3-tip").show(d);
            _tip.hide();
          }
          d3.select(this).select("rect").classed("mouseover", false)
        });

    var _kx = _w / _data.dx,
        _ky = _h / 1;

    var _colors = HueColors.scale(HueColors.DARK_BLUE, HueColors.BLUE, 5)

    g.append("svg:rect")
        .attr("width", _data.dy * _kx)
        .attr("height", function (d) {
          return d.dx * _ky;
        })
        .attr("class", function (d) {
          return d.children ? "parent" : "child";
        })
        .attr("stroke", HueColors.DARK_BLUE)
        .attr("fill", function (d, i) {
          return _colors[d.depth];
        });


    g.append("svg:text")
        .attr("transform", transform)
        .attr("dy", ".35em")
        .style("opacity", function (d) {
          return d.dx * _ky > 12 ? 1 : 0;
        })
        .text(function (d) {
          if (d.depth < 2) {
            return d.name + " (" + d.value + ")";
          }
          else {
            return d.parent.name + " - " + d.name + " (" + d.value + ")";
          }
        });

    d3.select(window)
        .on("click", function () {
          click(_data);
        });

    function click(d) {
      _tip.hide();
      if (!d.children) return;

      _kx = (d.y ? _w - 40 : _w) / (1 - d.y);
      _ky = _h / d.dx;
      _x.domain([d.y, 1]).range([d.y ? 40 : 0, _w]);
      _y.domain([d.x, d.x + d.dx]);

      var t = g.transition()
          .duration(d3.event.altKey ? 7500 : 750)
          .attr("transform", function (d) {
            return "translate(" + _x(d.y) + "," + _y(d.x) + ")";
          });

      t.select("rect")
          .attr("width", d.dy * _kx)
          .attr("height", function (d) {
            return d.dx * _ky;
          });

      t.select("text")
          .attr("transform", transform)
          .style("opacity", function (d) {
            return d.dx * _ky > 12 ? 1 : 0;
          });

      d3.event.stopPropagation();
    }

    function transform(d) {
      return "translate(8," + d.dx * _ky / 2 + ")";
    }

  }
};


function chartsUpdatingState() {
  $(document).find("svg").css("opacity", "0.5");
}


var tipBuilder = function () {
  var direction = d3_tip_direction,
      offset = d3_tip_offset,
      html = d3_tip_html,
      node = initNode(),
      svg = null,
      point = null,
      target = null

  function tip(vis) {
    svg = getSVGNode(vis)
    point = svg.createSVGPoint()
    document.body.appendChild(node)
  }

  // Public - show the tooltip on the screen
  //
  // Returns a tip
  tip.show = function () {
    var args = Array.prototype.slice.call(arguments)
    if (args[args.length - 1] instanceof SVGElement) target = args.pop()

    var content = html.apply(this, args),
        poffset = offset.apply(this, args),
        dir = direction.apply(this, args),
        nodel = d3.select(node), i = 0,
        coords

    nodel.html(content)
        .style({ opacity: 1, "pointer-events": "all" })

    while (i--) nodel.classed(directions[i], false)
    coords = direction_callbacks.get(dir).apply(this)
    nodel.classed(dir, true).style({
      top: (coords.top + poffset[0]) + "px",
      left: (coords.left + poffset[1]) + "px"
    })

    return tip
  }

  // Public - hide the tooltip
  //
  // Returns a tip
  tip.hide = function () {
    nodel = d3.select(node)
    nodel.style({ opacity: 0, "pointer-events": "none" })
    return tip
  }

  // Public: Proxy attr calls to the d3 tip container.  Sets or gets attribute value.
  //
  // n - name of the attribute
  // v - value of the attribute
  //
  // Returns tip or attribute value
  tip.attr = function (n, v) {
    if (arguments.length < 2 && typeof n === "string") {
      return d3.select(node).attr(n)
    } else {
      var args = Array.prototype.slice.call(arguments)
      d3.selection.prototype.attr.apply(d3.select(node), args)
    }

    return tip
  }

  // Public: Proxy style calls to the d3 tip container.  Sets or gets a style value.
  //
  // n - name of the property
  // v - value of the property
  //
  // Returns tip or style property value
  tip.style = function (n, v) {
    if (arguments.length < 2 && typeof n === "string") {
      return d3.select(node).style(n)
    } else {
      var args = Array.prototype.slice.call(arguments)
      d3.selection.prototype.style.apply(d3.select(node), args)
    }

    return tip
  }

  // Public: Set or get the direction of the tooltip
  //
  // v - One of n(north), s(south), e(east), or w(west), nw(northwest),
  //     sw(southwest), ne(northeast) or se(southeast)
  //
  // Returns tip or direction
  tip.direction = function (v) {
    if (!arguments.length) return direction
    direction = v == null ? v : d3.functor(v)

    return tip
  }

  // Public: Sets or gets the offset of the tip
  //
  // v - Array of [x, y] offset
  //
  // Returns offset or
  tip.offset = function (v) {
    if (!arguments.length) return offset
    offset = v == null ? v : d3.functor(v)

    return tip
  }

  // Public: sets or gets the html value of the tooltip
  //
  // v - String value of the tip
  //
  // Returns html value or tip
  tip.html = function (v) {
    if (!arguments.length) return html
    html = v == null ? v : d3.functor(v)

    return tip
  }

  function d3_tip_direction() {
    return "n"
  }

  function d3_tip_offset() {
    return [0, 0]
  }

  function d3_tip_html() {
    return " "
  }

  var direction_callbacks = d3.map({
        n: direction_n,
        s: direction_s,
        e: direction_e,
        w: direction_w,
        nw: direction_nw,
        ne: direction_ne,
        sw: direction_sw,
        se: direction_se
      }),

      directions = direction_callbacks.keys()

  function direction_n() {
    var bbox = getScreenBBox()
    return {
      top: bbox.n.y - node.offsetHeight,
      left: bbox.n.x - node.offsetWidth / 2
    }
  }

  function direction_s() {
    var bbox = getScreenBBox()
    return {
      top: bbox.s.y,
      left: bbox.s.x - node.offsetWidth / 2
    }
  }

  function direction_e() {
    var bbox = getScreenBBox()
    return {
      top: bbox.e.y - node.offsetHeight / 2,
      left: bbox.e.x
    }
  }

  function direction_w() {
    var bbox = getScreenBBox()
    return {
      top: bbox.w.y - node.offsetHeight / 2,
      left: bbox.w.x - node.offsetWidth
    }
  }

  function direction_nw() {
    var bbox = getScreenBBox()
    return {
      top: bbox.nw.y - node.offsetHeight,
      left: bbox.nw.x - node.offsetWidth
    }
  }

  function direction_ne() {
    var bbox = getScreenBBox()
    return {
      top: bbox.ne.y - node.offsetHeight,
      left: bbox.ne.x
    }
  }

  function direction_sw() {
    var bbox = getScreenBBox()
    return {
      top: bbox.sw.y,
      left: bbox.sw.x - node.offsetWidth
    }
  }

  function direction_se() {
    var bbox = getScreenBBox()
    return {
      top: bbox.se.y,
      left: bbox.e.x
    }
  }

  function initNode() {
    var node = d3.select(document.createElement("div"))
    node.style({
      position: "absolute",
      opacity: 0,
      pointerEvents: "none",
      boxSizing: "border-box"
    })

    return node.node()
  }

  function getSVGNode(el) {
    el = el.node()
    if (el != null) {
      if (el.tagName != null && el.tagName.toLowerCase() == "svg")
        return el

      return el.ownerSVGElement
    }
  }

  // Private - gets the screen coordinates of a shape
  //
  // Given a shape on the screen, will return an SVGPoint for the directions
  // n(north), s(south), e(east), w(west), ne(northeast), se(southeast), nw(northwest),
  // sw(southwest).
  //
  //    +-+-+
  //    |   |
  //    +   +
  //    |   |
  //    +-+-+
  //
  // Returns an Object {n, s, e, w, nw, sw, ne, se}
  function getScreenBBox() {
    var targetel = target || d3.event.target,
        bbox = {},
        matrix = targetel.getScreenCTM(),
        tbbox = targetel.getBBox(),
        width = tbbox.width,
        height = tbbox.height,
        x = tbbox.x,
        y = tbbox.y,
        scrollTop = document.documentElement.scrollTop || document.body.scrollTop,
        scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft


    point.x = x + scrollLeft
    point.y = y + scrollTop
    bbox.nw = point.matrixTransform(matrix)
    point.x += width
    bbox.ne = point.matrixTransform(matrix)
    point.y += height
    bbox.se = point.matrixTransform(matrix)
    point.x -= width
    bbox.sw = point.matrixTransform(matrix)
    point.y -= height / 2
    bbox.w = point.matrixTransform(matrix)
    point.x += width
    bbox.e = point.matrixTransform(matrix)
    point.x -= width / 2
    point.y -= height / 2
    bbox.n = point.matrixTransform(matrix)
    point.y += height
    bbox.s = point.matrixTransform(matrix)

    return bbox
  }

  return tip
};

d3.tip = tipBuilder;