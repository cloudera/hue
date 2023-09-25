import React from 'react';
import Switch from 'cuix/dist/components/Switch';

import { FormattingConfig } from '../FormattingUtils';
import { AiBarActionType } from '../../AiAssistBar';

import './SqlPreviewConfig.scss';

export interface SqlPreviewConfigProps {
  formattingConfig: FormattingConfig;
  updateFormattingConfig: (FormattingConfig) => void;
  actionType: AiBarActionType;
}

const SqlPreviewConfig = ({
  formattingConfig,
  updateFormattingConfig,
  actionType
}: SqlPreviewConfigProps) => {
  const { autoFormat, includeNql, replaceNql } = formattingConfig;
  return (
    <div className="hue-sql-preview-config">
      <Switch
        checked={autoFormat}
        onChange={(autoFormat: boolean) => {
          updateFormattingConfig({ ...formattingConfig, autoFormat });
        }}
        className="hue-sql-preview-config__switch"
        label="Autoformat SQL"
      />
      {(actionType === 'edit' || actionType === 'generate') && (
        <>
          <Switch
            checked={includeNql}
            onChange={(includeNql: boolean) => {
              updateFormattingConfig({ ...formattingConfig, includeNql });
            }}
            className="hue-sql-preview-config__switch"
            label="Include prompt as comment"
          />
          <Switch
            checked={replaceNql}
            onChange={(replaceNql: boolean) => {
              updateFormattingConfig({ ...formattingConfig, replaceNql });
            }}
            className="hue-sql-preview-config__switch"
            label="Replace comments"
          />
        </>
      )}
    </div>
  );
};

export default SqlPreviewConfig;
