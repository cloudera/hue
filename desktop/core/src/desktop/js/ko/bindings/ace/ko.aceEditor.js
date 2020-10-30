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
import ace from 'ext/aceHelper';

import apiHelper from 'api/apiHelper';
import AceLocationHandler, {
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from 'ko/bindings/ace/aceLocationHandler';
import huePubSub from 'utils/huePubSub';
import AceGutterHandler from 'ko/bindings/ace/aceGutterHandler';
import { registerBinding } from 'ko/bindings/bindingUtils';

export const NAME = 'aceEditor';
export const INSERT_AT_CURSOR_EVENT = 'editor.insert.at.cursor';

registerBinding(NAME, {
  init: function (element, valueAccessor) {
    const $el = $(element);
    const options = ko.unwrap(valueAccessor());
    const snippet = options.snippet;
    const aceOptions = options.aceOptions || {};

    const disposeFunctions = [];

    const dispose = function () {
      disposeFunctions.forEach(dispose => {
        dispose();
      });
    };

    ko.utils.domNodeDisposal.addDisposeCallback(element, dispose);

    $el.text(snippet.statement_raw());

    const editor = ace.edit(snippet.id());
    const AceRange = ace.require('ace/range').Range;

    const resizeAce = function () {
      window.setTimeout(() => {
        try {
          editor.resize(true);
        } catch (e) {
          // Can happen when the editor hasn't been initialized
        }
      }, 0);
    };

    const assistToggleSub = huePubSub.subscribe('assist.set.manual.visibility', resizeAce);
    const resizePubSub = huePubSub.subscribe('split.panel.resized', resizeAce);
    disposeFunctions.push(() => {
      assistToggleSub.remove();
      resizePubSub.remove();
    });

    const aceLocationHandler = new AceLocationHandler({
      editor: editor,
      editorId: $el.attr('id'),
      snippet: snippet,
      executor: snippet.executor,
      i18n: { expandStar: options.expandStar, contextTooltip: options.contextTooltip }
    });

    const aceGutterHandler = new AceGutterHandler({
      editor: editor,
      editorId: $el.attr('id'),
      executor: snippet.executor
    });
    disposeFunctions.push(() => {
      aceLocationHandler.dispose();
      aceGutterHandler.dispose();
    });

    editor.session.setMode(snippet.getAceMode());
    editor.setOptions({
      fontSize: apiHelper.getFromTotalStorage(
        'hue.ace',
        'fontSize',
        navigator.platform && navigator.platform.toLowerCase().indexOf('linux') > -1
          ? '14px'
          : '12px'
      )
    });

    function processErrorsAndWarnings(type, list) {
      editor.clearErrorsAndWarnings(type);
      let offset = 0;
      if (snippet.isSqlDialect() && editor.getSelectedText()) {
        const selectionRange = editor.getSelectionRange();
        offset = Math.min(selectionRange.start.row, selectionRange.end.row);
      }
      if (list.length > 0) {
        list.forEach((item, cnt) => {
          if (item.line !== null) {
            if (type === 'error') {
              editor.addError(item.message, item.line + offset);
            } else {
              editor.addWarning(item.message, item.line + offset);
            }
            if (cnt === 0) {
              editor.scrollToLine(item.line + offset, true, true, () => {});
              if (item.col !== null) {
                editor.renderer.scrollCursorIntoView(
                  { row: item.line + offset, column: item.col + 10 },
                  0.5
                );
              }
            }
          }
        });
      }
    }

    const errorsSub = snippet.errors.subscribe(newErrors => {
      processErrorsAndWarnings('error', newErrors);
    });

    const aceWarningsSub = snippet.aceWarnings.subscribe(newWarnings => {
      processErrorsAndWarnings('warning', newWarnings);
    });

    const aceErrorsSub = snippet.aceErrors.subscribe(newErrors => {
      processErrorsAndWarnings('error', newErrors);
    });

    disposeFunctions.push(() => {
      errorsSub.dispose();
      aceWarningsSub.dispose();
      aceErrorsSub.dispose();
    });

    let darkThemeEnabled = apiHelper.getFromTotalStorage('ace', 'dark.theme.enabled', false);
    editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');

    const editorOptions = {
      enableSnippets: true,
      showGutter: false,
      showLineNumbers: false,
      showPrintMargin: false,
      scrollPastEnd: 0.1,
      minLines: 1,
      maxLines: 25
    };

    editor.enabledMenuOptions = {
      setShowInvisibles: true,
      setTabSize: true,
      setShowGutter: true
    };

    editor.customMenuOptions = {
      setEnableDarkTheme: function (enabled) {
        darkThemeEnabled = enabled;
        apiHelper.setInTotalStorage('ace', 'dark.theme.enabled', darkThemeEnabled);
        editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
      },
      getEnableDarkTheme: function () {
        return darkThemeEnabled;
      },
      setEnableAutocompleter: function (enabled) {
        editor.setOption('enableBasicAutocompletion', enabled);
        apiHelper.setInTotalStorage('hue.ace', 'enableBasicAutocompletion', enabled);
        const $enableLiveAutocompletionChecked = $('#setEnableLiveAutocompletion:checked');
        const $setEnableLiveAutocompletion = $('#setEnableLiveAutocompletion');
        if (enabled && $enableLiveAutocompletionChecked.length === 0) {
          $setEnableLiveAutocompletion.trigger('click');
        } else if (!enabled && $enableLiveAutocompletionChecked.length !== 0) {
          $setEnableLiveAutocompletion.trigger('click');
        }
      },
      getEnableAutocompleter: function () {
        return editor.getOption('enableBasicAutocompletion');
      },
      setEnableLiveAutocompletion: function (enabled) {
        editor.setOption('enableLiveAutocompletion', enabled);
        apiHelper.setInTotalStorage('hue.ace', 'enableLiveAutocompletion', enabled);
        if (enabled && $('#setEnableAutocompleter:checked').length === 0) {
          $('#setEnableAutocompleter').trigger('click');
        }
      },
      getEnableLiveAutocompletion: function () {
        return editor.getOption('enableLiveAutocompletion');
      },
      setFontSize: function (size) {
        if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
          size += 'px';
        }
        editor.setOption('fontSize', size);
        apiHelper.setInTotalStorage('hue.ace', 'fontSize', size);
      },
      getFontSize: function () {
        let size = editor.getOption('fontSize');
        if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
          size += 'px';
        }
        return size;
      }
    };

    if (window.ENABLE_SQL_SYNTAX_CHECK && window.Worker) {
      let errorHighlightingEnabled = apiHelper.getFromTotalStorage(
        'hue.ace',
        'errorHighlightingEnabled',
        true
      );

      if (errorHighlightingEnabled) {
        aceLocationHandler.attachSqlSyntaxWorker();
      }

      editor.customMenuOptions.setErrorHighlighting = function (enabled) {
        errorHighlightingEnabled = enabled;
        apiHelper.setInTotalStorage('hue.ace', 'errorHighlightingEnabled', enabled);
        if (enabled) {
          aceLocationHandler.attachSqlSyntaxWorker();
        } else {
          aceLocationHandler.detachSqlSyntaxWorker();
        }
      };
      editor.customMenuOptions.getErrorHighlighting = function () {
        return errorHighlightingEnabled;
      };
      editor.customMenuOptions.setClearIgnoredSyntaxChecks = function () {
        apiHelper.setInTotalStorage('hue.syntax.checker', 'suppressedRules', {});
        $('#setClearIgnoredSyntaxChecks')
          .hide()
          .before('<div style="margin-top:5px;float:right;">done</div>');
      };
      editor.customMenuOptions.getClearIgnoredSyntaxChecks = function () {
        return false;
      };
    }

    $.extend(editorOptions, aceOptions);

    editorOptions['enableBasicAutocompletion'] = apiHelper.getFromTotalStorage(
      'hue.ace',
      'enableBasicAutocompletion',
      true
    );
    if (editorOptions['enableBasicAutocompletion']) {
      editorOptions['enableLiveAutocompletion'] = apiHelper.getFromTotalStorage(
        'hue.ace',
        'enableLiveAutocompletion',
        true
      );
    }
    editorOptions['tabSize'] = 2;
    editorOptions['useSoftTabs'] = true;

    editor.setOptions(editorOptions);

    const AceAutocomplete = ace.require('ace/autocomplete').Autocomplete;

    if (!editor.completer) {
      editor.completer = new AceAutocomplete();
    }
    editor.completer.exactMatch = !snippet.isSqlDialect();

    const initAutocompleters = function () {
      if (editor.completers) {
        editor.completers.length = 0;
        if (snippet.isSqlDialect()) {
          editor.useHueAutocompleter = true;
        } else {
          editor.completers.push(langTools.snippetCompleter);
          editor.completers.push(langTools.textCompleter);
          editor.completers.push(langTools.keyWordCompleter);
          editor.completers.push(snippet.autocompleter);
        }
      }
    };

    const langTools = ace.require('ace/ext/language_tools');
    langTools.textCompleter.setSqlMode(snippet.isSqlDialect());

    initAutocompleters();

    const UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/gi; //taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html

    const removeUnicodes = function (value) {
      return value.replace(UNICODES_TO_REMOVE, ' ');
    };

    let placeHolderElement = null;
    let placeHolderVisible = false;
    const placeHolderText = snippet.getPlaceHolder();
    if (placeHolderText) {
      placeHolderElement = $('<div>')
        .text(placeHolderText)
        .css('margin-left', '6px')
        .addClass('ace_invisible ace_emptyMessage');
      if (editor.getValue().length === 0) {
        placeHolderElement.appendTo(editor.renderer.scroller);
        placeHolderVisible = true;
      }
    }

    const pasteListener = editor.on('paste', e => {
      e.text = removeUnicodes(e.text);
    });

    disposeFunctions.push(() => {
      editor.off('paste', pasteListener);
    });

    const inputListener = editor.on('input', () => {
      if (editor.getValue().length === 0) {
        if (!placeHolderVisible && placeHolderElement) {
          placeHolderElement.appendTo(editor.renderer.scroller);
          placeHolderVisible = true;
        }
      } else {
        placeHolderElement.remove();
        placeHolderVisible = false;
      }
      if (options.updateOnInput) {
        snippet.statement_raw(removeUnicodes(editor.getValue()));
      }
    });

    disposeFunctions.push(() => {
      editor.off('input', inputListener);
    });

    if (snippet.aceCursorPosition()) {
      editor.moveCursorToPosition(snippet.aceCursorPosition());
      window.setTimeout(() => {
        editor.centerSelection();
      }, 0);
    }

    const focusListener = editor.on('focus', () => {
      initAutocompleters();
      snippet.inFocus(true);
      $('.ace-editor').data('last-active-editor', false);
      $el.data('last-active-editor', true);
      if (editor.session.$backMarkers) {
        for (const marker in editor.session.$backMarkers) {
          if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
            editor.session.removeMarker(editor.session.$backMarkers[marker].id);
          }
        }
      }
    });

    disposeFunctions.push(() => {
      editor.off('focus', focusListener);
    });

    const changeSelectionListener = editor.selection.on('changeSelection', () => {
      snippet.selectedStatement(editor.getSelectedText());
    });

    disposeFunctions.push(() => {
      editor.selection.off('changeSelection', changeSelectionListener);
    });

    const blurListener = editor.on('blur', () => {
      snippet.inFocus(false);
      snippet.statement_raw(removeUnicodes(editor.getValue()));
      if (options.onBlur) {
        options.onBlur($el, removeUnicodes(editor.getValue()));
      }
    });

    disposeFunctions.push(() => {
      editor.off('blur', blurListener);
    });

    editor.previousSize = 0;

    // TODO: Get rid of this
    const idInterval = window.setInterval(() => {
      editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
    }, 100);

    disposeFunctions.push(() => {
      window.clearInterval(idInterval);
    });

    editor.middleClick = false;
    const mousedownListener = editor.on('mousedown', e => {
      if (e.domEvent.which === 2) {
        // middle click
        editor.middleClick = true;
        const tempText = editor.getSelectedText();
        if (e.$pos) {
          editor.session.insert(e.$pos, tempText);
        }
        window.setTimeout(() => {
          editor.middleClick = false;
          if (e.$pos) {
            editor.moveCursorTo(e.$pos.row, e.$pos.column + tempText.length);
          }
        }, 200);
      }
    });

    disposeFunctions.push(() => {
      editor.off('mousedown', mousedownListener);
    });

    const aceReplaceSub = huePubSub.subscribe('ace.replace', data => {
      const Range = ace.require('ace/range').Range;
      const range = new Range(
        data.location.first_line - 1,
        data.location.first_column - 1,
        data.location.last_line - 1,
        data.location.last_column - 1
      );
      editor.getSession().getDocument().replace(range, data.text);
    });

    disposeFunctions.push(() => {
      aceReplaceSub.remove();
    });

    const clickListener = editor.on('click', () => {
      editor.clearErrorsAndWarnings();
    });

    disposeFunctions.push(() => {
      editor.off('click', clickListener);
    });

    const changeListener = editor.on('change', () => {
      snippet.statement_raw(removeUnicodes(editor.getValue()));
      editor.session.getMode().$id = snippet.getAceMode();
      const currentSize = editor.session.getLength();
      if (
        currentSize !== editor.previousSize &&
        currentSize >= editorOptions.minLines &&
        currentSize <= editorOptions.maxLines
      ) {
        editor.previousSize = editor.session.getLength();
        $(document).trigger('editorSizeChanged');
      }
      // automagically change snippet type
      // TODO: Remove completely, check if used in code, '% dialect'
      const firstLine = editor.session.getLine(0);
      if (
        !window.ENABLE_NOTEBOOK_2 &&
        firstLine.indexOf('%') === 0 &&
        firstLine.charAt(firstLine.length - 1) === ' '
      ) {
        const availableSnippets = snippet.availableSnippets;
        let removeFirstLine = false;
        for (let i = 0; i < availableSnippets.length; i++) {
          if ($.trim(firstLine.substr(1)) === availableSnippets[i].type()) {
            snippet.type(availableSnippets[i].type());
            removeFirstLine = true;
            break;
          }
        }
        if (removeFirstLine) {
          editor.session.remove(new AceRange(0, 0, 0, 200));
        }
      }
    });

    disposeFunctions.push(() => {
      editor.off('change', changeListener);
    });

    editor.commands.addCommand({
      name: 'execute',
      bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter|Ctrl-Enter' },
      exec: function () {
        snippet.statement_raw(removeUnicodes(editor.getValue()));
        snippet.execute();
      }
    });

    editor.commands.addCommand({
      name: 'switchTheme',
      bindKey: { win: 'Ctrl-Alt-t', mac: 'Command-Alt-t' },
      exec: function () {
        darkThemeEnabled = !darkThemeEnabled;
        apiHelper.setInTotalStorage('ace', 'dark.theme.enabled', darkThemeEnabled);
        editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
      }
    });

    editor.commands.addCommand({
      name: 'new',
      bindKey: { win: 'Ctrl-e', mac: 'Command-e' },
      exec: function () {
        huePubSub.publish('editor.create.new');
      }
    });

    editor.commands.addCommand({
      name: 'save',
      bindKey: { win: 'Ctrl-s', mac: 'Command-s|Ctrl-s' },
      exec: function () {
        huePubSub.publish('editor.save');
      }
    });

    editor.commands.addCommand({
      name: 'esc',
      bindKey: { win: 'Ctrl-Shift-p', mac: 'Ctrl-Shift-p|Command-Shift-p' },
      exec: function () {
        huePubSub.publish('editor.presentation.toggle');
      }
    });

    editor.commands.bindKey('Ctrl-P', 'golineup');

    editor.commands.addCommand({
      name: 'format',
      bindKey: {
        win: 'Ctrl-i|Ctrl-Shift-f|Ctrl-Alt-l',
        mac: 'Command-i|Ctrl-i|Ctrl-Shift-f|Command-Shift-f|Ctrl-Shift-l|Cmd-Shift-l'
      },
      exec: function () {
        if (
          [
            'ace/mode/hive',
            'ace/mode/impala',
            'ace/mode/sql',
            'ace/mode/mysql',
            'ace/mode/pgsql',
            'ace/mode/sqlite',
            'ace/mode/oracle'
          ].indexOf(snippet.getAceMode()) > -1
        ) {
          $.post(
            '/notebook/api/format',
            {
              statements:
                editor.getSelectedText() !== '' ? editor.getSelectedText() : editor.getValue()
            },
            data => {
              if (data.status === 0) {
                if (editor.getSelectedText() !== '') {
                  editor.session.replace(
                    editor.session.selection.getRange(),
                    data.formatted_statements
                  );
                } else {
                  editor.setValue(data.formatted_statements);
                  snippet.statement_raw(removeUnicodes(editor.getValue()));
                }
              }
            }
          );
        }
      }
    });

    editor.commands.addCommand({
      name: 'gotolinealternative',
      bindKey: { win: 'Ctrl-j', mac: 'Command-j|Ctrl-j' },
      exec: editor.commands.commands['gotoline'].exec
    });

    const isNewStatement = function () {
      return /^\s*$/.test(editor.getValue()) || /^.*;\s*$/.test(editor.getTextBeforeCursor());
    };

    const insertSqlAtCursor = function (text, cursorEndAdjust, menu) {
      const before = editor.getTextBeforeCursor();
      if (/\S+$/.test(before)) {
        text = ' ' + text;
      }
      if (menu) {
        menu.hide();
      }
      editor.session.insert(editor.getCursorPosition(), text);
      if (cursorEndAdjust !== 0) {
        const cursor = editor.getCursorPosition();
        editor.moveCursorToPosition({ row: cursor.row, column: cursor.column + cursorEndAdjust });
      }
      editor.clearSelection();
      editor.focus();
    };

    const insertTableAtCursorSub = huePubSub.subscribe('editor.insert.table.at.cursor', details => {
      if ($el.data('last-active-editor')) {
        const qualifiedName =
          snippet.database() === details.database
            ? details.name
            : details.database + '.' + details.name;
        if (isNewStatement()) {
          insertSqlAtCursor('SELECT * FROM ' + qualifiedName + ' LIMIT 100;', -1);
        } else {
          insertSqlAtCursor(qualifiedName + ' ', 0);
        }
      }
    });

    const insertColumnAtCursorSub = huePubSub.subscribe(
      'editor.insert.column.at.cursor',
      details => {
        if ($el.data('last-active-editor')) {
          if (isNewStatement()) {
            const qualifiedFromName =
              snippet.database() === details.database
                ? details.table
                : details.database + '.' + details.table;
            insertSqlAtCursor(
              'SELECT ' + details.name + ' FROM ' + qualifiedFromName + ' LIMIT 100;',
              -1
            );
          } else {
            insertSqlAtCursor(details.name + ' ', 0);
          }
        }
      }
    );

    const insertAtCursorSub = huePubSub.subscribe(INSERT_AT_CURSOR_EVENT, details => {
      if (
        (details.targetEditor && details.targetEditor === editor) ||
        $el.data('last-active-editor')
      ) {
        insertSqlAtCursor(details.text + ' ', details.cursorEndAdjust || 0);
      }
    });

    disposeFunctions.push(() => {
      insertTableAtCursorSub.remove();
      insertColumnAtCursorSub.remove();
      insertAtCursorSub.remove();
    });

    const dblClickHdfsItemSub = huePubSub.subscribe('assist.dblClickHdfsItem', assistHdfsEntry => {
      if ($el.data('last-active-editor')) {
        editor.session.insert(editor.getCursorPosition(), "'" + assistHdfsEntry.path + "'");
      }
    });

    disposeFunctions.push(() => {
      dblClickHdfsItemSub.remove();
    });

    const dblClickAdlsItemSub = huePubSub.subscribe('assist.dblClickAdlsItem', assistHdfsEntry => {
      if ($el.data('last-active-editor')) {
        editor.session.insert(editor.getCursorPosition(), 'adl:/' + assistHdfsEntry.path + "'");
      }
    });

    disposeFunctions.push(() => {
      dblClickAdlsItemSub.remove();
    });

    const dblClickAbfsItemSub = huePubSub.subscribe('assist.dblClickAbfsItem', assistHdfsEntry => {
      if ($el.data('last-active-editor')) {
        editor.session.insert(editor.getCursorPosition(), 'abfs://' + assistHdfsEntry.path + "'");
      }
    });

    disposeFunctions.push(() => {
      dblClickAbfsItemSub.remove();
    });

    const dblClickGitItemSub = huePubSub.subscribe('assist.dblClickGitItem', assistGitEntry => {
      if ($el.data('last-active-editor')) {
        editor.session.setValue(assistGitEntry.fileContent());
      }
    });

    disposeFunctions.push(() => {
      dblClickGitItemSub.remove();
    });

    const dblClickS3ItemSub = huePubSub.subscribe('assist.dblClickS3Item', assistS3Entry => {
      if ($el.data('last-active-editor')) {
        editor.session.insert(editor.getCursorPosition(), "'S3A://" + assistS3Entry.path + "'");
      }
    });

    disposeFunctions.push(() => {
      dblClickS3ItemSub.remove();
    });

    const sampleErrorInsertSub = huePubSub.subscribe('sample.error.insert.click', popoverEntry => {
      const table = popoverEntry.identifierChain[popoverEntry.identifierChain.length - 1]['name'];
      const text = 'SELECT * FROM ' + table + ' LIMIT 100;';
      insertSqlAtCursor(text, -1);
    });

    disposeFunctions.push(() => {
      sampleErrorInsertSub.remove();
    });

    let autocompleteTemporarilyDisabled = false;
    let autocompleteThrottle = -1;
    const afterExecListener = editor.commands.on('afterExec', e => {
      if (editor.getOption('enableLiveAutocompletion') && e.command.name === 'insertstring') {
        if (/\S+\(\)$/.test(e.args)) {
          editor.moveCursorTo(
            editor.getCursorPosition().row,
            editor.getCursorPosition().column - 1
          );
          return;
        }
        window.clearTimeout(autocompleteThrottle);
        autocompleteThrottle = window.setTimeout(() => {
          const textBeforeCursor = editor.getTextBeforeCursor();
          const questionMarkMatch = textBeforeCursor.match(/select\s+(\? from \S+[^.]\s*$)/i);
          if (questionMarkMatch && $('.ace_autocomplete:visible').length === 0) {
            editor.moveCursorTo(
              editor.getCursorPosition().row,
              editor.getCursorPosition().column - (questionMarkMatch[1].length - 1)
            );
            editor.removeTextBeforeCursor(1);
            huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, snippet.id());
            window.setTimeout(() => {
              editor.execCommand('startAutocomplete');
            }, 1);
          } else if (/\.$/.test(textBeforeCursor)) {
            huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, snippet.id());
            window.setTimeout(() => {
              editor.execCommand('startAutocomplete');
            }, 1);
          }
        }, 400);
      }
      editor.session.getMode().$id = snippet.getAceMode(); // forces the id again because of Ace command internals
      // if it's pig and before it's LOAD ' we disable the autocomplete and show a filechooser btn
      if (editor.session.getMode().$id === 'ace/mode/pig' && e.args) {
        const textBefore = editor.getTextBeforeCursor();
        if (
          (e.args === "'" &&
            textBefore.toUpperCase().indexOf('LOAD ') > -1 &&
            textBefore.toUpperCase().indexOf('LOAD ') === textBefore.toUpperCase().length - 5) ||
          (textBefore.toUpperCase().indexOf("LOAD '") > -1 &&
            textBefore.toUpperCase().indexOf("LOAD '") === textBefore.toUpperCase().length - 6)
        ) {
          if (editor.getOption('enableBasicAutocompletion')) {
            editor.disableAutocomplete();
            autocompleteTemporarilyDisabled = true;
          }
          const btn = editor.showFileButton();
          btn.on('click', ie => {
            ie.preventDefault();
            // TODO: Turn the ace file chooser into a component and remove css class references
            const $aceFileChooseContent = $('.ace-filechooser-content');
            if (!$aceFileChooseContent.data('jHueFileChooser')) {
              if ($aceFileChooseContent.data('spinner') == null) {
                $aceFileChooseContent.data('spinner', $aceFileChooseContent.html());
              } else {
                $aceFileChooseContent.html($aceFileChooseContent.data('spinner'));
              }
              $aceFileChooseContent.jHueFileChooser({
                onFileChoose: function (filePath) {
                  editor.session.insert(editor.getCursorPosition(), filePath + "'");
                  editor.hideFileButton();
                  if (autocompleteTemporarilyDisabled) {
                    editor.enableAutocomplete();
                    autocompleteTemporarilyDisabled = false;
                  }
                  $('.ace-filechooser').hide();
                },
                selectFolder: false,
                createFolder: false
              });
            }
            $('.ace-filechooser')
              .css({
                top: $(ie.currentTarget).position().top,
                left: $(ie.currentTarget).position().left
              })
              .show();
          });
        } else {
          editor.hideFileButton();
          if (autocompleteTemporarilyDisabled) {
            editor.enableAutocomplete();
            autocompleteTemporarilyDisabled = false;
          }
        }
        if (
          e.args !== "'" &&
          textBefore.toUpperCase().indexOf("LOAD '") > -1 &&
          textBefore.toUpperCase().indexOf("LOAD '") === textBefore.toUpperCase().length - 6
        ) {
          editor.hideFileButton();
          if (autocompleteTemporarilyDisabled) {
            editor.enableAutocomplete();
            autocompleteTemporarilyDisabled = false;
          }
        }
      }
    });

    disposeFunctions.push(() => {
      editor.commands.off('afterExec', afterExecListener);
    });
    editor.$blockScrolling = Infinity;
    snippet.ace(editor);
  },

  update: function (element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    const snippet = options.snippet;
    const AceRange = ace.require('ace/range').Range;
    if (snippet.ace()) {
      const editor = snippet.ace();
      if (typeof options.readOnly !== 'undefined') {
        editor.setReadOnly(options.readOnly);
      }
      const range = options.highlightedRange ? options.highlightedRange() : null;
      editor.session.setMode(snippet.getAceMode());
      if (range && JSON.stringify(range.start) !== JSON.stringify(range.end)) {
        let conflictingWithErrorMarkers = false;
        if (editor.session.$backMarkers) {
          for (const marker in editor.session.$backMarkers) {
            if (editor.session.$backMarkers[marker].clazz === 'ace_error-line') {
              const errorRange = editor.session.$backMarkers[marker].range;
              if (range.start.row <= errorRange.end.row && range.end.row >= errorRange.start.row) {
                conflictingWithErrorMarkers = true;
              }
            }
            if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
              editor.session.removeMarker(editor.session.$backMarkers[marker].id);
            }
          }
        }
        if (!conflictingWithErrorMarkers) {
          const lineOffset = snippet.lastAceSelectionRowOffset();
          window.setTimeout(() => {
            editor.session.addMarker(
              new AceRange(
                range.start.row + lineOffset,
                range.start.column,
                range.end.row + lineOffset,
                range.end.column
              ),
              'highlighted',
              'line'
            );
            ace
              .require('ace/lib/dom')
              .importCssString(
                '.highlighted {\
                  background-color: #E3F7FF;\
                  position: absolute;\
              }'
              );
            editor.scrollToLine(range.start.row + lineOffset, true, true, () => {});
          }, 0);
        }
      }
      try {
        editor._emit('change');
      } catch (e) {}
    }
  }
});
