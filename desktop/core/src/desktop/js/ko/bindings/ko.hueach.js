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

ko.bindingHandlers.hueach = {
  init: function(element, valueAccessor, allBindings) {
    const valueAccessorBuilder = function() {
      return {
        data: ko.observableArray([])
      };
    };
    ko.bindingHandlers.foreach.init(element, valueAccessorBuilder, allBindings);
  },
  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const $element = $(element);
    let $parent = $element.parent();
    const data =
      typeof valueAccessor().data === 'function' ? valueAccessor().data() : valueAccessor().data;
    const considerStretching = valueAccessor().considerStretching || false;
    const itemHeight = valueAccessor().itemHeight || 22;
    const scrollable = valueAccessor().scrollable || 'body';
    const scrollUp = valueAccessor().scrollUp || false;
    const scrollableOffset = valueAccessor().scrollableOffset || 0;
    const disableHueEachRowCount = valueAccessor().disableHueEachRowCount || 0;
    const forceRenderSub = valueAccessor().forceRenderSub || null;
    let renderTimeout = -1;
    let dataHasChanged = true;

    let wrappable = $(element);
    if (data.length > disableHueEachRowCount) {
      if ($parent.is('table')) {
        wrappable = $parent;
        $parent = wrappable.parent();
      }

      if (!wrappable.parent().hasClass('hueach')) {
        wrappable.wrap('<div class="hueach"></div>');
        $parent = wrappable.parent();
        wrappable.css({
          position: 'absolute',
          width: '100%'
        });
      }

      $parent.height(data.length * itemHeight);
      if (wrappable.is('table')) {
        $parent.height($parent.height() + (data.length > 0 ? itemHeight : 0));
      }
    }

    try {
      if (
        ko.utils.domData.get(element, 'originalData') &&
        JSON.stringify(ko.utils.domData.get(element, 'originalData')) === JSON.stringify(data)
      ) {
        dataHasChanged = false;
      }
    } catch (e) {}

    if (dataHasChanged) {
      ko.utils.domData.set(element, 'originalData', data);
    }

    let startItem = 0,
      endItem = 0;
    const valueAccessorBuilder = function() {
      return {
        data: ko.utils.domData.get(element, 'originalData')
          ? ko.observableArray(
              ko.utils.domData.get(element, 'originalData').slice(startItem, endItem)
            )
          : []
      };
    };

    const render = function() {
      if ($parent.parents('.hueach').length === 0) {
        let heightCorrection = 0,
          fluidCorrection = 0;
        const scrollTop = $parent.parents(scrollable).scrollTop();
        if (wrappable.is('table')) {
          if (scrollTop < scrollableOffset + itemHeight) {
            wrappable.find('thead').css('opacity', '1');
          } else {
            wrappable.find('thead').css('opacity', '0');
          }
        } else {
          wrappable.children(':visible').each((cnt, child) => {
            if ($(child).height() >= itemHeight) {
              heightCorrection += $(child).height();
            }
          });
          if (heightCorrection > 0) {
            ko.utils.domData.set(element, 'heightCorrection', heightCorrection);
          }
          if (heightCorrection === 0 && ko.utils.domData.get(element, 'heightCorrection')) {
            fluidCorrection = ko.utils.domData.get(element, 'heightCorrection') - 20;
          }
        }
        startItem = Math.max(
          0,
          Math.floor(
            Math.max(1, scrollTop - heightCorrection - fluidCorrection - scrollableOffset) /
              itemHeight
          ) - 10
        );
        if (wrappable.is('table') && startItem % 2 === 1) {
          startItem--;
        }
        endItem = Math.min(
          startItem + Math.ceil($parent.parents(scrollable).height() / itemHeight) + 20,
          data.length
        );
        wrappable.css('top', startItem * itemHeight + fluidCorrection + 'px');
      } else {
        startItem = 0;
        endItem = data.length;
      }
      bindingContext.$indexOffset = function() {
        return startItem;
      };
      ko.bindingHandlers.foreach.update(
        element,
        valueAccessorBuilder,
        allBindings,
        viewModel,
        bindingContext
      );
    };

    $parent.parents(scrollable).off('scroll');
    huePubSub.publish('scrollable.scroll.off', scrollable);

    $parent.parents(scrollable).on('scroll', render);
    if (scrollUp) {
      $parent.parents(scrollable).jHueScrollUp();
    }

    if ($parent.parents('.hueach').length > 0) {
      window.setTimeout(render, 100);
    }

    if (considerStretching) {
      huePubSub.subscribe('assist.stretchDown', () => {
        window.clearTimeout(renderTimeout);
        renderTimeout = window.setTimeout(() => {
          ko.utils.domData.set(element, 'hasStretched', true);
          render();
        }, 300);
      });
    }

    if (forceRenderSub) {
      huePubSub.subscribe(forceRenderSub, () => {
        window.setTimeout(render, 300);
      });
    }

    window.clearTimeout(renderTimeout);
    renderTimeout = window.setTimeout(() => {
      ko.utils.domData.set(element, 'hasStretched', true);
      render();
    }, 300);
  }
};
