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
import * as ko from 'knockout';

import huePubSub from 'utils/huePubSub';
import { registerBinding } from './bindingUtils';

export const DRAGGABLE_TEXT_META_EVENT = 'draggable.text.meta';
export const NAME = 'draggableText';

const moreThanTenPixels = (startX, startY, event) =>
  Math.sqrt(
    (startX - event.clientX) * (startX - event.clientX) +
      (startY - event.clientY) * (startY - event.clientY)
  ) > 10;

registerBinding(NAME, {
  init: (element, valueAccessor) => {
    const $element = $(element);
    const options = valueAccessor();

    let dragStartX = -1;
    let dragStartY = -1;
    let notifiedOnDragStarted = false;
    let $helper;

    $element.addClass('draggableText');

    $element.draggable({
      helper: () => {
        $helper = $('<div>').text(ko.unwrap(options.text)).css('z-index', '99999');
        return $helper;
      },
      appendTo: 'body',
      start: event => {
        dragStartX = event.clientX;
        dragStartY = event.clientY;
        huePubSub.publish(DRAGGABLE_TEXT_META_EVENT, options.meta);
        notifiedOnDragStarted = false;
      },
      drag: event => {
        huePubSub.publish('draggable.text.drag', {
          event: event,
          meta: options.meta
        });
        if (!notifiedOnDragStarted && moreThanTenPixels(dragStartX, dragStartY, event)) {
          huePubSub.publish('draggable.text.started', options.meta);
          notifiedOnDragStarted = true;
        }
      },
      stop: event => {
        if ($helper) {
          $helper.remove();
        }

        if (!moreThanTenPixels(dragStartX, dragStartY, event)) {
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

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      $element.draggable('destroy');
    });
  }
});
