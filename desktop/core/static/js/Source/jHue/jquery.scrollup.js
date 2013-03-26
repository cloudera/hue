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
 * jHue scroll to top plugin
 * Can be used globally with
 *   $.jHueScrollUp()
 * or with a target for the scroll up
 *   $(element).jHueScrollUp()
 *
 *   options:
 *    - threshold: (default 100) value in pixels, scroll amount before the link appears
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueScrollUp",
      defaults = {
        threshold: 100 // it displays it after 100 px of scroll
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

    if ($("#jHueScrollUpAnchor").length > 0) { // just one scroll up per page
      return;
    }

    var link = $("<a/>").attr("id", "jHueScrollUpAnchor").attr("href", "javascript:void(0)").html("<i class='icon-chevron-up'></i>").appendTo("body");

    $(window).scroll(function () {
      $(($(window).scrollTop() > _this.options.threshold) ? link.fadeIn(200) : link.fadeOut(200));
    });

    link.click(function (event) {
      $("body, html").animate({scrollTop: $(_this.element).position().top}, 300);
      return false;
    });
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

  $[pluginName] = function (options) {
    new Plugin($("body"), options);
  };

})(jQuery, window, document);
