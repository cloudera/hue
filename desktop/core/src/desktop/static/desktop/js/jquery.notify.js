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
 * jHue notify plugin
 *
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueNotify",
    TYPES = {
      INFO: "INFO",
      ERROR: "ERROR",
      GENERAL: "GENERAL"
    },
    defaults = {
      level: TYPES.GENERAL,
      message: "",
      sticky: false,
      css: null
    };

  function Plugin(options) {
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.show();
  }

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  Plugin.prototype.show = function () {
    var _this = this;
    var MARGIN = 4;

    _this.options.message = _this.options.message.replace(/(<([^>]+)>)/ig, ''); // escape HTML messages

    if (_this.options.message !== '' && $(".jHueNotify .message").last().text() !== _this.options.message) {

      var el = $("#jHueNotify").clone();
      el.removeAttr("id");

      // stops all the current animations and resets the style
      el.stop(true);
      el.attr("class", "alert jHueNotify");
      el.find(".close").hide();

      if ($(".jHueNotify").last().position() != null) {
        el.css("top", $(".jHueNotify").last().position().top + $(".jHueNotify").last().outerHeight() + MARGIN);
      }

      var scrollColor = '#f0c36d';

      if (_this.options.level == TYPES.ERROR) {
        el.addClass("alert-error");
        scrollColor = '#b94a48';
      }
      else if (_this.options.level == TYPES.INFO) {
        el.addClass("alert-info");
        scrollColor = '#0B7FAD';
      }
      el.find(".message").html("<strong>" + _this.options.message + "</strong>");

      if (_this.options.css != null) {
        el.attr("style", _this.options.css);
      }

      el.on('dblclick', function () {
        el.toggleClass('expanded');
      });

      if (_this.options.sticky) {
        el.find(".close").click(function () {
          el.fadeOut();
          el.nextAll(".jHueNotify").animate({
            top: '-=' + (el.outerHeight() + MARGIN)
          }, 200);
          el.remove();
        }).show();
        el.show();
      }
      else {
        var t = window.setTimeout(function () {
          el.fadeOut();
          el.nextAll(".jHueNotify").animate({
            top: '-=' + (el.outerHeight() + MARGIN)
          }, 200);
          el.remove();

        }, 3000);
        el.click(function () {
          window.clearTimeout(t);
          $(this).stop(true);
          $(this).fadeOut();
          $(this).nextAll(".jHueNotify").animate({
            top: '-=' + ($(this).outerHeight() + MARGIN)
          }, 200);
        });
        el.show();
      }
      el.appendTo(HUE_CONTAINER);
    }
  };

  $[pluginName] = function () {
  };

  $[pluginName].info = function (message) {
    new Plugin({level: TYPES.INFO, message: message});
  };

  $[pluginName].warn = function (message) {
    new Plugin({level: TYPES.GENERAL, message: message, sticky: true});
  };

  $[pluginName].error = function (message) {
    new Plugin({level: TYPES.ERROR, message: message, sticky: true});
  };

  $[pluginName].notify = function (options) {
    new Plugin(options);
  };

})(jQuery, window, document);
