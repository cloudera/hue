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

ko.bindingHandlers.logResizer = {
  init: function(element, valueAccessor) {
    const options = ko.unwrap(valueAccessor()),
      $resizer = $(element),
      $parent = $resizer.parents(options.parent),
      $target = $parent.find(options.target),
      onStart = options.onStart,
      onResize = options.onResize;

    const initialHeight = $.totalStorage('hue.editor.logs.size') || 80;

    window.setTimeout(() => {
      $target.css('height', initialHeight + 'px');
    }, 0);

    $resizer.draggable({
      axis: 'y',
      start: function() {
        if (onStart) {
          onStart();
        }
      },
      drag: function(event, ui) {
        let currentHeight = ui.offset.top - $target.offset().top - 20;
        if (options.minHeight && currentHeight < options.minHeight) {
          currentHeight = options.minHeight;
        }
        $.totalStorage('hue.editor.logs.size', currentHeight);
        $target.css('height', currentHeight + 'px');
        ui.offset.top = 0;
        ui.position.top = 0;
      },
      stop: function(event, ui) {
        ui.offset.top = 0;
        ui.position.top = 0;
        if (onResize) {
          onResize();
        }
      }
    });
  }
};
