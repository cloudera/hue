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

ko.bindingHandlers.visibleOnHover = {
  init: function(element, valueAccessor) {
    const options = valueAccessor();
    const $element = $(element);

    const selector = options.selector;
    let showTimeout = -1;
    let hideTimeout = -1;
    ko.utils.domData.set(
      element,
      'visibleOnHover.override',
      ko.utils.unwrapObservable(options.override) || false
    );
    let inside = false;

    const show = function() {
      if (options.childrenOnly) {
        $element.children(selector).fadeTo('fast', 1);
      } else {
        $element.find(selector).fadeTo('fast', 1);
      }
      window.clearTimeout(hideTimeout);
    };

    const hide = function() {
      if (!inside) {
        window.clearTimeout(showTimeout);
        hideTimeout = window.setTimeout(() => {
          if (options.childrenOnly) {
            $element.children(selector).fadeTo('fast', 0);
          } else {
            $element.find(selector).fadeTo('fast', 0);
          }
        }, 10);
      }
    };

    ko.utils.domData.set(element, 'visibleOnHover.show', show);
    ko.utils.domData.set(element, 'visibleOnHover.hide', hide);

    if (ko.utils.domData.get(element, 'visibleOnHover.override')) {
      window.setTimeout(show, 1);
    }

    $element.mouseenter(() => {
      showTimeout = window.setTimeout(() => {
        inside = true;
        show();
      }, 300);
    });

    $element.mouseleave(() => {
      window.clearTimeout(showTimeout);
      inside = false;
      if (!ko.utils.domData.get(element, 'visibleOnHover.override')) {
        hide();
      }
    });
  },
  update: function(element, valueAccessor) {
    if (ko.utils.unwrapObservable(valueAccessor().override)) {
      ko.utils.domData.set(element, 'visibleOnHover.override', true);
      ko.utils.domData.get(element, 'visibleOnHover.show')();
    } else {
      ko.utils.domData.set(element, 'visibleOnHover.override', false);
      ko.utils.domData.get(element, 'visibleOnHover.hide')();
    }
  }
};
