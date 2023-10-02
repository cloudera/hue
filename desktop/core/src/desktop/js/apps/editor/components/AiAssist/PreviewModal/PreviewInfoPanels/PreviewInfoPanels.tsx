import React from 'react';
import { GuardrailAlert, GuardrailAlertType } from '../../guardRails';

import './PreviewInfoPanels.scss';

export interface PreviewInfoPanelsProps {
  explanation?: string;
  summary?: string;
  assumptions?: string;
  alternativeActions?: string;
  guardrailAlert?: GuardrailAlert;
}

const PreviewInfoPanels = ({
  alternativeActions,
  explanation,
  summary,
  assumptions,
  guardrailAlert
}: PreviewInfoPanelsProps) => {
  const unsafeSqlDetected = guardrailAlert?.type === GuardrailAlertType.UNSAFE_SQL;
  return explanation || assumptions || unsafeSqlDetected || alternativeActions ? (
    <div className="hue-preview-info-panels">
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
