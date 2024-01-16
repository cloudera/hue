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

import React, { useState } from 'react';
import { Button } from 'antd';
import Modal from 'cuix/dist/components/Modal';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { stackoverflowDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { fluidxSlate800, fluidxSpacingS, fluidxSpacingXs } from '@cloudera/cuix-core/variables';
import { KeywordCase } from 'sql-formatter';

import { GuardrailAlert, GuardrailAlertType } from '../guardRails';
import SyntaxHighlighterDiff from '../SyntaxHighlighterDiff/SyntaxHighlighterDiff';
import InlineAlertCheck from '../InlineAlertCheck/InlineAlertCheck';
import { AiBarActionType } from '../AiAssistBar';

import { useFormatting, formatClean } from './formattingUtils';
import PreviewInfoPanels from './PreviewInfoPanels/PreviewInfoPanels';
import PreviewWarningPanels from './PreviewWarningPanels/PreviewWarningPanels';
import PreviewModalFooter from './PreviewModalFooter/PreviewModalFooter';
import SqlPreviewConfig from './SqlPreviewConfig/SqlPreviewConfig';

import './AiPreviewModal.scss';

const hasDiff = (codeA: string, codeB: string, dialect: string): boolean => {
  const cleanNew = formatClean(codeA, dialect);
  const cleanOld = formatClean(codeB, dialect);
  return cleanNew !== cleanOld;
};

interface PreviewModalProps {
  actionType: AiBarActionType;
  open: boolean;
  title: string;
  suggestion: string;
  assumptions: string;
  explanation: string;
  summary: string;
  nql?: string;
  guardrailAlert?: GuardrailAlert;
  onCancel: () => void;
  onInsert: (value: string) => void;
  primaryButtonLabel: string;
  showDiffFrom: string;
  lineNumberStart: number;
  dialect: string;
  keywordCase: KeywordCase | undefined;
}

const PreviewModal = ({
  actionType,
  open,
  title,
  suggestion: suggestionRaw = '',
  assumptions = '',
  explanation = '',
  summary = '',
  nql = '',
  guardrailAlert,
  onCancel,
  onInsert,
  primaryButtonLabel,
  showDiffFrom: showDiffFromRaw = '',
  lineNumberStart = 1,
  dialect,
  keywordCase
}: PreviewModalProps): JSX.Element => {
  const [guardRailWarningAcknowledged, setGuardRailWarningAcknowledged] = useState(false);
  const { formattingConfig, updateFormattingSettings, suggestion, showDiffFrom } = useFormatting({
    dialect,
    keywordCase,
    oldSql: showDiffFromRaw,
    newSql: suggestionRaw,
    nql
  });

  if (actionType === 'optimize' || actionType === 'fix' || actionType === 'edit') {
    const diffDetected = hasDiff(suggestionRaw, showDiffFromRaw, dialect);
    if (!diffDetected) {
      return (
        <Modal
          wrapClassName="cuix hue-ai-preview-modal hue-ai-preview-modal--no-diff"
          open={open}
          title={'No change suggested'}
          onCancel={onCancel}
          width={'100ch'}
          footer={
            <div className="hue-ai-preview-modal__footer">
              <Button key="submit" type="primary" onClick={onCancel}>
                OK
              </Button>
            </div>
          }
        >
          <p>
            {actionType === 'optimize'
              ? `No optimization to the SQL statement could be suggested.`
              : actionType === 'fix'
              ? `No fix to the SQL statement could be suggested.`
              : `The SQL statement could not be edited based on the input given. The AI has returned an unmodified SQL statement.`}
          </p>
          <PreviewInfoPanels
            alternativeActions={explanation || 'No alternative actions could be suggested'}
          />
        </Modal>
      );
    }
  }

  const unsafeSql = guardrailAlert?.type === GuardrailAlertType.UNSAFE_SQL;
  const hallucinatedSql = guardrailAlert?.type === GuardrailAlertType.HALLUCINATION;
  const syntaxtError = guardrailAlert?.type === GuardrailAlertType.SYNTAX_ERROR;
  const hasGuardRailWarning = unsafeSql || hallucinatedSql || syntaxtError;

  return (
    <Modal
      wrapClassName="cuix hue-ai-preview-modal"
      open={open}
      title={title}
      onCancel={onCancel}
      width={'80%'}
      footer={
        <PreviewModalFooter
          primaryButtonLabel={primaryButtonLabel}
          disableActions={hasGuardRailWarning && !guardRailWarningAcknowledged}
          showCopyToClipboard={actionType !== 'explain'}
          onPrimaryBtnClick={() => onInsert(suggestion)}
          onCancelBtnClick={onCancel}
          suggestion={suggestion}
        />
      }
    >
      <div className="hue-ai-preview-modal__diff-highlighter">
        {actionType !== 'explain' && (
          <SqlPreviewConfig
            actionType={actionType}
            formattingConfig={formattingConfig}
            updateFormattingConfig={updateFormattingSettings}
          />
        )}

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
      {!hallucinatedSql && (
        <PreviewInfoPanels
          summary={summary}
          explanation={explanation}
          assumptions={assumptions}
          guardrailAlert={guardrailAlert}
        />
      )}
      {hallucinatedSql && <PreviewWarningPanels guardrailAlert={guardrailAlert} />}
      <InlineAlertCheck
        show={hasGuardRailWarning}
        msg={guardrailAlert?.confirmationText}
        checkboxLabel="I understand this SQL"
        onCheckboxChange={setGuardRailWarningAcknowledged}
      />
    </Modal>
  );
};

export default PreviewModal;
