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
import { GuardrailAlert } from '../../guardRails';

import './PreviewWarningPanels.scss';

export interface PreviewWarningPanelsProps {
  guardrailAlert: GuardrailAlert;
}

const PreviewWarningPanels = ({ guardrailAlert }: PreviewWarningPanelsProps): JSX.Element => {
  return (
    <div className="hue-preview-warning-panels">
      <h4 className="hue-preview-warning__title">{guardrailAlert.title}</h4>
      <p className="hue-preview-warning__text-container">{guardrailAlert.msg}</p>

      {guardrailAlert.actions && (
        <>
          <h4 className="hue-preview-warning__actions-title">Alternative actions</h4>
          <ul className="hue-preview-warning__action-container">
            {guardrailAlert.actions.map((action, index) => (
              <li key={index}>{action}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};

export default PreviewWarningPanels;
