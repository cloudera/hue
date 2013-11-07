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

jQuery.cachedScripts = {};

jQuery.cacheScript = function (url, callback) {
  if (jQuery.cachedScripts != null && jQuery.cachedScripts[url] != null) {
    callback(jQuery.cachedScripts[url]);
  }
  else {
    var options = $.extend({}, {
      dataType: "script",
      cache: true,
      url: url,
      async: false,
      complete: function (script) {
        jQuery.cachedScripts[url] = script;
        callback(script);
      }
    });
    return jQuery.ajax(options);
  }
};

var FLOT_LOADED, FLOT_PIE_LOADED = false;

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
    $.cacheScript("/static/ext/js/jquery/plugins/jquery.flot.min.js", function (script, textStatus) {
      FLOT_LOADED = true;
      if (_this.options.type == TYPES.PIECHART) {
        $.cacheScript("/static/ext/js/jquery/plugins/jquery.flot.pie.min.js", function (script, textStatus) {
          FLOT_PIE_LOADED = true;
          flot_pie(_this);
        });
      }
      else {
        if (_this.options.enableSelection) {
          $.cacheScript("/static/ext/js/jquery/plugins/jquery.flot.selection.min.js", function (script, textStatus) {
            flot(_this);
          });
        }
        else {
          flot(_this);
        }
      }
    });
  };

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  function addSerie(element, serie) {
    if (!FLOT_LOADED) {
      window.setTimeout(function () {
        addSerie(element, serie);
      }, 500)
    }
    else {
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
    var _serie = getSerie(_this.options);
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
    var _plot = $.plot(_this.element, [_serie], _options);
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
            var x = item.datapoint[0].toFixed(2),
                y = item.datapoint[1].toFixed(2);

            showTooltip(item.pageX, item.pageY, x);
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
    var _flotSerie = {
      data: options.data,
      label: options.label
    }

    if (options.type == TYPES.LINECHART) {
      _flotSerie.lines = {show: true, fill: options.fill }
      _flotSerie.points = {show: true}
    }
    if (options.type == TYPES.BARCHART) {
      _flotSerie.bars = {show: true, fill: options.fill }
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
