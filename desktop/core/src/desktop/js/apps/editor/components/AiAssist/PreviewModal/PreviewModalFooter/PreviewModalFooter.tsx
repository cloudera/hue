import React, { useState } from 'react';
import { Button } from 'antd';
import execCommandCopy from 'copy-to-clipboard';
import DefaultButton from 'cuix/dist/components/Button/Button';
import CopyClipboardIcon from '@cloudera/cuix-core/icons/react/CopyClipboardIcon';
import CheckmarkIcon from '@cloudera/cuix-core/icons/react/CheckmarkIcon';

import './PreviewModalFooter.scss';

export interface PreviewModalFooterProps {
  disableActions: boolean;
  onPrimaryBtnClick: () => void;
  onCancelBtnClick: () => void;
  primaryButtonLabel: string;
  showCopyToClipboard: boolean;
  suggestion: string;
}

const PreviewModalFooter = ({
  disableActions,
  onPrimaryBtnClick,
  onCancelBtnClick,
  primaryButtonLabel,
  showCopyToClipboard,
  suggestion
}: PreviewModalFooterProps) => {
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

  const resetCopyState = (): void => {
    setCopied(false);
  };

  return (
    <div className="hue-preview-modal-footer">
      <Button
        disabled={disableActions}
        key="submit"
        type="primary"
        onClick={() => {
          onPrimaryBtnClick();
          resetCopyState();
        }}
      >
        {primaryButtonLabel}
      </Button>

      {showCopyToClipboard && (
        <DefaultButton
          disabled={disableActions}
          data-event=""
          icon={
            copied ? (
              <CheckmarkIcon className="hue-preview-modal-footer__copy-button-icon" />
            ) : (
              <CopyClipboardIcon />
            )
          }
          onClick={() => {
            copyToClipboard(suggestion);
          }}
        >
          Copy to clipboard
        </DefaultButton>
      )}

      <div className="hue-preview-modal-footer__spacer"></div>
      <DefaultButton
        data-event=""
        onClick={() => {
          onCancelBtnClick();
          resetCopyState();
        }}
      >
        Cancel
      </DefaultButton>
    </div>
  );
};

export default PreviewModalFooter;
