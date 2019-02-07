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

import hueUtils from 'utils/hueUtils';

ko.bindingHandlers.logScroller = {
  init: function(element, valueAccessor, allBindings) {
    const $element = $(element);

    $element.on('scroll', () => {
      $element.data('lastScrollTop', $element.scrollTop());
    });

    $element.on('wheel', () => {
      $element.data('hasUserScrolled', true);
    });

    function autoLogScroll() {
      const elementHeight = $element.innerHeight();
      const lastHeight = $element.data('lastHeight') || elementHeight;
      const lastScrollTop = $element.data('lastScrollTop') || 0;
      const hasUserScrolled = $element.data('hasUserScrolled') || false;
      const lastScrollHeight = $element.data('lastScrollHeight') || elementHeight;

      const stickToBottom =
        !hasUserScrolled ||
        elementHeight !== lastHeight ||
        lastScrollTop + elementHeight === lastScrollHeight;

      if (stickToBottom) {
        $element.scrollTop(element.scrollHeight - $element.height());
        $element.data('lastScrollTop', $element.scrollTop());
      }

      $element.data('lastScrollHeight', element.scrollHeight);
      $element.data('lastHeight', elementHeight);
    }

    const logValue = valueAccessor();
    logValue.subscribe(() => {
      window.setTimeout(autoLogScroll, 200);
    });

    if (typeof allBindings().logScrollerVisibilityEvent !== 'undefined') {
      allBindings().logScrollerVisibilityEvent.subscribe(() => {
        window.setTimeout(autoLogScroll, 0);
      });
    } else {
      hueUtils.waitForRendered(
        element,
        el => {
          return el.is(':visible');
        },
        autoLogScroll,
        300
      );
      ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
        window.clearTimeout($element.data('waitForRenderTimeout'));
      });
    }
  }
};
