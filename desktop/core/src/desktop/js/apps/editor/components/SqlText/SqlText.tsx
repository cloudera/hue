import React, { useEffect, useRef } from 'react';
import { formatSql } from '../../api';
import { getAceMode } from '../../../../ext/aceHelper';
import { hueLocalStorage } from '../../../../utils/storageUtils';

interface Ace {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  require: (module: string) => any;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getAce = (): Ace => (window as any).ace;

interface Props {
  dialect?: string;
  value?: string;
  format?: boolean;
  enableOverflow?: boolean;
  splitLines?: boolean;
}

const SqlText: React.FC<Props> = ({
  dialect = 'hive',
  value = '',
  format = false,
  enableOverflow = false,
  splitLines = false
}) => {
  const elementRef = useRef<HTMLDivElement>(null);
  let apa;

  useEffect(() => {
    apa = renderAce();
  }, [value]);

  async function renderAce(): Promise<void> {
    if (!value) {
      return;
    }
    const ace = getAce();
    const tokenizer = ace.require('ace/tokenizer');
    const text = ace.require('ace/layer/text');
    const config = ace.require('ace/config');

    const Tokenizer = tokenizer.Tokenizer;
    let ruleModule;
    try {
      ruleModule = ace.require(`${getAceMode(dialect)}_highlight_rules`);
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

    let editorText = value;
    if (format) {
      editorText = await formatSql({ statements: value, silenceErrors: true });
    }
    const lines = editorText.split('\n');

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const renderSimpleLine = (txt: any, stringBuilder: string[], tokens: any[]) => {
      let screenColumn = 0;
      let token = tokens[0];
      let tokenValue = token.value;
      if (tokenValue) {
        try {
          screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, tokenValue);
        } catch (e) {
          console.warn(
            tokenValue,
            'Failed to get screen column due to some parsing errors, skip rendering.'
          );
        }
      }
      for (let i = 1; i < tokens.length; i++) {
        token = tokens[i];
        tokenValue = token.value;
        try {
          screenColumn = txt.$renderToken(stringBuilder, screenColumn, token, tokenValue);
        } catch (e) {
          if (console && console.warn) {
            console.warn(
              tokenValue,
              'This token has some parsing errors and it has been rendered without highlighting.'
            );
          }
          stringBuilder.push(tokenValue);
          screenColumn = screenColumn + tokenValue.length;
        }
      }
    };

    let additionalClass = 'pull-left';
    if (!splitLines && !format) {
      additionalClass = 'pull-left';
    } else if (format) {
      additionalClass = 'ace-highlight-pre';
    }

    lines.forEach(line => {
      const renderedTokens: string[] = [];
      const tokens = tok.getLineTokens(line);
      if (tokens && tokens.tokens.length) {
        renderSimpleLine(new Text(document.createElement('div')), renderedTokens, tokens.tokens);
      }

      res.push(
        '<div class="ace_line ' + additionalClass + '">' + renderedTokens.join('') + '&nbsp;</div>'
      );
    });

    const overflowStyle = enableOverflow ? ' overflow: auto;' : '';
    //TODO - Move inline styles to CSS class
    // this.$el.innerHTML = `
    //   <div class="ace_editor ace-hue" style="background-color: transparent; ${overflowStyle}">
    //     <div class="ace_layer" style="position: static; ${overflowStyle}">${res.join('')}</div>
    //   </div>
    // `;

    // if (this.enableOverflow) {
    //   this.$el.style.overflow = 'auto';
    // }
    // (this.$el as HTMLElement).querySelectorAll('.ace_invisible_space').forEach(el => el.remove());
    return (
      <div class="ace_editor ace-hue" style={`"background-color: transparent; ${overflowStyle}"`}>
        <div class="ace_layer" style={`"position: static; ${overflowStyle}"`}>
          HELLO;
          {res.join('')}
        </div>
      </div>
    );
  }
  return apa;
};

export default SqlText;
