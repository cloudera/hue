import React from 'react';
import { GuardrailAlert, GuardrailAlertType } from '../../guardRails';

import './PreviewInfoPanels.scss';

export interface PreviewInfoPanelsProps {
  explanation: string;
  assumptions: string;
  guardrailAlert?: GuardrailAlert;
}

const PreviewInfoPanels = ({
  explanation,
  assumptions,
  guardrailAlert
}: PreviewInfoPanelsProps) => {
  const unsafeSqlDetected = guardrailAlert?.type === GuardrailAlertType.UNSAFE_SQL;
  return explanation || assumptions || unsafeSqlDetected ? (
    <div className="hue-preview-info-panels">
      {(explanation || assumptions) && (
        <>
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
    </div>
  ) : null;
};

export default PreviewInfoPanels;
