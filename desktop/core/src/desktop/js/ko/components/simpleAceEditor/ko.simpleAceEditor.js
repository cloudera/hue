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

import AceLocationHandler from 'sql/aceLocationHandler';
import componentUtils from 'ko/components/componentUtils';
import hueUtils from 'utils/hueUtils';
import SolrFormulaAutocompleter from './solrFormulaAutocompleter';
import SolrQueryAutocompleter from './solrQueryAutocompleter';
import SqlAutocompleter from 'sql/sqlAutocompleter';
import sqlWorkerHandler from 'sql/sqlWorkerHandler';

const SIMPLE_ACE_TEMPLATE = `
  <div class="simple-ace-single-line">
    <div class="ace-clearable" data-bind="css: { 'visible': value() !== '' }, click: clear"><i class="fa fa-times-circle"></i></div>
    <div class="ace-editor"></div>
  </div>
  <!-- ko if: autocompleter !== null -->
  <!-- ko component: { name: 'hueAceAutocompleter', params: { editor: ace, autocompleter: autocompleter } } --><!-- /ko -->
  <!-- /ko -->
`;

const SIMPLE_ACE_MULTI_TEMPLATE = `
  <div class="simple-ace-multi-line">
    <div class="ace-editor"></div>
  </div>
  <!-- ko if: autocompleter !== null -->
  <!-- ko component: { name: 'hueAceAutocompleter', params: { editor: ace, autocompleter: autocompleter } } --><!-- /ko -->
  <!-- /ko -->
`;

const AVAILABLE_AUTOCOMPLETERS = {
  solrFormula: SolrFormulaAutocompleter,
  solrQuery: SolrQueryAutocompleter,
  impalaQuery: SqlAutocompleter,
  hiveQuery: SqlAutocompleter,
  impala: SqlAutocompleter,
  hive: SqlAutocompleter
};

class SimpleAceEditor {
  constructor(params, element) {
    const $element = $(element);
    const self = this;
    self.value = params.value;
    self.parsedValue = params.parsedValue;
    self.ace = ko.observable();
    self.disposeFunctions = [];

    self.singleLine = !!params.singleLine;

    let aceOptions = params.aceOptions || {};

    if (!$element.attr('id')) {
      $element.attr('id', hueUtils.UUID());
    }

    const editor = ace.edit($element.find('.ace-editor')[0]);
    if (params.mode) {
      editor.getSession().setMode('ace/mode/' + ko.unwrap(params.mode));
    }
    editor.$blockScrolling = Infinity;
    editor.setTheme($.totalStorage('hue.ace.theme') || 'ace/theme/hue');
    self.ace(editor);

    if (params.autocomplete) {
      const sourceType =
        params.autocomplete.type.indexOf('Query') !== -1
          ? params.autocomplete.type.replace('Query', '')
          : params.autocomplete.type;

      const snippet = {
        autocompleteSettings: {
          temporaryOnly: params.temporaryOnly
        },
        type: ko.observable(sourceType),
        id: ko.observable($element.attr('id')),
        namespace: params.namespace,
        compute: params.compute,
        database: ko.observable(
          params.database && params.database() ? params.database() : 'default'
        ),
        availableDatabases: ko.observableArray([
          params.database && params.database() ? params.database() : 'default'
        ]),
        positionStatement: ko.observable({
          location: {
            first_line: 1,
            last_line: 1,
            first_column: 0,
            last_column: editor.getValue().length
          }
        }),
        whenContextSet: function() {
          const promise = $.Deferred()
            .resolve()
            .promise();
          promise.dispose = function() {};
          return promise;
        },
        isSqlDialect: ko.observable(true),
        aceCursorPosition: ko.observable(),
        inFocus: ko.observable()
      };

      if (sourceType === 'hive' || sourceType === 'impala') {
        sqlWorkerHandler.registerWorkers();
        const aceLocationHandler = new AceLocationHandler({
          editor: editor,
          editorId: $element.attr('id'),
          snippet: snippet
        });
        self.disposeFunctions.push(() => {
          aceLocationHandler.dispose();
        });
        aceLocationHandler.attachSqlSyntaxWorker();
      }

      const focusListener = editor.on('focus', () => {
        snippet.inFocus(true);
      });

      const blurListener = editor.on('blur', () => {
        snippet.inFocus(false);
      });

      self.disposeFunctions.push(() => {
        editor.off('focus', focusListener);
        editor.off('blur', blurListener);
      });

      const autocompleteArgs = {
        editor: function() {
          return editor;
        },
        snippet: snippet,
        fixedPrefix: params.fixedPrefix,
        fixedPostfix: params.fixedPostfix,
        support: params.autocomplete.support
      };

      const AutocompleterClass =
        AVAILABLE_AUTOCOMPLETERS[params.autocomplete.type] || SqlAutocompleter;
      self.autocompleter = new AutocompleterClass(autocompleteArgs);
    } else {
      self.autocompleter = null;
    }

    if (self.singleLine) {
      aceOptions = $.extend(aceOptions, {
        fontSize: '13px',
        maxLines: 1, // make it 1 line
        autoScrollEditorIntoView: true,
        highlightActiveLine: false,
        printMargin: false,
        showGutter: false
      });
    } else {
      aceOptions = $.extend(aceOptions, {
        maxLines: params.lines || 2
      });
    }

    if (params.autocomplete) {
      aceOptions = $.extend(aceOptions, {
        enableLiveAutocompletion: true,
        enableBasicAutocompletion: true
      });
    }

    editor.setOptions(aceOptions);

    if (params.onExec) {
      const bindPrefix = params.singleLine ? 'Enter|Shift-Enter|' : '';
      editor.commands.addCommand({
        name: 'enter',
        bindKey: { win: bindPrefix + 'Ctrl-Enter', mac: bindPrefix + 'Ctrl-Enter|Command-Enter' },
        exec: params.onExec
      });
    }

    if (params.singleLine) {
      editor.renderer.screenToTextCoordinates = function(x, y) {
        const pos = this.pixelToScreenCoordinates(x, y);
        return this.session.screenToDocumentPosition(
          Math.min(this.session.getScreenLength() - 1, Math.max(pos.row, 0)),
          Math.max(pos.column, 0)
        );
      };

      if (!params.onExec) {
        editor.commands.bindKey('Enter|Shift-Enter', 'null');
      }

      const pasteListener = editor.on('paste', e => {
        e.text = e.text.replace(/[\r\n]+/g, ' ');
      });

      const changeListener = editor.on('change', e => {
        if (e.action === 'insert' && (e.start.row !== 0 || e.end.row !== 0)) {
          editor.setValue(editor.getValue().replace(/[\r\n]+/g, ' '));
          editor.clearSelection();
        }
      });

      self.disposeFunctions.push(() => {
        editor.off('paste', pasteListener);
        editor.off('change', changeListener);
      });
    }

    if (self.value()) {
      editor.setValue(self.value());
      editor.clearSelection();
    }

    if (params.placeHolder && ko.unwrap(params.placeHolder)) {
      let placeHolderVisible = false;

      const $placeHolder = $('<div>')
        .text(ko.unwrap(params.placeHolder))
        .addClass('ace_invisible ace_emptyMessage');

      if (editor.getValue().length === 0) {
        $placeHolder.appendTo(editor.renderer.scroller);
        placeHolderVisible = true;
      }

      const inputListener = editor.on('input', () => {
        if (editor.getValue().length > 0 && placeHolderVisible) {
          $placeHolder.remove();
          placeHolderVisible = false;
        } else if (editor.getValue().length === 0 && !placeHolderVisible) {
          $placeHolder.appendTo(editor.renderer.scroller);
          placeHolderVisible = true;
        }
      });

      self.disposeFunctions.push(() => {
        editor.off('input', inputListener);
      });
    }

    if (params.autocomplete) {
      const AceAutocomplete = ace.require('ace/autocomplete').Autocomplete;

      if (!editor.completer) {
        editor.completer = new AceAutocomplete();
      }
      editor.completer.exactMatch = false;
      editor.useHueAutocompleter = true;

      const afterExecListener = editor.commands.on('afterExec', e => {
        if (e.command.name === 'insertstring') {
          let triggerAutocomplete = false;
          if (/\S+\(\)$/.test(e.args)) {
            editor.moveCursorTo(
              editor.getCursorPosition().row,
              editor.getCursorPosition().column - 1
            );
            triggerAutocomplete = true;
          } else if (params.autocomplete.type === 'solrQuery' && /:$/.test(e.args)) {
            triggerAutocomplete = true;
          }

          if (triggerAutocomplete) {
            window.setTimeout(() => {
              editor.execCommand('startAutocomplete');
            }, 1);
          }
        }
      });

      self.disposeFunctions.push(() => {
        editor.commands.off('afterExec', afterExecListener);
      });
    }

    let parseThrottle = -1;
    const valueUpdateListener = editor.on('input', () => {
      self.value(editor.getValue());
      if (self.parsedValue && self.autocompleter && self.autocompleter.parse) {
        window.clearTimeout(parseThrottle);
        parseThrottle = window.setTimeout(() => {
          const parseResult = self.autocompleter.parse(editor.getValue());
          if (parseResult) {
            self.parsedValue(parseResult.parsedValue);
          } else {
            // TODO: What to do when we can't parse?
            self.parsedValue(editor.getValue());
          }
        }, 200);
      }
    });

    self.disposeFunctions.push(() => {
      editor.off('input', valueUpdateListener);
    });
  }

  clear() {
    const self = this;
    if (self.ace()) {
      self.ace().setValue('');
    } else {
      self.value('');
    }
  }

  dispose() {
    const self = this;
    self.disposeFunctions.forEach(dispose => {
      dispose();
    });
  }
}

// Ace requires that the child to clone is first child, so we need separate components for single line & multi line
componentUtils.registerComponent(
  'hue-simple-ace-editor',
  {
    createViewModel: function(params, componentInfo) {
      return new SimpleAceEditor(params, componentInfo.element);
    }
  },
  SIMPLE_ACE_TEMPLATE
);

componentUtils.registerComponent(
  'hue-simple-ace-editor-multi',
  {
    createViewModel: function(params, componentInfo) {
      return new SimpleAceEditor(params, componentInfo.element);
    }
  },
  SIMPLE_ACE_MULTI_TEMPLATE
);
