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
import { Checkbox } from 'antd';
import { CheckboxChangeEvent } from 'antd/lib/checkbox';
import Alert from 'cuix/dist/components/Alert/Alert';

import './InlineAlertCheck.scss';

export interface InlineAlertCheckProps {
  show: boolean;
  onCheckboxChange: (checked: boolean) => void;
  msg: string | undefined;
  checkboxLabel: string;
}

const InlineAlertCheck = ({
  show,
  onCheckboxChange,
  msg,
  checkboxLabel
}: InlineAlertCheckProps): JSX.Element | null => {
  return show ? (
    <div className="hue-inline-alert-check">
      <Alert
        description={
          <>
            <p>{msg}</p>
            <Checkbox
              onChange={(e: CheckboxChangeEvent) => {
                onCheckboxChange(e.target.checked);
              }}
            >
              {checkboxLabel}
            </Checkbox>
          </>
        }
        type="warning"
      />
    </div>
  ) : null;
};

export default InlineAlertCheck;
