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
 * jHue horizontal scrollbar for dataTables_wrapper
 *
 */

const pluginName = 'jHueHorizontalScrollbar',
  defaults = {};

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  this.init();
}

function initWhenReady(el) {
  let $wrapper = $(el).parents('.dataTables_wrapper');
  if (!$wrapper.length) {
    return;
  }

  const colWidth = $(el).find('thead tr th').outerWidth();

  let wrapperWidth = $wrapper.width();
  let wrapperScrollWidth = $wrapper[0].scrollWidth;

  if ($wrapper.find('.hue-scrollbar-x-rail').length === 0 && wrapperWidth < wrapperScrollWidth) {
    $('.hue-scrollbar-x-rail').remove();
    const $scrollbarRail = $('<div>');
    const $scrollbar = $('<div>').addClass('hue-scrollbar-x');
    $scrollbar.width(Math.max(20, wrapperWidth * (wrapperWidth / wrapperScrollWidth)));
    $scrollbar.appendTo($scrollbarRail);
    try {
      $scrollbar.draggable('destroy');
    } catch (e) {}

    let throttleScrollTimeout = -1;
    let scrollbarWidth = 0;
    let railWidth = 0;
    $scrollbar.draggable({
      axis: 'x',
      containment: 'parent',
      start: function () {
        $wrapper = $(el).parents('.dataTables_wrapper');
        wrapperScrollWidth = $wrapper[0].scrollWidth;
        wrapperWidth = $wrapper.width();
        scrollbarWidth = $(this).outerWidth();
        railWidth = $scrollbarRail.innerWidth();
        $scrollbarRail.css('opacity', '1');
      },
      drag: (e, ui) => {
        $wrapper.scrollLeft(
          (wrapperScrollWidth - wrapperWidth) * (ui.position.left / (railWidth - scrollbarWidth))
        );
        window.clearTimeout(throttleScrollTimeout);
        throttleScrollTimeout = window.setTimeout(() => {
          $wrapper.trigger('scroll');
        }, 50);
      },
      stop: () => {
        $scrollbarRail.css('opacity', '');
      }
    });

    $wrapper.bind('mousewheel', function (e) {
      const _deltaX = e.deltaX * e.deltaFactor,
        _deltaY = e.deltaY;

      if (Math.abs(_deltaX) >= Math.abs(_deltaY)) {
        const self = this;
        self.scrollLeft += _deltaX;
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        if (self.scrollLeft > 0) {
          $scrollbar.css(
            'left',
            ($scrollbarRail[0].getBoundingClientRect().width -
              $scrollbar[0].getBoundingClientRect().width) *
              (self.scrollLeft / (self.scrollWidth - self.getBoundingClientRect().width)) +
              'px'
          );
          window.clearTimeout(throttleScrollTimeout);
          throttleScrollTimeout = window.setTimeout(() => {
            $wrapper.trigger('scroll');
          }, 50);
        }
      }
    });
    $scrollbarRail.addClass('hue-scrollbar-x-rail').appendTo($wrapper);
    $scrollbarRail.width(wrapperWidth - colWidth);
    $scrollbarRail.css('marginLeft', colWidth + 'px');
    if ($scrollbarRail.position().top > $(window).height() - 10) {
      $scrollbarRail.css('bottom', '0');
    }
    $wrapper.bind('scroll_update', () => {
      $scrollbar.css(
        'left',
        ($scrollbarRail.width() - $scrollbar.width()) *
          ($wrapper.scrollLeft() / (wrapperScrollWidth - wrapperWidth)) +
          'px'
      );
    });
  } else {
    if (wrapperWidth === wrapperScrollWidth) {
      $('.hue-scrollbar-x-rail').hide();
    } else {
      $('.hue-scrollbar-x-rail').show();
    }
    $wrapper.find('.hue-scrollbar-x-rail').width(wrapperWidth - colWidth);
    const scrollbar = $wrapper.find('.hue-scrollbar-x');
    scrollbar.width(Math.max(20, wrapperWidth * (wrapperWidth / wrapperScrollWidth)));

    const scrollbarRail = $wrapper.find('.hue-scrollbar-x-rail');
    scrollbarRail.width(wrapperWidth - colWidth);
    scrollbarRail.css('marginLeft', colWidth + 'px');
    scrollbar.css(
      'left',
      (scrollbarRail.width() - scrollbar.width()) *
        ($wrapper.scrollLeft() / (wrapperScrollWidth - wrapperWidth)) +
        'px'
    );
  }
}

Plugin.prototype.init = function () {
  const el = this.element;

  const checkWidth = function () {
    if ($(el).parents('.dataTables_wrapper').width() > 0) {
      initWhenReady(el);
    } else {
      window.setTimeout(checkWidth, 100);
    }
  };

  checkWidth();
};

$.fn[pluginName] = function (options) {
  return this.each(function () {
    $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
  });
};
