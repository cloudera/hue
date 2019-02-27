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
 * jHue row selector plugin
 *
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueRowSelector",
    defaults = {};

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
    $(_this.element).closest("tr").click(function (e) {
      if ($(e.target).data("row-selector-exclude") || $(e.target).closest("td").hasClass("row-selector-exclude")) {
        return;
      }
      if (!$(e.target).is("a")) {
        var href = $.trim($(_this.element).attr("href"));
        if (href != "" && href != "#" && href.indexOf("void(0)") == -1) {
          huePubSub.publish('open.link', $(_this.element).attr("href"));
        } else {
          $(_this.element).click();
        }
      }
    }).css("cursor", "pointer");
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
