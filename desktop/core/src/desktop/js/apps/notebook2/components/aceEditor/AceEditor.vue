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
  <div>
    <div :id="id" class="ace-editor" />
    <ace-autocomplete v-if="editor" :editor="editor" :editor-id="id" :executor="executor" />
  </div>
</template>

<script lang="ts">
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

  @Component({
    components: { AceAutocomplete },
    methods: { I18n }
  })
  export default class AceEditor extends Vue {
    @Prop()
    value!: string;
    @Prop()
    id!: string;
    @Prop()
    executor!: Executor;
    @Prop({ required: false, default: () => ({}) })
    aceOptions?: Ace.Options;

    subTracker = new SubscriptionTracker();
    editor: Ace.Editor | null = null;

    private isSqlDialect(): boolean {
      return (<EditorInterpreter>this.executor.connector()).is_sql;
    }

    mounted(): void {
      const editorElement = this.$el.querySelector('.ace-editor');
      if (!editorElement) {
        return;
      }
      editorElement.textContent = this.value;
      const editor = <Ace.Editor>ace.edit(editorElement);

      const resizeAce = () => {
        defer(() => {
          try {
            editor.resize(true);
          } catch (e) {
            // Can happen when the editor hasn't been initialized
          }
        });
      };

      this.subTracker.subscribe('assist.set.manual.visibility', resizeAce);
      this.subTracker.subscribe('split.panel.resized', resizeAce);

      const aceLocationHandler = new AceLocationHandler({
        editor: editor,
        editorId: this.id,
        executor: this.executor
      });
      this.subTracker.addDisposable(aceLocationHandler);

      const aceGutterHandler = new AceGutterHandler({
        editor: editor,
        editorId: this.id,
        executor: this.executor
      });
      this.subTracker.addDisposable(aceGutterHandler);

      editor.session.setMode(getAceMode(this.executor.connector().dialect));

      editor.setOptions({
        fontSize: apiHelper.getFromTotalStorage(
          'hue.ace',
          'fontSize',
          navigator.platform && navigator.platform.toLowerCase().indexOf('linux') > -1
            ? '14px'
            : '12px'
        )
      });

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

      if ((<hueWindow>window).ENABLE_SQL_SYNTAX_CHECK && window.Worker) {
        let errorHighlightingEnabled = apiHelper.getFromTotalStorage(
          'hue.ace',
          'errorHighlightingEnabled',
          true
        );

        if (errorHighlightingEnabled) {
          aceLocationHandler.attachSqlSyntaxWorker();
        }

        editor.customMenuOptions.setErrorHighlighting = (enabled: boolean) => {
          errorHighlightingEnabled = enabled;
          apiHelper.setInTotalStorage('hue.ace', 'errorHighlightingEnabled', enabled);
          if (enabled) {
            aceLocationHandler.attachSqlSyntaxWorker();
          } else {
            aceLocationHandler.detachSqlSyntaxWorker();
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

      const enableBasicAutocompletion = apiHelper.getFromTotalStorage(
        'hue.ace',
        'enableBasicAutocompletion',
        true
      );

      const editorOptions: Ace.Options = {
        enableBasicAutocompletion,
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

      if (enableBasicAutocompletion) {
        editorOptions.enableLiveAutocompletion = apiHelper.getFromTotalStorage(
          'hue.ace',
          'enableLiveAutocompletion',
          true
        );
      }

      editor.setOptions(editorOptions);

      const AceAutocomplete = ace.require('ace/autocomplete').Autocomplete;

      if (!editor.completer) {
        editor.completer = new AceAutocomplete();
      }
      editor.completer.exactMatch = !this.isSqlDialect();

      const initAutocompleters = () => {
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
      };

      const langTools = ace.require('ace/ext/language_tools');
      langTools.textCompleter.setSqlMode(this.isSqlDialect());

      initAutocompleters();
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
      window.setTimeout(() => {
        this.$emit('ace-created', editor);
      }, 3000);

      editor.$blockScrolling = Infinity;

      this.editor = editor;
    }

    destroyed(): void {
      this.subTracker.dispose();
    }
  }

  export const COMPONENT_NAME = 'ace-editor';
  wrap(COMPONENT_NAME, AceEditor);
</script>

<style lang="scss" scoped>
  .ace-editor {
    height: 200px;
  }
</style>
