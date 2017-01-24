// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/bindings/headerScroll
 * @description
 *
 * Usage:
 * Place it on an element that needs to be fixed at the top.
 * <div class="page-header" data-bind="headerScroll">
 *   ...
 * </div>
 *
 * Note:
 * We recommend you create a single <div> that wraps the above element.
 * e.g.
 * <div class="page-header-wrapper">
 *   <div class="page-header" data-bind="headerScroll">
 *     ...
 *   </div>
 * </div>
 *
 * Otherwise, you could see two undesirable outcome:
 * 1. The existing parent of the above element is body. Then you might get a flicker effect
 * when the window's height is approximately equal to the viewport height.
 *
 * 2. The existing parent of the above element contains other elements. Then those other
 * children might disappear on scroll.
 */
import 'bootstrap/affix';

import ko from 'knockout';

ko.bindingHandlers.headerScroll = {
  init: function(element) {
    var $element = $(element);
    var $parent = $element.parent();

    $element.affix({
      offset: {
        top: $element[0].offsetTop
      }
    });

    // We assume the element's height doesn't change.
    // If it does change, we need to enhance this utility
    // and add an event subscriber.

    var updateParentHeight = function() {
      if ($element.height() > 0) {
        $parent.height($element.height());
      } else {
        setTimeout(updateParentHeight, 100);
      }
    };

    $(function() {
      setTimeout(updateParentHeight, 100);
    });
  }
};
