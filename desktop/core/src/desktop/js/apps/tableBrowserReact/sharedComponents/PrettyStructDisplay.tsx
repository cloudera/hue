// Licensed to Cloudera, Inc. under one or more contributor license agreements.
// See the NOTICE file distributed with this work for additional information
// regarding copyright ownership. Cloudera, Inc. licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may not use this file
// except in compliance with the License. You may obtain a copy of the License at
// http://www.apache.org/licenses/LICENSE-2.0
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations under
// the License.

import React, { useMemo } from 'react';
import { i18nReact } from '../../../utils/i18nReact';
import './PrettyStructDisplay.scss';

export type FormatOptions = {
  indentSize?: number; // spaces per indent level (default 2)
  uppercaseTypes?: boolean; // UPPERCASE type names (default true)
};

function prettyPrintStructType(input?: string, opts: FormatOptions = {}): string {
  if (!input) {
    return '';
  }

  const indentSize = opts.indentSize ?? 2;
  const uppercaseTypes = opts.uppercaseTypes ?? true;

  // Normalize odd whitespace (including zero-width spaces)
  const src = input.replace(/[\u200B-\u200D\uFEFF]/g, '').trim();

  // Known keywords/types across engines (not exhaustive, but solid defaults)
  const KEYWORDS = new Set(['struct', 'array', 'map']);
  const PRIMITIVES = new Set([
    'string',
    'varchar',
    'char',
    'int',
    'integer',
    'bigint',
    'smallint',
    'tinyint',
    'float',
    'double',
    'real',
    'decimal',
    'numeric',
    'boolean',
    'date',
    'timestamp',
    'timestamptz',
    'binary',
    'varbinary',
    'json',
    'interval'
  ]);

  let out = '';
  let i = 0;
  let depth = 0; // angle bracket depth: < >
  let parenDepth = 0; // parentheses depth: ( )
  let lastWord = ''; // last parsed word (to detect STRUCT/ARRAY/MAP before '<')
  let prev = ''; // last emitted character (for spacing decisions)

  // Track whether we’re inside a STRUCT’s field-list at each depth
  const structStack: boolean[] = []; // structStack[depth] = true if that level is a STRUCT<...>

  // When true, a primitive type token should be uppercased (e.g., after ":" or in generics)
  let expectType = false;

  const pad = () => ' '.repeat(depth * indentSize);

  const emit = (s: string) => {
    out += s;
    if (s.length) {
      prev = s[s.length - 1];
    }
  };

  const needSpace = () => {
    if (!out.length) {
      return;
    }
    if (!/\s|[<>\(\),:]/.test(prev)) {
      emit(' ');
    }
  };

  const readWord = () => {
    const start = i;
    while (i < src.length && /[A-Za-z0-9_]/.test(src[i])) {
      i++;
    }
    return src.slice(start, i);
  };

  const readNumber = () => {
    const start = i;
    while (i < src.length && /[0-9]/.test(src[i])) {
      i++;
    }
    return src.slice(start, i);
  };

  const emitWord = (raw: string) => {
    const lower = raw.toLowerCase();
    let word = raw;

    // Decide casing
    if (uppercaseTypes) {
      if (KEYWORDS.has(lower)) {
        word = lower.toUpperCase();
      } else if (PRIMITIVES.has(lower) && expectType) {
        word = lower.toUpperCase();
      }
    }

    needSpace();
    emit(word);
    lastWord = lower;
  };

  while (i < src.length) {
    const ch = src[i];

    // Skip redundant whitespace
    if (/\s/.test(ch)) {
      i++;
      continue;
    }

    if (ch === '`') {
      // Backticked identifier: copy verbatim
      const start = i;
      i++; // skip opening `
      while (i < src.length && src[i] !== '`') {
        i++;
      }
      i = Math.min(i + 1, src.length); // include closing ` if present
      const ident = src.slice(start, i);
      needSpace();
      emit(ident);
      lastWord = '';
      continue;
    }

    if (/[A-Za-z_]/.test(ch)) {
      const word = readWord();
      emitWord(word);
      continue;
    }

    if (/[0-9]/.test(ch)) {
      // numbers (e.g., DECIMAL(10,2))
      const num = readNumber();
      needSpace();
      emit(num);
      continue;
    }

    if (ch === '(') {
      emit('(');
      parenDepth++;
      i++;
      continue;
    }

    if (ch === ')') {
      parenDepth = Math.max(0, parenDepth - 1);
      emit(')');
      i++;
      continue;
    }

    if (ch === ':') {
      emit(': ');
      expectType = true; // next word likely a type (or keyword like STRUCT/ARRAY/MAP)
      i++;
      continue;
    }

    if (ch === '<') {
      // Decide if this is after STRUCT/ARRAY/MAP
      const isStruct = lastWord === 'struct';
      emit('<');
      depth++;
      structStack[depth] = !!isStruct;
      // Break after '<' for readability
      emit('\n' + pad());
      // Inside generics, after '<' we expect a type; inside STRUCT we expect a field name first
      expectType = !isStruct;
      i++;
      continue;
    }

    if (ch === '>') {
      // Close nested block: move indent first
      depth = Math.max(0, depth - 1);
      if (prev !== '\n') {
        emit('\n' + pad());
      }
      emit('>');
      expectType = false;
      structStack.length = depth + 1;
      i++;
      continue;
    }

    if (ch === ',') {
      if (parenDepth > 0) {
        // Keep commas in parentheses inline: DECIMAL(10,2)
        emit(', ');
      } else {
        emit(',\n' + pad());
      }
      const insideStruct = structStack[depth] === true;
      expectType = !insideStruct;
      i++;
      continue;
    }

    if (ch === '.') {
      emit('.');
      i++;
      continue;
    }

    // Any other punctuation—emit as-is
    emit(ch);
    i++;
  }

  return out
    .replace(/[ \t]+\n/g, '\n') // strip spaces at EOL
    .replace(/\n{3,}/g, '\n\n') // collapse extra blank lines
    .trim();
}

export type PrettyStructDisplayProps = {
  structType?: string;
  indentSize?: number;
  uppercaseTypes?: boolean;
  className?: string;
  style?: React.CSSProperties;
  ariaLabel?: string;
  compact?: boolean;
};

export default function PrettyStructDisplay({
  structType = '',
  indentSize = 2,
  uppercaseTypes = false,
  className,
  style,
  ariaLabel,
  compact = false
}: PrettyStructDisplayProps): JSX.Element {
  const { t } = i18nReact.useTranslation();
  const formatted = useMemo(
    () => prettyPrintStructType(structType, { indentSize, uppercaseTypes }),
    [structType, indentSize, uppercaseTypes]
  );

  // Tokenized colored rendering: reuse the same tokenizer logic but emit nodes with spans
  const nodes = useMemo(() => {
    if (!structType) {
      return [] as React.ReactNode[];
    }

    // Reuse essential pieces from the pretty printer
    const KEYWORDS = new Set(['struct', 'array', 'map']);
    const NUMBERS = new Set([
      'int',
      'integer',
      'bigint',
      'smallint',
      'tinyint',
      'float',
      'double',
      'real',
      'decimal',
      'numeric'
    ]);
    const TEXTS = new Set(['string', 'varchar', 'char', 'binary', 'varbinary']);
    const TIMES = new Set(['date', 'timestamp', 'timestamptz', 'interval']);
    const PRIMITIVES = new Set([
      ...Array.from(NUMBERS),
      ...Array.from(TEXTS),
      'boolean',
      'json',
      ...Array.from(TIMES)
    ]);

    const categorize = (
      wordLower: string
    ): 'number' | 'text' | 'boolean' | 'time' | 'json' | 'complex' | 'other' => {
      if (NUMBERS.has(wordLower)) {
        return 'number';
      }
      if (TEXTS.has(wordLower)) {
        return 'text';
      }
      if (wordLower === 'boolean') {
        return 'boolean';
      }
      if (TIMES.has(wordLower)) {
        return 'time';
      }
      if (wordLower === 'json') {
        return 'json';
      }
      if (KEYWORDS.has(wordLower)) {
        return 'complex';
      }
      return 'other';
    };

    const indent = indentSize;

    // Normalize and then re-tokenize similarly to pretty printer but building nodes
    const src = structType.replace(/[\u200B-\u200D\uFEFF]/g, '').trim();
    const out: React.ReactNode[] = [];
    let i = 0;
    let depth = 0;
    let parenDepth = 0;
    let lastWord = '';
    let prev: string | null = null;
    const structStack: boolean[] = [];
    let expectType = false;

    const padStr = (d: number) => ' '.repeat(d * indent);
    const emitText = (s: string) => {
      if (!s) {
        return;
      }
      out.push(s);
      prev = s[s.length - 1] || prev;
    };
    const needSpace = () => {
      if (!out.length) {
        return;
      }
      if (prev && !/\s|[<>\(\),:]/.test(prev)) {
        emitText(' ');
      }
    };
    const readWord = () => {
      const start = i;
      while (i < src.length && /[A-Za-z0-9_]/.test(src[i])) {
        i++;
      }
      return src.slice(start, i);
    };
    const readNumber = () => {
      const start = i;
      while (i < src.length && /[0-9]/.test(src[i])) {
        i++;
      }
      return src.slice(start, i);
    };
    const emitWordNode = (raw: string) => {
      const lower = raw.toLowerCase();
      let display = raw;
      const isKeyword = KEYWORDS.has(lower);
      const isPrimitive = PRIMITIVES.has(lower);
      // Decide casing
      if (uppercaseTypes) {
        if (isKeyword) {
          display = lower.toUpperCase();
        } else if (isPrimitive && expectType) {
          display = lower.toUpperCase();
        }
      }
      // Only color code when it is a type token (keyword or primitive in type position)
      const shouldColor = isKeyword || (isPrimitive && expectType);
      if (shouldColor) {
        const category = categorize(lower);
        needSpace();
        out.push(
          <span
            key={`${out.length}-w`}
            className={`hue-pretty-type-label hue-pretty-type--${category}`}
          >
            {display}
          </span>
        );
      } else {
        needSpace();
        emitText(display);
      }
      lastWord = lower;
    };

    while (i < src.length) {
      const ch = src[i];

      if (/\s/.test(ch)) {
        i++;
        continue;
      }

      if (ch === '`') {
        const start = i;
        i++;
        while (i < src.length && src[i] !== '`') {
          i++;
        }
        i = Math.min(i + 1, src.length);
        const ident = src.slice(start, i);
        needSpace();
        emitText(ident);
        lastWord = '';
        continue;
      }

      if (/[A-Za-z_]/.test(ch)) {
        const word = readWord();
        emitWordNode(word);
        continue;
      }

      if (/[0-9]/.test(ch)) {
        const num = readNumber();
        needSpace();
        emitText(num);
        continue;
      }

      if (ch === '(') {
        emitText('(');
        parenDepth++;
        i++;
        continue;
      }
      if (ch === ')') {
        parenDepth = Math.max(0, parenDepth - 1);
        emitText(')');
        i++;
        continue;
      }
      if (ch === ':') {
        emitText(': ');
        expectType = true;
        i++;
        continue;
      }
      if (ch === '<') {
        const isStruct = lastWord === 'struct';
        emitText('<');
        depth++;
        structStack[depth] = !!isStruct;
        emitText('\n' + padStr(depth));
        expectType = !isStruct;
        i++;
        continue;
      }
      if (ch === '>') {
        depth = Math.max(0, depth - 1);
        if (prev !== '\n') {
          emitText('\n' + padStr(depth));
        }
        emitText('>');
        expectType = false;
        structStack.length = depth + 1;
        i++;
        continue;
      }
      if (ch === ',') {
        if (parenDepth > 0) {
          emitText(', ');
        } else {
          emitText(',\n' + padStr(depth));
        }
        const insideStruct = structStack[depth] === true;
        expectType = !insideStruct;
        i++;
        continue;
      }
      if (ch === '.') {
        emitText('.');
        i++;
        continue;
      }
      // default
      emitText(ch);
      i++;
    }

    return out;
  }, [structType, indentSize, uppercaseTypes]);

  const cssClasses = [
    'hue-pretty-struct-display',
    compact && 'hue-pretty-struct-display--compact',
    className
  ]
    .filter(Boolean)
    .join(' ');

  const computedAria = ariaLabel ?? t('Struct type pretty print');

  return (
    <div className={cssClasses} style={style} aria-label={computedAria}>
      <pre>
        <code>{nodes.length ? nodes : formatted}</code>
      </pre>
    </div>
  );
}
