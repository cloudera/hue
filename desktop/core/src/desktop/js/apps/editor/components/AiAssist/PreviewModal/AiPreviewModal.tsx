import React, { useState, FunctionComponent } from 'react';
// import { Button } from 'antd';
import { Button } from 'antd';
import LinkButton from 'cuix/dist/components/Button/LinkButton';
import DefaultButton from 'cuix/dist/components/Button/Button';
import Modal from 'cuix/dist/components/Modal';
import execCommandCopy from 'copy-to-clipboard';
import PrimaryButton from 'cuix/dist/components/Button/PrimaryButton';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { stackoverflowDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { fluidxSlate800, fluidxSpacingS, fluidxSpacingXs } from '@cloudera/cuix-core/variables';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import CheckmarkIcon from '@cloudera/cuix-core/icons/react/CheckmarkIcon';
import { diffLines, Change } from 'diff';
import classNames from 'classnames';

import SyntaxHighlighterDiff from '../SyntaxHighlighterDiff/SyntaxHighlighterDiff';

import './AiPreviewModal.scss';

const PreviewModal = ({
  open,
  title,
  suggestion = '',
  assumptions = '',
  explanation = '',
  onCancel,
  onInsert,
  primaryButtonLabel,
  showDiffFrom = '',
  lineNumberStart = 1,
  showCopyToClipboard = true
}) => {
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

  const [copied, setCopied] = useState(false);

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
