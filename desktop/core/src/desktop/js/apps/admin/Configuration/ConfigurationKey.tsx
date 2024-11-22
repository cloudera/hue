// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import React from 'react';
import { Tooltip } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { AdminConfigValue } from './ConfigurationTab';
import './Configuration.scss';

export const ConfigurationKey: React.FC<{ record: AdminConfigValue }> = ({ record }) => {
  if (record.is_anonymous) {
    return (
      <div>
        Default section
        {record.help && (
          <Tooltip title={record.help}>
            <InfoCircleOutlined className="config__help-tooltip" />
          </Tooltip>
        )}
      </div>
    );
  }
  if (record?.values) {
    return (
      <span>
        <span className="config__main-item--heading">{record.key}</span>
        {record.help && (
          <Tooltip title={record.help}>
            <InfoCircleOutlined className="config__help-tooltip" />
          </Tooltip>
        )}
      </span>
    );
  } else {
    return (
      <span>
        <span className="config--last-heading">{record.key}</span>
        {record.value && <span className="config__set-value">{record.value}</span>}
        <div>
          <span className="config__last-item--help-text">{record.help}</span>
          <span className="last-config-key">
            {record.default && (
              <span className="config__default-value">Default: {record.default}</span>
            )}
          </span>
        </div>
      </span>
    );
  }
};
