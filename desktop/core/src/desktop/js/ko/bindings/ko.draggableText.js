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

ko.bindingHandlers.draggableText = {
  init: function(element, valueAccessor) {
    const $element = $(element);
    const options = valueAccessor();
    if ((ko.isObservable(options.text) && !options.text()) || !options.text) {
      return;
    }
    $element.addClass('draggableText');

    const $helper = $('<div>')
      .text(ko.isObservable(options.text) ? options.text() : options.text)
      .css('z-index', '99999');
    let dragStartX = -1;
    let dragStartY = -1;
    let notifiedOnDragStarted = false;
    $element.draggable({
      helper: function() {
        return $helper;
      },
      appendTo: 'body',
      start: function(event) {
        dragStartX = event.clientX;
        dragStartY = event.clientY;
        huePubSub.publish('draggable.text.meta', options.meta);
        notifiedOnDragStarted = false;
      },
      drag: function(event) {
        huePubSub.publish('draggable.text.drag', {
          event: event,
          meta: options.meta
        });
        if (
          !notifiedOnDragStarted &&
          Math.sqrt(
            (dragStartX - event.clientX) * (dragStartX - event.clientX) +
              (dragStartY - event.clientY) * (dragStartY - event.clientY)
          ) >= 10
        ) {
          huePubSub.publish('draggable.text.started', options.meta);
          notifiedOnDragStarted = true;
        }
      },
      stop: function(event) {
        if (
          Math.sqrt(
            (dragStartX - event.clientX) * (dragStartX - event.clientX) +
              (dragStartY - event.clientY) * (dragStartY - event.clientY)
          ) < 10
        ) {
          $helper.remove();
          const elementAtStart = document.elementFromPoint(dragStartX, dragStartY);
          const elementAtStop = document.elementFromPoint(event.clientX, event.clientY);
          if (elementAtStart === elementAtStop) {
            $(elementAtStop).trigger('click');
          }
        }
        notifiedOnDragStarted = false;
        huePubSub.publish('draggable.text.stopped');
      }
    });
  }
};
