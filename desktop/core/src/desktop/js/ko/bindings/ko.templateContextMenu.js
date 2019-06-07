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

ko.bindingHandlers.templateContextMenu = {
  init: function(element, valueAccessor, allBindings, viewModel) {
    const options = valueAccessor();

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
      let $menu = $('#hueContextMenu_' + options.template);
      if ($menu.length === 0) {
        $menu = $(
          '<ul id="hueContextMenu_' +
            options.template +
            '" class="hue-context-menu" data-bind="template: { name: \'' +
            options.template +
            '\', data: viewModel, afterRender: afterRender }"></ul>'
        ).appendTo(window.HUE_CONTAINER);
      } else {
        ko.cleanNode($menu[0]);
      }
      $menu.data('active', true);

      $menu.css('top', 0);
      $menu.css('left', 0);
      $menu.css('opacity', 0);
      $menu.show();

      const hideMenu = function() {
        if (!$menu.data('active')) {
          $menu.hide();
          ko.cleanNode($menu[0]);
        }
      };

      ko.applyBindings(
        {
          afterRender: function() {
            const menuWidth = $menu.outerWidth(true);
            const menuHeight = $menu.outerHeight(true);
            $menu.css(
              'left',
              event.clientX + menuWidth > $(window).width()
                ? $(window).width() - menuWidth
                : event.clientX
            );
            $menu.css(
              'top',
              event.clientY + menuHeight > $(window).height()
                ? $(window).height() - menuHeight
                : event.clientY
            );
            $menu.css('opacity', 1);
            if (options.scrollContainer) {
              $(options.scrollContainer).one('scroll', hideMenu);
            }
            window.setTimeout(() => {
              $menu.data('active', false);
              $(document).one('click', hideMenu);
            }, 100);
          },
          viewModel: options.viewModel || viewModel
        },
        $menu[0]
      );

      ko.contextFor($menu[0]).$contextSourceElement = element;
      event.preventDefault();
      event.stopPropagation();
    });
  }
};
