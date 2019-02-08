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

import huePubSub from 'utils/huePubSub';

/*
 * jHue scroll to left plugin
 * Can be used globally with
 *   $.jHueScrollLeft()
 * or with a target for the scroll left
 *   $(element).jHueScrollLeft()
 *
 *   options:
 *    - threshold: (default 100) value in pixels, scroll amount before the link appears
 */

const pluginName = 'jHueScrollLeft',
  defaults = {
    threshold: 100 // it displays it after 100 px of scroll
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  if ($(element).attr('jHueLeftScrollified') !== 'true') {
    this.setupScrollLeft();
  }
}

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
};

Plugin.prototype.setupScrollLeft = function() {
  const _this = this;
  let link = null,
    isActive = true;

  if ($('#jHueScrollLeftAnchor').length > 0) {
    // just one scroll up per page
    link = $('#jHueScrollLeftAnchor');
    $(document).off('click', '#jHueScrollLeftAnchor');
  } else {
    link = $('<a/>')
      .attr('id', 'jHueScrollLeftAnchor')
      .addClass('hueAnchor hueAnchorScroller')
      .attr('href', 'javascript:void(0)')
      .html("<i class='fa fa-fw fa-chevron-left'></i>")
      .appendTo(HUE_CONTAINER);
  }

  $(_this.element).attr('jHueLeftScrollified', 'true');

  if ($(_this.element).is('body')) {
    setScrollBehavior($(window), $('body, html'));
  } else {
    setScrollBehavior($(_this.element), $(_this.element));
  }

  function positionOtherAnchors() {
    const upPosition =
      $('#jHueScrollUpAnchor')
        .css('right')
        .replace(/px/gi, '') * 1;
    let right = upPosition - 30;
    if ($('#jHueScrollUpAnchor').is(':visible')) {
      right = upPosition;
    }

    if ($('#jHueScrollLeftAnchor').is(':visible')) {
      $('#jHueScrollLeftAnchor').css('right', right + 50 + 'px');
      right += 50;
    }

    $('.hue-datatable-search').css('right', right + 50 + 'px');
  }

  function setScrollBehavior(scrolled, scrollable) {
    scrolled.scroll(() => {
      if (scrolled.scrollLeft() > _this.options.threshold) {
        if (link.is(':hidden')) {
          positionOtherAnchors();
          if (isActive) {
            link.fadeIn(200, positionOtherAnchors);
          }
        }
        if (
          $(_this.element).data('lastScrollLeft') == null ||
          $(_this.element).data('lastScrollLeft') < scrolled.scrollLeft()
        ) {
          $('#jHueScrollLeftAnchor').data('caller', scrollable);
        }
        $(_this.element).data('lastScrollLeft', scrolled.scrollTop());
      } else {
        checkForAllScrolls();
      }
    });
  }

  function checkForAllScrolls() {
    let _allOk = true;
    $(document)
      .find("[jHueLeftScrollified='true']")
      .each((cnt, item) => {
        if ($(item).is('body')) {
          if ($(window).scrollLeft() > _this.options.threshold) {
            _allOk = false;
            $('#jHueScrollLeftAnchor').data('caller', $('body, html'));
          }
        } else if ($(item).scrollLeft() > _this.options.threshold) {
          _allOk = false;
          $('#jHueScrollLeftAnchor').data('caller', $(item));
        }
      });
    if (_allOk) {
      if (isActive) {
        link.fadeOut(200, positionOtherAnchors);
      }
      $('#jHueScrollLeftAnchor').data('caller', null);
    }
  }

  $(document).on('click', '#jHueScrollLeftAnchor', event => {
    if ($('#jHueScrollLeftAnchor').data('caller') != null) {
      $('#jHueScrollLeftAnchor')
        .data('caller')
        .animate({ scrollLeft: 0 }, 300, () => {
          $(document)
            .find("[jHueLeftScrollified='true']")
            .trigger('scroll_update');
          if (
            $(document)
              .find("[jHueLeftScrollified='true']")
              .not($('#jHueScrollLeftAnchor').data('caller'))
              .is('body') &&
            $(window).scrollLeft() > _this.options.threshold
          ) {
            $('#jHueScrollLeftAnchor').data('caller', $('body, html'));
          } else {
            checkForAllScrolls();
          }
        });
    }
    return false;
  });

  huePubSub.subscribe('hue.scrollleft.show', () => {
    isActive = true;
  });

  huePubSub.subscribe('hue.scrollleft.hide', () => {
    isActive = false;
    if (link.is(':visible')) {
      link.hide();
    }
  });
};

$.fn[pluginName] = function(options) {
  return this.each(function() {
    $.data(this, 'plugin_' + pluginName, new Plugin(this, options));
  });
};

$[pluginName] = function(options) {
  new Plugin($('body'), options);
};
