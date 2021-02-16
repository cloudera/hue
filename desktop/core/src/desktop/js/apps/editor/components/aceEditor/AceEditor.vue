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
      :editor="editor"
      :editor-id="id"
      :executor="executor"
    />
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue';

  import ace, { getAceMode } from 'ext/aceHelper';
  import { Ace } from 'ext/ace';

  import { attachPredictTypeahead } from './acePredict';
  import AceAutocomplete from './autocomplete/AceAutocomplete.vue';
  import AceGutterHandler from './AceGutterHandler';
  import AceLocationHandler from './AceLocationHandler';
  import { formatSql } from 'apps/editor/api';
  import Executor from 'apps/editor/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import {
    AutocompleteParser,
    IdentifierChainEntry,
    ParsedLocation,
    SqlParserProvider
  } from 'parse/types';
  import { EditorInterpreter } from 'types/config';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';
  import { defer } from 'utils/hueUtils';
  import I18n from 'utils/i18n';
  import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
  import { SqlReferenceProvider } from 'sql/reference/types';

  // Taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
  const UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/gi;

  const INSERT_AT_CURSOR_EVENT = 'editor.insert.at.cursor';
  const CURSOR_POSITION_CHANGED_EVENT = 'editor.cursor.position.changed';

  const removeUnicodes = (value: string) => value.replace(UNICODES_TO_REMOVE, ' ');

  export default defineComponent({
    components: {
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
      aceOptions: {
        type: Object as PropType<Ace.Options>,
        required: false,
        default: () => ({})
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
      'value-changed',
      'create-new-doc',
      'save-doc',
      'toggle-presentation-mode',
      'ace-created',
      'cursor-changed'
    ],
    setup() {
      const subTracker = new SubscriptionTracker();
      return { subTracker };
    },
    data() {
      return {
        editor: null as Ace.Editor | null,
        autocompleteParser: null as AutocompleteParser | null,
        aceLocationHandler: null as AceLocationHandler | null,
        lastFocusedEditor: false
      };
    },
    mounted(): void {
      const editorElement = <HTMLElement>this.$refs['editorElement'];
      if (!editorElement) {
        return;
      }

      if (this.sqlParserProvider) {
        this.sqlParserProvider
          .getAutocompleteParser(this.executor.connector().dialect || 'generic')
          .then(autocompleteParser => {
            this.autocompleteParser = autocompleteParser;
          });
      }

      editorElement.textContent = this.initialValue;
      const editor = <Ace.Editor>ace.edit(editorElement);

      this.configureEditorOptions(editor);
      this.addCustomAceConfigOptions(editor);

      editor.$blockScrolling = Infinity;

      this.aceLocationHandler = new AceLocationHandler({
        editor: editor,
        editorId: this.id,
        executor: this.executor
      });
      this.subTracker.addDisposable(this.aceLocationHandler);

      const aceGutterHandler = new AceGutterHandler({
        editor: editor,
        editorId: this.id,
        executor: this.executor
      });
      this.subTracker.addDisposable(aceGutterHandler);

      editor.session.setMode(getAceMode(this.executor.connector().dialect));

      if ((<hueWindow>window).ENABLE_SQL_SYNTAX_CHECK && window.Worker) {
        let errorHighlightingEnabled = getFromLocalStorage(
          'hue.ace.errorHighlightingEnabled',
          true
        );

        if (errorHighlightingEnabled) {
          this.aceLocationHandler.attachSqlSyntaxWorker();
        }

        editor.customMenuOptions.setErrorHighlighting = (enabled: boolean) => {
          errorHighlightingEnabled = enabled;
          setInLocalStorage('hue.ace.errorHighlightingEnabled', enabled);
          if (this.aceLocationHandler) {
            if (enabled) {
              this.aceLocationHandler.attachSqlSyntaxWorker();
            } else {
              this.aceLocationHandler.detachSqlSyntaxWorker();
            }
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
      editor.completer.exactMatch = !this.isSqlDialect();

      const langTools = ace.require('ace/ext/language_tools');
      langTools.textCompleter.setSqlMode(this.isSqlDialect());

      if (editor.completers) {
        editor.completers.length = 0;
        if (this.isSqlDialect()) {
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

      if ((<hueWindow>window).ENABLE_PREDICT) {
        attachPredictTypeahead(editor, this.executor.connector());
      }

      let placeholderVisible = false;
      const placeholderElement = this.createPlaceholderElement();
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

      const boundTriggerChange = this.triggerChange.bind(this);
      editor.on('change', boundTriggerChange);
      editor.on('blur', boundTriggerChange);
      editor.on('focus', onFocus);
      editor.on('paste', onPaste);
      editor.on('input', onInput);
      editor.on('mousedown', onMouseDown);

      this.subTracker.addDisposable({
        dispose: () => {
          editor.off('change', boundTriggerChange);
          editor.off('blur', boundTriggerChange);
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

      this.subTracker.subscribe('ace.editor.focused', (editor: Ace.Editor): void => {
        this.lastFocusedEditor = editor === this.editor;
      });

      this.subTracker.subscribe('assist.set.manual.visibility', resizeAce);
      this.subTracker.subscribe('split.panel.resized', resizeAce);

      this.subTracker.subscribe(
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

      if (this.initialCursorPosition) {
        editor.moveCursorToPosition(this.initialCursorPosition);
        editor.renderer.scrollCursorIntoView();
      }

      this.subTracker.subscribe(
        CURSOR_POSITION_CHANGED_EVENT,
        (event: { editorId: string; position: Ace.Position }) => {
          if (event.editorId === this.id) {
            this.$emit('cursor-changed', event.position);
          }
        }
      );

      this.editor = editor;
      this.registerEditorCommands();
      this.addInsertSubscribers();
      this.$emit('ace-created', editor);
    },

    unmounted(): void {
      this.subTracker.dispose();
    },

    methods: {
      I18n,

      isSqlDialect(): boolean {
        return (<EditorInterpreter>this.executor.connector()).is_sql;
      },

      createPlaceholderElement(): HTMLElement {
        const element = document.createElement('div');
        element.innerText = I18n('Example: SELECT * FROM tablename, or press CTRL + space');
        element.style.marginLeft = '6px';
        element.classList.add('ace_invisible');
        element.classList.add('ace_emptyMessage');
        return element;
      },

      cursorAtStartOfStatement(): boolean {
        return (
          !!this.editor &&
          (/^\s*$/.test(this.editor.getValue()) ||
            /^.*;\s*$/.test(this.editor.getTextBeforeCursor()))
        );
      },

      addInsertSubscribers(): void {
        this.subTracker.subscribe(
          INSERT_AT_CURSOR_EVENT,
          (details: { text: string; targetEditor: Ace.Editor; cursorEndAdjust?: number }): void => {
            if (details.targetEditor === this.editor || this.lastFocusedEditor) {
              this.insertSqlAtCursor(details.text, details.cursorEndAdjust);
            }
          }
        );

        this.subTracker.subscribe(
          'editor.insert.table.at.cursor',
          (details: { name: string; database: string }) => {
            if (!this.lastFocusedEditor) {
              return;
            }
            const qualifiedName =
              this.executor.database() === details.database
                ? details.name
                : `${details.database}.${details.name}`;
            if (this.cursorAtStartOfStatement()) {
              this.insertSqlAtCursor(`SELECT * FROM ${qualifiedName} LIMIT 100;`, -1);
            } else {
              this.insertSqlAtCursor(`${qualifiedName} `);
            }
          }
        );

        this.subTracker.subscribe(
          'editor.insert.column.at.cursor',
          (details: { name: string; table: string; database: string }): void => {
            if (!this.lastFocusedEditor) {
              return;
            }
            if (this.cursorAtStartOfStatement()) {
              const qualifiedFromName =
                this.executor.database() === details.database
                  ? details.table
                  : details.database + '.' + details.table;
              this.insertSqlAtCursor(
                `SELECT ${details.name} FROM ${qualifiedFromName} LIMIT 100;`,
                -1
              );
            }
          }
        );

        this.subTracker.subscribe(
          'sample.error.insert.click',
          (popoverEntry: { identifierChain: IdentifierChainEntry[] }): void => {
            if (!this.lastFocusedEditor || !popoverEntry.identifierChain.length) {
              return;
            }
            const table =
              popoverEntry.identifierChain[popoverEntry.identifierChain.length - 1].name;
            this.insertSqlAtCursor(`SELECT * FROM ${table} LIMIT 100;`, -1);
          }
        );
      },

      addCustomAceConfigOptions(editor: Ace.Editor): void {
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
      },

      configureEditorOptions(editor: Ace.Editor): void {
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
          ...this.aceOptions
        };

        editor.setOptions(editorOptions);
      },

      insertSqlAtCursor(text: string, cursorEndAdjust?: number): void {
        if (!this.editor) {
          return;
        }

        const before = this.editor.getTextBeforeCursor();

        const textToInsert = /\S+$/.test(before) ? ' ' + text : text;
        this.editor.session.insert(this.editor.getCursorPosition(), textToInsert);
        if (cursorEndAdjust) {
          const positionAfterInsert = this.editor.getCursorPosition();
          this.editor.moveCursorToPosition({
            row: positionAfterInsert.row,
            column: positionAfterInsert.column + cursorEndAdjust
          });
        }
        this.editor.clearSelection();
        this.editor.focus();
      },

      triggerChange(): void {
        if (this.editor) {
          this.$emit('value-changed', removeUnicodes(this.editor.getValue()));
        }
      },

      registerEditorCommands(): void {
        if (!this.editor) {
          return;
        }

        this.editor.commands.addCommand({
          name: 'execute',
          bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter|Ctrl-Enter' },
          exec: async () => {
            if (this.aceLocationHandler) {
              this.aceLocationHandler.refreshStatementLocations();
            }
            if (this.editor && this.executor.activeExecutable) {
              this.triggerChange();
              await this.executor.activeExecutable.reset();
              await this.executor.activeExecutable.execute();
            }
          }
        });

        this.editor.commands.addCommand({
          name: 'switchTheme',
          bindKey: { win: 'Ctrl-Alt-t', mac: 'Command-Alt-t' },
          exec: () => {
            if (
              this.editor &&
              this.editor.customMenuOptions &&
              this.editor.customMenuOptions.getEnableDarkTheme &&
              this.editor.customMenuOptions.setEnableDarkTheme
            ) {
              const enabled = this.editor.customMenuOptions.getEnableDarkTheme();
              this.editor.customMenuOptions.setEnableDarkTheme(!enabled);
            }
          }
        });

        this.editor.commands.addCommand({
          name: 'new',
          bindKey: { win: 'Ctrl-e', mac: 'Command-e' },
          exec: () => {
            this.$emit('create-new-doc');
          }
        });

        this.editor.commands.addCommand({
          name: 'save',
          bindKey: { win: 'Ctrl-s', mac: 'Command-s|Ctrl-s' },
          exec: () => {
            this.$emit('save-doc');
          }
        });

        this.editor.commands.addCommand({
          name: 'togglePresentationMode',
          bindKey: { win: 'Ctrl-Shift-p', mac: 'Ctrl-Shift-p|Command-Shift-p' },
          exec: () => {
            this.$emit('toggle-presentation-mode');
          }
        });

        this.editor.commands.addCommand({
          name: 'format',
          bindKey: {
            win: 'Ctrl-i|Ctrl-Shift-f|Ctrl-Alt-l',
            mac: 'Command-i|Ctrl-i|Ctrl-Shift-f|Command-Shift-f|Ctrl-Shift-l|Cmd-Shift-l'
          },
          exec: async () => {
            if (this.editor) {
              this.editor.setReadOnly(true);
              try {
                if (this.editor.getSelectedText()) {
                  const selectionRange = this.editor.getSelectionRange();
                  const formatted = await formatSql({
                    statements: this.editor.getSelectedText(),
                    silenceErrors: true
                  });
                  this.editor.getSession().replace(selectionRange, formatted);
                } else {
                  const formatted = await formatSql({
                    statements: this.editor.getValue(),
                    silenceErrors: true
                  });
                  this.editor.setValue(formatted, 1);
                }
                this.triggerChange();
              } catch (e) {}
              this.editor.setReadOnly(false);
            }
          }
        });

        this.editor.commands.bindKey('Ctrl-P', 'golineup');
        this.editor.commands.bindKey({ win: 'Ctrl-j', mac: 'Command-j|Ctrl-j' }, 'gotoline');
      }
    }
  });
</script>

<style lang="scss">
  @import './AceEditor.scss';
</style>
