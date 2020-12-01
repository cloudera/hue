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
    <ace-autocomplete v-if="editor" :editor="editor" :editor-id="id" :executor="executor" />
  </div>
</template>

<script lang="ts">
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';
  import ace, { getAceMode } from 'ext/aceHelper';
  import { Ace } from 'ext/ace';

  import AceAutocomplete from './autocomplete/AceAutocomplete.vue';
  import AceGutterHandler from './AceGutterHandler';
  import AceLocationHandler from './AceLocationHandler';
  import Executor from 'apps/notebook2/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import { INSERT_AT_CURSOR_EVENT } from 'ko/bindings/ace/ko.aceEditor';
  import { CURSOR_POSITION_CHANGED_EVENT } from 'ko/bindings/ace/aceLocationHandler';
  import { IdentifierChainEntry, ParsedLocation } from 'parse/types';
  import { EditorInterpreter } from 'types/config';
  import { hueWindow } from 'types/types';
  import huePubSub from 'utils/huePubSub';
  import { defer } from 'utils/hueUtils';
  import I18n from 'utils/i18n';
  import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

  // Taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
  const UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/gi;

  const removeUnicodes = (value: string) => value.replace(UNICODES_TO_REMOVE, ' ');

  @Component({
    components: { AceAutocomplete },
    methods: { I18n }
  })
  export default class AceEditor extends Vue {
    @Prop({ required: false, default: '' })
    initialValue!: string;
    @Prop({ required: false })
    initialCursorPosition?: Ace.Position;
    @Prop()
    id!: string;
    @Prop()
    executor!: Executor;
    @Prop({ required: false, default: () => ({}) })
    aceOptions?: Ace.Options;

    subTracker = new SubscriptionTracker();
    editor: Ace.Editor | null = null;
    aceLocationHandler: AceLocationHandler | null = null;
    lastFocusedEditor = false;

    private isSqlDialect(): boolean {
      return (<EditorInterpreter>this.executor.connector()).is_sql;
    }

    mounted(): void {
      const editorElement = <HTMLElement>this.$refs['editorElement'];
      if (!editorElement) {
        return;
      }

      const height = localStorage.getItem('ace.editor.custom.height') || '128';
      (<HTMLElement>this.$el).style.height = height + 'px';

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

      const triggerChange = () => {
        this.$emit('value-changed', removeUnicodes(editor.getValue()));
      };

      editor.commands.addCommand({
        name: 'execute',
        bindKey: { win: 'Ctrl-Enter', mac: 'Command-Enter|Ctrl-Enter' },
        exec: async () => {
          if (this.aceLocationHandler) {
            this.aceLocationHandler.refreshStatementLocations();
          }
          if (this.editor && this.executor.activeExecutable) {
            triggerChange();
            await this.executor.activeExecutable.reset();
            await this.executor.activeExecutable.execute();
          }
        }
      });

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

      let placeholderVisible = false;
      const placeholderElement = this.createPlaceholderElement();
      const onInput = () => {
        if (!placeholderVisible) {
          if (!editor.getValue().length) {
            editor.renderer.scroller.append(placeholderElement);
            placeholderVisible = true;
          }
        } else {
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

      editor.on('change', triggerChange);
      editor.on('blur', triggerChange);
      editor.on('focus', onFocus);
      editor.on('paste', onPaste);
      editor.on('input', onInput);
      editor.on('mousedown', onMouseDown);

      this.subTracker.addDisposable({
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
      this.addInsertSubscribers();
      this.$emit('ace-created', editor);
    }

    createPlaceholderElement(): HTMLElement {
      const element = document.createElement('div');
      element.innerText = I18n('Example: SELECT * FROM tablename, or press CTRL + space');
      element.style.marginLeft = '6px';
      element.classList.add('ace_invisible');
      element.classList.add('ace_emptyMessage');
      return element;
    }

    cursorAtStartOfStatement(): boolean {
      return (
        !!this.editor &&
        (/^\s*$/.test(this.editor.getValue()) || /^.*;\s*$/.test(this.editor.getTextBeforeCursor()))
      );
    }

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
          const table = popoverEntry.identifierChain[popoverEntry.identifierChain.length - 1].name;
          this.insertSqlAtCursor(`SELECT * FROM ${table} LIMIT 100;`, -1);
        }
      );
    }

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
          const setElem = <HTMLInputElement>document.getElementById('setEnableLiveAutocompletion');
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
          if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
            size += 'px';
          }
          editor.setOption('fontSize', size);
          setInLocalStorage('hue.ace.fontSize', size);
        },
        getFontSize: (): string => {
          let size = <string>editor.getOption('fontSize');
          if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
            size += 'px';
          }
          return size;
        }
      };
    }

    configureEditorOptions(editor: Ace.Editor): void {
      const enableBasicAutocompletion = getFromLocalStorage(
        'hue.ace.enableBasicAutocompletion',
        true
      );

      const enableLiveAutocompletion =
        enableBasicAutocompletion && getFromLocalStorage('hue.ace.enableLiveAutocompletion', true);

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
        showGutter: false,
        showLineNumbers: false,
        showPrintMargin: false,
        scrollPastEnd: 0.1,
        minLines: 1,
        maxLines: 25,
        tabSize: 2,
        useSoftTabs: true,
        ...this.aceOptions
      };

      editor.setOptions(editorOptions);
    }

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
    }

    destroyed(): void {
      this.subTracker.dispose();
    }
  }

  export const COMPONENT_NAME = 'ace-editor';
  wrap(COMPONENT_NAME, AceEditor);
</script>

<style lang="scss" scoped>
  .ace-editor-component {
    height: 100%;

    .ace-editor {
      height: 100%;
    }
  }
</style>
