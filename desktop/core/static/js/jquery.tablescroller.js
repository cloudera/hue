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
 * jHue table scroller plugin
 *
 * Three data attributes can be set on the table to modify the default behavior of the plugin:
 * - data-tablescroller-min-height="N" where N is a value in pixels: specifies a minimum height for the scrolling table,
 *      overriding the default 500px set by the plugin
 * - data-tablescroller-min-height-disable="true": disable enforcing a minimum height for the table
 * - data-tablescroller-disable="true": disable the plugin for the specific table
 * - data-tablescroller-enforce-height="true": displays the table at its maximum height accordingly to the page
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueTableScroller",
      defaults = {
        minHeight: 400
      };

  function Plugin(element, options) {
    this.element = element;
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.init();
  }

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  Plugin.prototype.init = function () {
    var _this = this;

    $(_this.element).data("original-height", $(_this.element).height());

    var disableScrollingTable = $(_this.element).find("table").eq(0).data("tablescroller-disable");
    if (disableScrollingTable == null || disableScrollingTable != true) {
      resizeScrollingTable(_this.element);
      var _resizeTimeout = -1;
      var winWidth = $(window).width();
      var winHeight = $(window).height();
      $(window).resize(function () {
        window.clearTimeout(_resizeTimeout);
        _resizeTimeout = window.setTimeout(function(){
          // prevents endless loop in IE8
          if (winWidth != $(window).width() || winHeight != $(window).height()) {
            resizeScrollingTable(_this.element);
            winWidth = $(window).width();
            winHeight = $(window).height();
          }
        }, 400);
      });
    }

    function resizeScrollingTable(el) {
      $(el).css("overflow-y", "").css("height", "");
      var heightAfter = 0;
      $(el).nextAll(":visible").each(function () {
        heightAfter += $(this).outerHeight(true);
      });

      var heightCondition = $(el).height() > ($(window).height() - $(el).offset().top - heightAfter);
      var enforceHeight = $(_this.element).find("table").eq(0).data("tablescroller-enforce-height");
      if (enforceHeight !== undefined && enforceHeight == true) {
        heightCondition = true;
      }

      if (heightCondition) {
        var specificMinHeight = $(el).find("table").eq(0).data("tablescroller-min-height");
        var minHeightVal = _this.options.minHeight;
        if (!isNaN(parseFloat(specificMinHeight)) && isFinite(specificMinHeight)) {
          minHeightVal = parseFloat(specificMinHeight);
        }
        var disableMinHeight = $(_this.element).find("table").eq(0).data("tablescroller-min-height-disable");
        if (disableMinHeight != null && disableMinHeight == true) {
          if (heightCondition) {
            $(el).css("overflow-y", "auto").height($(window).height() - $(el).offset().top - heightAfter);
          }
        }
        else {
          if (($(window).height() - $(el).offset().top - heightAfter) > minHeightVal){
            $(el).css("overflow-y", "auto").height($(window).height() - $(el).offset().top - heightAfter);
          }
          else {
            if ($(el).data("original-height") > minHeightVal){
              $(el).css("overflow-y", "auto").height(minHeightVal);
            }
          }
        }
      }
    }
  };

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      if (!$.data(this, 'plugin_' + pluginName)) {
        $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
      }
      else {
        $.data(this, 'plugin_' + pluginName).setOptions(options);
      }
    });
  }

})(jQuery, window, document);
