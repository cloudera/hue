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
 * jHue table scroller plugin
 *
 * Three data attributes can be set on the table to modify the default behavior of the plugin:
 * - data-tablescroller-min-height="N" where N is a value in pixels: specifies a minimum height for the scrolling table,
 *      overriding the default 500px set by the plugin
 * - data-tablescroller-min-height-disable="true": disable enforcing a minimum height for the table
 * - data-tablescroller-disable="true": disable the plugin for the specific table
 * - data-tablescroller-enforce-height="true": displays the table at its maximum height accordingly to the page
 */

const pluginName = 'jHueTableScroller',
  defaults = {
    minHeight: 300,
    maxHeight: -1,
    heightAfterCorrection: 40
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
  resizeScrollingTable(this);
};

Plugin.prototype.init = function() {
  const _this = this;

  $(_this.element).data('original-height', $(_this.element).height());

  const disableScrollingTable = $(_this.element)
    .find('table')
    .eq(0)
    .data('tablescroller-disable');
  if (disableScrollingTable == null || disableScrollingTable !== true) {
    resizeScrollingTable(_this);
    let _resizeTimeout = -1;
    $(window).resize(() => {
      window.clearTimeout(_resizeTimeout);
      _resizeTimeout = window.setTimeout(() => {
        resizeScrollingTable(_this);
      }, 400);
    });
  }
};

function resizeScrollingTable(_this) {
  const el = _this.element;
  $(el)
    .css('overflow-y', '')
    .css('height', '');
  $(el).css('overflow-x', 'auto');
  let heightAfter = _this.options.heightAfterCorrection;
  $(el)
    .nextAll(':visible')
    .each(function() {
      heightAfter += $(this).outerHeight(true);
    });

  let heightCondition = $(el).height() > $(window).height() - $(el).offset().top - heightAfter;
  const enforceHeight = $(_this.element)
    .find('table')
    .eq(0)
    .data('tablescroller-enforce-height');
  if (enforceHeight !== undefined && enforceHeight == true) {
    heightCondition = true;
  }

  const fixedHeight =
    $(_this.element)
      .find('table')
      .eq(0)
      .data('tablescroller-fixed-height') || _this.options.maxHeight;

  if (heightCondition) {
    const specificMinHeight = $(el)
      .find('table')
      .eq(0)
      .data('tablescroller-min-height');
    let minHeightVal = _this.options.minHeight;
    if (!isNaN(parseFloat(specificMinHeight)) && isFinite(specificMinHeight)) {
      minHeightVal = parseFloat(specificMinHeight);
    }
    const disableMinHeight = $(_this.element)
      .find('table')
      .eq(0)
      .data('tablescroller-min-height-disable');
    if (disableMinHeight != null && disableMinHeight == true) {
      if (heightCondition) {
        $(el)
          .css('overflow-y', 'auto')
          .height(
            fixedHeight > -1 ? fixedHeight : $(window).height() - $(el).offset().top - heightAfter
          );
      }
    } else if ($(window).height() - $(el).offset().top - heightAfter > minHeightVal) {
      $(el)
        .css('overflow-y', 'auto')
        .height(
          fixedHeight > -1 ? fixedHeight : $(window).height() - $(el).offset().top - heightAfter
        );
    } else {
      if ($(el).data('original-height') > minHeightVal) {
        $(el)
          .css('overflow-y', 'auto')
          .height(minHeightVal);
      }
      if (fixedHeight > -1) {
        $(el)
          .css('overflow-y', 'auto')
          .css('maxHeight', fixedHeight);
      }
    }
  } else if (fixedHeight > -1) {
    $(el)
      .css('overflow-y', 'auto')
      .css('maxHeight', fixedHeight);
  }
}

$.fn[pluginName] = function(options) {
  return this.each(function() {
    if (!$.data(this, 'plugin_' + pluginName)) {
      $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
    } else {
      $.data(this, 'plugin_' + pluginName).setOptions(options);
    }
  });
};
