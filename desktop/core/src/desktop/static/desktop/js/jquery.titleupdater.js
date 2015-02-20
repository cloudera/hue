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
 * jHue title updater plugin
 *
 */
;
(function ($, window, document, undefined) {

  var pluginName = "jHueTitleUpdater",
    defaults = {
      message: "",
      reset: false
    };

  function Plugin(options) {
    this.options = $.extend({}, defaults, options);
    this._defaults = defaults;
    this._name = pluginName;
    this.updateStatusBar();
  }

  Plugin.prototype.setOptions = function (options) {
    this.options = $.extend({}, defaults, options);
  };

  Plugin.prototype.updateStatusBar = function () {
    var _this = this;
    if (_this.options.reset && $(document).data("jHueTitleUpdaterOriginal") != null) {
      document.title = $(document).data("jHueTitleUpdaterOriginal");
      $(document).data("jHueTitleUpdaterOriginal", null);
    }
    else if (_this.options.message != "") {
      if ($(document).data("jHueTitleUpdaterOriginal") == null) {
        $(document).data("jHueTitleUpdaterOriginal", document.title);
      }
      document.title = _this.options.message + " - " + $(document).data("jHueTitleUpdaterOriginal");
    }
  };

  $[pluginName] = function () {
  };

  $[pluginName].reset = function () {
    new Plugin({ reset: true});
  };

  $[pluginName].set = function (message) {
    new Plugin({ message: message});
  };

})(jQuery, window, document);
