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

    if ($(element).find('svg').length > 0 && _data.length == 0) {
      $(element).find('svg').empty();
    }

    if (_data.length > 0 && isNaN(_data[0].value)) {
      _data = [];
      $(element).find('svg').empty();
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

        var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');

        _d3.datum(_data)
            .transition().duration(150)
            .each("end", _options.onComplete != null ? _options.onComplete : void(0))
            .call(_chart);
        if (_options.fqs) {
          $.each(_options.fqs(), function (cnt, item) {
            if (item.field() == _options.field()) {
              _chart.selectSlices(item.filter());
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
        var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
        _d3.selectAll(".nv-slice").on('click',
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
      if (item.lat != null) {
        _lats.push(item.lat);
      }
    });
    var _lngs = [];
    _data.forEach(function (item) {
      if (item.lng != null) {
        _lngs.push(item.lng);
      }
    });

    if ($(element).parents(".tab-pane").length > 0){
      $(element).height($(element).parents(".tab-pane").height() - 100);
    }
    else {
      $(element).height(300);
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
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributorss'
          }).addTo(_map);
        }

        _map.fitBounds(getMapBounds(_lats, _lngs));

        _data.forEach(function (item) {
          if (item.lng != null && item.lat != null) {
            var _marker = L.marker([item.lat, item.lng]).addTo(_map);
            if (item.label != null) {
              _marker.bindPopup(item.label);
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
  if ($(element).find('svg').length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
    $(element).find('svg').empty();
  }
  if (_datum.length > 0 && _datum[0].values.length > 0 && (isNaN(_datum[0].values[0].x) || isNaN(_datum[0].values[0].y))) {
    _datum = [];
    $(element).find('svg').empty();
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
          .tickFormat(d3.format(',0f'));

      var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
      _d3.datum(_datum)
          .transition().duration(150)
          .each("end", options.onComplete != null ? options.onComplete : void(0))
          .call(_chart);

      nv.utils.windowResize(_chart.update);

      return _chart;
    }, function () {
      var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
      _d3.selectAll(".nv-line").on('click',
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

  if ($(element).find('svg').length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
    $(element).find('svg').empty();
  }

  if (_datum.length > 0 && _datum[0].values.length > 0 && isNaN(_datum[0].values[0].y)) {
    _datum = [];
    $(element).find('svg').empty();
  }

  if ($(element).is(":visible")) {
    nv.addGraph(function () {
      var _chart;


      var insertLinebreaks = function (d) {
        var _el = d3.select(this);
        var _mom = moment(d);
        if (_mom != null && _mom.isValid()) {
          var _words = _mom.format("hh:mm:ss YYYY-MM-DD").split(" ");
          _el.text('');
          for (var i = 0; i < _words.length; i++) {
            var tspan = _el.append("tspan").text(_words[i]);
            if (i > 0) {
              tspan.attr("x", 0).attr("dy", '15');
            }
          }
        }
      };

      if (isTimeline) {
        if ($(element).find('svg').length > 0 && $(element).find('.nv-discreteBarWithAxes').length > 0) {
          $(element).find('svg').empty();
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
        if (_isDiscrete) {
          if ($(element).find('svg').length > 0 && $(element).find('.nv-multiBarWithLegend').length > 0) {
            $(element).find('svg').empty();
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
          if ($(element).find('svg').length > 0 && $(element).find('.nv-discreteBarWithAxes').length > 0) {
            $(element).find('svg').empty();
          }
          _chart = nv.models.multiBarWithBrushChart();
          if (_datum.length > 0 && _datum[0].values.length > 10) {
            _chart.enableSelection();
          }
          _chart.xAxis.showMaxMin(false).tickFormat(d3.format(',0f'));
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
          .tickFormat(d3.format(',0f'));

      var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
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
          _chart.selectBars(item.filter());
        }
      });

      nv.utils.windowResize(_chart.update);

      return _chart;
    }, function () {
      var _d3 = ($(element).find('svg').length > 0) ? d3.select($(element).find('svg')[0]) : d3.select($(element)[0]).append('svg');
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

function chartsUpdatingState() {
  $(document).find("svg").css("opacity", "0.5");
}
