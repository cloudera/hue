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

ko.bindingHandlers.aceResizer = {
  init: function(element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    const ace = options.snippet.ace.bind(options.snippet);
    const $target = $(options.target);
    const $resizer = $(element);
    const $contentPanel = $('.content-panel');
    const $execStatus = $resizer.prev('.snippet-execution-status');
    const $variables = $resizer.siblings('.snippet-row').find('.variables');

    let lastEditorSize = $.totalStorage('hue.editor.editor.size') || 131;
    let editorHeight = Math.floor(lastEditorSize / 16);
    $target.height(lastEditorSize);
    let autoExpand =
      typeof options.snippet.aceAutoExpand !== 'undefined' ? options.snippet.aceAutoExpand : true;
    let draggedOnce = false;

    function throttleChange() {
      if (autoExpand && !draggedOnce) {
        const maxAutoLines = Math.floor(($(window).height() - 80) / 2 / 16);
        let resized = false;
        if (ace().session.getLength() > editorHeight) {
          if (ace().session.getLength() < maxAutoLines) {
            $target.height(ace().session.getLength() * 16);
          } else {
            $target.height(maxAutoLines * 16); // height of maxAutoLines
          }
          resized = true;
        } else {
          $target.height(
            Math.max(
              ace().session.getLength() * 16,
              $.totalStorage('hue.editor.editor.size') || 131
            )
          );
          resized = true;
        }
        if (ace().session.getLength() === editorHeight) {
          resized = false;
        }
        if (resized && $target.height() !== lastEditorSize) {
          ace().resize();
          editorHeight = Math.min(maxAutoLines, ace().session.getLength());
          lastEditorSize = $target.height();
          huePubSub.publish('redraw.fixed.headers');
        }
      }
    }

    let changeTimeout = -1;
    ace().on('change', () => {
      window.clearTimeout(changeTimeout);
      changeTimeout = window.setTimeout(throttleChange, 10);
    });

    const setAutoExpandSubscription = huePubSub.subscribe('ace.set.autoexpand', options => {
      if (ace().container.id === options.snippet.id()) {
        autoExpand = options.autoExpand;
      }
    });

    $resizer.draggable({
      axis: 'y',
      start: options.onStart ? options.onStart : function() {},
      drag: function(event, ui) {
        draggedOnce = true;
        const currentHeight =
          ui.offset.top +
          $contentPanel.scrollTop() -
          (125 + $execStatus.outerHeight(true) + $variables.outerHeight(true));
        $target.css('height', currentHeight + 'px');
        ace().resize();
        ui.offset.top = 0;
        ui.position.top = 0;
      },
      stop: function(event, ui) {
        ui.offset.top = 0;
        ui.position.top = 0;
        $.totalStorage('hue.editor.editor.size', $target.height());
        huePubSub.publish('redraw.fixed.headers');
        $(document).trigger('editorSizeChanged');
      }
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      setAutoExpandSubscription.remove();
    });
  }
};
