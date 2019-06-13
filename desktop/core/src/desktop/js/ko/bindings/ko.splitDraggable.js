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

ko.bindingHandlers.splitDraggable = {
  init: function(element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    let leftPanelWidth =
      $.totalStorage(options.appName + '_left_panel_width') != null
        ? Math.max($.totalStorage(options.appName + '_left_panel_width'), 250)
        : 250;
    let rightPanelWidth =
      $.totalStorage(options.appName + '_right_panel_width') != null
        ? Math.max($.totalStorage(options.appName + '_right_panel_width'), 250)
        : 290;

    const containerSelector = options.containerSelector || '.panel-container';
    const contentPanelSelector = options.contentPanelSelector || '.content-panel';

    const onPosition = options.onPosition || function() {};

    const hasLeftPanel = !!options.leftPanelVisible;
    const hasRightPanel = !!options.rightPanelVisible;

    const isRightPanel = !!options.isRightPanel;

    const $resizer = $(element);
    const $leftPanel = $('.left-panel');
    const $rightPanel = $('.right-panel');
    const $contentPanel = $(contentPanelSelector);
    const $container = $(containerSelector);

    const positionPanels = function() {
      if (isRightPanel) {
        const oppositeWidth =
          hasLeftPanel && ko.unwrap(options.leftPanelVisible)
            ? $leftPanel.width() + $resizer.width()
            : 0;
        const totalWidth = $container.width() - oppositeWidth;
        if (ko.unwrap(options.rightPanelVisible) && ko.unwrap(options.rightPanelAvailable)) {
          $resizer.show();
          rightPanelWidth = Math.min(rightPanelWidth, $container.width() - 100);
          const contentPanelWidth = totalWidth - rightPanelWidth - $resizer.width();
          $rightPanel.css('width', rightPanelWidth + 'px');
          $contentPanel.css('width', contentPanelWidth + 'px');
          $resizer.css('left', $container.width() - rightPanelWidth - $resizer.width() + 'px');
          $contentPanel.css('right', rightPanelWidth + $resizer.width() + 'px');
        } else {
          if (oppositeWidth === 0) {
            $contentPanel.css('width', '100%');
          } else {
            $contentPanel.css('width', totalWidth);
          }
          $contentPanel.css('right', '0');
          $resizer.hide();
        }
      } else {
        const oppositeWidth =
          hasRightPanel &&
          ko.unwrap(options.rightPanelVisible) &&
          ko.unwrap(options.rightPanelAvailable)
            ? $rightPanel.width() + $resizer.width()
            : 0;
        const totalWidth = $container.width() - oppositeWidth;
        if (ko.unwrap(options.leftPanelVisible)) {
          $resizer.show();
          leftPanelWidth = Math.min(leftPanelWidth, totalWidth - 100);
          const contentPanelWidth = totalWidth - leftPanelWidth - $resizer.width();
          $leftPanel.css('width', leftPanelWidth + 'px');
          $contentPanel.css('width', contentPanelWidth + 'px');
          $resizer.css('left', leftPanelWidth + 'px');
          $contentPanel.css('left', leftPanelWidth + $resizer.width() + 'px');
        } else {
          if (oppositeWidth === 0) {
            $contentPanel.css('width', '100%');
          } else {
            $contentPanel.css('width', totalWidth);
          }
          $contentPanel.css('left', '0');
          $resizer.hide();
        }
      }
      onPosition();
    };

    if (ko.isObservable(options.leftPanelVisible)) {
      options.leftPanelVisible.subscribe(positionPanels);
    }

    if (ko.isObservable(options.rightPanelVisible)) {
      options.rightPanelVisible.subscribe(positionPanels);
    }

    if (ko.isObservable(options.rightPanelAvailable)) {
      options.rightPanelAvailable.subscribe(positionPanels);
    }

    let dragTimeout = -1;
    $resizer.draggable({
      axis: 'x',
      containment: $container,
      drag: function(event, ui) {
        if (isRightPanel) {
          ui.position.left = Math.min($container.width() - 200, ui.position.left);
        } else {
          ui.position.left = Math.min(
            $container.width() - $container.position().left - 200,
            Math.max(250, ui.position.left)
          );
        }

        window.clearTimeout(dragTimeout);
        dragTimeout = window.setTimeout(() => {
          if (isRightPanel) {
            const oppositeWidth =
              hasLeftPanel && ko.unwrap(options.leftPanelVisible)
                ? $leftPanel.width() + $resizer.width()
                : 0;
            const totalWidth = $container.width() - oppositeWidth;
            rightPanelWidth = $container.width() - ui.position.left;
            $rightPanel.css('width', rightPanelWidth + 'px');
            $contentPanel.css('width', totalWidth - rightPanelWidth + 'px');
            // $contentPanel.css("right", rightPanelWidth + $resizer.width());
          } else {
            const oppositeWidth =
              hasRightPanel && ko.unwrap(options.rightPanelVisible)
                ? $rightPanel.width() + $resizer.width()
                : 0;
            const totalWidth = $container.width() - oppositeWidth;
            leftPanelWidth = ui.position.left;
            $leftPanel.css('width', leftPanelWidth + 'px');
            $contentPanel.css('width', totalWidth - leftPanelWidth - $resizer.width() + 'px');
            $contentPanel.css('left', leftPanelWidth + $resizer.width());
          }
          onPosition();
        }, 10);
      },
      stop: function() {
        if (isRightPanel) {
          $.totalStorage(options.appName + '_right_panel_width', rightPanelWidth);
        } else {
          $.totalStorage(options.appName + '_left_panel_width', leftPanelWidth);
        }
        window.setTimeout(positionPanels, 100);
        huePubSub.publish('split.panel.resized');
      }
    });

    let positionTimeout = -1;
    $(window).resize(() => {
      window.clearTimeout(positionTimeout);
      positionTimeout = window.setTimeout(() => {
        positionPanels();
      }, 1);
    });

    function initialPositioning() {
      if (!$container.is(':visible')) {
        window.setTimeout(initialPositioning, 50);
      } else {
        positionPanels();
        // Even though the container is visible some slow browsers might not
        // have rendered the panels
        window.setTimeout(positionPanels, 100);
      }
    }

    initialPositioning();
  }
};
