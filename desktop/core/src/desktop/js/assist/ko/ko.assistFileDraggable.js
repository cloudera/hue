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

ko.bindingHandlers.assistFileDraggable = {
  init: function(element, valueAccessor, allBindings, boundEntry) {
    const $element = $(element);

    let dragStartY = -1;
    let dragStartX = -1;
    $element.draggable({
      start: event => {
        const $container = $('.doc-browser-drag-container');
        boundEntry.selected(true);
        huePubSub.publish('doc.browser.dragging', {
          selectedEntries: [boundEntry],
          originEntry: boundEntry,
          dragToSelect: false
        });
        huePubSub.publish('doc.drag.to.select', false);

        dragStartX = event.clientX;
        dragStartY = event.clientY;

        const $helper = $('.assist-file-entry-drag')
          .clone()
          .appendTo($container);
        $helper.find('.drag-text').text(boundEntry.definition().name);
        $helper
          .find('i')
          .removeClass()
          .addClass($element.find('.doc-browser-primary-col i').attr('class'));
        $helper.show();
      },
      drag: () => {},
      stop: event => {
        const elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
        const elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
        if (
          elementAtStart.nodeName === 'A' &&
          elementAtStop.nodeName === 'A' &&
          Math.sqrt(
            (dragStartX - event.clientX) * (dragStartX - event.clientX) +
              (dragStartY - event.clientY) * (dragStartY - event.clientY)
          ) < 8
        ) {
          $(elementAtStop).trigger('click');
        }
        boundEntry.selected(false);
      },
      helper: () => $('<div>').addClass('doc-browser-drag-container'),
      appendTo: 'body',
      cursorAt: {
        top: 0,
        left: 0
      }
    });
  }
};
