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

ko.bindingHandlers.assistFileDroppable = {
  init: function(element, valueAccessor, allBindings, boundEntry) {
    const $element = $(element);

    let dragData;
    const dragSub = huePubSub.subscribe('doc.browser.dragging', data => {
      dragData = data;
    });
    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      dragSub.remove();
    });

    if (boundEntry.isDirectory) {
      $element.droppable({
        drop: () => {
          if (dragData && !dragData.dragToSelect && boundEntry.isDirectory()) {
            boundEntry.moveHere(dragData.selectedEntries);
            dragData.originEntry.load();
          }
          $element.removeClass('assist-file-entry-drop');
        },
        over: () => {
          if (
            !$element.hasClass('assist-file-entry-drop') &&
            dragData &&
            !dragData.dragToSelect &&
            boundEntry.isDirectory()
          ) {
            $element.addClass('assist-file-entry-drop');
          }
        },
        out: () => {
          $element.removeClass('assist-file-entry-drop');
        }
      });
    }
  }
};
