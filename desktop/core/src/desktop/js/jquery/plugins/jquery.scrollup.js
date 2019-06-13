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
 * jHue scroll to top plugin
 * Can be used globally with
 *   $.jHueScrollUp()
 * or with a target for the scroll up
 *   $(element).jHueScrollUp()
 *
 *   options:
 *    - threshold: (default 100) value in pixels, scroll amount before the link appears
 */

const pluginName = 'jHueScrollUp',
  defaults = {
    threshold: 100, // it displays it after 100 px of scroll
    scrollLeft: false
  };

function Plugin(element, options) {
  this.element = element;
  this.options = $.extend({}, defaults, options);
  this._defaults = defaults;
  this._name = pluginName;
  if ($(element).attr('jHueScrollified') !== 'true') {
    this.setupScrollUp();
  }
  if (this.options.scrollLeft) {
    $(element).jHueScrollLeft(this.options.threshold);
  }
}

Plugin.prototype.setOptions = function(options) {
  this.options = $.extend({}, defaults, options);
};

Plugin.prototype.setupScrollUp = function() {
  const _this = this;
  let link = null;

  if ($('#jHueScrollUpAnchor').length > 0) {
    // just one scroll up per page
    link = $('#jHueScrollUpAnchor');
    $(document).off('click', '#jHueScrollUpAnchor');
  } else {
    link = $('<a/>')
      .attr('id', 'jHueScrollUpAnchor')
      .addClass('hueAnchor hueAnchorScroller')
      .attr('href', 'javascript:void(0)')
      .html("<i class='fa fa-fw fa-chevron-up'></i>")
      .appendTo(HUE_CONTAINER);
  }

  $(_this.element).attr('jHueScrollified', 'true');

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

  huePubSub.subscribe('reposition.scroll.anchor.up', () => {
    $('#jHueScrollUpAnchor').css('right', '20px');
    if (!$(_this.element).is('body') && $(_this.element).is(':visible')) {
      const adjustRight =
        $(window).width() - ($(_this.element).width() + $(_this.element).offset().left);
      if (adjustRight > 0) {
        $('#jHueScrollUpAnchor').css('right', adjustRight + 'px');
      }
    }
    positionOtherAnchors();
  });

  function setScrollBehavior(scrolled, scrollable) {
    scrolled.scroll(() => {
      if (scrolled.scrollTop() > _this.options.threshold) {
        if (link.is(':hidden')) {
          huePubSub.publish('reposition.scroll.anchor.up');
          link.fadeIn(200, () => {
            huePubSub.publish('reposition.scroll.anchor.up');
          });
        }
        if (
          $(_this.element).data('lastScrollTop') == null ||
          $(_this.element).data('lastScrollTop') < scrolled.scrollTop()
        ) {
          $('#jHueScrollUpAnchor').data('caller', scrollable);
        }
        $(_this.element).data('lastScrollTop', scrolled.scrollTop());
      } else {
        checkForAllScrolls();
      }
    });
    window.setTimeout(() => {
      huePubSub.publish('reposition.scroll.anchor.up');
    }, 0);
  }

  function checkForAllScrolls() {
    let _allOk = true;
    $(document)
      .find("[jHueScrollified='true']")
      .each((cnt, item) => {
        if ($(item).is('body')) {
          if ($(window).scrollTop() > _this.options.threshold) {
            _allOk = false;
            $('#jHueScrollUpAnchor').data('caller', $('body, html'));
          }
        } else if ($(item).scrollTop() > _this.options.threshold) {
          _allOk = false;
          $('#jHueScrollUpAnchor').data('caller', $(item));
        }
      });
    if (_allOk) {
      link.fadeOut(200, positionOtherAnchors);
      $('#jHueScrollUpAnchor').data('caller', null);
    }
  }

  $(document).on('click', '#jHueScrollUpAnchor', event => {
    if ($('#jHueScrollUpAnchor').data('caller') != null) {
      $('#jHueScrollUpAnchor')
        .data('caller')
        .animate({ scrollTop: 0 }, 300, () => {
          if (
            $(document)
              .find("[jHueScrollified='true']")
              .not($('#jHueScrollUpAnchor').data('caller'))
              .is('body') &&
            $(window).scrollTop() > _this.options.threshold
          ) {
            $('#jHueScrollUpAnchor').data('caller', $('body, html'));
          } else {
            checkForAllScrolls();
          }
        });
    }
    return false;
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
