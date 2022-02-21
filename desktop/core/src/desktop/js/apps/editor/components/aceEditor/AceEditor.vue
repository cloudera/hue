<!--
  Licensed to Cloudera, Inc. under one
  or more contributor license agreements.  See the NOTICE file
  distributed with this work for additional information
  regarding copyright ownership.  Cloudera, Inc. licenses this file
  to you under the Apache License, Version 2.0 (the
  "License"); you may not use this file except in compliance
  with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->

<template>
  <div class="ace-editor-component">
    <div :id="id" ref="editorElement" class="ace-editor" />
    <ace-autocomplete
      v-if="editor && autocompleteParser"
      :autocomplete-parser="autocompleteParser"
      :sql-reference-provider="sqlReferenceProvider"
      :sql-analyzer-provider="sqlAnalyzerProvider"
      :editor="editor"
      :editor-id="id"
      :executor="executor"
    />
    <ace-syntax-dropdown v-if="editor" :editor="editor" :editor-id="id" />
  </div>
</template>

<script lang="ts">
  import { ActiveStatementChangedEventDetails } from 'apps/editor/components/aceEditor/types';
  import { defineComponent, onMounted, PropType, ref, toRefs } from 'vue';
  import ace, { getAceMode } from 'ext/aceHelper';
  import { Ace } from 'ext/ace';

  import { attachPredictTypeahead } from './acePredict';
  import AceSyntaxDropdown from './AceSyntaxDropdown.vue';
  import AceAutocomplete from './autocomplete/AceAutocomplete.vue';
  import AceGutterHandler from './AceGutterHandler';
  import AceLocationHandler, {
    ACTIVE_STATEMENT_CHANGED_EVENT,
    ActiveLocationHighlighting
  } from './AceLocationHandler';
  import { EXECUTE_ACTIVE_EXECUTABLE_TOPIC } from '../events';
  import { formatSql } from 'apps/editor/api';
  import Executor from 'apps/editor/execution/executor';
  import { SqlAnalyzerProvider } from 'catalog/analyzer/types';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import {
    AutocompleteParser,
    IdentifierChainEntry,
    ParsedLocation,
    SqlParserProvider
  } from 'parse/types';
  import { Connector, EditorInterpreter } from 'config/types';
  import { SqlReferenceProvider } from 'sql/reference/types';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';
  import defer from 'utils/timing/defer';
  import I18n from 'utils/i18n';
  import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

  // Taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
  const UNICODES_TO_REMOVE =
    /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/gi;

  const INSERT_AT_CURSOR_EVENT = 'editor.insert.at.cursor';
  const CURSOR_POSITION_CHANGED_EVENT = 'editor.cursor.position.changed';

  const removeUnicodes = (value: string) => value.replace(UNICODES_TO_REMOVE, ' ');

  export default defineComponent({
    name: 'AceEditor',
    components: {
      AceSyntaxDropdown,
      AceAutocomplete
    },
    props: {
      initialValue: {
        type: String,
        required: false,
        default: ''
      },
      initialCursorPosition: {
        type: Object as PropType<Ace.Position>,
        default: undefined
      },
      id: {
        type: String,
        required: true
      },
      executor: {
        type: Object as PropType<Executor>,
        required: true
      },
      activeLocationHighlighting: {
        type: String as () => ActiveLocationHighlighting,
        required: false,
        default: () => 'all'
      },
      aceOptions: {
        type: Object as PropType<Ace.Options>,
        required: false,
        default: () => ({})
      },
      sqlAnalyzerProvider: {
        type: Object as PropType<SqlAnalyzerProvider>,
        default: undefined
      },
      sqlParserProvider: {
        type: Object as PropType<SqlParserProvider>,
        default: undefined
      },
      sqlReferenceProvider: {
        type: Object as PropType<SqlReferenceProvider>,
        default: undefined
      }
    },
    emits: [
      'active-statement-changed',
      'value-changed',
      'create-new-doc',
      'save-doc',
      'toggle-presentation-mode',
      'ace-created',
      'cursor-changed'
    ],
    setup(props, { emit }) {
      const {
        id,
        sqlAnalyzerProvider,
        sqlReferenceProvider,
        executor,
        initialCursorPosition,
        activeLocationHighlighting,
        sqlParserProvider,
        initialValue,
        aceOptions
      } = toRefs(props);
      const subTracker = new SubscriptionTracker();
      const editorElement = ref<HTMLElement | null>(null);

      const editorRef = ref<Ace.Editor | null>(null);
      let lastFocusedEditor = false;
      const autocompleteParser = ref<AutocompleteParser | null>(null);

      const configureEditorOptions = (editor: Ace.Editor): void => {
        const enableBasicAutocompletion = getFromLocalStorage(
          'hue.ace.enableBasicAutocompletion',
          true
        );

        const enableLiveAutocompletion =
          enableBasicAutocompletion &&
          getFromLocalStorage('hue.ace.enableLiveAutocompletion', true);

        const editorOptions: Ace.Options = {
          enableBasicAutocompletion,
          enableLiveAutocompletion,
          fontSize: getFromLocalStorage(
            'hue.ace.fontSize',
            navigator.platform && navigator.platform.toLowerCase().indexOf('linux') > -1
              ? '14px'
              : '12px'
          ),
          enableSnippets: true,
          showGutter: true,
          showLineNumbers: true,
          showPrintMargin: false,
          scrollPastEnd: 0.1,
          minLines: 3,
          maxLines: 25,
          tabSize: 2,
          useSoftTabs: true,
          ...aceOptions.value
        };

        editor.setOptions(editorOptions);
      };

      const addCustomAceConfigOptions = (editor: Ace.Editor): void => {
        let darkThemeEnabled = getFromLocalStorage('ace.dark.theme.enabled', false);

        editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');

        editor.enabledMenuOptions = {
          setShowInvisibles: true,
          setTabSize: true,
          setShowGutter: true
        };

        editor.customMenuOptions = {
          setEnableDarkTheme: (enabled: boolean): void => {
            darkThemeEnabled = enabled;
            setInLocalStorage('ace.dark.theme.enabled', darkThemeEnabled);
            editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
          },
          getEnableDarkTheme: () => darkThemeEnabled,
          setEnableAutocompleter: (enabled: boolean): void => {
            editor.setOption('enableBasicAutocompletion', enabled);
            setInLocalStorage('hue.ace.enableBasicAutocompletion', enabled);
            const setElem = <HTMLInputElement>(
              document.getElementById('setEnableLiveAutocompletion')
            );
            if (setElem && ((enabled && !setElem.checked) || (!enabled && setElem.checked))) {
              setElem.click();
            }
          },
          getEnableAutocompleter: () => editor.getOption('enableBasicAutocompletion'),
          setEnableLiveAutocompletion: (enabled: boolean): void => {
            editor.setOption('enableLiveAutocompletion', enabled);
            setInLocalStorage('hue.ace.enableLiveAutocompletion', enabled);
            const setElem = <HTMLInputElement>document.getElementById('setEnableAutocompleter');
            if (setElem && enabled && !setElem.checked) {
              setElem.click();
            }
          },
          getEnableLiveAutocompletion: () => editor.getOption('enableLiveAutocompletion'),
          setFontSize: (size: string): void => {
            if (
              size.toLowerCase().indexOf('px') === -1 &&
              size.toLowerCase().indexOf('em') === -1
            ) {
              size += 'px';
            }
            editor.setOption('fontSize', size);
            setInLocalStorage('hue.ace.fontSize', size);
          },
          getFontSize: (): string => {
            let size = <string>editor.getOption('fontSize');
            if (
              size.toLowerCase().indexOf('px') === -1 &&
              size.toLowerCase().indexOf('em') === -1
            ) {
              size += 'px';
            }
            return size;
          }
        };
      };

      const registerEditorCommands = (
        editor: Ace.Editor,
        aceLocationHandler: AceLocationHandler,
        triggerChange: () => void
      ): void => {
        editor.commands.addCommand({
          name: 'execute',
          bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter|Ctrl-Enter' },
          exec: async () => {
            aceLocationHandler.refreshStatementLocations();
            if (editor && executor.value.activeExecutable) {
              triggerChange();
              huePubSub.publish(EXECUTE_ACTIVE_EXECUTABLE_TOPIC, executor.value.activeExecutable);
            }
          }
        });

        editor.commands.addCommand({
          name: 'switchTheme',
          bindKey: { win: 'Ctrl-Alt-t', mac: 'Command-Alt-t' },
          exec: () => {
            if (
              editor.customMenuOptions &&
              editor.customMenuOptions.getEnableDarkTheme &&
              editor.customMenuOptions.setEnableDarkTheme
            ) {
              const enabled = editor.customMenuOptions.getEnableDarkTheme();
              editor.customMenuOptions.setEnableDarkTheme(!enabled);
            }
          }
        });

        editor.commands.addCommand({
          name: 'new',
          bindKey: { win: 'Ctrl-e', mac: 'Command-e' },
          exec: () => {
            emit('create-new-doc');
          }
        });

        editor.commands.addCommand({
          name: 'save',
          bindKey: { win: 'Ctrl-s', mac: 'Command-s|Ctrl-s' },
          exec: () => {
            emit('save-doc');
          }
        });

        editor.commands.addCommand({
          name: 'togglePresentationMode',
          bindKey: { win: 'Ctrl-Shift-p', mac: 'Ctrl-Shift-p|Command-Shift-p' },
          exec: () => {
            emit('toggle-presentation-mode');
          }
        });

        editor.commands.addCommand({
          name: 'format',
          bindKey: {
            win: 'Ctrl-i|Ctrl-Shift-f|Ctrl-Alt-l',
            mac: 'Command-i|Ctrl-i|Ctrl-Shift-f|Command-Shift-f|Ctrl-Shift-l|Cmd-Shift-l'
          },
          exec: async () => {
            editor.setReadOnly(true);
            try {
              if (editor.getSelectedText()) {
                const selectionRange = editor.getSelectionRange();
                const formatted = await formatSql({
                  statements: editor.getSelectedText(),
                  silenceErrors: true
                });
                editor.getSession().replace(selectionRange, formatted);
              } else {
                const formatted = await formatSql({
                  statements: editor.getValue(),
                  silenceErrors: true
                });
                editor.setValue(formatted, 1);
              }
              triggerChange();
            } catch (e) {}
            editor.setReadOnly(false);
          }
        });

        editor.commands.bindKey('Ctrl-P', 'golineup');
        editor.commands.bindKey({ win: 'Ctrl-j', mac: 'Command-j|Ctrl-j' }, 'gotoline');
      };

      const addInsertSubscribers = (editor: Ace.Editor): void => {
        const cursorAtStartOfStatement = (): boolean => {
          return /^\s*$/.test(editor.getValue()) || /^.*;\s*$/.test(editor.getTextBeforeCursor());
        };

        const insertSqlAtCursor = (text: string, cursorEndAdjust?: number): void => {
          const before = editor.getTextBeforeCursor();

          const textToInsert = /\S+$/.test(before) ? ' ' + text : text;
          editor.session.insert(editor.getCursorPosition(), textToInsert);
          if (cursorEndAdjust) {
            const positionAfterInsert = editor.getCursorPosition();
            editor.moveCursorToPosition({
              row: positionAfterInsert.row,
              column: positionAfterInsert.column + cursorEndAdjust
            });
          }
          editor.clearSelection();
          editor.focus();
        };

        subTracker.subscribe(
          INSERT_AT_CURSOR_EVENT,
          (details: { text: string; targetEditor: Ace.Editor; cursorEndAdjust?: number }): void => {
            if (details.targetEditor === editor || lastFocusedEditor) {
              insertSqlAtCursor(details.text, details.cursorEndAdjust);
            }
          }
        );

        subTracker.subscribe(
          'editor.insert.table.at.cursor',
          (details: { name: string; database: string }) => {
            if (!lastFocusedEditor) {
              return;
            }
            const qualifiedName =
              executor.value.database() === details.database
                ? details.name
                : `${details.database}.${details.name}`;
            if (cursorAtStartOfStatement()) {
              insertSqlAtCursor(`SELECT * FROM ${qualifiedName} LIMIT 100;`, -1);
            } else {
              insertSqlAtCursor(`${qualifiedName} `);
            }
          }
        );

        subTracker.subscribe(
          'editor.insert.column.at.cursor',
          (details: { name: string; table: string; database: string }): void => {
            if (!lastFocusedEditor) {
              return;
            }
            if (cursorAtStartOfStatement()) {
              const qualifiedFromName =
                executor.value.database() === details.database
                  ? details.table
                  : details.database + '.' + details.table;
              insertSqlAtCursor(`SELECT ${details.name} FROM ${qualifiedFromName} LIMIT 100;`, -1);
            }
          }
        );

        subTracker.subscribe(
          'sample.error.insert.click',
          (popoverEntry: { identifierChain: IdentifierChainEntry[] }): void => {
            if (!lastFocusedEditor || !popoverEntry.identifierChain.length) {
              return;
            }
            const table =
              popoverEntry.identifierChain[popoverEntry.identifierChain.length - 1].name;
            insertSqlAtCursor(`SELECT * FROM ${table} LIMIT 100;`, -1);
          }
        );
      };

      if (sqlParserProvider.value) {
        sqlParserProvider.value
          .getAutocompleteParser(executor.value.connector().dialect || 'generic')
          .then(parser => {
            autocompleteParser.value = parser;
          });
      }

      onMounted(() => {
        const element = editorElement.value;
        if (!element) {
          return;
        }

        element.textContent = initialValue.value;

        const editor = <Ace.Editor>ace.edit(element);

        configureEditorOptions(editor);
        addCustomAceConfigOptions(editor);

        const aceLocationHandler = new AceLocationHandler({
          editor,
          editorId: id.value,
          executor: executor.value as Executor,
          activeLocationHighlighting: activeLocationHighlighting.value,
          sqlReferenceProvider: sqlReferenceProvider.value
        });
        subTracker.addDisposable(aceLocationHandler);

        editor.$blockScrolling = Infinity;

        const aceGutterHandler = new AceGutterHandler({
          editor,
          editorId: id.value,
          executor: executor.value as Executor
        });
        subTracker.addDisposable(aceGutterHandler);

        editor.session.setMode(getAceMode(executor.value.connector().dialect));

        if ((<hueWindow>window).ENABLE_SQL_SYNTAX_CHECK && window.Worker) {
          let errorHighlightingEnabled = getFromLocalStorage(
            'hue.ace.errorHighlightingEnabled',
            true
          );

          if (errorHighlightingEnabled) {
            aceLocationHandler.attachSqlSyntaxWorker();
          }

          editor.customMenuOptions.setErrorHighlighting = (enabled: boolean) => {
            errorHighlightingEnabled = enabled;
            setInLocalStorage('hue.ace.errorHighlightingEnabled', enabled);
            if (enabled) {
              aceLocationHandler.attachSqlSyntaxWorker();
            } else {
              aceLocationHandler.detachSqlSyntaxWorker();
            }
          };
          editor.customMenuOptions.getErrorHighlighting = () => errorHighlightingEnabled;
          editor.customMenuOptions.setClearIgnoredSyntaxChecks = () => {
            setInLocalStorage('hue.syntax.checker.suppressedRules', {});
            const el = document.getElementById('setClearIgnoredSyntaxChecks');
            if (!el || !el.parentNode) {
              return;
            }
            el.style.display = 'none';
            const doneElem = document.createElement('div');
            doneElem.style.marginTop = '5px';
            doneElem.style.float = 'right';
            doneElem.innerText = 'done';
            el.insertAdjacentElement('beforebegin', doneElem);
          };
          editor.customMenuOptions.getClearIgnoredSyntaxChecks = () => false;
        }

        const AceAutocomplete = ace.require('ace/autocomplete').Autocomplete;

        if (!editor.completer) {
          editor.completer = new AceAutocomplete();
        }

        const isSqlDialect = (<EditorInterpreter>executor.value.connector()).is_sql;

        editor.completer.exactMatch = !isSqlDialect;

        const langTools = ace.require('ace/ext/language_tools');
        langTools.textCompleter.setSqlMode(isSqlDialect);

        if (editor.completers) {
          editor.completers.length = 0;
          if (isSqlDialect) {
            editor.useHueAutocompleter = true;
          } else {
            editor.completers.push(langTools.snippetCompleter);
            editor.completers.push(langTools.textCompleter);
            editor.completers.push(langTools.keyWordCompleter);
          }
        }

        const onFocus = (): void => {
          huePubSub.publish('ace.editor.focused', editor);

          // TODO: Figure out why this is needed
          if (editor.session.$backMarkers) {
            for (const marker in editor.session.$backMarkers) {
              if (editor.session.$backMarkers[marker].clazz === 'highlighted') {
                editor.session.removeMarker(editor.session.$backMarkers[marker].id);
              }
            }
          }
        };

        const onPaste = (e: { text: string }): void => {
          e.text = removeUnicodes(e.text);
        };

        const connector: Connector = executor.value.connector();
        if (sqlAnalyzerProvider.value && connector.optimizer === 'api') {
          try {
            attachPredictTypeahead(editor, connector, sqlAnalyzerProvider.value);
          } catch (e) {
            console.warn('Failed attaching predict typeahead...');
            console.error(e);
          }
        }

        let placeholderVisible = false;

        const createPlaceholderElement = (): HTMLElement => {
          const element = document.createElement('div');
          if (connector.dialect === 'hplsql') {
            element.innerText = I18n(
              'Example: CREATE PROCEDURE name AS SELECT * FROM tablename limit 10 GO'
            );
          } else {
            element.innerText = I18n('Example: SELECT * FROM tablename, or press CTRL + space');
          }
          element.style.marginLeft = '6px';
          element.classList.add('ace_invisible');
          element.classList.add('ace_emptyMessage');
          return element;
        };

        const placeholderElement = createPlaceholderElement();
        const onInput = () => {
          if (!placeholderVisible && !editor.getValue().length) {
            editor.renderer.scroller.append(placeholderElement);
            placeholderVisible = true;
          } else if (placeholderVisible) {
            placeholderElement.remove();
            placeholderVisible = false;
          }
        };

        onInput();

        const onMouseDown = (e: { domEvent: MouseEvent; $pos?: Ace.Position }): void => {
          if (e.domEvent.button === 1) {
            // middle click
            const position = e.$pos;
            if (!position) {
              return;
            }
            const tempText = editor.getSelectedText();
            editor.session.insert(position, tempText);
            defer(() => {
              editor.moveCursorTo(position.row, position.column + tempText.length);
            });
          }
        };

        const triggerChange = (): void => {
          emit('value-changed', removeUnicodes(editor.getValue()));
        };

        editor.on('change', triggerChange);
        editor.on('blur', triggerChange);
        editor.on('focus', onFocus);
        editor.on('paste', onPaste);
        editor.on('input', onInput);
        editor.on('mousedown', onMouseDown);

        subTracker.addDisposable({
          dispose: () => {
            editor.off('change', triggerChange);
            editor.off('blur', triggerChange);
            editor.off('focus', onFocus);
            editor.off('paster', onPaste);
            editor.off('input', onInput);
            editor.off('mousedown', onMouseDown);
          }
        });

        const resizeAce = () => {
          defer(() => {
            try {
              editor.resize(true);
            } catch (e) {
              // Can happen when the editor hasn't been initialized
            }
          });
        };

        subTracker.subscribe('ace.editor.focused', (focusedEditor: Ace.Editor): void => {
          lastFocusedEditor = editor === focusedEditor;
        });

        subTracker.subscribe('assist.set.manual.visibility', resizeAce);
        subTracker.subscribe('split.panel.resized', resizeAce);

        subTracker.subscribe(
          'ace.replace',
          (data: { text: string; location: ParsedLocation }): void => {
            const Range = ace.require('ace/range').Range;
            const range = new Range(
              data.location.first_line - 1,
              data.location.first_column - 1,
              data.location.last_line - 1,
              data.location.last_column - 1
            );
            editor.getSession().getDocument().replace(range, data.text);
          }
        );

        if (initialCursorPosition.value) {
          editor.moveCursorToPosition(initialCursorPosition.value);
          editor.renderer.scrollCursorIntoView();
        }

        registerEditorCommands(editor, aceLocationHandler, triggerChange);
        addInsertSubscribers(editor);
        editorRef.value = editor;
        emit('ace-created', editor);
      });

      subTracker.subscribe(
        CURSOR_POSITION_CHANGED_EVENT,
        (event: { editorId: string; position: Ace.Position }) => {
          if (event.editorId === id.value) {
            emit('cursor-changed', event.position);
          }
        }
      );

      subTracker.subscribe(
        ACTIVE_STATEMENT_CHANGED_EVENT,
        (details: ActiveStatementChangedEventDetails) => {
          if (id.value === details.id) {
            emit('active-statement-changed', details);
          }
        }
      );

      return { autocompleteParser, editorElement, subTracker, editor: editorRef, I18n };
    }
  });
</script>

<style lang="scss">
  @import './AceEditor.scss';
</style>
