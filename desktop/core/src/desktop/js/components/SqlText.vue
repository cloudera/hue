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
  import Vue from 'vue';
  import Component from 'vue-class-component';
  import { Prop, Watch } from 'vue-property-decorator';

  interface Ace {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    require: (module: string) => any;
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const getAce = (): Ace => (window as any).ace;

  @Component
  export default class SqlText extends Vue {
    @Prop({ required: false })
    dialect = 'hive';
    @Prop({ required: false })
    value = '';
    @Prop({ required: false })
    formatted = false;
    @Prop({ required: false })
    enableOverflow = false;
    @Prop({ required: false })
    splitLines = false;

    @Watch('value')
    renderAce(): void {
      if (this.value) {
        const ace = getAce();
        const impalaRules = ace.require('ace/mode/impala_highlight_rules');
        const hiveRules = ace.require('ace/mode/hive_highlight_rules');
        const tokenizer = ace.require('ace/tokenizer');
        const text = ace.require('ace/layer/text');
        const config = ace.require('ace/config');

        const Tokenizer = tokenizer.Tokenizer;
        const Rules =
          this.dialect === 'impala'
            ? impalaRules.ImpalaHighlightRules
            : hiveRules.HiveHighlightRules;

        const res: string[] = [];

        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore: totalStorage interface missing
        config.loadModule(['theme', $.totalStorage('hue.ace.theme') || 'ace/theme/hue']);

        const Text = text.Text;

        const tok = new Tokenizer(new Rules().getRules());
        const lines = this.value.split('\n');

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

        let additionalClass = '';
        if (!this.splitLines && !this.formatted) {
          additionalClass = 'pull-left';
        } else if (this.formatted) {
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

        const element = this.$el.firstElementChild;
        if (!element) {
          return;
        }
        element.innerHTML =
          '<div class="ace_editor ace-hue"' +
          (this.enableOverflow ? ' style="overflow: initial !important;"' : '') +
          '><div class="ace_layer" style="position: static;' +
          (this.enableOverflow ? ' overflow: initial !important;' : '') +
          '">' +
          res.join('') +
          '</div></div>';
        if (this.enableOverflow) {
          $(element).css({ overflow: 'auto' });
        }
        $(element).find('.ace_invisible_space').remove();
      }
    }

    mounted(): void {
      this.renderAce();
    }
  }
</script>

<style lang="scss" scoped></style>
