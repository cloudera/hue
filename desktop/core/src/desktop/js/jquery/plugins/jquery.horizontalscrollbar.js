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
  if ($(el).parents('.dataTables_wrapper').length > 0) {
    const colWidth = $(el)
      .find('thead tr th')
      .outerWidth();
    if (
      $(el)
        .parents('.dataTables_wrapper')
        .find('.hue-scrollbar-x-rail').length == 0 &&
      $(el)
        .parents('.dataTables_wrapper')
        .width() < $(el).parents('.dataTables_wrapper')[0].scrollWidth
    ) {
      $('.hue-scrollbar-x-rail').remove();
      const scrollbarRail = $('<div>');
      const scrollbar = $('<div>').addClass('hue-scrollbar-x');
      scrollbar.width(
        Math.max(
          20,
          $(el)
            .parents('.dataTables_wrapper')
            .width() *
            ($(el)
              .parents('.dataTables_wrapper')
              .width() /
              $(el).parents('.dataTables_wrapper')[0].scrollWidth)
        )
      );
      scrollbar.appendTo(scrollbarRail);
      try {
        scrollbar.draggable('destroy');
      } catch (e) {}
      let throttleScrollTimeout = -1;

      let drag_start_position_offset = null;
      scrollbar.draggable({
        axis: 'x',
        containment: 'parent',
        start: function(e, ui) {
          drag_start_position_offset = e.clientX - ui.position.left;
        },
        drag: function(e, ui) {
          const scrollbarOffsetMin = scrollbarRail.offset().left;
          const scrollbarOffsetMax = scrollbarOffsetMin + scrollbarRail.width() - $(this).width();
          let scrollbarPosition = e.clientX - drag_start_position_offset;
          const scrollbarPositionMax = scrollbarOffsetMax - scrollbarOffsetMin;
          scrollbarPosition = Math.min(scrollbarPosition, scrollbarPositionMax);
          scrollbarPosition = Math.max(scrollbarPosition, 0);
          ui.position.left = scrollbarPosition;
          const percentage = scrollbarPosition / (scrollbarRail.width() - $(this).width());
          const dataTables = $(el).parents('.dataTables_wrapper');
          dataTables.scrollLeft(
            (dataTables[0].scrollWidth - dataTables[0].clientWidth) * percentage
          );
          throttleScrollTimeout = window.setTimeout(() => {
            $(el)
              .parents('.dataTables_wrapper')
              .trigger('scroll');
          }, 2);
        }
      });
      $(el)
        .parents('.dataTables_wrapper')
        .bind('mousewheel', function(e) {
          const _deltaX = e.deltaX * e.deltaFactor,
            _deltaY = e.deltaY;

          if (Math.abs(_deltaX) >= Math.abs(_deltaY)) {
            const self = this;
            self.scrollLeft += _deltaX;
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            if (self.scrollLeft > 0) {
              scrollbar.css(
                'left',
                (scrollbarRail[0].getBoundingClientRect().width -
                  scrollbar[0].getBoundingClientRect().width) *
                  (self.scrollLeft / (self.scrollWidth - self.getBoundingClientRect().width)) +
                  'px'
              );
              window.clearTimeout(throttleScrollTimeout);
              throttleScrollTimeout = window.setTimeout(() => {
                $(el)
                  .parents('.dataTables_wrapper')
                  .trigger('scroll');
              }, 50);
            }
          }
        });
      scrollbarRail.addClass('hue-scrollbar-x-rail').appendTo($(el).parents('.dataTables_wrapper'));
      scrollbarRail.width(
        $(el)
          .parents('.dataTables_wrapper')
          .width() - colWidth
      );
      scrollbarRail.css('marginLeft', colWidth + 'px');
      if (scrollbarRail.position().top > $(window).height() - 10) {
        scrollbarRail.css('bottom', '0');
      }
      $(el)
        .parents('.dataTables_wrapper')
        .bind('scroll_update', () => {
          scrollbar.css(
            'left',
            (scrollbarRail.width() - scrollbar.width()) *
              ($(el)
                .parents('.dataTables_wrapper')
                .scrollLeft() /
                ($(el).parents('.dataTables_wrapper')[0].scrollWidth -
                  $(el)
                    .parents('.dataTables_wrapper')
                    .width())) +
              'px'
          );
        });
    } else {
      if (
        $(el)
          .parents('.dataTables_wrapper')
          .width() === $(el).parents('.dataTables_wrapper')[0].scrollWidth
      ) {
        $('.hue-scrollbar-x-rail').hide();
      } else {
        $('.hue-scrollbar-x-rail').show();
      }
      $(el)
        .parents('.dataTables_wrapper')
        .find('.hue-scrollbar-x-rail')
        .width(
          $(el)
            .parents('.dataTables_wrapper')
            .width() - colWidth
        );
      const scrollbar = $(el)
        .parents('.dataTables_wrapper')
        .find('.hue-scrollbar-x');
      scrollbar.width(
        Math.max(
          20,
          $(el)
            .parents('.dataTables_wrapper')
            .width() *
            ($(el)
              .parents('.dataTables_wrapper')
              .width() /
              $(el).parents('.dataTables_wrapper')[0].scrollWidth)
        )
      );

      const scrollbarRail = $(el)
        .parents('.dataTables_wrapper')
        .find('.hue-scrollbar-x-rail');
      scrollbarRail.width(
        $(el)
          .parents('.dataTables_wrapper')
          .width() - colWidth
      );
      scrollbarRail.css('marginLeft', colWidth + 'px');
      scrollbar.css(
        'left',
        (scrollbarRail.width() - scrollbar.width()) *
          ($(el)
            .parents('.dataTables_wrapper')
            .scrollLeft() /
            ($(el).parents('.dataTables_wrapper')[0].scrollWidth -
              $(el)
                .parents('.dataTables_wrapper')
                .width())) +
          'px'
      );
    }
  }
}

Plugin.prototype.init = function() {
  const el = this.element;

  const checkWidth = function() {
    if (
      $(el)
        .parents('.dataTables_wrapper')
        .width() > 0
    ) {
      initWhenReady(el);
    } else {
      window.setTimeout(checkWidth, 100);
    }
  };

  checkWidth();
};

$.fn[pluginName] = function(options) {
  return this.each(function() {
    $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
  });
};
