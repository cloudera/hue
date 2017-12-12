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

(function () {

  ko.HUE_CHARTS = {
    TYPES: {
      COUNTER: "counter",
      LINECHART: "lines",
      BARCHART: "bars",
      TIMELINECHART: "timeline",
      POINTCHART: "points",
      PIECHART: "pie",
      MAP: "map",
      GRADIENTMAP: "gradientmap",
      SCATTERCHART: "scatter"
    }
  };

  ko.bindingHandlers.pieChart = {
    init: function (element, valueAccessor) {
      window.setTimeout(function(){
        var _options = valueAccessor();
        var _data = _options.transformer(_options.data);
        _data = _data.filter(function (val) {
          return val.value >= 0;
        });
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
                .showLabels(true).showLegend(false)
                .tooltipContent(function (key, y, e, graph) {
                  return '<h3>' + hueUtils.htmlEncode(key) + '</h3><p>' + y + '</p>'
                });

            var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");

            _d3.datum(_data)
                .transition().duration(150)
                .each("end", _options.onComplete != null ? _options.onComplete : void(0))
                .call(_chart);

            if (_options.fqs) {
              $.each(_options.fqs(), function (cnt, item) {
                if (item.id() == _options.data.widget_id && item.field() == _options.field()) {
                  _chart.selectSlices($.map(item.filter(), function (it) {
                    return it.value();
                  }));
                }
              });
            }

            $(element).data("chart", _chart);

            var _resizeTimeout = -1;
            nv.utils.windowResize(function () {
              window.clearTimeout(_resizeTimeout);
              _resizeTimeout = window.setTimeout(function () {
                _chart.update();
              }, 200);
            });

            $(element).on("forceUpdate", function () {
              _chart.update();
            });

            $(element).height($(element).width());
            var _parentSelector = typeof _options.parentSelector != "undefined" ? _options.parentSelector : ".card-widget";
            $(element).parents(_parentSelector).on("resize", function () {
              if (typeof _options.maxWidth != "undefined") {
                var _max = _options.maxWidth * 1;
                $(element).width(Math.min($(element).parent().width(), _max));
              }
              $(element).height($(element).width());
              _chart.update();
            });

            return _chart;
          }, function () {
            var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
            _d3.selectAll(".nv-slice").on("click",
                function (d, i) {
                  if (typeof _options.onClick != "undefined") {
                    chartsUpdatingState();
                    _options.onClick(d);
                  }
                });
          });
        }
      }, 0);
    },
    update: function (element, valueAccessor) {
      var _options = valueAccessor();
      var _data = _options.transformer(_options.data);
      _data = _data.filter(function (val) {
        return val.value >= 0;
      });
      var _chart = $(element).data("chart");
      if (_chart) {
        var _d3 = d3v3.select($(element).find("svg")[0]);
        _d3.datum(_data)
              .transition().duration(150)
              .each("end", _options.onComplete != null ? _options.onComplete : void(0))
              .call(_chart);

        if (_options.fqs) {
            $.each(_options.fqs(), function (cnt, item) {
              if (item.id() == _options.data.widget_id && item.field() == _options.field()) {
                _chart.selectSlices($.map(item.filter(), function (it) {
                  return it.value();
                }));
              }
            });
          }
        chartsNormalState();
      }
      else if (_data.length > 0) {
        ko.bindingHandlers.pieChart.init(element, valueAccessor);
      }
    }
  };

  ko.bindingHandlers.barChart = {
    init: function (element, valueAccessor) {
      window.setTimeout(function () {
        barChartBuilder(element, valueAccessor(), false);
      }, 0);
    },
    update: function (element, valueAccessor) {
      var _options = valueAccessor();

      var _datum = _options.transformer(_options.datum);
      var _chart = $(element).data("chart");

      if (_chart) {
        if (_chart.multibar){
          _chart.multibar.stacked(typeof _options.stacked != "undefined" ? _options.stacked : false);
        }

        var _isDiscrete = false;
        for (var j = 0; j < _datum.length; j++) {
          for (var i = 0; i < _datum[j].values.length; i++) {
            if (isNaN(_datum[j].values[i].x * 1)) {
              _isDiscrete = true;
              break;
            }
          }
        }

        var _isPivot = _options.isPivot != null ? _options.isPivot : false;

        if ((_isDiscrete && $(element).data('chart_type') !== 'discrete_bar') || (!_isDiscrete && $(element).data('chart_type') === 'discrete_bar') || (_isPivot && !$(element).data('chart_pivot')) || (!_isPivot && $(element).data('chart_pivot'))){
          ko.bindingHandlers.barChart.init(element, valueAccessor);
        }
        else {
          window.setTimeout(function () {
          var _d3 = d3v3.select($(element).find("svg")[0]);
          _d3.datum(_datum)
            .transition().duration(150)
            .each("end", function () {
              if (_options.onComplete != null) {
                _options.onComplete();
              }
            }).call(_chart);

          if (_chart.selectBars) {
            var _field = (typeof _options.field == "function") ? _options.field() : _options.field;
            $.each(_options.fqs(), function (cnt, item) {
              if (item.id() == _options.datum.widget_id) {
                if (item.field() == _field) {
                  if (item.properties) {
                    _chart.selectBars({
                      singleValues: $.map(item.filter(), function (it) {
                        return it.value();
                      }),
                      rangeValues: $.map(item.properties(), function (it) {
                        return {from: it.from(), to: it.to()};
                      })
                    });
                  }
                  else {
                    _chart.selectBars($.map(item.filter(), function (it) {
                      return it.value();
                    }));
                  }
                }
                if (Array.isArray(item.field())) {
                  _chart.selectBars({
                    field: item.field(),
                    selected: $.map(item.filter(), function (it) {
                      return {values: it.value()};
                    })
                  });
                }
              }
            });
          }
          chartsNormalState();
        }, 0);

        }
      }
      else if (_datum.length > 0) {
        ko.bindingHandlers.barChart.init(element, valueAccessor);
      }
    }
  };

  ko.bindingHandlers.timelineChart = {
    init: function (element, valueAccessor) {
      if (valueAccessor().type && valueAccessor().type() == "line"){
        window.setTimeout(function(){
          lineChartBuilder(element, valueAccessor(), true);
        }, 0);
        $(element).data("type", "line");
      }
      else {
        window.setTimeout(function(){
          barChartBuilder(element, valueAccessor(), true);
        }, 0);
        $(element).data("type", "bar");
      }
    },
    update: function (element, valueAccessor) {
      var _options = valueAccessor();
      if (valueAccessor().type && valueAccessor().type() != $(element).data("type")){
        if ($(element).find("svg").length > 0) {
          $(element).find("svg").remove();
        }
        if (valueAccessor().type() == "line"){
          window.setTimeout(function(){
            lineChartBuilder(element, valueAccessor(), true);
          }, 0);
        }
        else {
          window.setTimeout(function(){
            barChartBuilder(element, valueAccessor(), true);
          }, 0);
        }
        $(element).data("type", valueAccessor().type());
      }
      var _datum = _options.transformer(_options.datum);
      var _chart = $(element).data("chart");
      if (_chart) {
        window.setTimeout(function () {
          _chart.multibar.stacked(typeof _options.stacked != "undefined" ? _options.stacked : false);
          var enableSelection = true;
          if (typeof _options.enableSelection !== 'undefined') {
            enableSelection = _options.enableSelection;
          }
          if (_datum.length > 0 && _datum[0].values.length > 10 && enableSelection) {
            _chart.enableSelection();
          }
          else {
            _chart.disableSelection();
          }
          var _d3 = d3v3.select($(element).find("svg")[0]);
          _d3.datum(_datum)
            .transition().duration(150)
            .each("end", function () {
              if (_options.onComplete != null) {
                _options.onComplete();
              }
            }).call(_chart);
          _d3.selectAll("g.nv-x.nv-axis g text").each(function (d) {
            insertLinebreaks(d, this);
          });
          if (_chart.selectBars) {
            var _field = (typeof _options.field == "function") ? _options.field() : _options.field;
            $.each(_options.fqs(), function (cnt, item) {
              if (item.id() == _options.datum.widget_id) {
                if (item.field() == _field) {
                  _chart.selectBars($.map(item.filter(), function (it) {
                    return it.value();
                  }));
                }
                if (Array.isArray(item.field())) {
                  _chart.selectBars({
                    field: item.field(),
                    selected: $.map(item.filter(), function (it) {
                      return {values: it.value()};
                    })
                  });
                }
              }
            });
          }
          chartsNormalState();
        }, 0);
      }
      else if (_datum.length > 0) {
        ko.bindingHandlers.timelineChart.init(element, valueAccessor);
      }
    }
  };

  ko.bindingHandlers.lineChart = {
    init: function (element, valueAccessor) {
      window.setTimeout(function(){
        lineChartBuilder(element, valueAccessor(), false);
      }, 0);
    },
    update: function (element, valueAccessor) {
      var _options = valueAccessor();
      var _datum = _options.transformer(_options.datum);
      var _chart = $(element).data("chart");
      if (_chart) {
        window.setTimeout(function () {
          var _d3 = d3v3.select($(element).find("svg")[0]);
          if (_datum.length > 0 && _datum[0].values.length > 0 && typeof _datum[0].values[0].x.isValid === 'function'){
            _chart.xAxis.tickFormat(function(d) { return d3v3.time.format("%Y-%m-%d %H:%M:%S")(new Date(d)); })
            _chart.onChartUpdate(function () {
              _d3.selectAll("g.nv-x.nv-axis g text").each(function (d){
                insertLinebreaks(d, this);
              });
            });
          }
          _d3.datum(_datum)
            .transition().duration(150)
            .each("end", function () {
              if (_options.onComplete != null) {
                _options.onComplete();
              }
            }).call(_chart);
          chartsNormalState();
        }, 0);
      }
      else if (_datum.length > 0) {
        ko.bindingHandlers.lineChart.init(element, valueAccessor);
      }
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
      else {
        $(element).width($(element).parent().width() - 10);
      }

      $(element).height($(element).width() / 2.23);

      var _scope = typeof _options.data.scope != "undefined" ? String(_options.data.scope) : "world";
      var _data = _options.transformer(_options.data);
      var _is2d = false;
      var _pivotCategories = [];
      var _maxWeight = 0;

      function comparePivotValues(a, b) {
        if (a.count < b.count)
          return 1;
        if (a.count > b.count)
          return -1;
        return 0;
      }

      $(_data).each(function (cnt, item) {
        if (item.value > _maxWeight) _maxWeight = item.value;
        if (item.obj.is2d) _is2d = true;
        if (item.obj.pivot && item.obj.pivot.length > 0) {
          item.obj.pivot.forEach(function (piv) {

            var _category = null;
            _pivotCategories.forEach(function (category) {
              if (category.value == piv.value) {
                _category = category;
                if (piv.count > _category.count) {
                  _category.count = piv.count;
                }
              }
            });

            if (_category == null) {
              _category = {
                value: piv.value,
                count: -1
              };
              _pivotCategories.push(_category);
            }

          });
        }
      });

      _pivotCategories.sort(comparePivotValues);

      var _chunk = _maxWeight / _data.length;
      var _mapdata = {};
      var _maphovers = {};
      var _fills = {};
      var _legend = [];

      var _noncountries = [];


      if (_options.isScale) {
        _fills["defaultFill"] = HueColors.WHITE;
        var _colors = _is2d ? HueColors.d3Scale() : HueColors.scale(HueColors.LIGHT_BLUE, HueColors.DARK_BLUE, _data.length);
        $(_colors).each(function (cnt, item) {
          _fills["fill_" + cnt] = item;
        });

        function getHighestCategoryValue(cnt, item) {
          var _cat = "";
          var _max = -1;
          if (item.obj.pivot && item.obj.pivot.length > 0) {
            item.obj.pivot.forEach(function (piv) {
              if (piv.count > _max) {
                _max = piv.count;
                _cat = piv.value;
              }
            });
          }
          var _found = cnt;
          if (_cat != "") {
            _pivotCategories.forEach(function (cat, i) {
              if (cat.value == _cat) {
                _found = i;
              }
            });
          }
          return {
            idx: _found,
            cat: _cat
          };
        }

        function addToLegend(category) {
          var _found = false;
          _legend.forEach(function (lg) {
            if (lg.cat == category.cat) {
              _found = true;
            }
          });
          if (!_found) {
            _legend.push(category);
          }
        }

        $(_data).each(function (cnt, item) {
          addToLegend(getHighestCategoryValue(cnt, item));
          var _place = typeof item.label == "string" ? item.label.toUpperCase() : item.label;
          if (_place != null) {
            if (_scope != "world" && _scope != "usa" && _scope != "europe" && _place.indexOf(".") == -1) {
              _place = HueGeo.getISOAlpha2(_scope) + "." + _place;
            }
            if ((_scope == "world" || _scope == "europe") && _place.length == 2) {
              _place = HueGeo.getISOAlpha3(_place);
            }
            _mapdata[_place] = {
              fillKey: "fill_" + (_is2d ? getHighestCategoryValue(cnt, item).idx : (Math.ceil(item.value / _chunk) - 1)),
              id: _place,
              cat: item.obj.cat,
              value: item.obj.values ? item.obj.values : item.obj.value,
              pivot: _is2d ? item.obj.pivot : [],
              selected: item.obj.selected,
              fields: item.obj.fields ? item.obj.fields : null
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
            if (_scope != "world" && _scope != "usa" && _scope != "europe" && _place.indexOf(".") == -1) {
              _place = HueGeo.getISOAlpha2(_scope) + "." + _place;
            }
            if ((_scope == "world" || _scope == "europe") && _place.length == 2) {
              _place = HueGeo.getISOAlpha3(_place);
            }
            _mapdata[_place] = {
              fillKey: "selected",
              id: _place,
              cat: item.obj.cat,
              value: item.obj.values ? item.obj.values : item.obj.value,
              pivot: [],
              selected: item.obj.selected,
              fields: item.obj.fields ? item.obj.fields : null
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
          legendData: _legend,
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
                _hover = '<br/>';
                if (data.pivot && data.pivot.length > 0) {
                  data.pivot.sort(comparePivotValues);
                  data.pivot.forEach(function (piv, cnt) {
                    _hover += (cnt == 0 ? "<strong>" : "") + piv.value + ": " + piv.count + (cnt == 0 ? "</strong>" : "") + "<br/>";
                  });
                }
                else {
                  _hover += mapHovers[data.id];
                }
              }
              return '<div class="hoverinfo" style="text-align: center"><strong>' + geography.properties.name + '</strong>' + _hover + '</div>'
            }
          }
        });
        if (options.onComplete != null) {
          options.onComplete();
        }
        if (_is2d) {
          _map.legend();
        }
      }

      createDatamap(element, _options, _fills, _mapdata, _noncountries, _maphovers)

      var _parentSelector = typeof _options.parentSelector != "undefined" ? _options.parentSelector : ".card-widget";

      $(element).parents(_parentSelector).one("resize", function () {
        ko.bindingHandlers.mapChart.render(element, valueAccessor);
      });

      var _resizeTimeout = -1;
      nv.utils.windowResize(function () {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(function () {
          ko.bindingHandlers.mapChart.render(element, valueAccessor);
        }, 200);
      });

      chartsNormalState();
    },
    init: function (element, valueAccessor) {
      ko.bindingHandlers.mapChart.render(element, valueAccessor);
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
      if (typeof allBindingsAccessor().mapChart.visible != "undefined") {
        if ((typeof allBindingsAccessor().mapChart.visible == "boolean" && allBindingsAccessor().mapChart.visible) || (typeof allBindingsAccessor().mapChart.visible == "function" && allBindingsAccessor().mapChart.visible())) {
          $(element).show();
          ko.bindingHandlers.mapChart.render(element, valueAccessor);
        }
        else {
          $(element).hide();
        }
      }
      else {
        ko.bindingHandlers.mapChart.render(element, valueAccessor);
      }

    }
  };

  ko.bindingHandlers.scatterChart = {
    update: function (element, valueAccessor) {
      var options = valueAccessor();
      var _datum = options.transformer(options.datum);
      window.setTimeout(function () {
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
            var _chart = nv.models.scatterChart()
                .transitionDuration(350)
                .color(d3v3.scale.category10().range());

            _chart.tooltipContent(function (key, x, y, obj) {
              return '<h3>' + key + '</h3><div class="center">' + obj.point.size + '</div>';
            });

            _chart.xAxis.tickFormat(d3v3.format('.02f'));
            _chart.yAxis.tickFormat(d3v3.format('.02f'));
            _chart.scatter.onlyCircles(true);

            var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
            _d3.datum(_datum)
                .transition().duration(150)
                .each("end", options.onComplete != null ? options.onComplete : void(0))
                .call(_chart);

            var _resizeTimeout = -1;
            nv.utils.windowResize(function () {
              window.clearTimeout(_resizeTimeout);
              _resizeTimeout = window.setTimeout(function () {
                _chart.update();
              }, 200);
            });

            $(element).on("forceUpdate", function () {
              _chart.update();
            });

            return _chart;
          });
        }
      }, 0);
    }
  };

  var insertLinebreaks = function (d, ref) {
    var _el = d3v3.select(ref);
    var _mom = moment(d);
    if (_mom != null && _mom.isValid()) {
      var _words = _mom.format("HH:mm:ss YYYY-MM-DD").split(" ");
      _el.text("");
      for (var i = 0; i < _words.length; i++) {
        var tspan = _el.append("tspan").text(_words[i]);
        if (i > 0) {
          tspan.attr("x", 0).attr("dy", "15");
        }
      }
    }
  };

  function lineChartBuilder(element, options, isTimeline) {
    var _datum = options.transformer(options.datum);
    $(element).height(300);
    if ($(element).find("svg").length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
      $(element).find("svg").empty();
    }
    if (_datum.length > 0 && _datum[0].values.length > 0 && (isNaN(_datum[0].values[0].x) || isNaN(_datum[0].values[0].y))) {
      _datum = [];
      $(element).find("svg").empty();
    }

    var _hideSelection = options.hideSelection != null ? options.hideSelection : false;

    if ($(element).is(":visible")) {
      nv.addGraph(function () {
        var _chart = nv.models.lineWithBrushChart();
        $(element).data("chart", _chart);
        _chart.transitionDuration(0);
        var enableSelection = true;
        if (typeof options.enableSelection !== 'undefined') {
          enableSelection = options.enableSelection;
        }
        if (_datum.length > 0 && _datum[0].values.length > 10 && enableSelection) {
          _chart.enableSelection();
        }
        if (_hideSelection) {
          _chart.hideSelection();
        }
        if (options.showControls != null) {
          _chart.showControls(false);
        }
        _chart.onSelectRange(function (from, to) {
          chartsUpdatingState();
          options.onSelectRange($.isNumeric(from) ? new Date(moment(from).valueOf()) : from, $.isNumeric(to) ? new Date(moment(to).valueOf()) : to);
        });
        _chart.xAxis.showMaxMin(false);
        if (isTimeline){
          _chart.xAxis.tickFormat(function(d) { return d3v3.time.format("%Y-%m-%d %H:%M:%S")(new Date(d)); })
          _chart.onChartUpdate(function () {
            _d3.selectAll("g.nv-x.nv-axis g text").each(function (d){
              insertLinebreaks(d, this);
            });
          });
        }

        _chart.yAxis
            .tickFormat(d3v3.format(",0f"));

        var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
        _d3.datum(_datum)
            .transition().duration(150)
            .each("end", function () {
              if (options.onComplete != null) {
                options.onComplete();
              }
              if (isTimeline) {
                _d3.selectAll("g.nv-x.nv-axis g text").each(function (d){
                  insertLinebreaks(d, this);
                });
              }
            }).call(_chart);

        var _resizeTimeout = -1;
        nv.utils.windowResize(function () {
          window.clearTimeout(_resizeTimeout);
          _resizeTimeout = window.setTimeout(function () {
            _chart.update();
          }, 200);
        });

        $(element).on("forceUpdate", function () {
          _chart.update();
        });

        return _chart;
      }, function () {
        var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
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
    var _hideSelection = options.hideSelection != null ? options.hideSelection : false;

    if ($(element).find("svg").length > 0 && (_datum.length == 0 || _datum[0].values.length == 0)) {
      $(element).find("svg").remove();
    }

    if (_datum.length > 0 && _datum[0].values.length > 0 && isNaN(_datum[0].values[0].y)) {
      _datum = [];
      $(element).find("svg").remove();
    }

    nv.addGraph(function () {
      var _chart;
      if (isTimeline) {
        if ($(element).find("svg").length > 0 && $(element).find(".nv-discreteBarWithAxes").length > 0) {
          $(element).find("svg").empty();
        }
        _chart = nv.models.multiBarWithBrushChart();
        if (_datum.length > 0) $(element).data('chart_type', 'multibar_brush');
        var enableSelection = true;
        if (typeof options.enableSelection !== 'undefined') {
          enableSelection = options.enableSelection;
        }
        if (_datum.length > 0 && _datum[0].values.length > 10 && enableSelection) {
          _chart.enableSelection();
        }
        else {
          _chart.disableSelection();
        }
        if (_hideSelection) {
          _chart.hideSelection();
        }
        _chart.onSelectRange(function (from, to) {
          chartsUpdatingState();
          options.onSelectRange(from, to);
        });
        _chart.staggerLabels(false);
        _chart.xAxis.tickFormat(d3v3.time.format("%Y-%m-%d %H:%M:%S"));
        _chart.multibar.hideable(true);
        _chart.multibar.stacked(typeof options.stacked != "undefined" ? options.stacked : false);
        _chart.onStateChange(options.onStateChange);
        _chart.onChartUpdate(function () {
          _d3.selectAll("g.nv-x.nv-axis g text").each(function (d) {
            insertLinebreaks(d, this);
          });
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
        if (_isDiscrete && !_isPivot) {
          if ($(element).find("svg").length > 0 && $(element).find(".nv-multiBarWithLegend").length > 0) {
            $(element).find("svg").remove();
          }
          if (_datum.length > 0) $(element).data('chart_type', 'discrete_bar');
          $(element).data('chart_pivot', false);
          _chart = nv.models.growingDiscreteBarChart()
            .x(function (d) {
              return d.x
            })
            .y(function (d) {
              return d.y
            })
            .staggerLabels(true)
            .tooltipContent(function (key, x, y) {
              return '<h3>' + key + '</h3><p>' + y + ' on ' + hueUtils.htmlEncode(x) + '</p>'
            });
        }
        else if (_isDiscrete && _isPivot) {
          if ($(element).find("svg").length > 0 && $(element).find(".nv-discreteBarWithAxes").length > 0) {
            $(element).find("svg").remove();
          }
          if (_datum.length > 0) $(element).data('chart_type', 'discrete_bar');
          $(element).data('chart_pivot', true);
          _chart = nv.models.growingMultiBarChart()
            .x(function (d) {
              return d.x
            })
            .y(function (d) {
              return d.y
            })
            .tooltipContent(function (key, x, y) {
              return '<h3>' + key + '</h3><p>' + y + ' on ' + hueUtils.htmlEncode(x) + '</p>'
            });
        }
        else {
          if ($(element).find("svg").length > 0 && $(element).find(".nv-discreteBarWithAxes").length > 0) {
            $(element).find("svg").remove();
          }
          if (_datum.length > 0) $(element).data('chart_type', 'multibar_brush');
          _chart = nv.models.multiBarWithBrushChart();
          _chart.tooltipContent(function (key, x, y) {
            return '<h3>' + hueUtils.htmlEncode(key) + '</h3><p>' + y + ' on ' + hueUtils.htmlEncode(x) + '</p>'
          });
          if (_datum.length > 0 && _datum[0].values.length > 10) {
            _chart.enableSelection();
          }

          if (_isPivot || _hideSelection) {
            _chart.hideSelection();
          }
          else {
            _chart.xAxis.showMaxMin(false).tickFormat(d3v3.format(",0f"));
          }
          _chart.staggerLabels(true);
          _chart.multibar.hideable(true);
          _chart.multibar.stacked(typeof options.stacked != "undefined" ? options.stacked : false);
          _chart.onStateChange(options.onStateChange);
          _chart.onSelectRange(function (from, to) {
            chartsUpdatingState();
            options.onSelectRange(from, to);
          });
        }
      }
      if ($(element).width() < 300 && typeof _chart.showLegend != "undefined") {
        _chart.showLegend(false);
      }
      _chart.transitionDuration(0);

      _chart.yAxis
        .tickFormat(d3v3.format("s"));

      $(element).data("chart", _chart);

      var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
      _d3.datum(_datum)
        .transition().duration(150)
        .each("end", function () {
          if (options.onComplete != null) {
            options.onComplete();
          }
          if (isTimeline) {
            _d3.selectAll("g.nv-x.nv-axis g text").each(function (d) {
              insertLinebreaks(d, this);
            });
          }
        }).call(_chart);

      if (_chart.selectBars) {
        var _field = (typeof options.field == "function") ? options.field() : options.field;
        $.each(options.fqs(), function (cnt, item) {
          if (item.id() == options.datum.widget_id) {
            if (item.field() == _field) {
              _chart.selectBars($.map(item.filter(), function (it) {
                return it.value();
              }));
            }
            if (Array.isArray(item.field())) {
              _chart.selectBars({
                field: item.field(),
                selected: $.map(item.filter(), function (it) {
                  return {values: it.value()};
                })
              });
            }
          }
        });
      }

      if (!options.skipWindowResize) {
        var _resizeTimeout = -1;
        nv.utils.windowResize(function () {
          window.clearTimeout(_resizeTimeout);
          _resizeTimeout = window.setTimeout(function () {
            _chart.update();
          }, 200);
        });
      }

      $(element).on("forceUpdate", function () {
        _chart.update();
      });

      return _chart;
    }, function () {
      var _d3 = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
      _d3.selectAll(".nv-bar").on("click",
        function (d, i) {
          if (typeof options.onClick != "undefined") {
            chartsUpdatingState();
            options.onClick(d);
          }
        });
    });
  }

  ko.bindingHandlers.partitionChart = {
    render: function (element, valueAccessor) {
      chartsNormalState();
      var MIN_HEIGHT_FOR_TOOLTIP = 24;

      var _options = valueAccessor();
      var _data = _options.transformer(valueAccessor().datum);

      var _w = $(element).width(),
          _h = 300,
          _x = d3v3.scale.linear().range([0, _w]),
          _y = d3v3.scale.linear().range([0, _h]);

      if ($(element).find("svg").length > 0) {
        $(element).find("svg").empty();
      }

      var _tip = d3v3.tip()
          .attr("class", "d3-tip")
          .html(function (d) {
            if (d.depth == 0) {
              return _options.tooltip || "";
            }
            else if (d.depth > 0 && d.depth < 2) {
              return d.name + " (" + d.value + ")";
            }
            else {
              return d.parent.name + " - " + d.name + " (" + d.value + ")";
            }
          })
          .offset([-12, 0])


      var _svg = ($(element).find("svg.tip").length > 0) ? d3v3.select($(element).find("svg.tip")[0]) : d3v3.select($(element)[0]).append("svg");
      _svg.attr("class", "tip")
          .style("height", "0px")
      _svg.call(_tip);


      var _vis = ($(element).find("svg").length > 0) ? d3v3.select($(element).find("svg")[0]) : d3v3.select($(element)[0]).append("svg");
      _vis.attr("class", "partitionChart")
          .style("width", _w + "px")
          .style("height", _h + "px")
          .attr("width", _w)
          .attr("height", _h);

      var _partition = d3v3.layout.partition()
          .value(function (d) {
            return d.size;
          });

      var g = _vis.selectAll("g")
          .data(_partition.nodes(_data))
          .enter().append("svg:g")
          .attr("transform", function (d) {
            return "translate(" + _x(d.y) + "," + _y(d.x) + ")";
          })
          .on("mouseover", function (d, i) {
            if (element.querySelectorAll("rect")[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP || d.depth == 0) {
              _tip.attr("class", "d3-tip").show(d);
            }

            if (this.__data__.parent == undefined) return;
            d3v3.select(this).select("rect").classed("mouseover", true)
          })
          .on("mouseout", function (d, i) {
            if (element.querySelectorAll("rect")[i].getBBox().height < MIN_HEIGHT_FOR_TOOLTIP || d.depth == 0) {
              _tip.attr("class", "d3-tip").show(d);
              _tip.hide();
            }
            d3v3.select(this).select("rect").classed("mouseover", false)
          });

      if (typeof _options.zoomable == "undefined" || _options.zoomable) {
        g.on("click", click)
          .on("dblclick", function (d, i) {
            if (typeof _options.onClick != "undefined" && d.depth > 0) {
              chartsUpdatingState();
              _options.onClick(d);
            }
          });
      }
      else {
        g.on("click", function (d, i) {
          if (typeof _options.onClick != "undefined" && d.depth > 0) {
            chartsUpdatingState();
            _options.onClick(d);
          }
        });
      }

      var _kx = _w / _data.dx,
          _ky = _h / 1;

      var _colors = [HueColors.cuiD3Scale('gray')[0]];

      g.append("svg:rect")
          .attr("width", _data.dy * _kx)
          .attr("height", function (d) {
            return d.dx * _ky;
          })
          .attr("class", function (d) {
            return d.children ? "parent" : "child";
          })
          .attr("stroke", function (d) {
            return HueColors.cuiD3Scale('gray')[3];
          })
          .attr("fill", function (d, i) {
            var _fill = _colors[d.depth] || _colors[_colors.length - 1];
            if (d.obj && _options.fqs) {
              $.each(_options.fqs(), function (cnt, item) {
                $.each(item.filter(), function (icnt, filter) {
                  if (JSON.stringify(filter.value()) == JSON.stringify(d.obj.fq_values)) {
                    _fill = HueColors.cuiD3Scale('gray')[3];
                  }
                });
              });
            }
            return _fill;
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

      d3v3.select(window)
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
            .delay(250)
            .duration(d3v3.event.altKey ? 7500 : 750)
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

        d3v3.event.stopPropagation();
      }

      function transform(d) {
        return "translate(8," + d.dx * _ky / 2 + ")";
      }

      if (_options.onComplete) {
        _options.onComplete();
      }

    },
    init: function (element, valueAccessor) {
      ko.bindingHandlers.partitionChart.render(element, valueAccessor);
    },
    update: function (element, valueAccessor) {
      ko.bindingHandlers.partitionChart.render(element, valueAccessor);
    }
  };

  function chartsUpdatingState() {
    $(document).find("svg").css("opacity", "0.5");
  }
  window.chartsUpdatingState = chartsUpdatingState;

  function chartsNormalState() {
    $(document).find("svg").css("opacity", "1");
  }
  window.chartsNormalState = chartsNormalState;

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
          nodel = d3v3.select(node), i = 0,
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
      nodel = d3v3.select(node)
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
        return d3v3.select(node).attr(n)
      } else {
        var args = Array.prototype.slice.call(arguments)
        d3v3.selection.prototype.attr.apply(d3v3.select(node), args)
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
        return d3v3.select(node).style(n)
      } else {
        var args = Array.prototype.slice.call(arguments)
        d3v3.selection.prototype.style.apply(d3v3.select(node), args)
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
      direction = v == null ? v : d3v3.functor(v)

      return tip
    }

    // Public: Sets or gets the offset of the tip
    //
    // v - Array of [x, y] offset
    //
    // Returns offset or
    tip.offset = function (v) {
      if (!arguments.length) return offset
      offset = v == null ? v : d3v3.functor(v)

      return tip
    }

    // Public: sets or gets the html value of the tooltip
    //
    // v - String value of the tip
    //
    // Returns html value or tip
    tip.html = function (v) {
      if (!arguments.length) return html
      html = v == null ? v : d3v3.functor(v)

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

    var direction_callbacks = d3v3.map({
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
      var node = d3v3.select(document.createElement("div"))
      node.style({
        position: "absolute",
        background: HueColors.cuiD3Scale()[0],
        padding: "4px",
        color: HueColors.WHITE,
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
      var targetel = target || d3v3.event.target,
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

  if (typeof d3v3 !== 'undefined') {
    d3v3.tip = tipBuilder;
  }

})();