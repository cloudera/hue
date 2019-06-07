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

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

ko.bindingHandlers.assistVerticalResizer = {
  init: function(element, valueAccessor) {
    const $container = $(element);
    const options = ko.unwrap(valueAccessor());
    const panelDefinitions = options.panels;

    const checkForElements = function() {
      const $allPanels = $container.children('.assist-inner-panel');
      const $allExtras = $container.children('.assist-fixed-height');
      if (
        panelDefinitions().length === $allPanels.length &&
        ($allExtras.length > 0 || options.noFixedHeights)
      ) {
        ko.bindingHandlers.assistVerticalResizer.updateWhenRendered(element, valueAccessor);
      } else {
        timeout = window.setTimeout(checkForElements, 10);
      }
    };

    checkForElements();
    let timeout = -1;
    panelDefinitions.subscribe(() => {
      window.clearTimeout(timeout);
      timeout = window.setTimeout(checkForElements, 10);
    });
  },

  updateWhenRendered: function(element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    const panelDefinitions = options.panels;

    const $container = $(element);
    let $allPanels = $container.children('.assist-inner-panel');
    const $allResizers = $container.children('.assist-resizer');
    const $allExtras = $container.children('.assist-fixed-height');

    let allExtrasHeight = 0;
    $allExtras.each((idx, extra) => {
      allExtrasHeight += $(extra).outerHeight(true);
    });

    window.clearInterval($container.data('height_interval'));

    if (panelDefinitions().length === 0) {
      $allExtras.show();
      return;
    }
    if (panelDefinitions().length === 1) {
      const adjustHeightSingle = function() {
        $allPanels.height($container.innerHeight() - allExtrasHeight);
      };

      const heightAdjustInterval = window.setInterval(adjustHeightSingle, 800);
      adjustHeightSingle();
      $container.data('height_interval', heightAdjustInterval);

      $(window).resize(adjustHeightSingle);
      huePubSub.subscribe('assist.forceRender', () => {
        window.setTimeout(adjustHeightSingle, 200);
      });
      $allExtras.show();
      $allPanels.show();
      return;
    }

    const panelRatios = apiHelper.getFromTotalStorage('assist', 'innerPanelRatios', {});

    let totalRatios = 0;
    $.each($allPanels, (idx, panel) => {
      const panelDef = panelDefinitions()[idx];
      if (!panelRatios[panelDef.type]) {
        panelRatios[panelDef.type] = 1 / panelDefinitions().length;
      }
      totalRatios += panelRatios[panelDef.type];
      $(panel).data('minHeight', panelDef.minHeight);
    });

    // Normalize the ratios in case new panels were added or removed.
    if (totalRatios !== 1) {
      const diff = 1 / totalRatios;
      $.each(panelDefinitions(), (idx, panel) => {
        panelRatios[panel.type] = panelRatios[panel.type] * diff;
      });
    }

    let totalHeight = -1;
    let containerTop = $container.offset().top;

    // Resizes all containers according to the set ratios
    const resizeByRatio = function() {
      if (totalHeight === $container.innerHeight()) {
        return;
      }
      $allPanels = $container.children('.assist-inner-panel');
      totalHeight = $container.innerHeight();
      containerTop = $container.offset().top;

      $.each($allPanels, (idx, panel) => {
        const panelDef = panelDefinitions()[idx];
        if (!panelRatios[panelDef.type] || $allPanels.length === 1) {
          panelRatios[panelDef.type] = 1 / panelDefinitions().length;
        }
        totalRatios += panelRatios[panelDef.type];
        $(panel).data('minHeight', panelDef.minHeight);
      });

      const availableForPanels = totalHeight - allExtrasHeight;
      let leftoverSpace = 0;
      $allPanels.each((idx, panel) => {
        const $panel = $(panel);
        const desiredHeight = availableForPanels * panelRatios[panelDefinitions()[idx].type];
        const newHeight = Math.max($panel.data('minHeight'), desiredHeight);
        $panel.height(newHeight);
        leftoverSpace += newHeight - desiredHeight;
      });
      // The minheight is greater than the ratio so we shrink where possible
      if (leftoverSpace > 0) {
        $allPanels.each((idx, panel) => {
          if (leftoverSpace === 0) {
            return false;
          }
          const $panel = $(panel);
          const currentHeight = $panel.height();
          const possibleContribution = Math.min(
            currentHeight - $panel.data('minHeight'),
            leftoverSpace
          );
          if (possibleContribution > 0) {
            $panel.height(currentHeight - possibleContribution);
            leftoverSpace -= possibleContribution;
          }
        });
      }
    };

    resizeByRatio();
    $(window).resize(resizeByRatio);

    window.setTimeout(resizeByRatio, 1000);
    huePubSub.subscribe('assist.forceRender', () => {
      window.setTimeout(resizeByRatio, 200);
    });

    $allExtras.show();
    $allPanels.show();

    const fitPanelHeights = function($panelsToResize, desiredTotalHeight) {
      let currentHeightOfPanels = 0;

      let noMoreSpace = true;
      $panelsToResize.each((idx, panel) => {
        const $panel = $(panel);
        const panelHeight = $panel.outerHeight(true);
        noMoreSpace = noMoreSpace && panelHeight <= $panel.data('minHeight');
        currentHeightOfPanels += panelHeight;
      });

      let distanceToGo = desiredTotalHeight - currentHeightOfPanels;
      if (noMoreSpace && distanceToGo < 0) {
        return;
      }

      // Add all to the first panel if expanding (distanceToGo is positive
      if (distanceToGo >= 0) {
        $panelsToResize.first().height($panelsToResize.first().height() + distanceToGo + 'px');
        return;
      }

      // Remove as much as possible on each panel if shrinking (distanceToGo is negative)
      $panelsToResize.each((idx, panel) => {
        const $panel = $(panel);
        const initialHeight = $panel.height();
        const newHeight = Math.max($panel.data('minHeight'), initialHeight + distanceToGo);
        if (initialHeight === newHeight) {
          return true;
        }
        $panel.height(newHeight);
        distanceToGo += initialHeight - newHeight;
        if (distanceToGo >= 0) {
          return false;
        }
      });
    };

    $allResizers.each((idx, resizer) => {
      const $resizer = $(resizer);
      let extrasBeforeHeight = 0;
      $resizer.prevAll('.assist-fixed-height').each((idx, extra) => {
        extrasBeforeHeight += $(extra).outerHeight(true);
      });
      const $panelsBefore = $resizer.prevAll('.assist-inner-panel');
      let limitBefore = extrasBeforeHeight;
      $panelsBefore.each((idx, panel) => {
        limitBefore += $(panel).data('minHeight');
      });

      const extrasAfterHeight = allExtrasHeight - extrasBeforeHeight;
      const $panelsAfter = $resizer.nextAll('.assist-inner-panel');
      let requiredSpaceAfter = extrasAfterHeight;
      $panelsAfter.each((idx, panel) => {
        requiredSpaceAfter += $(panel).data('minHeight');
      });

      $resizer.draggable({
        axis: 'y',
        drag: function(event, ui) {
          const limitAfter = totalHeight - requiredSpaceAfter;
          const position = ui.offset.top - containerTop;
          if (position > limitBefore && position < limitAfter) {
            fitPanelHeights($panelsBefore, position - extrasBeforeHeight);
            fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - position);
          } else if (position > limitAfter) {
            fitPanelHeights($panelsBefore, limitAfter - extrasBeforeHeight);
            fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - limitAfter);
          } else if (position < limitBefore) {
            fitPanelHeights($panelsBefore, limitBefore - extrasBeforeHeight);
            fitPanelHeights($panelsAfter, totalHeight - extrasAfterHeight - limitBefore);
          }

          ui.offset.top = 0;
          ui.position.top = 0;
        },
        stop: function(event, ui) {
          ui.offset.top = 0;
          ui.position.top = 0;
          let totalHeightForPanels = 0;
          $allPanels.each((idx, panel) => {
            totalHeightForPanels += $(panel).outerHeight(true);
          });
          $allPanels.each((idx, panel) => {
            panelRatios[panelDefinitions()[idx].type] =
              $(panel).outerHeight(true) / totalHeightForPanels;
          });
          apiHelper.setInTotalStorage('assist', 'innerPanelRatios', panelRatios);
        }
      });
    });
  }
};
