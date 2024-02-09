/*
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
*/

import { useState } from 'react';
import { format, KeywordCase } from 'sql-formatter';

import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

import { nqlCommentRegex, multiLineCommentRegex } from '../sharedRegexes';

const SINGLE_LINE_COMMENT_REGEX = /^(\s)*--.*$/gm;
const LOCAL_STORAGE_KEY = 'hue.aiAssistBar.sqlFormattingConf';
const MAX_LINE_LENGTH = 90;
const SPACE = ' ';
const LINE_BREAK = '\n';

/***
 * Insert line breaks in a string so that no line is longer than 90 characters.
 * Useful for formatting LLM text responses.
 */
const insertLineBreaks = (input: string): string => {
  let output = '';
  let lineLength = 0;

  input.split(SPACE).forEach(word => {
    const append = word + SPACE;
    if (lineLength + word.length > MAX_LINE_LENGTH) {
      output += LINE_BREAK + append;
      lineLength = append.length;
    } else {
      output += append;
      lineLength += append.length;
    }

    if (word.includes(LINE_BREAK)) {
      const index = word.lastIndexOf(LINE_BREAK);
      lineLength = word.length - index;
    }
  });

  return output;
};

const appendComments = (previousSql: string, newSql: string, newComment: string): string => {
  let existingComments = '';
  let query = newSql;

  const commentsKeptInNewSql = newSql.match(nqlCommentRegex)?.join('\n') || undefined;

  // We don't know for sure if an AI modified SQL will
  // retain the commemts in the original SQL.
  if (commentsKeptInNewSql) {
    existingComments = commentsKeptInNewSql;
    query = newSql.replace(existingComments, '').trim();
  } else {
    const commentsFromPreviousSql = previousSql.match(nqlCommentRegex)?.join('\n') || undefined;
    existingComments = commentsFromPreviousSql ? commentsFromPreviousSql.trim() : '';
  }

  existingComments = existingComments ? existingComments + '\n' : '';
  return `${existingComments}/* ${newComment.trim()} */\n${query.trim()}`;
};

const replaceNqlComment = (newSql: string, newComment: string): string => {
  const commentsKeptInNewSql = newSql.match(nqlCommentRegex)?.join('\n') || undefined;

  // We don't know for sure if an AI modified SQL will
  // retain the commemts in the original SQL.
  const query = commentsKeptInNewSql ? newSql.replace(commentsKeptInNewSql, '') : newSql;
  return `/* ${newComment.trim()} */\n${query.trim()}`;
};

const includeNqlAsComment = ({ oldSql, newSql, nql, includeNql, replaceNql }) => {
  const addComment = nql && includeNql;
  const nqlWithPrefix = nql && nql.trim().startsWith('NQL:') ? nql : `NQL: ${nql}`;
  const commentWithLinebreaks = insertLineBreaks(nqlWithPrefix);
  const sqlWithNqlComment = replaceNql
    ? replaceNqlComment(newSql, commentWithLinebreaks)
    : appendComments(oldSql, newSql, commentWithLinebreaks);
  return addComment ? sqlWithNqlComment : newSql;
};

export const removeComments = (statement: string): string => {
  return statement.replace(SINGLE_LINE_COMMENT_REGEX, '').replace(multiLineCommentRegex, '');
};

export const formatClean = (sql: string, dialect: string): string => {
  const cleanedSql = removeComments(sql).trim();
  let newFormat = sql;
  try {
    newFormat = format(cleanedSql, { language: dialect, keywordCase: 'upper' });
  } catch (e) {
    console.error(e);
  }
  return newFormat;
};

export const extractLeadingNqlComments = (sql: string): string => {
  const comments = sql.match(nqlCommentRegex) || [];
  const prefixSingleLine = '-- NQL:';
  const prefixMultiLine = '/* NQL:';
  const commentsTexts = comments
    .map(comment => comment.trim())
    .filter(comment => comment.startsWith(prefixSingleLine) || comment.startsWith(prefixMultiLine))
    .map(comment => {
      return comment.startsWith(prefixSingleLine)
        ? comment.slice(prefixSingleLine.length).trim()
        : comment.slice(prefixMultiLine.length, -2).trim();
    });

  return commentsTexts.join('\n');
};

export interface FormattingConfig {
  autoFormat: boolean;
  includeNql: boolean;
  replaceNql: boolean;
}

interface useFormattingProps {
  dialect: string;
  keywordCase: KeywordCase;
  oldSql: string;
  newSql: string;
  nql: string;
  preventAutoFormat: boolean;
}
export const useFormatting = ({
  dialect,
  keywordCase,
  oldSql,
  newSql,
  nql,
  preventAutoFormat
}: useFormattingProps): {
  formattingConfig: FormattingConfig;
  updateFormattingSettings: (newSettings: FormattingConfig) => void;
  suggestion: string;
  showDiffFrom: string;
} => {
  const defaultConfig: FormattingConfig = {
    autoFormat: true,
    includeNql: true,
    replaceNql: false
  };

  const savedConfiguration = getFromLocalStorage(LOCAL_STORAGE_KEY, defaultConfig);
  const overriddenConfiguration = {
    ...savedConfiguration,
    autoFormat: preventAutoFormat ? false : savedConfiguration.autoFormat
  };
  const [formattingConfig, setFormattingConfig] =
    useState<FormattingConfig>(overriddenConfiguration);
  const { autoFormat, includeNql, replaceNql } = formattingConfig;

  const updateFormattingSettings = (newSettings: FormattingConfig) => {
    setFormattingConfig(newSettings);
    setInLocalStorage(LOCAL_STORAGE_KEY, newSettings);
  };

  const formatSql = (sql: string) => {
    let newFormat = sql;
    if (autoFormat) {
      try {
        newFormat = format(sql, { language: dialect, keywordCase });
      } catch (e) {
        console.error('Ignored formatting SQL due to error. Proceeding with unformatted SQL.');
        console.error(e);
      }
    }
    return newFormat;
  };

  const withNqlComments = includeNqlAsComment({
    oldSql,
    newSql,
    nql,
    includeNql,
    replaceNql
  });
  const suggestion = formatSql(withNqlComments);
  const showDiffFrom = formatSql(oldSql);

  return {
    formattingConfig,
    updateFormattingSettings,
    suggestion,
    showDiffFrom
  };
};
