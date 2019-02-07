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
import hueUtils from 'utils/hueUtils';

ko.bindingHandlers.dockable = {
  init: function(element, valueAccessor) {
    const options = valueAccessor() || {};
    const scrollable = options.scrollable ? options.scrollable : window;
    const triggerAdjust = options.triggerAdjust || 0;
    const zIndex = options.zIndex || 1000;
    $(element).addClass('dockable');

    let initialTopPosition = -1;
    let initialSize = {
      w: $(element).width() - hueUtils.scrollbarWidth(),
      h: $(element).outerHeight() + (options.jumpCorrection || 0)
    };

    const ghost = $('<div>')
      .css({ display: 'none', height: initialSize.h })
      .insertBefore($(element));

    function dock() {
      if (initialTopPosition === -1) {
        initialTopPosition = $(element).position().top;
        ghost.height($(element).outerHeight() + (options.jumpCorrection || 0));
      }
      if ($(scrollable).scrollTop() + triggerAdjust > initialTopPosition) {
        $(element).attr(
          'style',
          'position: fixed!important; top: ' +
            options.topSnap +
            '; width: ' +
            initialSize.w +
            'px!important; z-index: ' +
            zIndex
        );
        ghost.show();
      } else {
        $(element).removeAttr('style');
        ghost.hide();
      }
    }

    $(scrollable).on('scroll', dock);

    const scrollOffSubscription = huePubSub.subscribe('scrollable.scroll.off', scrollElement => {
      if (scrollElement === scrollable) {
        $(scrollable).on('scroll', dock);
      }
    });

    function resetInitialStyle() {
      $(element).removeAttr('style');
      initialSize = {
        w: $(element).width() - hueUtils.scrollbarWidth(),
        h: $(element).outerHeight() + (options.jumpCorrection || 0)
      };
      dock();
    }

    $(window).on('resize', resetInitialStyle);

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $(window).off('resize', resetInitialStyle);
      $(scrollable).off('scroll', dock);
      scrollOffSubscription.remove();
    });
  }
};
