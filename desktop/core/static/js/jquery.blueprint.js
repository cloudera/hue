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
/*
 * jHue Blueprint plugin
 * it's a layer of abstraction on top of other chart/drawing/mapping plugins
 */

(function ($, window, document, undefined) {
  var pluginName = "jHueBlueprint",
      COLORS = {
        ORANGE: "#FB950D",
        GREEN: "#419E08",
        BLUE: "#338BB8"
      },
      TYPES = {
        LINECHART: "lines",
        BARCHART: "bars",
        POINTCHART: "points",
        PIECHART: "pie",
        MAP: "map"
      },
      defaults = {
        data: [],
        type: TYPES.LINECHART,
        fill: false,
        width: "100%",
        height: 200,
        borderWidth: 0,
        tooltips: true,
        enableSelection: false,
        isDateTime: false,
        isCategories: false,
        useCanvas: false,
        onSelect: function () {
        },
        onItemClick: function () {
        }
      };

  function Plugin(element, options) {
    this.element = element;
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.init();
  }

  Plugin.prototype.init = function () {
    var _this = this;
    if (_this.options.type == TYPES.PIECHART) {
      flot_pie(_this);
    }
    else {
      flot(_this);
    }
  };

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  function addSerie(element, serie) {
    var _series = $(element).data("plotSeries");
    if (_series == null) {
      if (typeof console != "undefined") {
        console.warn("$(elem).jHueBlueprint('add', options) requires an existing data serie to work. Use $(elem).jHueBlueprint(options) instead.");
      }
    }
    else {
      _series.push(getSerie(serie));
      var _plot = $.plot(element, _series, { grid: { borderWidth: element.data('plugin_' + pluginName).options.borderWidth } });
      $(element).data("plotObj", _plot);
      $(element).data("plotSeries", _series);
    }
  };

  function showTooltip(x, y, contents) {
    $("<div id='jHueBlueprintTooltip'>" + contents + "</div>").css({
      top: y + 5,
      left: x + 5
    }).appendTo("body").fadeIn(200);
  }


  function flot(plugin) {
    var _this = plugin;
    $(_this.element).width(_this.options.width).height(_this.options.height);
    var _options = {
      grid: {
        borderWidth: _this.options.borderWidth,
        clickable: true
      }
    }
    if (_this.options.tooltips) {
      _options.grid.hoverable = true;
    }
    if (_this.options.enableSelection) {
      _options.selection = {
        mode: "x",
        color: COLORS.GREEN
      }
    }
    if (_this.options.isDateTime) {
      _options.xaxis = {
        mode: "time"
      }
    }
    if (_this.options.isCategories) {
      _options.xaxis = {
        mode: "categories"
      }
    }
    if (_this.options.useCanvas) {
      _options.canvas = true;
    }
    var _serie = getSerie(_this.options);
    var _plot = $.plot($(_this.element), [_serie], _options);

    $(_this.element).bind("plotselected", function (event, ranges) {
      _this.options.onSelect(ranges);
    });

    if (_this.options.tooltips) {
      var previousPoint = null;
      $(_this.element).bind("plothover", function (event, pos, item) {

        if (item) {
          if (previousPoint != item.dataIndex) {

            previousPoint = item.dataIndex;

            $("#jHueBlueprintTooltip").remove();
            var x = item.datapoint[0],
                y = item.datapoint[1];

            if (_this.options.isDateTime && typeof moment != "undefined"){
              x = moment(x).utc().format("YYYY-MM-DD[T]HH:mm:ss[Z]");
            }

            if (_this.options.isCategories){
              x = item.series.data[item.dataIndex][0];
            }

            showTooltip(item.pageX, item.pageY, "X: "+x+", Y: "+y);
          }
        } else {
          $("#jHueBlueprintTooltip").remove();
          previousPoint = null;
        }
      });
    }
    $(_this.element).bind("plotclick", function (event, pos, item) {
      _this.options.onItemClick(pos, item);
    });
    $(_this.element).data("plotObj", _plot);
    $(_this.element).data("plotSeries", [_serie]);
  }

  function flot_pie(plugin) {
    var _this = plugin;
    $(_this.element).width(_this.options.width).height(_this.options.height);
    var _options = {
      grid: {
        borderWidth: _this.options.borderWidth,
        clickable: true
      },
      series: {
        pie: {
          show: true
        }
      }
    };
    if (_this.options.tooltips) {
      _options.grid.hoverable = true;
    }
    var _plot = $.plot(_this.element, _this.options.data, _options);
    $(_this.element).data("plotObj", _plot);
  }


  function getSerie(options) {
    var _chartData = options.data;
    if (options.isDateTime){
      var _newChartData = [];
      for (var i=0;i<_chartData.length;i++){
        var _tuple = _chartData[i];
        _tuple[0] = moment(_tuple[0]).unix()*1000;
        _newChartData.push(_tuple)
        }
      _chartData = _newChartData;
    }
    var _flotSerie = {
      data: _chartData,
      label: options.label
    }

    if (options.type == TYPES.LINECHART) {
      _flotSerie.lines = {show: true, fill: options.fill }
      _flotSerie.points = {show: true}
    }
    if (options.type == TYPES.BARCHART) {
      _flotSerie.bars = {show: true, fill: options.fill, barWidth: 0.6, align: "center" }
      _flotSerie.points = {show: true}
    }
    if (options.type == TYPES.POINTCHART) {
      _flotSerie.points = {show: true}
    }
    if (options.type == TYPES.PIECHART) {
      _flotSerie.pie = {show: true}
    }
    if (options.color != null) {
      _flotSerie.color = options.color;
    }
    return _flotSerie;
  }

  $.fn[pluginName] = function (options) {
    var _args = Array.prototype.slice.call(arguments);
    if (_args.length == 1) {
      return this.each(function () {
        if (!$.data(this, 'plugin_' + pluginName)) {
          $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
        }
      });
    }
    else {
      if (_args[0] == "add") { // add a serie to the graph
        addSerie(this, _args[1]);
      }
    }
  }

  $[pluginName] = function (options) {
    if (typeof console != "undefined") {
      console.warn("$(elem).jHueBlueprint() is a preferred call method.");
    }
    $(options.element).jHueBlueprint(options);
  };

  $[pluginName].COLORS = COLORS;
  $[pluginName].TYPES = TYPES;


})(jQuery, window, document);
