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

ko.bindingHandlers.splitFlexDraggable = {
  init: function(element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    let sidePanelWidth =
      $.totalStorage(options.appName + '_' + options.orientation + '_panel_width') != null
        ? $.totalStorage(options.appName + '_' + options.orientation + '_panel_width')
        : 290;

    const $resizer = $(element);
    const $sidePanel = $(options.sidePanelSelector);
    const $container = $(options.containerSelector);

    const isLeft = options.orientation === 'left';

    const onPosition = options.onPosition || function() {};

    $sidePanel.css('flex-basis', sidePanelWidth + 'px');
    $resizer.draggable({
      axis: 'x',
      containment: $container,
      start: function() {
        sidePanelWidth = $sidePanel.width();
      },
      drag: function(event, ui) {
        if (isLeft) {
          $sidePanel.css('flex-basis', Math.max(sidePanelWidth + ui.position.left, 200) + 'px');
        } else {
          $sidePanel.css('flex-basis', Math.max(sidePanelWidth - ui.position.left, 200) + 'px');
        }
        onPosition();
        ui.position.left = 0;
      },
      stop: function() {
        sidePanelWidth = $sidePanel.width();
        $.totalStorage(
          options.appName + '_' + options.orientation + '_panel_width',
          sidePanelWidth
        );
        window.setTimeout(positionPanels, 100);
        huePubSub.publish('split.panel.resized');
      }
    });

    const positionPanels = function() {
      if (options.sidePanelVisible()) {
        $sidePanel.css('flex-basis', Math.max(sidePanelWidth, 200) + 'px');
        onPosition();
      }
    };

    options.sidePanelVisible.subscribe(positionPanels);

    let positionTimeout = -1;
    $(window).resize(() => {
      window.clearTimeout(positionTimeout);
      positionTimeout = window.setTimeout(() => {
        positionPanels();
      }, 1);
    });

    function initialPositioning() {
      if (!$container.is(':visible') && !$sidePanel.is(':visible')) {
        window.setTimeout(initialPositioning, 50);
      } else {
        positionPanels();
        // Even though the container is visible some slow browsers might not
        // have rendered the panels
        window.setTimeout(positionPanels, 50);
      }
    }

    initialPositioning();
  }
};
