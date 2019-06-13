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

import $ from 'jquery';

/*
 * jHue Delayed Input plugin
 * use it with
 * $("#element").jHueDelayedInput( __FUNCTION_YOU_WANT_TO_CALL__, __TIMEOUT_IN_MS__ [optional])
 */

const pluginName = 'jHueDelayedInput',
  defaults = {
    fn: null,
    timeout: 300,
    skipOnEnterAndKeys: false
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  this.init();
}

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
};

Plugin.prototype.init = function() {
  const _this = this;
  let _timeout = -1;
  if (_this.options.fn != null) {
    const event = isIE11 ? 'input' : 'keyup';

    $(_this.element).on(event, e => {
      if (!(_this.options.skipOnEnterAndKeys && [13, 37, 38, 39, 40].indexOf(e.keyCode) > -1)) {
        window.clearTimeout(_timeout);
        _timeout = window.setTimeout(_this.options.fn, _this.options.timeout);
      }
    });
  }
};

$.fn[pluginName] = function(fn, timeout, skipOnEnterAndKeys) {
  const _options = {
    fn: fn,
    timeout: timeout,
    skipOnEnterAndKeys: typeof skipOnEnterAndKeys !== 'undefined' && skipOnEnterAndKeys
  };
  return this.each(function() {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, _options));
    } else {
      $.data(this, 'plugin_' + pluginName).setOptions(_options);
    }
  });
};
