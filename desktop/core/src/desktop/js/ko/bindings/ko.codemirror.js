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

ko.bindingHandlers.codemirror = {
  init: function(element, valueAccessor) {
    const options = $.extend(valueAccessor(), {});
    const editor = CodeMirror.fromTextArea(element, options);
    element.editor = editor;
    editor.setValue(options.data());
    editor.refresh();
    const wrapperElement = $(editor.getWrapperElement());

    $(document).on('refreshCodemirror', () => {
      editor.setSize('100%', 300);
      editor.refresh();
    });

    $(document).on('addFieldToSource', (e, field) => {
      if ($(element).data('template')) {
        editor.replaceSelection('{{' + field.name() + '}}');
      }
    });

    $(document).on('addFunctionToSource', (e, fn) => {
      if ($(element).data('template')) {
        editor.replaceSelection(fn);
      }
    });

    const $chosenSelect = $('.chosen-select');

    $chosenSelect.chosen({
      disable_search_threshold: 10,
      width: '75%'
    });
    $chosenSelect.trigger('chosen:updated');

    let sourceDelay = -1;
    editor.on('change', cm => {
      clearTimeout(sourceDelay);
      const _cm = cm;
      sourceDelay = setTimeout(() => {
        let _value = _cm.getValue();
        if (options.stripScript) {
          _value = _value.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
        }
        valueAccessor().data(_value);
        if (
          $('.widget-html-pill')
            .parent()
            .hasClass('active')
        ) {
          $('[contenteditable=true]').html(hueUtils.stripHtmlFromFunctions(valueAccessor().data()));
        }
      }, 100);
    });

    ko.utils.domNodeDisposal.addDisposeCallback(element, () => {
      wrapperElement.remove();
    });
  },
  update: function(element) {
    const editor = element.editor;
    editor.refresh();
  }
};
