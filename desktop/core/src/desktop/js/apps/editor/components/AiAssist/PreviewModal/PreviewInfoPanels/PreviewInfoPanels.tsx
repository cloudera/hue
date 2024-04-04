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

import React from 'react';
import LinkButton from 'cuix/dist/components/Button/LinkButton';

import { GuardrailAlert, GuardrailAlertType } from '../../guardRails';

import './PreviewInfoPanels.scss';

export interface PreviewInfoPanelsProps {
  explanation?: string;
  summary?: string;
  assumptions?: string;
  alternativeActions?: string;
  guardrailAlert?: GuardrailAlert;
  isCaseInsensitive?: boolean;
  onToggleCaseInsensitive: () => void;
}

const PreviewInfoPanels = ({
  alternativeActions,
  explanation,
  summary,
  assumptions,
  guardrailAlert,
  isCaseInsensitive,
  onToggleCaseInsensitive
}: PreviewInfoPanelsProps): JSX.Element | null => {
  const unsafeSqlDetected = guardrailAlert?.type === GuardrailAlertType.UNSAFE_SQL;
  const hasGuardRailSuggestions = guardrailAlert?.type === GuardrailAlertType.SUGGESTED_IMPROVEMENT;
  return explanation ||
    assumptions ||
    unsafeSqlDetected ||
    alternativeActions ||
    hasGuardRailSuggestions ? (
    <div className="hue-preview-info-panels">
      {hasGuardRailSuggestions && (
        <p>
          {isCaseInsensitive
            ? 'This query has been transformed to use case insensitive pattern matching on string based values for better results.'
            : 'This query can be transformed to use case insensitive pattern matching on string based values for better results.'}
          <LinkButton
            className="hue-preview-info-panels__toggle-pattern-matching-button"
            data-event=""
            onClick={() => {
              onToggleCaseInsensitive();
            }}
          >
            {isCaseInsensitive ? 'Undo' : 'Transform now'}
          </LinkButton>
        </p>
      )}
      {(explanation || assumptions) && (
        <>
          {summary && (
            <>
              <h4 className="hue-preview-info__title">Summary</h4>
              <p className="hue-preview-info__text-container">{summary}</p>
            </>
          )}
          <h4 className="hue-preview-info__title">{explanation ? 'Explanation' : 'Assumptions'}</h4>
          <p className="hue-preview-info__text-container">
            {explanation ? explanation : assumptions}{' '}
          </p>
        </>
      )}
      {unsafeSqlDetected && (
        <>
          <h4 className="hue-preview-info__title">Additional info</h4>
          <p className="hue-preview-info__text-container">{guardrailAlert?.aiMsg}</p>
        </>
      )}
      {alternativeActions && (
        <>
          <h4 className="hue-preview-info__title">Alternative actions</h4>
          <p className="hue-preview-info__text-container">{alternativeActions}</p>
        </>
      )}
    </div>
  ) : null;
};

export default PreviewInfoPanels;
