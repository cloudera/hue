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
import ko from 'knockout';

import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.templatePopover = {
  init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
    const options = ko.unwrap(valueAccessor());

    const clickTrigger = options.trigger === 'click';
    let $container = $('#popover-container');
    if (!$container.length) {
      $container = $('<div>')
        .attr('id', 'popover-container')
        .appendTo(window.HUE_CONTAINER);
      $('<div>')
        .addClass('temp-content')
        .hide()
        .appendTo($container);
      $('<div>')
        .addClass('temp-title')
        .hide()
        .appendTo($container);
    }

    const $content = $container.find('.temp-content');
    const $title = $container.find('.temp-title');

    $.extend(options, { html: true, trigger: 'manual', container: '#popover-container' });

    const $element = $(element);

    const visible = options.visible || ko.observable(false);

    let trackElementInterval = -1;

    const hidePopover = function() {
      if (visible()) {
        window.clearInterval(trackElementInterval);
        $element.popover('hide');
        visible(false);
        $(document).off('click', hideOnClickOutside);
      }
    };

    const closeSub = huePubSub.subscribe('close.popover', hidePopover);

    const hideOnClickOutside = function(event) {
      if (
        visible() &&
        $element.data('popover') &&
        !$.contains($element.data('popover').$tip[0], event.target)
      ) {
        hidePopover();
      }
    };

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      if (visible && $element.data('popover')) {
        hidePopover();
      }
      closeSub.remove();
    });

    const afterRender = function() {
      options.content = $content.html();
      options.title = $title.html();
      let triggerTitle;
      if ($element.attr('title')) {
        triggerTitle = $element.attr('title');
        $element.attr('title', null);
      }
      $element.popover(options);
      $element.popover('show');
      if (triggerTitle) {
        $element.attr('title', triggerTitle);
      }
      const $tip = $element.data('popover').$tip;
      if (window.HUE_CONTAINER !== 'body') {
        $tip.css({ position: 'fixed', 'z-index': 2000 });
        $tip.appendTo(window.HUE_CONTAINER);

        $tip.offset({
          left: $element.offset().left + $element.outerWidth(true) + 10,
          top: $element.offset().top + $element.outerHeight(true) / 2 - $tip.outerHeight(true) / 2
        });
      }
      ko.cleanNode($tip.get(0));
      ko.applyBindings(viewModel, $tip.get(0));
      $tip.find('.close-popover, .close-template-popover').click(event => {
        hidePopover();
        event.stopPropagation();
      });
      if (options.minWidth) {
        const heightBefore = $tip.outerHeight(true);
        const widthBefore = $tip.outerWidth(true);
        $tip.css('min-width', options.minWidth);
        // The min-width might affect the height/width in which case we reposition the popover depending on placement
        const heightDiff = (heightBefore - $tip.outerHeight(true)) / 2;
        const widthDiff = (widthBefore - $tip.outerWidth(true)) / 2;
        if (
          (!options.placement || options.placement === 'left' || options.placement === 'right') &&
          heightDiff !== 0
        ) {
          $tip.css('top', $tip.position().top + heightDiff + 'px');
        } else if (
          options.placement &&
          (options.placement === 'bottom' || options.placement === 'top') &&
          widthDiff !== 0
        ) {
          $tip.css('left', $tip.position().left + widthDiff + 'px');
        }
      }
      let lastWidth = $element.outerWidth(true);
      let lastOffset = $element.offset();
      let lastHeight = $element.outerHeight(true);
      trackElementInterval = window.setInterval(() => {
        const elementWidth = $element.outerWidth(true);
        const elementHeight = $element.outerHeight(true);
        const elementOffset = $element.offset();
        if (
          lastHeight !== elementHeight ||
          lastWidth !== $element.outerWidth(true) ||
          lastOffset.top !== elementOffset.top ||
          lastOffset.left !== elementOffset.left
        ) {
          $tip.css({
            left: elementOffset.left + elementWidth / 2 - $tip.outerWidth(true) / 2,
            top: elementOffset.top + elementHeight + 10
          });
          lastWidth = elementWidth;
          lastOffset = elementOffset;
          lastHeight = elementHeight;
        }
      }, 50);
      $content.empty();
      $title.empty();
      $(document).on('click', hideOnClickOutside);
      visible(true);
    };

    const showPopover = function(preventClose) {
      if (!preventClose) {
        huePubSub.publish('close.popover');
      }
      ko.renderTemplate(
        options.contentTemplate,
        viewModel,
        {
          afterRender: function() {
            if (options.titleTemplate) {
              ko.renderTemplate(
                options.titleTemplate,
                viewModel,
                {
                  afterRender: function() {
                    afterRender();
                  }
                },
                $title.get(0),
                'replaceChildren'
              );
            } else {
              afterRender();
            }
          }
        },
        $content.get(0),
        'replaceChildren'
      );
    };

    if (visible()) {
      window.setTimeout(() => {
        showPopover(true);
      }, 0);
    }

    if (clickTrigger) {
      $element.click(e => {
        if (visible()) {
          hidePopover();
        } else {
          showPopover();
        }
        e.stopPropagation();
      });
    } else {
      $element.mouseenter(showPopover);
      $element.mouseleave(hidePopover);
    }
  }
};
