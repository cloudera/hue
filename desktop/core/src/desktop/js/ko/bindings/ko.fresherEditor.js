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

import hueUtils from 'utils/hueUtils';

ko.bindingHandlers.fresherEditor = {
  init: function(element, valueAccessor) {
    const _el = $(element);
    const options = $.extend(valueAccessor(), {});
    _el.html(options.data());
    _el.freshereditor({
      excludes: [
        'strikethrough',
        'removeFormat',
        'insertorderedlist',
        'justifyfull',
        'insertheading1',
        'insertheading2',
        'superscript',
        'subscript'
      ]
    });
    _el.freshereditor('edit', true);
    _el.on('mouseup', () => {
      storeSelection();
      updateValues();
    });

    let sourceDelay = -1;
    _el.on('keyup', () => {
      clearTimeout(sourceDelay);
      storeSelection();
      sourceDelay = setTimeout(() => {
        updateValues();
      }, 100);
    });

    $('.chosen-select').chosen({
      disable_search_threshold: 10,
      width: '75%'
    });

    $(document).on('addFieldToVisual', (e, field) => {
      _el.focus();
      pasteHtmlAtCaret('{{' + field.name() + '}}');
    });

    $(document).on('addFunctionToVisual', (e, fn) => {
      _el.focus();
      pasteHtmlAtCaret(fn);
    });

    function updateValues() {
      $('[data-template]')[0].editor.setValue(hueUtils.stripHtmlFromFunctions(_el.html()));
      valueAccessor().data(_el.html());
    }

    function storeSelection() {
      if (window.getSelection) {
        // IE9 and non-IE
        const sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          const range = sel.getRangeAt(0);
          _el.data('range', range);
        }
      } else if (document.selection && document.selection.type !== 'Control') {
        // IE < 9
        _el.data('selection', document.selection);
      }
    }

    function pasteHtmlAtCaret(html) {
      let sel, range;
      if (window.getSelection) {
        // IE9 and non-IE
        sel = window.getSelection();
        if (sel.getRangeAt && sel.rangeCount) {
          if (_el.data('range')) {
            range = _el.data('range');
          } else {
            range = sel.getRangeAt(0);
          }
          range.deleteContents();

          // Range.createContextualFragment() would be useful here but is
          // non-standard and not supported in all browsers (IE9, for one)
          const el = document.createElement('div');
          el.innerHTML = html;
          const frag = document.createDocumentFragment();
          let node, lastNode;
          while ((node = el.firstChild)) {
            lastNode = frag.appendChild(node);
          }
          range.insertNode(frag);

          // Preserve the selection
          if (lastNode) {
            range = range.cloneRange();
            range.setStartAfter(lastNode);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
          }
        }
      } else if (document.selection && document.selection.type !== 'Control') {
        // IE < 9
        if (_el.data('selection')) {
          _el
            .data('selection')
            .createRange()
            .pasteHTML(html);
        } else {
          document.selection.createRange().pasteHTML(html);
        }
      }
    }
  }
};
