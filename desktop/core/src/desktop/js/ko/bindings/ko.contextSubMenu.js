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

ko.bindingHandlers.contextSubMenu = {
  init: function(element, valueAccessor) {
    const menuSelector = valueAccessor();
    const $element = $(element);

    const $menu = $element.find(menuSelector);
    const $parentMenu = $element.parent('.hue-context-menu');
    let open = false;

    const closeSubMenu = function() {
      open = false;
      $menu.hide();
      $element.removeClass('active');
    };

    let hideTimeout = -1;
    $element.add($menu).on('mouseenter', () => {
      $element.addClass('active');
      if (!open) {
        huePubSub.publish('hue.sub.menu.close');
      }
      open = true;
      window.clearTimeout(hideTimeout);
      const menuHeight = $menu.outerHeight();
      $menu.css(
        'top',
        $element.position().top + $parentMenu.position().top + menuHeight > $(window).height()
          ? $(window).height() - menuHeight - 8
          : $element.position().top + $parentMenu.position().top
      );
      $menu.css('left', $element.offset().left + $element.outerWidth(true));
      $menu.css('opacity', 0);
      $menu.show();
      $menu.css('opacity', 1);
      huePubSub.subscribeOnce('hue.sub.menu.close', closeSubMenu);
    });

    $element.add($menu).on('mouseleave', () => {
      window.clearTimeout(hideTimeout);
      hideTimeout = window.setTimeout(closeSubMenu, 300);
    });
  }
};
