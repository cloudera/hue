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
 *    - secondClickScrollToTop: (default false) if specified, the anchor stays for longer and you can re-click on it to scroll to this element
 */

(function ($, window, document, undefined) {

  var pluginName = "jHueScrollUp",
      defaults = {
        threshold: 100, // it displays it after 100 px of scroll
        secondClickScrollToTop: false
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

    var link = $("<a/>").attr("id", "jHueScrollUpAnchor").attr("href", "javascript:void(0)").html("<i class='fa fa-chevron-up'></i>").appendTo("body");
    if ($("#jHueScrollUpAnchor").length > 0) { // just one scroll up per page
      link = $("#jHueScrollUpAnchor");
      link.off("click");
    }

    if ($(_this.element).is("body")) {
      $(window).scroll(function () {
        $(($(window).scrollTop() > _this.options.threshold) ? link.fadeIn(200) : link.fadeOut(200));
      });
      link.click(function (event) {
        $("body, html").animate({scrollTop: $(_this.element).position().top}, 300);
        return false;
      });
    }
    else {
      $(_this.element).scroll(function () {
        var _fadeOutMs = 200;
        if (_this.options.secondClickScrollToTop) {
          _fadeOutMs = 1000;
        }
        $(($(_this.element).scrollTop() > _this.options.threshold) ? link.fadeIn(200) : link.fadeOut(_fadeOutMs));
      });
      link.on("click", function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (_this.options.secondClickScrollToTop) {
          if ($(_this.element).data("lastClick") == null || (new Date()).getTime() - $(_this.element).data("lastClick") > 1500) {
            $(_this.element).animate({scrollTop: 0}, 300);
          }
          else {
            $("body, html").animate({scrollTop: 0}, 300);
            link.fadeOut(200);
          }
          $(_this.element).data("lastClick", (new Date()).getTime());
        }
        else {
          $(_this.element).animate({scrollTop: 0}, 300);
        }
        return false;
      });
    }
  };

  $.fn[pluginName] = function (options) {
    return this.each(function () {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    });
  }

  $[pluginName] = function (options) {
    new Plugin($("body"), options);
  };

})(jQuery, window, document);
