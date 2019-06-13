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

// TODO: Depends on Ace

ko.bindingHandlers.highlight = {
  init: function(element) {
    $(element).addClass('ace-highlight');
  },
  update: function(element, valueAccessor) {
    const options = $.extend(
      {
        dialect: 'hive',
        value: '',
        formatted: false
      },
      valueAccessor()
    );

    let value = ko.unwrap(options.value);

    if (typeof value !== 'undefined' && value !== '') {
      // allows highlighting static code
      if (options.path) {
        value = value[options.path];
      }
      ace.require(
        [
          'ace/mode/impala_highlight_rules',
          'ace/mode/hive_highlight_rules',
          'ace/mode/xml_highlight_rules',
          'ace/tokenizer',
          'ace/layer/text',
          'ace/config'
        ],
        (impalaRules, hiveRules, xmlRules, tokenizer, text, config) => {
          const res = [];

          const Tokenizer = tokenizer.Tokenizer;
          let Rules = hiveRules.HiveHighlightRules;
          if (options.dialect && ko.unwrap(options.dialect) === 'impala') {
            Rules = impalaRules.ImpalaHighlightRules;
          }

          config.loadModule(['theme', $.totalStorage('hue.ace.theme') || 'ace/theme/hue']);

          const Text = text.Text;

          const tok = new Tokenizer(new Rules().getRules());
          const lines = value.split('\n');

          const renderSimpleLine = function(txt, stringBuilder, tokens) {
            let screenColumn = 0;
            let token = tokens[0];
            let value = token.value;
            if (value) {
              screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, value);
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
          if (!options.splitLines && !options.formatted) {
            additionalClass = 'pull-left';
          } else if (options.formatted) {
            additionalClass = 'ace-highlight-pre';
          }

          lines.forEach(line => {
            const renderedTokens = [];
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

          element.innerHTML =
            '<div class="ace_editor ace-hue"' +
            (options.enableOverflow ? ' style="overflow: initial !important;"' : '') +
            '><div class="ace_layer" style="position: static;' +
            (options.enableOverflow ? ' overflow: initial !important;' : '') +
            '">' +
            res.join('') +
            '</div></div>';
          if (options.enableOverflow) {
            $(element).css({ overflow: 'auto' });
          }
          $(element)
            .find('.ace_invisible_space')
            .remove();
        }
      );
    }
  }
};
