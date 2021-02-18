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

<!-- This one is based on ko.highlight.js -->

<template>
  <div class="ace-highlight" />
</template>

<script lang="ts">
  import $ from 'jquery';
  import { defineComponent } from 'vue';

  import { formatSql } from 'apps/editor/api';
  import { getAceMode } from 'ext/aceHelper';
  import { hueLocalStorage } from 'utils/storageUtils';

  interface Ace {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    require: (module: string) => any;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getAce = (): Ace => (window as any).ace;

  export default defineComponent({
    props: {
      dialect: {
        type: String,
        default: 'hive'
      },
      value: {
        type: String,
        default: ''
      },
      format: {
        type: Boolean,
        default: false
      },
      enableOverflow: {
        type: Boolean,
        default: false
      },
      splitLines: {
        type: Boolean,
        default: false
      }
    },

    watch: {
      async value(): Promise<void> {
        this.renderAce();
      }
    },

    mounted(): void {
      this.renderAce();
    },

    methods: {
      async renderAce(): Promise<void> {
        if (!this.value) {
          return;
        }
        const ace = getAce();
        const tokenizer = ace.require('ace/tokenizer');
        const text = ace.require('ace/layer/text');
        const config = ace.require('ace/config');

        const Tokenizer = tokenizer.Tokenizer;
        let ruleModule;
        try {
          ruleModule = ace.require(`${getAceMode(this.dialect)}_highlight_rules`);
        } catch (err) {}
        const Rules =
          ruleModule && Object.keys(ruleModule).length === 1
            ? ruleModule[Object.keys(ruleModule)[0]]
            : ace.require(`sql_highlight_rules`).SqlHighlightRules;
        const res: string[] = [];

        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        config.loadModule(['theme', hueLocalStorage('hue.ace.theme') || 'ace/theme/hue']);

        const Text = text.Text;

        const tok = new Tokenizer(new Rules().getRules());

        let editorText = this.value;
        if (this.format) {
          editorText = await formatSql({ statements: this.value, silenceErrors: true });
        }
        const lines = editorText.split('\n');

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const renderSimpleLine = (txt: any, stringBuilder: string[], tokens: any[]) => {
          let screenColumn = 0;
          let token = tokens[0];
          let value = token.value;
          if (value) {
            try {
              screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, value);
            } catch (e) {
              console.warn(
                value,
                'Failed to get screen column due to some parsing errors, skip rendering.'
              );
            }
          }
          for (let i = 1; i < tokens.length; i++) {
            token = tokens[i];
            value = token.value;
            try {
              screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, value);
            } catch (e) {
              if (console && console.warn) {
                console.warn(
                  value,
                  'This token has some parsing errors and it has been rendered without highlighting.'
                );
              }
              stringBuilder.push(value);
              screenColumn = screenColumn + value.length;
            }
          }
        };

        let additionalClass = 'pull-left';
        if (!this.splitLines && !this.format) {
          additionalClass = 'pull-left';
        } else if (this.format) {
          additionalClass = 'ace-highlight-pre';
        }

        lines.forEach(line => {
          const renderedTokens: string[] = [];
          const tokens = tok.getLineTokens(line);

          if (tokens && tokens.tokens.length) {
            renderSimpleLine(
              new Text(document.createElement('div')),
              renderedTokens,
              tokens.tokens
            );
          }

          res.push(
            '<div class="ace_line ' +
              additionalClass +
              '">' +
              renderedTokens.join('') +
              '&nbsp;</div>'
          );
        });

        const overflowStyle = this.enableOverflow ? ' overflow: initial !important;' : '';
        //TODO - Move inline styles to CSS class
        this.$el.innerHTML = `
          <div class="ace_editor ace-hue" style="background-color: transparent; ${overflowStyle}">
            <div class="ace_layer" style="position: static; ${overflowStyle}">${res.join('')}</div>
          </div>
        `;

        if (this.enableOverflow) {
          $(this.$el).css({ overflow: 'auto' });
        }
        $(this.$el).find('.ace_invisible_space').remove();
      }
    }
  });
</script>

<style lang="scss" scoped></style>
