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
import Switch from 'cuix/dist/components/Switch';

import { FormattingConfig } from '../formattingUtils';
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
}: SqlPreviewConfigProps): JSX.Element => {
  const { autoFormat, includeNql, replaceNql } = formattingConfig;
  return (
    <div className="hue-sql-preview-config">
      <Switch
        disabled={actionType === 'fix'}
        checked={autoFormat}
        onChange={(autoFormat: boolean) => {
          updateFormattingConfig({ ...formattingConfig, autoFormat });
        }}
        className="hue-sql-preview-config__switch"
        label="Autoformat SQL"
        title={actionType === 'fix' ? 'Autoformat is not available for SQL containing errors' : ''}
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
