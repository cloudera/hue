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

    var link = $("<a/>").attr("id", "jHueScrollUpAnchor").attr("href", "javascript:void(0)").html("<i class='fa fa-chevron-up'></i>").appendTo("body");
    if ($("#jHueScrollUpAnchor").length > 0) { // just one scroll up per page
      link = $("#jHueScrollUpAnchor");
      $(document).off("click", "#jHueScrollUpAnchor");
    }

    $(_this.element).attr("jHueScrollified", "true");

    if ($(_this.element).is("body")) {
      setScrollBehavior($(window), $("body, html"));
    }
    else {
      setScrollBehavior($(_this.element), $(_this.element));
    }

    function setScrollBehavior(scrolled, scrollable) {
      scrolled.scroll(function () {
        if (scrolled.scrollTop() > _this.options.threshold) {
          if (link.is(":hidden")) {
            link.fadeIn(200);
          }
          if ($(_this.element).data("lastScrollTop") == null || $(_this.element).data("lastScrollTop") < scrolled.scrollTop()) {
            $("#jHueScrollUpAnchor").data("caller", scrollable);
          }
          $(_this.element).data("lastScrollTop", scrolled.scrollTop());
        }
        else {
          checkForAllScrolls();
        }
      });
    }

    function checkForAllScrolls() {
      var _allOk = true;
      $(document).find("[jHueScrollified='true']").each(function (cnt, item) {
        if ($(item).is("body")) {
          if ($(window).scrollTop() > _this.options.threshold) {
            _allOk = false;
            $("#jHueScrollUpAnchor").data("caller", $("body, html"));
          }
        }
        else {
          if ($(item).scrollTop() > _this.options.threshold) {
            _allOk = false;
            $("#jHueScrollUpAnchor").data("caller", $(item));
          }
        }
      });
      if (_allOk) {
        link.fadeOut(200);
        $("#jHueScrollUpAnchor").data("caller", null);
      }
    }

    $(document).on("click", "#jHueScrollUpAnchor", function (event) {
      if ($("#jHueScrollUpAnchor").data("caller") != null) {
        $("#jHueScrollUpAnchor").data("caller").animate({scrollTop: 0}, 300, function () {
          if ($(document).find("[jHueScrollified='true']").not($("#jHueScrollUpAnchor").data("caller")).is("body") && $(window).scrollTop() > _this.options.threshold) {
            $("#jHueScrollUpAnchor").data("caller", $("body, html"));
          }
          else {
            checkForAllScrolls();
          }
        });
      }
      return false;
    });
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
