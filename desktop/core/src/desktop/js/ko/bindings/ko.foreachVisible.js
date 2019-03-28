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
 * This binding limits the rendered items based on what is visible within a scrollable container. It supports
 * multiple any amount of nested children with foreachVisible bindings
 *
 * The minHeight parameter is the initial expected rendered height of each entry, once rendered the real
 * height is used. It keeps a number of elements above and below the visible elements to make slow scrolling
 * smooth.
 *
 * The height of the container element has to be less than or equal to the inner height of the window.
 *
 * Example:
 *
 * <div class="container" style="overflow-y: scroll; height: 100px">
 *  <ul data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }">
 *    <li>...</li>
 *  </ul>
 * </div>
 *
 * For tables the binding has to be attached to the tbody element:
 *
 * <div class="container" style="overflow-y: scroll; height: 100px">
 *  <table>
 *    <thead>...</thead>
 *    <tbody data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }>
 *      <tr>...</tr>
 *    </tbody>
 *  </ul>
 * </div>
 *
 * Currently the binding only supports one element inside the bound element otherwise the height
 * calculations will be off. In other words this will make it go bonkers:
 *
 * <div class="container" style="overflow-y: scroll; height: 100px">
 *  <ul data-bind="foreachVisible: { data: items, minHeight: 20, container: '.container' }">
 *    <li>...</li>
 *    <li style="display: none;">...</li>
 *  </ul>
 * </div>
 *
 */
ko.bindingHandlers.foreachVisible = {
  init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    return ko.bindingHandlers.template.init(
      element,
      () => {
        return {
          foreach: [],
          templateEngine: ko.nativeTemplateEngine.instance
        };
      },
      allBindings,
      viewModel,
      bindingContext
    );
  },

  update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
    const options = valueAccessor();
    let $element = $(element);
    let isTable = false;

    if ($element.parent().is('table')) {
      $element = $element.parent();
      isTable = true;
    }

    const $container = $element.closest(options.container);

    const id = Math.random();

    // This is possibly a parent element that has the foreachVisible binding
    const $parentFVElement = bindingContext.$parentForeachVisible || null;
    const parentId = bindingContext.$parentForeachVisibleId || -1;
    // This is the element from the parent foreachVisible rendered element that contains
    // this one or container for root
    let $parentFVOwnerElement = $container;
    $element.data('parentForeachVisible', $parentFVElement);

    const depth = bindingContext.$depth || 0;

    // Locate the owning element if within another foreach visible binding
    if ($parentFVElement) {
      const myOffset = $element.offset().top;
      $parentFVElement.children().each((idx, child) => {
        const $child = $(child);
        if (myOffset > $child.offset().top) {
          $parentFVOwnerElement = $child;
        } else {
          return false;
        }
      });
    }

    if ($parentFVOwnerElement.data('disposalFunction')) {
      $parentFVOwnerElement.data('disposalFunction')();
      $parentFVOwnerElement.data('lastKnownHeights', null);
    }

    let entryMinHeight = options.minHeight;
    const allEntries = ko.utils.unwrapObservable(options.data);

    let visibleEntryCount = 0;
    let incrementLimit = 0; // The diff required to re-render, set to visibleCount below
    let elementIncrement = 0; // Elements to add on either side of the visible elements, set to 3x visibleCount
    let endIndex = 0;
    const updateVisibleEntryCount = function() {
      // TODO: Drop the window innerHeight limitation.
      // Sometimes after resizeWrapper() is called the reported innerHeight of the $container is the same as
      // the wrapper causing the binding to render all the items. This limits the visibleEntryCount to the
      // window height.
      const newEntryCount = Math.ceil(
        Math.min($(window).innerHeight(), $container.innerHeight()) / entryMinHeight
      );
      if (newEntryCount !== visibleEntryCount) {
        const diff = newEntryCount - visibleEntryCount;
        elementIncrement = options.elementIncrement || 25;
        incrementLimit = options.incrementLimit || 5;
        visibleEntryCount = newEntryCount;
        endIndex += diff;
        huePubSub.publish('foreach.visible.update', id);
      }
    };

    // TODO: Move intervals to webworker
    const updateCountInterval = setInterval(updateVisibleEntryCount, 300);
    updateVisibleEntryCount();

    // In case this element was rendered before use the last known indices
    let startIndex = Math.max($parentFVOwnerElement.data('startIndex') || 0, 0);
    endIndex = Math.min(
      $parentFVOwnerElement.data('endIndex') || visibleEntryCount + elementIncrement,
      allEntries.length - 1
    );

    const huePubSubs = [];

    const scrollToIndex = function(idx, offset, instant, callback) {
      const lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
      if (!lastKnownHeights || lastKnownHeights.length <= idx) {
        return;
      }
      let top = 0;
      for (let i = 0; i < idx; i++) {
        top += lastKnownHeights[i];
      }
      const bottom = top + lastKnownHeights[idx];
      window.setTimeout(() => {
        const newScrollTop = top + offset;
        if (instant) {
          if (newScrollTop >= $container.height() + $container.scrollTop()) {
            $container.scrollTop(bottom - $container.height());
          } else if (newScrollTop <= $container.scrollTop()) {
            $container.scrollTop(newScrollTop);
          }
        } else {
          $container.stop().animate({ scrollTop: newScrollTop }, '500', 'swing', () => {
            if (callback) {
              callback();
            }
          });
        }
      }, 0);
    };

    if (!options.skipScrollEvent) {
      huePubSubs.push(
        huePubSub.subscribe('assist.db.scrollTo', targetEntry => {
          let foundIndex = -1;
          $.each(allEntries, (idx, entry) => {
            if (targetEntry === entry) {
              foundIndex = idx;
              return false;
            }
          });
          if (foundIndex !== -1) {
            const offset = depth > 0 ? $parentFVOwnerElement.position().top : 0;
            scrollToIndex(foundIndex, offset, false, () => {
              huePubSub.publish('assist.db.scrollToComplete', targetEntry);
            });
          }
        })
      );
    }

    if (ko.isObservable(viewModel.foreachVisible)) {
      viewModel.foreachVisible({
        scrollToIndex: function(index) {
          const offset = depth > 0 ? $parentFVOwnerElement.position().top : 0;
          scrollToIndex(index, offset, true);
        }
      });
    }

    const childBindingContext = bindingContext.createChildContext(
      bindingContext.$rawData,
      null,
      context => {
        ko.utils.extend(context, {
          $parentForeachVisible: $element,
          $parentForeachVisibleId: id,
          $depth: depth + 1,
          $indexOffset: function() {
            return startIndex;
          }
        });
      }
    );

    let $wrapper = $element.parent();
    if (!$wrapper.hasClass('foreach-wrapper')) {
      $wrapper = $('<div>')
        .css({
          position: 'relative',
          width: '100%'
        })
        .addClass('foreach-wrapper')
        .insertBefore($element);
      if (options.usePreloadBackground) {
        $wrapper.addClass('assist-preloader-wrapper');
        $element.addClass('assist-preloader');
      }
      $element
        .css({
          position: 'absolute',
          top: 0,
          width: '100%'
        })
        .appendTo($wrapper);
    }

    // This is kept up to date with the currently rendered elements, it's used to keep track of any
    // height changes of the elements.
    let renderedElements = [];

    if (
      !$parentFVOwnerElement.data('lastKnownHeights') ||
      $parentFVOwnerElement.data('lastKnownHeights').length !== allEntries.length
    ) {
      const lastKnownHeights = [];
      $.each(allEntries, () => {
        lastKnownHeights.push(entryMinHeight);
      });
      $parentFVOwnerElement.data('lastKnownHeights', lastKnownHeights);
    }

    const resizeWrapper = function() {
      let totalHeight = 0;
      const lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
      if (!lastKnownHeights) {
        return;
      }
      $.each(lastKnownHeights, (idx, height) => {
        totalHeight += height;
      });
      $wrapper.height(totalHeight + 'px');
    };
    resizeWrapper();

    const updateLastKnownHeights = function() {
      if ($container.data('busyRendering')) {
        return;
      }
      const lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
      // Happens when closing first level and the third level is open, disposal tells the parents
      // to update their heights...
      if (!lastKnownHeights) {
        return;
      }
      let diff = false;
      let updateEntryCount = false;
      $.each(renderedElements, (idx, renderedElement) => {
        // TODO: Figure out why it goes over index at the end scroll position
        if (startIndex + idx < lastKnownHeights.length) {
          const renderedHeight = $(renderedElement).outerHeight(true);
          if (renderedHeight > 5 && lastKnownHeights[startIndex + idx] !== renderedHeight) {
            if (renderedHeight < entryMinHeight) {
              entryMinHeight = renderedHeight;
              updateEntryCount = true;
            }
            lastKnownHeights[startIndex + idx] = renderedHeight;
            diff = true;
          }
        }
      });

      if (updateEntryCount) {
        updateVisibleEntryCount();
      }
      // Only resize if a difference in height was noticed.
      if (diff) {
        $parentFVOwnerElement.data('lastKnownHeights', lastKnownHeights);
        resizeWrapper();
      }
    };

    let updateHeightsInterval = window.setInterval(updateLastKnownHeights, 600);

    huePubSubs.push(
      huePubSub.subscribe('foreach.visible.update.heights', targetId => {
        if (targetId === id) {
          clearInterval(updateHeightsInterval);
          updateLastKnownHeights();
          huePubSub.publish('foreach.visible.update.heights', parentId);
          updateHeightsInterval = window.setInterval(updateLastKnownHeights, 600);
        }
      })
    );

    updateLastKnownHeights();

    const positionList = function() {
      const lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
      if (!lastKnownHeights) {
        return;
      }
      let top = 0;
      for (let i = 0; i < startIndex; i++) {
        top += lastKnownHeights[i];
      }
      $element.css('top', top + 'px');
    };

    const afterRender = function() {
      renderedElements = isTable ? $element.children('tbody').children() : $element.children();
      $container.data('busyRendering', false);
      if (typeof options.fetchMore !== 'undefined' && endIndex === allEntries.length - 1) {
        options.fetchMore();
      }
      huePubSub.publish('foreach.visible.update.heights', id);
    };

    const render = function() {
      if ((endIndex === 0 && allEntries.length > 1) || endIndex < 0) {
        ko.bindingHandlers.template.update(
          element,
          () => {
            return {
              foreach: [],
              templateEngine: ko.nativeTemplateEngine.instance,
              afterRender: function() {
                // This is called once for each added element (not when elements are removed)
                clearTimeout(throttle);
                throttle = setTimeout(afterRender, 0);
              }
            };
          },
          allBindings,
          viewModel,
          childBindingContext
        );
        return;
      }
      $container.data('busyRendering', true);
      // Save the start and end index for when the list is removed and is shown again.
      $parentFVOwnerElement.data('startIndex', startIndex);
      $parentFVOwnerElement.data('endIndex', endIndex);
      positionList();

      // This is to ensure that our afterRender is called (the afterRender of KO below isn't called
      // when only elements are removed)
      let throttle = setTimeout(afterRender, 0);

      ko.bindingHandlers.template.update(
        element,
        () => {
          return {
            foreach: allEntries.slice(startIndex, endIndex + 1),
            templateEngine: ko.nativeTemplateEngine.instance,
            afterRender: function() {
              // This is called once for each added element (not when elements are removed)
              clearTimeout(throttle);
              throttle = setTimeout(afterRender, 0);
            }
          };
        },
        allBindings,
        viewModel,
        childBindingContext
      );
    };

    const setStartAndEndFromScrollTop = function() {
      const lastKnownHeights = $parentFVOwnerElement.data('lastKnownHeights');
      if (!lastKnownHeights) {
        return;
      }

      let parentSpace = 0;

      let $lastParent = $parentFVElement;
      let $lastRef = $element;

      while ($lastParent) {
        // Include the header, parent() is .foreach-wrapper, parent().parent() is the container (ul or div)
        const lastRefOffset = $lastRef
          .parent()
          .parent()
          .offset().top;
        let lastAddedSpace = 0;
        $lastParent.children().each((idx, child) => {
          const $child = $(child);
          if (lastRefOffset > $child.offset().top) {
            lastAddedSpace = $child.outerHeight(true);
            parentSpace += lastAddedSpace;
          } else {
            // Remove the height of the child which is the parent of this
            parentSpace -= lastAddedSpace;
            return false;
          }
        });
        parentSpace += $lastParent.position().top;
        $lastRef = $lastParent;
        $lastParent = $lastParent.data('parentForeachVisible');
      }
      let position = Math.min($container.scrollTop() - parentSpace, $wrapper.height());

      for (let i = 0; i < lastKnownHeights.length; i++) {
        position -= lastKnownHeights[i];
        if (position <= 0) {
          startIndex = Math.max(i - elementIncrement, 0);
          endIndex = Math.min(allEntries.length - 1, i + elementIncrement + visibleEntryCount);
          break;
        }
      }
    };

    let renderThrottle = -1;
    let preloadGhostThrottle = -1;
    let lastScrollTop = -1;
    const onScroll = function() {
      if (
        startIndex > incrementLimit &&
        Math.abs(lastScrollTop - $container.scrollTop()) < incrementLimit * options.minHeight
      ) {
        return;
      }
      lastScrollTop = $container.scrollTop();

      setStartAndEndFromScrollTop();

      // adds a preload ghost image just on scroll and removes it 200ms after the scroll stops
      if (options.usePreloadBackground) {
        $wrapper.addClass('assist-preloader-ghost');
        clearTimeout(preloadGhostThrottle);
        preloadGhostThrottle = setTimeout(() => {
          $wrapper.removeClass('assist-preloader-ghost');
        }, 200);
      }

      clearTimeout(renderThrottle);
      const startDiff = Math.abs($parentFVOwnerElement.data('startIndex') - startIndex);
      const endDiff = Math.abs($parentFVOwnerElement.data('endIndex') - endIndex);
      if (
        startDiff > incrementLimit ||
        endDiff > incrementLimit ||
        (startDiff !== 0 && startIndex === 0) ||
        (endDiff !== 0 && endIndex === allEntries.length - 1)
      ) {
        renderThrottle = setTimeout(render, 0);
      }
    };

    huePubSubs.push(
      huePubSub.subscribe('foreach.visible.update', callerId => {
        if (callerId === id && endIndex > 0) {
          setStartAndEndFromScrollTop();
          clearTimeout(renderThrottle);
          renderThrottle = setTimeout(render, 0);
        }
      })
    );

    $container.bind('scroll', onScroll);

    $parentFVOwnerElement.data('disposalFunction', () => {
      setTimeout(() => {
        huePubSub.publish('foreach.visible.update.heights', parentId);
      }, 0);
      huePubSubs.forEach(pubSub => {
        pubSub.remove();
      });
      $container.unbind('scroll', onScroll);
      clearInterval(updateCountInterval);
      clearInterval(updateHeightsInterval);
      $parentFVOwnerElement.data('disposalFunction', null);
    });

    if (typeof options.pubSubDispose !== 'undefined') {
      huePubSubs.push(
        huePubSub.subscribe(options.pubSubDispose, $parentFVOwnerElement.data('disposalFunction'))
      );
    }

    ko.utils.domNodeDisposal.addDisposeCallback(
      $wrapper[0],
      $parentFVOwnerElement.data('disposalFunction')
    );

    setStartAndEndFromScrollTop();
    render();
  }
};

ko.expressionRewriting.bindingRewriteValidators['foreachVisible'] = false;
ko.virtualElements.allowedBindings['foreachVisible'] = true;
