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
    <div :id="id" class="ace-editor" />
    <ace-autocomplete v-if="editor" :editor="editor" :editor-id="id" :executor="executor" />
  </div>
</template>

<script lang="ts">
  import { INSERT_AT_CURSOR_EVENT } from 'ko/bindings/ace/ko.aceEditor';
  import { IdentifierChainEntry } from 'parse/types';
  import huePubSub from 'utils/huePubSub';
  import AceAutocomplete from './autocomplete/AceAutocomplete.vue';
  import $ from 'jquery';
  import { EditorInterpreter } from 'types/config';
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop } from 'vue-property-decorator';
  import { wrap } from 'vue/webComponentWrapper';
  import { Ace } from 'ext/ace';

  import apiHelper from 'api/apiHelper';
  import AceGutterHandler from 'ko/bindings/ace/aceGutterHandler';
  import { hueWindow } from 'types/types';
  import ace, { getAceMode } from 'ext/aceHelper';

  import Executor from 'apps/notebook2/execution/executor';
  import SubscriptionTracker from 'components/utils/SubscriptionTracker';
  import AceLocationHandler from './AceLocationHandler';
  import { defer } from 'utils/hueUtils';
  import I18n from 'utils/i18n';

  //taken from https://www.cs.tut.fi/~jkorpela/chars/spaces.html
  const UNICODES_TO_REMOVE = /[\u1680\u180E\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200A\u200B\u202F\u205F\u3000\uFEFF]/gi;

  const removeUnicodes = (value: string) => value.replace(UNICODES_TO_REMOVE, ' ');

  @Component({
    components: { AceAutocomplete },
    methods: { I18n }
  })
  export default class AceEditor extends Vue {
    @Prop()
    initialValue!: string;
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
      const editorElement = this.$el.querySelector('.ace-editor');
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
        let errorHighlightingEnabled = apiHelper.getFromTotalStorage(
          'hue.ace',
          'errorHighlightingEnabled',
          true
        );

        if (errorHighlightingEnabled) {
          this.aceLocationHandler.attachSqlSyntaxWorker();
        }

        editor.customMenuOptions.setErrorHighlighting = (enabled: boolean) => {
          errorHighlightingEnabled = enabled;
          apiHelper.setInTotalStorage('hue.ace', 'errorHighlightingEnabled', enabled);
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
          apiHelper.setInTotalStorage('hue.syntax.checker', 'suppressedRules', {});
          $('#setClearIgnoredSyntaxChecks')
            .hide()
            .before('<div style="margin-top:5px;float:right;">done</div>');
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

      // const processErrorsAndWarnings = (
      //   type: string,
      //   list: { line: number; message: string; col: number | null }[]
      // ): void => {
      //   editor.clearErrorsAndWarnings(type);
      //   let offset = 0;
      //   if ((<EditorInterpreter>this.executor.connector()).is_sql && editor.getSelectedText()) {
      //     const selectionRange = editor.getSelectionRange();
      //     offset = Math.min(selectionRange.start.row, selectionRange.end.row);
      //   }
      //   if (list.length > 0) {
      //     list.forEach((item, cnt) => {
      //       if (item.line !== null) {
      //         if (type === 'error') {
      //           editor.addError(item.message, item.line + offset);
      //         } else {
      //           editor.addWarning(item.message, item.line + offset);
      //         }
      //         if (cnt === 0) {
      //           editor.scrollToLine(item.line + offset, true, true, () => {
      //             /* empty */
      //           });
      //           if (item.col !== null) {
      //             editor.renderer.scrollCursorIntoView(
      //               { row: item.line + offset, column: item.col + 10 },
      //               0.5
      //             );
      //           }
      //         }
      //       }
      //     });
      //   }
      // };

      // const errorsSub = snippet.errors.subscribe(newErrors => {
      //   processErrorsAndWarnings('error', newErrors);
      // });
      //
      // const aceWarningsSub = snippet.aceWarnings.subscribe(newWarnings => {
      //   processErrorsAndWarnings('warning', newWarnings);
      // });
      //
      // const aceErrorsSub = snippet.aceErrors.subscribe(newErrors => {
      //   processErrorsAndWarnings('error', newErrors);
      // });

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

      editor.on('change', triggerChange);
      editor.on('blur', triggerChange);
      editor.on('focus', onFocus);

      this.subTracker.addDisposable({
        dispose: () => {
          editor.off('change', triggerChange);
          editor.off('blur', triggerChange);
          editor.off('focus', onFocus);
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

      this.editor = editor;
      this.addInsertSubscribers();
      this.$emit('ace-created', editor);
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
      let darkThemeEnabled = apiHelper.getFromTotalStorage('ace', 'dark.theme.enabled', false);

      editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');

      editor.enabledMenuOptions = {
        setShowInvisibles: true,
        setTabSize: true,
        setShowGutter: true
      };

      editor.customMenuOptions = {
        setEnableDarkTheme: (enabled: boolean): void => {
          darkThemeEnabled = enabled;
          apiHelper.setInTotalStorage('ace', 'dark.theme.enabled', darkThemeEnabled);
          editor.setTheme(darkThemeEnabled ? 'ace/theme/hue_dark' : 'ace/theme/hue');
        },
        getEnableDarkTheme: () => darkThemeEnabled,
        setEnableAutocompleter: (enabled: boolean): void => {
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
        getEnableAutocompleter: () => editor.getOption('enableBasicAutocompletion'),
        setEnableLiveAutocompletion: (enabled: boolean): void => {
          editor.setOption('enableLiveAutocompletion', enabled);
          apiHelper.setInTotalStorage('hue.ace', 'enableLiveAutocompletion', enabled);
          if (enabled && $('#setEnableAutocompleter:checked').length === 0) {
            $('#setEnableAutocompleter').trigger('click');
          }
        },
        getEnableLiveAutocompletion: () => editor.getOption('enableLiveAutocompletion'),
        setFontSize: (size: string): void => {
          if (size.toLowerCase().indexOf('px') === -1 && size.toLowerCase().indexOf('em') === -1) {
            size += 'px';
          }
          editor.setOption('fontSize', size);
          apiHelper.setInTotalStorage('hue.ace', 'fontSize', size);
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
      const enableBasicAutocompletion = apiHelper.getFromTotalStorage(
        'hue.ace',
        'enableBasicAutocompletion',
        true
      );

      const enableLiveAutocompletion =
        enableBasicAutocompletion &&
        apiHelper.getFromTotalStorage('hue.ace', 'enableLiveAutocompletion', true);

      const editorOptions: Ace.Options = {
        enableBasicAutocompletion,
        enableLiveAutocompletion,
        fontSize: apiHelper.getFromTotalStorage(
          'hue.ace',
          'fontSize',
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
