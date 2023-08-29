import React, { useState } from 'react';
// import { Button } from 'antd';
import { Button } from 'antd';
import DefaultButton from 'cuix/dist/components/Button/Button';
import Switch from 'cuix/dist/components/Switch';
import Modal from 'cuix/dist/components/Modal';
import execCommandCopy from 'copy-to-clipboard';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { stackoverflowDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { fluidxSlate800, fluidxSpacingS, fluidxSpacingXs } from '@cloudera/cuix-core/variables';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import CheckmarkIcon from '@cloudera/cuix-core/icons/react/CheckmarkIcon';
import { KeywordCase, format } from 'sql-formatter';

import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import { nqlCommentRegex } from '../sharedRegexes';

import SyntaxHighlighterDiff from '../SyntaxHighlighterDiff/SyntaxHighlighterDiff';

import './AiPreviewModal.scss';

const insertLineBreaks = (input: string): string => {
  let output = '';
  let lineLength = 0;
  const MAX_LINE_LENGTH = 90;
  const SPACE = ' ';
  const LINE_BREAK = '\n';

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

const replaceNQLComment = (newSql: string, newComment: string): string => {
  const commentsKeptInNewSql = newSql.match(nqlCommentRegex)?.join('\n') || undefined;

  // We don't know for sure if an AI modified SQL will
  // retain the commemts in the original SQL.
  const query = commentsKeptInNewSql ? newSql.replace(commentsKeptInNewSql, '') : newSql;
  return `/* ${newComment.trim()} */\n${query.trim()}`;
};

interface PreviewModalProps {
  actionType: 'generate' | 'edit' | 'optimize' | 'fix';
  open: boolean;
  title: string;
  autoFormat: boolean;
  suggestion: string;
  assumptions: string;
  explanation: string;
  nql?: string;
  onCancel: () => void;
  onInsert: (value: string) => void;
  primaryButtonLabel: string;
  showDiffFrom: string;
  lineNumberStart: number;
  showCopyToClipboard: boolean;
  dialect: string;
  keywordCase: KeywordCase | undefined;
}

const PreviewModal = ({
  actionType,
  open,
  title,
  autoFormat,
  suggestion: suggestionRaw = '',
  assumptions = '',
  explanation = '',
  nql = '',
  onCancel,
  onInsert,
  primaryButtonLabel,
  showDiffFrom: showDiffFromRaw = '',
  lineNumberStart = 1,
  showCopyToClipboard = true,
  dialect,
  keywordCase
}: PreviewModalProps) => {
  const [copied, setCopied] = useState(false);
  const [userChoiceAutoFormat, setUserChoiceAutoFormat] = useState<boolean>(
    getFromLocalStorage('hue.aiAssistBar.previewModal.autoFormat', true)
  );
  const [userChoiceIncludeNql, setUserChoiceIncludeNql] = useState<boolean>(
    getFromLocalStorage('hue.aiAssistBar.previewModal.includeNql', true)
  );
  const [userChoiceReplaceNql, setUserChoiceReplaceNql] = useState<boolean>(
    getFromLocalStorage('hue.aiAssistBar.previewModal.replaceNql', false)
  );

  const formatSql = (sql: string) => {
    const applyAutoFormat =
      (userChoiceAutoFormat === undefined && autoFormat) || userChoiceAutoFormat;
    if (applyAutoFormat) {
      try {
        sql = format(sql, { language: dialect, keywordCase });
      } catch (e) {
        // Handle gracefully
      }
    }
    return sql;
  };

  const includeNqlAsComment = (previousSql: string, sql: string, nql: string) => {
    const addComment = nql && userChoiceIncludeNql;
    const nqlWithPrefix = nql && nql.trim().startsWith('NQL:') ? nql : `NQL: ${nql}`;
    const commentWithLinebreaks = insertLineBreaks(nqlWithPrefix);
    const sqlWithNqlComment = userChoiceReplaceNql
      ? replaceNQLComment(sql, commentWithLinebreaks)
      : appendComments(previousSql, sql, commentWithLinebreaks);
    return addComment ? sqlWithNqlComment : sql;
  };

  const suggestion = formatSql(includeNqlAsComment(showDiffFromRaw, suggestionRaw, nql));
  const showDiffFrom = formatSql(showDiffFromRaw);

  const clearStates = () => {
    setCopied(false);
  };
  const handleInsert = () => {
    clearStates();
    onInsert(suggestion);
  };

  const handleCancel = () => {
    clearStates();
    onCancel();
  };

  const copyToClipboard = (text: string): void => {
    navigator.permissions.query({ name: 'clipboard-write' }).then(result => {
      if (result.state === 'granted') {
        navigator.clipboard.writeText(text);
      } else {
        execCommandCopy(text);
      }
    });
    setCopied(true);
  };

  if (actionType === 'optimize' || actionType === 'fix') {
    const noDiffDetected =
      format(suggestionRaw, { language: dialect, keywordCase: 'upper' }) ===
      format(showDiffFromRaw, { language: dialect, keywordCase: 'upper' });

    if (noDiffDetected) {
      return (
        <Modal
          wrapClassName="cuix hue-ai-preview-modal"
          open={open}
          title={title}
          onCancel={handleCancel}
          width={'80%'}
          footer={
            <div className="hue-ai-preview-modal__footer">
              <Button key="submit" type="primary" onClick={handleCancel}>
                OK
              </Button>
            </div>
          }
        >
          <p>
            {actionType === 'optimize'
              ? `No optimization to the SQL statement could be suggested.`
              : `No fix to the SQL statement could be suggested.`}
          </p>
          <div className="hue-ai-preview-modal__text-container">
            <h4 className="hue-ai-preview-modal__text-container-title">Alternative actions</h4>
            <p className="hue-ai-preview-modal__assumptions">{explanation}</p>
          </div>
        </Modal>
      );
    }
  }

  return (
    <Modal
      wrapClassName="cuix hue-ai-preview-modal"
      open={open}
      title={title}
      onCancel={handleCancel}
      width={'80%'}
      footer={
        <div className="hue-ai-preview-modal__footer">
          <Button key="submit" type="primary" onClick={handleInsert}>
            {primaryButtonLabel}
          </Button>

          {showCopyToClipboard && (
            <DefaultButton
              className="hue-ai-preview-modal__copy-button"
              data-event=""
              icon={
                copied ? (
                  <CheckmarkIcon className="hue-ai-preview-modal__copy-button-icon" />
                ) : (
                  <CopyClipboardIcon />
                )
              }
              onClick={() => copyToClipboard(suggestion)}
            >
              Copy to clipboard
            </DefaultButton>
          )}

          <div className="hue-ai-preview-modal__footer-spacer"></div>
          <DefaultButton data-event="" onClick={handleCancel}>
            Cancel
          </DefaultButton>
        </div>
      }
    >
      <div className="hue-ai-preview-modal__diff-highlighter">
        <div className="hue-ai-preview-modal__config-container">
          <Switch
            checked={userChoiceAutoFormat === undefined ? autoFormat : userChoiceAutoFormat}
            onChange={(useAutoformat: boolean) => {
              setInLocalStorage('hue.aiAssistBar.previewModal.autoFormat', useAutoformat);
              setUserChoiceAutoFormat(useAutoformat);
            }}
            className="hue-ai-preview-modal__config-switch"
            label="Autoformat SQL"
          />
          <Switch
            checked={userChoiceIncludeNql}
            onChange={(includeNql: boolean) => {
              setInLocalStorage('hue.aiAssistBar.previewModal.includeNql', includeNql);
              setUserChoiceIncludeNql(includeNql);
            }}
            className="hue-ai-preview-modal__config-switch"
            label="Include prompt as comment"
          />
          <Switch
            checked={userChoiceReplaceNql}
            onChange={(reolaceNql: boolean) => {
              setInLocalStorage('hue.aiAssistBar.previewModal.replaceNql', reolaceNql);
              setUserChoiceReplaceNql(reolaceNql);
            }}
            className="hue-ai-preview-modal__config-switch"
            label="Replace comments"
          />
        </div>

        {showDiffFrom && (
          <SyntaxHighlighterDiff
            lineNumberStart={lineNumberStart}
            newCode={suggestion}
            oldCode={showDiffFrom}
          />
        )}
        {!showDiffFrom && (
          <SyntaxHighlighter
            showLineNumbers
            className="hue-ai-preview-modal__syntax-highlighter"
            language="SQL"
            style={stackoverflowDark}
            customStyle={{
              backgroundColor: fluidxSlate800,
              padding: `${fluidxSpacingXs} ${fluidxSpacingS}`
            }}
            // TODO: rename class
            codeTagProps={{ className: 'hue-explain-sql__code' }}
            wrapLines={true}
          >
            {suggestion}
          </SyntaxHighlighter>
        )}
      </div>
      <div className="hue-ai-preview-modal__text-container">
        <h4 className="hue-ai-preview-modal__text-container-title">
          {explanation ? 'Explanation' : 'Assumptions'}
        </h4>
        <p className="hue-ai-preview-modal__assumptions">
          {explanation ? explanation : assumptions}{' '}
        </p>
      </div>
    </Modal>
  );
};

export default PreviewModal;
