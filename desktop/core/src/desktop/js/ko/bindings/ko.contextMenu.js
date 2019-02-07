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

/**
 * This binding can be used to show a custom context menu on right-click,
 * It assumes that the context menu is nested within the bound element and
 * the selector for the menu has to be supplied as a parameter.
 *
 * Example:
 *
 * <div data-bind="contextMenu: {
 *   menuSelector: '.hue-context-menu',
 *   beforeOpen: function () { ... }
 * }">
 *   <ul class="hue-context-menu">...</ul>
 * </div>
 *
 */
ko.bindingHandlers.contextMenu = {
  initContextMenu: function($menu, $scrollContainer) {
    let active = false;

    let currentLeft = 0;
    let currentTop = 0;
    let openScrollTop = 0;
    let openScrollLeft = 0;

    const adjustForScroll = function() {
      $menu.css('top', currentTop - $scrollContainer.scrollTop() + openScrollTop);
      $menu.css('left', currentLeft - $scrollContainer.scrollLeft() + openScrollLeft);
    };

    return {
      show: function(event) {
        $menu.css('top', 0);
        $menu.css('left', 0);
        $menu.css('opacity', 0);
        $menu.show();
        openScrollTop = $scrollContainer.scrollTop();
        openScrollLeft = $scrollContainer.scrollLeft();
        const menuWidth = $menu.outerWidth(true);
        if (event.clientX + menuWidth > $(window).width()) {
          currentLeft = $(window).width() - menuWidth;
        } else {
          currentLeft = event.clientX;
        }
        $menu.css('left', currentLeft);

        const menuHeight = $menu.outerHeight(true);
        if (event.clientY + menuHeight > $(window).height()) {
          currentTop = $(window).height() - menuHeight;
        } else {
          currentTop = event.clientY;
        }
        $menu.css('top', currentTop);
        $menu.css('opacity', 1);
        active = true;
        $scrollContainer.on('scroll', adjustForScroll);
      },
      hide: function() {
        if (active) {
          $scrollContainer.off('scroll', adjustForScroll);
          $menu.css('opacity', 0);
          window.setTimeout(() => {
            $menu.hide();
          }, 300);
          active = false;
        }
      }
    };
  },
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const $element = $(element);
    const options = valueAccessor();
    const $menu = $element.find(options.menuSelector);

    bindingContext.$altDown = ko.observable(false);

    window.addEventListener('keydown', e => {
      bindingContext.$altDown(e.altKey);
    });

    window.addEventListener('keyup', () => {
      bindingContext.$altDown(false);
    });

    const $scrollContainer =
      $(options.scrollContainer).length > 0 ? $(options.scrollContainer) : $(window);

    const menu = ko.bindingHandlers.contextMenu.initContextMenu($menu, $scrollContainer);

    element.addEventListener('contextmenu', event => {
      if (document.selection && document.selection.empty) {
        document.selection.empty();
      } else if (window.getSelection) {
        const sel = window.getSelection();
        sel.removeAllRanges();
      }
      if (typeof options.beforeOpen === 'function') {
        options.beforeOpen.bind(viewModel)();
      }
      menu.show(event);
      huePubSub.publish('contextmenu-active', element);
      event.preventDefault();
      event.stopPropagation();
    });

    huePubSub.subscribe('contextmenu-active', origin => {
      if (origin !== element) {
        menu.hide();
      }
    });
    document.addEventListener('contextmenu', () => {
      menu.hide();
    });
    $menu.click(e => {
      menu.hide();
      e.stopPropagation();
    });
    $(document).click(event => {
      if ($element.find($(event.target)).length === 0) {
        menu.hide();
      }
    });
  }
};
