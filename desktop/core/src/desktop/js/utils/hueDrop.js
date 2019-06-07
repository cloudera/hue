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

import huePubSub from 'utils/huePubSub';

const hueDrop = () => {
  let draggableMeta = {};

  huePubSub.subscribe('draggable.text.meta', meta => {
    draggableMeta = meta;
  });

  return {
    fromAssist: function(element, callback) {
      if (typeof element === 'function' && !(element instanceof $)) {
        callback = element;
      }
      if (typeof element === 'string') {
        element = $(element);
      }
      if (element.length > 0) {
        element.droppable({
          accept: '.draggableText',
          drop: function(e, ui) {
            if (callback) {
              callback({
                text: ui.helper.text(),
                meta: draggableMeta
              });
            }
          }
        });
      } else {
        console.warn('hueDrop.fromAssist could not be attached to the element');
      }
    },
    fromDesktop: function(element, callback, method) {
      if (window.FileReader) {
        if (typeof element === 'function' && !(element instanceof $)) {
          callback = element;
        }
        if (typeof element === 'string') {
          element = $(element);
        }

        const handleFileSelect = e => {
          e.stopPropagation();
          e.preventDefault();
          const dt = e.dataTransfer;
          const files = dt.files;
          for (let i = 0, f; (f = files[i]); i++) {
            const reader = new FileReader();
            reader.onload = (function(file) {
              return function(e) {
                callback(e.target.result);
              };
            })(f);
            switch (method) {
              case 'arrayBuffer':
                reader.readAsArrayBuffer(f);
                break;
              case 'binaryString':
                reader.readAsBinaryString(f);
                break;
              case 'dataURL':
                reader.readAsDataURL(f);
                break;
              default:
                reader.readAsText(f);
            }
          }
        };

        const handleDragOver = e => {
          e.stopPropagation();
          e.preventDefault();
          e.dataTransfer.dropEffect = 'copy';
        };

        if (element.length > 0) {
          element[0].addEventListener('dragover', handleDragOver, false);
          element[0].addEventListener('drop', handleFileSelect, false);
        } else {
          console.warn('hueDrop.fromDesktop could not be attached to the element');
        }
      } else {
        console.warn(
          'FileReader is not supported by your browser. Please consider upgrading to fully experience Hue!'
        );
      }
    }
  };
};

export default hueDrop;
